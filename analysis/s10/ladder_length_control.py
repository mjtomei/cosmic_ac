#!/usr/bin/env python3
"""Is the OLMo-2 ladder's register shift a LENGTH effect?

§4.7 attributes the assistant register to the post-training stages tuned
toward human demonstrations and preferences (SFT, DPO) and not to RLVR. The
measurement is `olmo_ladder.py report`, ARM 1: for each adjacent pair of
checkpoints, the mean log-ratio of Kobak style-word rates between the two
stages' generations, minus what the same procedure returns on
frequency-matched control words.

That estimator is already a RATE ratio, so a uniform inflation of output
length cancels. But the stages do not produce uniformly longer text -- they
produce differently SHAPED text, and register words are not spread evenly
through a continuation:

    base      102.7 words/prompt      style rate 27.2 per 1,000
    SFT        79.1                              34.9
    DPO       104.5                              42.4
    instruct  106.5                              44.0

SFT is the SHORTEST and DPO the longest, and the writeup's own null
calibration notes the per-transition pedestal was "largest at DPO only because
DPO's generations are longest". If a post-trained model front-loads a scaffold
("It is important to recognise that...") and then runs on, then two texts of
the same rate but different lengths carry the register in different places,
and the 150-new-token cap chops each stage at a different point in that
structure. A length-matched re-measurement is the direct test.

THE TRUNCATION RULE (exact)

Tokens are the analysis unit used everywhere else in this study: matches of
`[a-z']+` on the lowercased generation. For prompt i, let n_i,s be the token
count of stage s's generation. Three matched variants are computed:

  group   L_i = min over ALL FOUR stages of n_i,s; every stage's generation
          for prompt i is cut to its first L_i tokens. One corpus, usable for
          every transition and for the regression. Prompts where any stage
          emitted nothing (18 of 800) contribute zero tokens.

  pair    L_i = min(n_i,a, n_i,b) for the transition (a,b) under test only.
          Keeps more text per transition; the corpus differs per transition.

  fixedK  balanced panel: keep only prompts where all four stages reach K
          tokens, cut all four to exactly K. Guards against `group` being
          dominated by the prompts with one very short member.

Under `group` and `fixedK` the two sides of every transition have IDENTICAL
token counts, prompt by prompt, so a surviving difference cannot be length.

TWO ESTIMATORS, because the shipped one is superseded

  orig  exactly as `olmo_ladder.py report` ARM 1 ships it: control candidates
        drawn from the EARLIER checkpoint's vocabulary only and bucketed on
        int(log2(count in the earlier checkpoint)) -- the ratio's own
        denominator. This is the M3/M9 defect; its numbers (+0.76/+0.86/+0.37,
        end-to-end +1.24) are the ones in the writeup's footnote, so they are
        reproduced here for a like-for-like comparison, not endorsed.

  sym   the correction (same construction as rlhf_pref_analyze.py TEST A):
        candidates from set(a) | set(b), bucketed on the COMBINED count. The
        null pedestal is printed beside it.

The question this script answers is not "which estimator is right" but
"does either estimator's stage pattern survive equalising length". Both are
therefore run on both the full and the truncated text.

Usage: python ladder_length_control.py | tee ladder_length_control.txt
"""
import csv
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "olmo_ladder")
STAGES = ["base", "sft", "dpo", "instruct"]
# same order as olmo_ladder.TRANSITIONS -- the shared rng makes order matter
TRANSITIONS = [("base", "instruct", "END-TO-END base->instruct"),
               ("base", "sft", "instruction demonstrations"),
               ("sft", "dpo", "PREFERENCE OPTIMISATION"),
               ("dpo", "instruct", "RLVR (placebo stage)")]
TOK = re.compile(r"[a-z']+")
FIXED_K = 50


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def load_tokens():
    """{stage: [ [tok, ...] per prompt ]} -- the generations, tokenised once."""
    out = {}
    for s in STAGES:
        gens = json.load(open(os.path.join(OUT, f"{s}_gen.json")))
        out[s] = [TOK.findall(g.lower()) for g in gens]
    n = {len(v) for v in out.values()}
    assert len(n) == 1, f"stage generation counts differ: {n}"
    return out


def counts(docs):
    c, n = Counter(), 0
    for d in docs:
        c.update(d)
        n += len(d)
    return c, n


