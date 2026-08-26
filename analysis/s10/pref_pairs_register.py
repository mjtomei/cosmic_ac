#!/usr/bin/env python3
"""Does the PREFERENCE DATA itself carry the assistant register?

§4.7 attributes the register to the post-training stages tuned toward human
demonstrations and preferences. That attribution is currently indirect: it is
read off the OLMo-2 checkpoints' OUTPUT, one stage at a time. If the claim is
right, the register should also be visible in the stages' INPUT -- in the
preference pairs themselves, before any model has been trained on them. A
chosen response should carry more of Kobak's style vocabulary than the
response it beat.

That is a directly checkable, cheap, CPU-only proposition, and it is the arm
that would falsify the story: if chosen and rejected responses carry the
register equally, then whatever DPO installs, it did not read it off the
preference labels.

DATA

  allenai/olmo-2-1124-7b-preference-mix     the actual DPO data for
                                            OLMo-2-1124-7B-DPO, i.e. the exact
                                            input to the ladder's DPO stage
  allenai/llama-3.1-tulu-3-8b-preference-mixture
                                            the Tulu-3 8B mixture the OLMo-2
                                            recipe is built from

Both are public parquet on the Hub; the shards are cached under tulu_prefs/
and never committed (that directory self-ignores).

WHAT IS MEASURED

For each pair, the register rate of the final assistant turn:

    rate = 1,000 * (style-word tokens) / (tokens)      tokens = [a-z']+

and the within-pair difference chosen - rejected. A rate difference is
already length-normalised, so a chosen response that is merely LONGER cannot
score higher on it. Three further length controls are run anyway, because
length and register co-vary in generated text:

  1. restrict to pairs whose absolute token-count difference is below the
     median -- the near-equal-length half of the corpus
  2. regress the within-pair rate difference on the within-pair log-length
     difference. The intercept is the length-neutral difference; the slope
     says how much length carries; R^2 says how much of the difference is
     length at all
  3. truncate BOTH responses to the shorter one's token count and recompute,
     so the two sides have identical length pair by pair (the same rule
     ladder_length_control.py applies to the OLMo generations)

PLACEBO

The same statistic on frequency-matched control words -- 10 independent lists
drawn to match the style words' corpus-frequency profile. If the procedure
returns a difference on word lists with no special property, the style-word
difference is a pedestal and means nothing. This is the correction the
rlhf_pref/olmo_ladder arms needed (M3/M9), applied here from the start.

CONFOUND, NAMED

In these mixtures the chosen and rejected responses usually come from
DIFFERENT models, and the preference label is mostly an LLM judge's rating,
not a human's. A raw chosen-vs-rejected difference can therefore be an
artifact of which models were sampled. The SAME-MODEL subset (chosen_model ==
rejected_model, available in the OLMo-2 mixture) removes that: two samples
from one model, one preferred. It is reported separately and is the figure to
quote.

Usage:
  python pref_pairs_register.py                 # both mixtures, all pairs
  python pref_pairs_register.py --sample 100000 # deterministic subsample
  python pref_pairs_register.py --dataset olmo2
"""
import argparse
import csv
import glob
import math
import os
import random
import re
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "tulu_prefs")
TOK = re.compile(r"[a-z']+")
MIN_TOK = 5          # a 0-4 word response has no meaningful rate
NCTL = 10            # frequency-matched control lists
SEED = 5

DATASETS = {
    "olmo2": ("allenai/olmo-2-1124-7b-preference-mix", "olmo2_train-*.parquet"),
    "tulu3": ("allenai/llama-3.1-tulu-3-8b-preference-mixture",
              "tulu3_train-*.parquet"),
}

_WMAP = None         # word -> (is_style, tuple of control-list indices)


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def last_assistant(msgs):
    """chosen/rejected are conversations; the pair differs in the final
    assistant turn, so that is what is scored."""
    if not msgs:
        return ""
    for m in reversed(msgs):
        if m.get("role") == "assistant":
            return m.get("content") or ""
    return msgs[-1].get("content") or ""


# ------------------------------------------------------------------ pass A
def freq_worker(job):
    path, groups = job
    import pyarrow.parquet as pq
    f = pq.ParquetFile(path)
    c = Counter()
    for g in groups:
        t = f.read_row_group(g, columns=["chosen", "rejected"]).to_pylist()
        for r in t:
            for side in ("chosen", "rejected"):
                c.update(TOK.findall(last_assistant(r[side]).lower()))
    return c


def build_controls(paths, style, nproc):
    """Corpus word frequencies from a few row groups per shard, then NCTL
    control lists matched on int(log2(count+1)) -- the symmetric bucketing
    the corrected estimator uses."""
    jobs = []
    import pyarrow.parquet as pq
    for p in paths:
        ng = pq.ParquetFile(p).metadata.num_row_groups
        jobs.append((p, list(range(0, ng, max(1, ng // 4)))[:4]))
    with Pool(min(nproc, len(jobs))) as pool:
        tot = Counter()
        for c in pool.imap(freq_worker, jobs):
            tot.update(c)
    sset = set(style)
    # SORTED: the control draw must not depend on dict insertion order (which
    # depends on which worker finished first) or on PYTHONHASHSEED.
    cand = sorted(w for w in tot if len(w) >= 4 and w.isalpha() and w not in sset)
    bk = defaultdict(list)
    for w in cand:
        bk[int(math.log2(tot[w] + 1))].append(w)

    def pool_for(x):
        for o in (0, 1, -1, 2, -2, 3, -3):
            if bk.get(x + o):
                return bk[x + o]
        return max(bk.values(), key=len)
    present = [w for w in style if tot[w] > 0]
    rng = random.Random(SEED)
    lists = [[rng.choice(pool_for(int(math.log2(tot[w] + 1)))) for w in present]
             for _ in range(NCTL)]
    wmap = {}
    for w in present:
        wmap[w] = (True, ())
    for j, L in enumerate(lists):
        for w in L:
            is_s, idx = wmap.get(w, (False, ()))
            wmap[w] = (is_s, idx + (j,))
    return wmap, tot, present


# ------------------------------------------------------------------ pass B
def _init(wmap):
    global _WMAP
    _WMAP = wmap


def _count(toks):
    """(style hits, per-control-list hits) over a token list."""
    s = 0
    c = [0] * NCTL
    g = _WMAP.get
    for w in toks:
        m = g(w)
        if m is not None:
            if m[0]:
                s += 1
            for j in m[1]:
                c[j] += 1
    return s, c


def score_worker(job):
    path, groups, keep, base = job
    import pyarrow.parquet as pq
    f = pq.ParquetFile(path)
    cols = ["chosen", "rejected", "source"]
    names = set(f.schema_arrow.names)
    has_model = "chosen_model" in names and "rejected_model" in names
    if has_model:
        cols += ["chosen_model", "rejected_model"]
    rows, srcs, mods, dropped = [], [], [], [0, 0, 0]   # both, chosen, rejected
    for g in groups:
        t = f.read_row_group(g, columns=cols).to_pylist()
        for i, r in enumerate(t):
            gi = base + i
            if keep is not None and gi not in keep:
                continue
            tc = TOK.findall(last_assistant(r["chosen"]).lower())
            tr = TOK.findall(last_assistant(r["rejected"]).lower())
            if len(tc) < MIN_TOK or len(tr) < MIN_TOK:
                # which side was degenerate matters: dropping short REJECTED
                # responses removes the most obviously bad negatives, which is
                # a selection the reader should see
                dropped[0 if (len(tc) < MIN_TOK and len(tr) < MIN_TOK)
                        else (1 if len(tc) < MIN_TOK else 2)] += 1
                continue
            sc, cc = _count(tc)
            sr, cr = _count(tr)
            L = min(len(tc), len(tr))
            sct, cct = _count(tc[:L])
            srt, crt = _count(tr[:L])
            cmod = r.get("chosen_model") if has_model else None
            rmod = r.get("rejected_model") if has_model else None
            # both-null must NOT count as "same model"
            same = bool(cmod) and bool(rmod) and cmod == rmod
            rows.append([len(tc), len(tr), sc, sr, sct, srt, int(same)]
                        + cc + cr + cct + crt)
            srcs.append(r.get("source") or "(unlabelled)")
            mods.append((cmod or "?", rmod or "?"))
        base += len(t)
    return (np.array(rows, dtype=np.int32) if rows
            else np.zeros((0, 7 + 4 * NCTL), dtype=np.int32)), srcs, mods, dropped


# ------------------------------------------------------------------- stats
def boot_ci(d, seed=SEED, B=2000, chunk=20):
    """Pair bootstrap: resample PAIRS, which is the unit of the design.

    Chunked because n runs to 3e5 here and a (B, n) index matrix would be
    several GB."""
    rng = np.random.default_rng(seed)
    n = len(d)
    if n == 0:
        return float("nan"), float("nan")
    d = np.asarray(d, dtype=np.float64)
    m = np.empty(B)
    for i in range(0, B, chunk):
        k = min(chunk, B - i)
        idx = rng.integers(0, n, size=(k, n))
        m[i:i + k] = d[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def ols(y, X):
    b = np.linalg.pinv(X.T @ X) @ (X.T @ y)
    r = y - X @ b
    n, k = X.shape
    s2 = float(r @ r) / (n - k)
    V = s2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(V))
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float(r @ r) / ss if ss else float("nan")
    return b, se, r2


def report_block(label, dc, dr, nc, nr):
    """dc, dr: per-pair chosen/rejected rates already computed."""
    d = dc - dr
    lo, hi = boot_ci(d)
    win = float((d > 0).mean())
    tie = float((d == 0).mean())
    nz = int((d != 0).sum())
    wex = float((d > 0).sum()) / max(1, nz)
    wlo, whi = boot_ci((d[d != 0] > 0).astype(float)) if nz else (0.0, 0.0)
    print(f"  {label}")
    print(f"    n = {len(d):,} pairs   chosen {dc.mean():.3f} vs rejected "
          f"{dr.mean():.3f} style words per 1,000")
    print(f"    mean within-pair delta {d.mean():+.4f} per 1,000  "
          f"95% pair-bootstrap CI [{lo:+.4f}, {hi:+.4f}]")
    print(f"    win-rate of the higher-register member (chosen higher): "
          f"{100*win:.2f}%   ties {100*tie:.2f}%   excluding ties "
          f"{100*wex:.2f}%  CI [{100*wlo:.2f}%, {100*whi:.2f}%]")
    print(f"    mean tokens: chosen {nc.mean():.1f}  rejected {nr.mean():.1f}  "
          f"(chosen longer in {100*float((nc>nr).mean()):.1f}% of pairs)")
    return d


def reciprocal_balance(d, mods, minn=20):
    """The strongest available control on model identity.

    In these mixtures the chosen response usually comes from a stronger model
    than the rejected one (gpt-4 / Qwen-32B vs falcon-7b / SmolLM2-1.7B), so a
    raw chosen-minus-rejected difference could be nothing but "the better
    model writes more register words". Some ordered model pairs (A over B)
    also occur in the OTHER direction (B over A). If the difference is a
    preference for register, both directions are positive and their average
    stays positive. If it is model identity, the two directions cancel.
    """
    cell = defaultdict(list)
    for i, (a, b) in enumerate(mods):
        cell[(a, b)].append(i)
    out = []
    seen = set()
    for (a, b), idx in cell.items():
        if a == b:            # a self-cell has no other direction
            continue
        if (b, a) in seen or (b, a) not in cell:
            continue
        rev = cell[(b, a)]
        if len(idx) < minn or len(rev) < minn:
            continue
        seen.add((a, b))
        out.append((a, b, len(idx), len(rev),
                    float(d[idx].mean()), float(d[rev].mean())))
    return out


def analyse(name, ds_id, R, srcs, mods, present, nsrc_show=10):
    nc = R[:, 0].astype(float)
    nr = R[:, 1].astype(float)
    rc = 1000.0 * R[:, 2] / nc
    rr = 1000.0 * R[:, 3] / nr
    L = np.minimum(nc, nr)
    rct = 1000.0 * R[:, 4] / L
    rrt = 1000.0 * R[:, 5] / L
    same = R[:, 6].astype(bool)
    C = R[:, 7:]
    cc = C[:, 0:NCTL].astype(float)
    cr = C[:, NCTL:2 * NCTL].astype(float)
    cct = C[:, 2 * NCTL:3 * NCTL].astype(float)
    crt = C[:, 3 * NCTL:4 * NCTL].astype(float)

    print(f"\n{'='*78}\n{name}   {ds_id}\n{'='*78}")
    print(f"  {len(R):,} pairs scored, {len(present)} of the 407 style words "
          f"present in the corpus")
    print(f"  {int(nc.sum()+nr.sum()):,} response tokens scored "
          f"(chosen {int(nc.sum()):,} + rejected {int(nr.sum()):,})\n")

    print("=== (a) the headline: within-pair difference in register RATE ===")
    print("    a rate is per-1,000-words, so it is already length-normalised")
    d_all = report_block("ALL PAIRS", rc, rr, nc, nr)

    print("\n=== placebo: the same statistic on frequency-matched controls ===")
    pl = (1000.0 * cc / nc[:, None]) - (1000.0 * cr / nr[:, None])
    per = pl.mean(axis=0)
    lo, hi = boot_ci(pl.mean(axis=1))
    print(f"  {NCTL} control lists, each matched to the style words' frequency "
          f"profile")
    print(f"  mean control delta {per.mean():+.4f} per 1,000  "
          f"[{lo:+.4f}, {hi:+.4f}]   per-list range "
          f"{per.min():+.4f} .. {per.max():+.4f}, "
          f"{int((per > 0).sum())}/{NCTL} positive")
    print(f"  -> style-word delta MINUS control pedestal: "
          f"{d_all.mean() - per.mean():+.4f} per 1,000")

    print("\n=== (c1) length control I: near-equal-length pairs only ===")
    ad = np.abs(nc - nr)
    med = float(np.median(ad))
    m = ad < med
    print(f"  median |token difference| = {med:.0f}; keeping the "
          f"{int(m.sum()):,} pairs strictly below it")
    report_block("|len diff| BELOW MEDIAN", rc[m], rr[m], nc[m], nr[m])
    lad = np.abs(np.log(nc) - np.log(nr))
    m2 = lad < 0.05
    if m2.sum() > 100:
        report_block("|log-length ratio| < 0.05 (within 5% on length)",
                     rc[m2], rr[m2], nc[m2], nr[m2])

    print("\n=== (c2) length control II: truncate both sides to the shorter ===")
    print("    both responses cut to their first min(n_chosen, n_rejected) "
          "tokens, so lengths are identical pair by pair")
    report_block("TRUNCATED TO COMMON LENGTH", rct, rrt, L, L)
    plt_ = (1000.0 * cct / L[:, None]) - (1000.0 * crt / L[:, None])
    print(f"    control placebo on the truncated text: "
          f"{plt_.mean():+.4f} per 1,000")

    print("\n=== (c3) length control III: regress the pair difference on "
          "the pair's log-length difference ===")
    x = np.log(nc) - np.log(nr)
    X = np.column_stack([np.ones(len(x)), x])
    b, se, r2 = ols(d_all, X)
    print(f"  delta_rate_i = a + b * (log n_chosen - log n_rejected)")
    print(f"    a (intercept: length-neutral difference) {b[0]:+.4f}  "
          f"SE {se[0]:.4f}  t {b[0]/se[0]:+.1f}")
    print(f"    b (slope on log-length difference)       {b[1]:+.4f}  "
          f"SE {se[1]:.4f}  t {b[1]/se[1]:+.1f}")
    print(f"    R^2 = {r2:.4f}   -> length explains {100*r2:.1f}% of the "
          f"within-pair register difference")
    print(f"    mean log-length difference {x.mean():+.4f}; the part of the "
          f"raw delta attributable to it: {b[1]*x.mean():+.4f} of "
          f"{d_all.mean():+.4f}")

    print("\n=== the model-identity confound ===")
    if same.any():
        print(f"  {int(same.sum()):,} pairs have chosen_model == rejected_model "
              f"({100*float(same.mean()):.1f}%) -- two samples from ONE model, "
              f"one preferred. This is the figure to quote.")
        report_block("SAME MODEL both sides", rc[same], rr[same],
                     nc[same], nr[same])
        pls = pl[same].mean(axis=1)
        lo, hi = boot_ci(pls)
        print(f"    control placebo on the same-model subset: "
              f"{pls.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]")
        st = same & (np.abs(nc - nr) < np.median(np.abs(nc - nr)[same]))
        report_block("SAME MODEL, |len diff| below its median", rc[st], rr[st],
                     nc[st], nr[st])
        report_block("SAME MODEL, truncated to common length", rct[same],
                     rrt[same], L[same], L[same])
        b2, se2, r22 = ols((rc - rr)[same],
                           np.column_stack([np.ones(int(same.sum())),
                                            x[same]]))
        print(f"    same-model regression: intercept {b2[0]:+.4f} "
              f"(SE {se2[0]:.4f}), slope {b2[1]:+.4f} (SE {se2[1]:.4f}), "
              f"R^2 {r22:.4f}")
        if (~same).any():
            report_block("DIFFERENT models", rc[~same], rr[~same],
                         nc[~same], nr[~same])
        rb = reciprocal_balance(d_all, mods)
        if rb:
            tot_n = sum(r[2] + r[3] for r in rb)
            fwd = sum(r[4] * r[2] for r in rb) / sum(r[2] for r in rb)
            rev = sum(r[5] * r[3] for r in rb) / sum(r[3] for r in rb)
            bal = np.array([(r[4] + r[5]) / 2 for r in rb])
            wt = np.array([min(r[2], r[3]) for r in rb], dtype=float)
            print(f"\n  reciprocal model-pair balance: {len(rb)} ordered model "
                  f"pairs (>=20 each way, self-pairs excluded), {tot_n:,} "
                  f"pairs total")
            print(f"    A-over-B mean delta {fwd:+.4f}; B-over-A mean delta "
                  f"{rev:+.4f}")
            print(f"    direction-balanced (average of the two directions): "
                  f"mean over cells {bal.mean():+.4f}, median "
                  f"{np.median(bal):+.4f}, weighted by min(n) "
                  f"{float((bal*wt).sum()/wt.sum()):+.4f}; "
                  f"{int((bal > 0).sum())}/{len(bal)} cells positive")
            print(f"    -> if the difference were model identity, the two "
                  f"directions would be opposite in sign and cancel")
    else:
        print("  this mixture does not record chosen_model/rejected_model, so "
              "the same-model control cannot be run here")

    print("\n=== by source subset (largest first) ===")
    S = np.array(srcs)
    order = [s for s, _ in Counter(srcs).most_common(nsrc_show)]
    dt = rct - rrt
    print(f"  {'source':<50s} {'n':>8s} {'delta':>9s} {'trunc':>9s} {'win%':>7s}")
    for s in order:
        m = S == s
        d = (rc - rr)[m]
        print(f"  {s[:50]:<50s} {int(m.sum()):>8,d} {d.mean():>+9.3f} "
              f"{dt[m].mean():>+9.3f} {100*float((d>0).mean()):>7.2f}")
    return d_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="both",
                    choices=["olmo2", "tulu3", "both"])
    ap.add_argument("--sample", type=int, default=0,
                    help="deterministic pair subsample (seed 5); 0 = all")
    ap.add_argument("--nproc", type=int, default=12)
    a = ap.parse_args()
    style = load_style()
    names = ["olmo2", "tulu3"] if a.dataset == "both" else [a.dataset]
    print(f"preference-pair register scan")
    print(f"  {len(style)} style words (kobak_excess_words.csv, type=style)")
    print(f"  cache: {CACHE}")
    for nm in names:
        ds_id, pat = DATASETS[nm]
        paths = sorted(glob.glob(os.path.join(CACHE, pat)))
        if not paths:
            print(f"  {nm}: no shards on disk, skipping")
            continue
        import pyarrow.parquet as pq
        meta = [(p, pq.ParquetFile(p)) for p in paths]
        nrows = sum(f.metadata.num_rows for _, f in meta)
        print(f"\n  {nm}: {len(paths)} shards, {nrows:,} rows on disk")
        keep = None
        if a.sample and a.sample < nrows:
            rng = random.Random(SEED)
            sel = set(rng.sample(range(nrows), a.sample))
            keep, off = {}, 0
            for p, f in meta:
                n = f.metadata.num_rows
                keep[p] = {i - off for i in sel if off <= i < off + n}
                off += n
            print(f"    deterministic subsample: {a.sample:,} of {nrows:,} "
                  f"pairs (seed {SEED})")
        wmap, tot, present = build_controls(paths, style, a.nproc)
        jobs = []
        for p, f in meta:
            ng = f.metadata.num_row_groups
            # row offset of each group within its shard: `keep` holds
            # shard-local row indices, and a worker gets a contiguous slice of
            # groups that need not start at group 0.
            off, offs = 0, []
            for i in range(ng):
                offs.append(off)
                off += f.metadata.row_group(i).num_rows
            step = max(1, ng // max(1, a.nproc // len(paths) + 1))
            for i in range(0, ng, step):
                jobs.append((p, list(range(i, min(i + step, ng))),
                             keep[p] if keep else None, offs[i]))
        with Pool(a.nproc, initializer=_init, initargs=(wmap,)) as pool:
            parts = list(pool.imap(score_worker, jobs))
        R = np.concatenate([p[0] for p in parts if len(p[0])])
        srcs = [s for p in parts for s in p[1]]
        mods = [m for p in parts for m in p[2]]
        drop = [sum(p[3][k] for p in parts) for k in range(3)]
        print(f"    {sum(drop):,} pairs dropped (a side under {MIN_TOK} "
              f"tokens): {drop[0]:,} both sides, {drop[1]:,} chosen only, "
              f"{drop[2]:,} rejected only")
        analyse(nm, ds_id, R, srcs, mods, present)


if __name__ == "__main__":
    main()