# ---------------------------------------------------------------- estimators
def excess_orig(C, N, a, b, style, sset, rng, reps=1000):
    """olmo_ladder.py report ARM 1, verbatim (asymmetric control pool)."""
    def pref(w):
        return math.log(((C[b][w] + 0.5) / N[b]) / ((C[a][w] + 0.5) / N[a]))
    cand = [w for w in C[a] if len(w) >= 4 and w.isalpha() and w not in sset]
    bk = defaultdict(list)
    for w in cand:
        bk[int(math.log2(C[a][w] + 1))].append(w)

    def pool(x):
        for o in (0, 1, -1, 2, -2, 3, -3):
            if bk.get(x + o):
                return bk[x + o]
        return max(bk.values(), key=len)
    pres = [w for w in style if C[a][w] + C[b][w] > 0]
    real = sum(pref(w) for w in pres) / len(pres)
    pools = [pool(int(math.log2(C[a][w] + 1))) for w in pres]
    draws = sorted(sum(pref(rng.choice(p)) for p in pools) / len(pools)
                   for _ in range(reps))
    med = draws[len(draws) // 2]
    return real - med, sum(1 for d in draws if d >= real) / reps, len(pres)


def excess_sym(C, N, a, b, style, sset, rng, reps=1000, nulls=20):
    """The corrected estimator: symmetric pool, bucketed on combined count."""
    def pref(w):
        return math.log(((C[b][w] + 0.5) / N[b]) / ((C[a][w] + 0.5) / N[a]))
    # SORTED: a set union iterates in hash order, which varies per process, so
    # an unsorted candidate list makes the control draw irreproducible. (The
    # `orig` estimator above is left byte-for-byte as shipped, iterating a
    # Counter, whose insertion order is deterministic -- that is what lets it
    # reproduce the writeup's +1.2412 exactly.)
    allw = set(C[a]) | set(C[b])
    cand = sorted(w for w in allw if len(w) >= 4 and w.isalpha() and w not in sset)
    bk = defaultdict(list)

    def bucket_of(w):
        return int(math.log2(C[a][w] + C[b][w] + 1))
    for w in cand:
        bk[bucket_of(w)].append(w)

    def pool(x):
        for o in (0, 1, -1, 2, -2, 3, -3):
            if bk.get(x + o):
                return bk[x + o]
        return max(bk.values(), key=len)

    def exc(words, r):
        v = sum(pref(w) for w in words) / len(words)
        pl = [pool(bucket_of(w)) for w in words]
        dr = sorted(sum(pref(rng.choice(p)) for p in pl) / len(pl)
                    for _ in range(r))
        return v - dr[len(dr) // 2], sum(1 for d in dr if d >= v) / r

    pres = [w for w in style if C[a][w] + C[b][w] > 0]
    e, p = exc(pres, reps)
    prof = [bucket_of(w) for w in pres]
    ped = []
    for s in range(nulls):
        r = random.Random(1000 + s)
        fake = [r.choice(pool(bx)) for bx in prof]
        ped.append(exc(fake, 200)[0])
    return e, p, len(pres), sum(ped) / len(ped)


# --------------------------------------------------------------- truncations
def truncate_group(T):
    n = len(T[STAGES[0]])
    L = [min(len(T[s][i]) for s in STAGES) for i in range(n)]
    return {s: [T[s][i][:L[i]] for i in range(n)] for s in STAGES}, L


def truncate_pair(T, a, b):
    n = len(T[a])
    L = [min(len(T[a][i]), len(T[b][i])) for i in range(n)]
    return {a: [T[a][i][:L[i]] for i in range(n)],
            b: [T[b][i][:L[i]] for i in range(n)]}, L


def truncate_fixed(T, k):
    n = len(T[STAGES[0]])
    keep = [i for i in range(n) if all(len(T[s][i]) >= k for s in STAGES)]
    return {s: [T[s][i][:k] for i in keep] for s in STAGES}, keep


# ------------------------------------------------------------------ printing
def paired_pref(Tf, Tt, a, b, style, sset, reps=400):
    """Per-word log-ratios for transition (a,b) on the full and the truncated
    corpus, over the SAME word set, plus each corpus's symmetric control
    median. Lets the two estimates be compared word-paired."""
    out = []
    for TT in (Tf, Tt):
        C = {s: counts(TT[s])[0] for s in (a, b)}
        N = {s: counts(TT[s])[1] for s in (a, b)}
        out.append((C, N))
    (Cf, Nf), (Ct, Nt) = out
    words = [w for w in style
             if Cf[a][w] + Cf[b][w] > 0 and Ct[a][w] + Ct[b][w] > 0]

    def mk(C, N):
        def pref(w):
            return math.log(((C[b][w] + 0.5) / N[b]) / ((C[a][w] + 0.5) / N[a]))
        cand = sorted(w for w in set(C[a]) | set(C[b])
                      if len(w) >= 4 and w.isalpha() and w not in sset)
        bk = defaultdict(list)

        def bo(w):
            return int(math.log2(C[a][w] + C[b][w] + 1))
        for w in cand:
            bk[bo(w)].append(w)

        def pool(x):
            for o in (0, 1, -1, 2, -2, 3, -3):
                if bk.get(x + o):
                    return bk[x + o]
            return max(bk.values(), key=len)
        rng = random.Random(5)
        pl = [pool(bo(w)) for w in words]
        dr = sorted(sum(pref(rng.choice(p)) for p in pl) / len(pl)
                    for _ in range(reps))
        return (np.array([pref(w) for w in words]), dr[len(dr) // 2])
    vf, cmf = mk(Cf, Nf)
    vt, cmt = mk(Ct, Nt)
    return vf, vt, cmf, cmt, words


def stage_table(label, T, style):
    sset = set(style)
    print(f"  {label}")
    print(f"    {'stage':<10s} {'prompts':>8s} {'words':>10s} {'w/prompt':>9s} "
          f"{'style/1k':>9s}")
    rates = {}
    for s in STAGES:
        c, n = counts(T[s])
        sc = sum(c[w] for w in sset if w in c)
        rates[s] = 1000.0 * sc / n if n else float("nan")
        print(f"    {s:<10s} {len(T[s]):>8d} {n:>10,d} "
              f"{n/max(len(T[s]),1):>9.1f} {rates[s]:>9.3f}")
    print(f"    rate deltas per 1,000 words: base->sft {rates['sft']-rates['base']:+.3f}"
          f"   sft->dpo {rates['dpo']-rates['sft']:+.3f}"
          f"   dpo->instruct {rates['instruct']-rates['dpo']:+.3f}"
          f"   END base->instruct {rates['instruct']-rates['base']:+.3f}")
    return rates


# --------------------------------------------------------------- regressions
def ols_cluster(y, X, cl, names):
    """OLS with cluster-robust (by prompt) SEs. Returns list of rows."""
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    r = y - X @ b
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in np.unique(cl):
        m = cl == g
        u = X[m].T @ r[m]
        meat += np.outer(u, u)
    G, n, k = len(np.unique(cl)), len(y), X.shape[1]
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    V = XtXi @ (adj * meat) @ XtXi
    se = np.sqrt(np.diag(V))
    return [(nm, b[i], se[i], b[i] / se[i]) for i, nm in enumerate(names)]


def show(rows, title):
    print(f"    {title}")
    print(f"      {'term':<26s} {'coef':>10s} {'SE':>9s} {'t':>7s}")
    for nm, c, s, t in rows:
        print(f"      {nm:<26s} {c:>+10.4f} {s:>9.4f} {t:>+7.2f}")


def control_rate_matrix(T, style, seed=5, reps=20):
    """Per-(prompt,stage) rate of frequency-matched CONTROL words, averaged
    over `reps` draws of a control list. Subtracting it turns a raw style rate
    into a per-prompt EXCESS with the estimator's pedestal removed."""
    sset = set(style)
    C, N = {}, {}
    for s in STAGES:
        C[s], N[s] = counts(T[s])
    tot = Counter()
    for s in STAGES:
        tot.update(C[s])
    cand = sorted(w for w in tot if len(w) >= 4 and w.isalpha() and w not in sset)
    bk = defaultdict(list)
    for w in cand:
        bk[int(math.log2(tot[w] + 1))].append(w)

    def pool(x):
        for o in (0, 1, -1, 2, -2, 3, -3):
            if bk.get(x + o):
                return bk[x + o]
        return max(bk.values(), key=len)
    pres = [w for w in style if tot[w] > 0]
    rng = random.Random(seed)
    lists = [[rng.choice(pool(int(math.log2(tot[w] + 1)))) for w in pres]
             for _ in range(reps)]
    n = len(T[STAGES[0]])
    out = {}
    for s in STAGES:
        col = np.zeros(n)
        for i in range(n):
            d = T[s][i]
            if not d:
                continue
            cnt = Counter(d)
            col[i] = np.mean([sum(cnt[w] for w in L) for L in lists]) / len(d) * 1000
        out[s] = col
    return out, len(pres)


def regressions(T, style, label):
    sset = set(style)
    n = len(T[STAGES[0]])
    ctl, npres = control_rate_matrix(T, style)
    rows = []
    for si, s in enumerate(STAGES):
        for i in range(n):
            d = T[s][i]
            if len(d) < 5:              # a 0-4 word generation has no rate
                continue
            sc = sum(1 for w in d if w in sset)
            rows.append((i, si, 1000.0 * sc / len(d), ctl[s][i], len(d)))
    pid = np.array([r[0] for r in rows])
    st = np.array([r[1] for r in rows])
    rate = np.array([r[2] for r in rows])
    exc = rate - np.array([r[3] for r in rows])
    ln = np.log(np.array([r[4] for r in rows], dtype=float))
    print(f"  {label}: n = {len(rows)} prompt-stage rows, "
          f"{len(np.unique(pid))} prompts, control list of {npres} "
          f"frequency-matched words (mean of 20 draws)")
    one = np.ones(len(rows))
    D = np.column_stack([(st == k).astype(float) for k in (1, 2, 3)])
    for yname, y in (("style rate /1k", rate), ("EXCESS over controls /1k", exc)):
        X = np.column_stack([one, st.astype(float), ln])
        show(ols_cluster(y, X, pid, ["const", "stage (0..3 linear)",
                                     "log(tokens)"]),
             f"{yname} ~ stage(linear) + log(tokens)   [prompt-clustered SE]")
        X = np.column_stack([one, D, ln])
        show(ols_cluster(y, X, pid,
                         ["const", "sft", "dpo", "instruct", "log(tokens)"]),
             f"{yname} ~ stage dummies + log(tokens)   [base = reference]")
        X = np.column_stack([one, D])
        show(ols_cluster(y, X, pid, ["const", "sft", "dpo", "instruct"]),
             f"{yname} ~ stage dummies, NO length term")
        # prompt fixed effects: demean everything within prompt
        yy, DD, ll = y.copy(), D.copy(), ln.copy()
        for g in np.unique(pid):
            m = pid == g
            yy[m] -= yy[m].mean()
            DD[m] -= DD[m].mean(axis=0)
            ll[m] -= ll[m].mean()
        if ll.std() < 1e-9:
            # under group/fixed truncation every stage has the SAME token
            # count within a prompt, so log(tokens) IS the prompt effect and
            # cannot be separated from it. That collinearity is the point of
            # the truncation, not a defect of the regression.
            show(ols_cluster(yy, DD, pid, ["sft", "dpo", "instruct"]),
                 f"{yname} ~ stage dummies + PROMPT FIXED EFFECTS "
                 f"(log(tokens) dropped: zero within-prompt variance after "
                 f"truncation -- perfectly collinear with the prompt effect)")
        else:
            X = np.column_stack([DD, ll])
            show(ols_cluster(yy, X, pid,
                             ["sft", "dpo", "instruct", "log(tokens)"]),
                 f"{yname} ~ stage dummies + log(tokens) + PROMPT FIXED EFFECTS")
        print()


def main():
    style = load_style()
    sset = set(style)
    T = load_tokens()
    print(f"OLMo-2 ladder, length control")
    print(f"  {len(style)} style words (kobak_excess_words.csv, type=style, alpha)")
    print(f"  generations: {os.path.join(OUT, '<stage>_gen.json')}, "
          f"{len(T['base'])} prompts x {len(STAGES)} stages\n")

    Tg, Lg = truncate_group(T)
    Tk, keep = truncate_fixed(T, FIXED_K)
    print("=== 1. corpus shape and the raw (already length-normalised) rate ===")
    r_full = stage_table("FULL text", T, style)
    print()
    r_grp = stage_table(f"TRUNCATED to the per-prompt 4-stage minimum "
                        f"(mean L = {sum(Lg)/len(Lg):.1f} tokens, "
                        f"{sum(1 for x in Lg if x == 0)} empty groups)",
                        Tg, style)
    print()
    r_fix = stage_table(f"TRUNCATED to a fixed {FIXED_K} tokens, balanced panel "
                        f"({len(keep)} of {len(T['base'])} prompts qualify)",
                        Tk, style)
    print()

    print("=== 2. stage deltas: log-ratio excess, full vs truncated ===")
    print("    'orig' = the shipped asymmetric estimator (olmo_ladder.py report,")
    print("    superseded M3/M9 defect); 'sym' = the corrected symmetric one.\n")
    res = {}
    for est, fn in (("orig", excess_orig), ("sym", excess_sym)):
        for var, TT in (("full", T), ("group", Tg), (f"fixed{FIXED_K}", Tk)):
            C = {s: counts(TT[s])[0] for s in STAGES}
            N = {s: counts(TT[s])[1] for s in STAGES}
            rng = random.Random(17)      # fresh, transitions in shipped order
            for a, b, what in TRANSITIONS:
                out = fn(C, N, a, b, style, sset, rng)
                res[(est, var, a, b)] = out
        # pairwise truncation, one corpus per transition
        rng = random.Random(17)
        for a, b, what in TRANSITIONS:
            Tp, Lp = truncate_pair(T, a, b)
            C = {s: counts(Tp[s])[0] for s in (a, b)}
            N = {s: counts(Tp[s])[1] for s in (a, b)}
            res[(est, "pair", a, b)] = fn(C, N, a, b, style, sset, rng)

    hdr = f"  {'transition':<24s}"
    for est in ("orig", "sym"):
        for var in ("full", "group", "pair", f"fixed{FIXED_K}"):
            hdr += f" {est+'/'+var:>13s}"
    print(hdr)
    for a, b, what in TRANSITIONS:
        line = f"  {a+'->'+b:<24s}"
        for est in ("orig", "sym"):
            for var in ("full", "group", "pair", f"fixed{FIXED_K}"):
                line += f" {res[(est,var,a,b)][0]:>+13.4f}"
        print(line + f"   {what}")
    print()
    print("  p-values (fraction of 1,000 control draws at or above the real value)")
    for a, b, what in TRANSITIONS:
        line = f"  {a+'->'+b:<24s}"
        for est in ("orig", "sym"):
            for var in ("full", "group", "pair", f"fixed{FIXED_K}"):
                line += f" {res[(est,var,a,b)][1]:>13.3f}"
        print(line)
    print()
    print("  style words present in the pair's two corpora (the n each mean "
          "is taken over)")
    for a, b, what in TRANSITIONS:
        line = f"  {a+'->'+b:<24s}"
        for est in ("orig", "sym"):
            for var in ("full", "group", "pair", f"fixed{FIXED_K}"):
                line += f" {res[(est,var,a,b)][2]:>13d}"
        print(line)
    print()
    print("  null pedestal of the SYMMETRIC estimator (20 random "
          "frequency-matched lists):")
    for a, b, what in TRANSITIONS:
        line = f"  {a+'->'+b:<24s}"
        for var in ("full", "group", "pair", f"fixed{FIXED_K}"):
            line += f" {res[('sym',var,a,b)][3]:>+13.4f}"
        print(line)
    print()

    print("=== 2b. is the full-vs-truncated move bigger than word noise? ===")
    print("    paired bootstrap over the style words (seed 5, 2,000 draws):")
    print("    the SAME words are resampled for both corpora, so the interval")
    print("    is on the DIFFERENCE truncated - full, not on two separate ones.")
    print("    The point estimates differ slightly from section 2's because a")
    print("    paired test can only use words present in BOTH corpora (n below)")
    print("    and draws its own control median.")
    print(f"  {'transition':<24s} {'sym/full':>10s} {'sym/group':>10s} "
          f"{'diff':>9s} {'95% CI on diff':>22s}")
    for a, b, what in TRANSITIONS:
        pf, pg, cmf, cmg, words = paired_pref(T, Tg, a, b, style, sset)
        n = len(words)
        rng = np.random.default_rng(5)
        idx = rng.integers(0, n, size=(2000, n))
        ef = pf[idx].mean(axis=1) - cmf
        eg = pg[idx].mean(axis=1) - cmg
        d = eg - ef
        print(f"  {a+'->'+b:<24s} {pf.mean()-cmf:>+10.4f} "
              f"{pg.mean()-cmg:>+10.4f} {(pg.mean()-cmg)-(pf.mean()-cmf):>+9.4f}"
              f"   [{np.percentile(d,2.5):+.4f}, {np.percentile(d,97.5):+.4f}]"
              f"  n={n}")
    print()

    print("=== 3. per-prompt regressions: register on stage, length as covariate ===")
    regressions(T, style, "FULL text")
    regressions(Tg, style, "TRUNCATED (per-prompt 4-stage minimum)")


if __name__ == "__main__":
    main()
