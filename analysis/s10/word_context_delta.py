#!/usr/bin/env python3
"""Instruct-vs-base likelihood of the INSTRUMENT WORDS in their Hansard context.

THE IDEA (Matthew's)

The corpus-wide likelihood delta was a triple-replicated null, but it averaged
over every token, diluting any signal across the ~96% of positions where
nothing is expected to happen. This restricts the same quantity to the
positions of the Kobak style words themselves:

    delta(occurrence) = log P_instruct(word | context) - log P_base(word | context)

summed over the word's tokens. That asks a sharper question than frequency
counting can: not "do members use these words more" but "when they use them,
is the SURROUNDING USAGE the assistant's usage" -- the collocations and frames
post-training installs. Permeation of phrasing, not just vocabulary.

THE CONTROL THAT MAKES IT INTERPRETABLE

Matched placebo words are scored IN THE SAME SEGMENTS. Post-2023 text is
globally less familiar to both checkpoints (topics after their cutoffs), and
that base-side drift was 3x any delta in the corpus-wide version. Here the
contrast

    (instrument-position delta) - (placebo-position delta), pre vs post

differences out anything that acts on the segment as a whole, because both
position classes sit in identical text. What survives is specific to the
instrument words' contexts.

Occurrences whose first token is the segment's first token are skipped (no
prediction exists for position 0). Words are located by regex word boundary
and mapped to token spans via the fast tokenizer's offset mapping; both
checkpoints tokenise identically (verified in align_ratio.py).

Usage: python word_context_delta.py score    # GPU: 2 passes over 15k segments
       python word_context_delta.py report
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = "align_ratio/items.json"
OUT = "word_context"
import sys as _sys
_FAM = "mistral" if "--family=mistral" in _sys.argv else "qwen3"
PAIR = ([("mistral_base", "mistralai/Mistral-7B-v0.3"),
         ("mistral_instruct", "mistralai/Mistral-7B-Instruct-v0.3")]
        if _FAM == "mistral" else
        [("base", "Qwen/Qwen3-8B-Base"), ("instruct", "Qwen/Qwen3-8B")])
TOKEN_RE = re.compile(r"[a-z']+")
PLACEBOS_PER_WORD = 3


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def build_lexicons(items):
    """Instrument + a frequency-matched placebo lexicon, from pre-era counts
    of the sampled segments themselves (bucketing needs no more than that)."""
    style = set(load_style())
    pre_c = Counter()
    for it in items:
        if it["era"] == "pre":
            pre_c.update(TOKEN_RE.findall(it["text"].lower()))
    rng = random.Random(int(hashlib.sha1(b"wordctx").hexdigest()[:8], 16))
    excluded = style | {w for w, _ in pre_c.most_common(120)}
    bucket = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(n + 1))].append(w)
    placebo = set()
    for w in style:
        if pre_c[w] == 0:
            continue
        b = int(math.log2(pre_c[w] + 1))
        pool = None
        for off in (0, 1, -1, 2, -2, 3, -3):
            if bucket.get(b + off):
                pool = bucket[b + off]
                break
        if pool:
            for _ in range(PLACEBOS_PER_WORD):
                placebo.add(rng.choice(pool))
    placebo -= style
    return style, placebo


def occurrences(text, lex_i, lex_p, enc_offsets):
    """Map word occurrences to token index spans via offsets.
    Returns [(tok_start, tok_end_inclusive, is_instrument), ...]."""
    spans = []
    for m in re.finditer(r"[A-Za-z']+", text):
        w = m.group(0).lower()
        if w in lex_i:
            spans.append((m.start(), m.end(), True))
        elif w in lex_p:
            spans.append((m.start(), m.end(), False))
    if not spans:
        return []
    out = []
    si = 0
    cur = []
    for ti, (a, b) in enumerate(enc_offsets):
        if a == b:      # special token
            continue
        while si < len(spans) and spans[si][1] <= a:
            if cur:
                out.append((cur[0], cur[-1], spans[si][2]))
            cur = []
            si += 1
        if si >= len(spans):
            break
        s = spans[si]
        if b > s[0] and a < s[1]:
            cur.append(ti)
    if cur and si < len(spans):
        out.append((cur[0], cur[-1], spans[si][2]))
    return out


def score(args):
    os.environ.setdefault("CUDA_CACHE_MAXSIZE", "17179869184")
    os.environ.setdefault("CUDA_CACHE_PATH", "/home/matt/.nv_cache_s10")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    global OUT, ITEMS
    OUT = getattr(args, "out", None) or OUT
    ITEMS = getattr(args, "items", None) or ITEMS
    os.makedirs(OUT, exist_ok=True)
    items = json.load(open(ITEMS))
    lex_i, lex_p = build_lexicons(items)
    json.dump({"instrument": sorted(lex_i), "placebo": sorted(lex_p)},
              open(f"{OUT}/lexicons.json", "w"))
    print(f"{len(items):,} segments; {len(lex_i)} instrument words, "
          f"{len(lex_p)} placebo words")

    tok = AutoTokenizer.from_pretrained(PAIR[0][1])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # precompute token spans once — both checkpoints tokenise identically
    print("locating occurrences...", flush=True)
    occ = []
    B = 256
    for i in range(0, len(items), B):
        texts = [it["text"] for it in items[i:i + B]]
        enc = tok(texts, truncation=True, max_length=512,
                  return_offsets_mapping=True)
        for j, offs in enumerate(enc["offset_mapping"]):
            occ.append(occurrences(texts[j], lex_i, lex_p, offs))
    n_i = sum(1 for o in occ for s in o if s[2])
    n_p = sum(1 for o in occ for s in o if not s[2])
    print(f"  {n_i:,} instrument occurrences, {n_p:,} placebo occurrences")

    for role, mid in PAIR:
        path = f"{OUT}/{role}_occ_lp.json"
        if os.path.exists(path):
            print(f"  {role}: cached")
            continue
        print(f"  scoring {role}: {mid}", flush=True)
        model = AutoModelForCausalLM.from_pretrained(
            mid, dtype=torch.bfloat16, device_map="cuda").eval()
        res = []
        BB = args.batch
        with torch.inference_mode():
            for i in range(0, len(items), BB):
                texts = [it["text"] for it in items[i:i + BB]]
                enc = tok(texts, return_tensors="pt", padding=True,
                          truncation=True, max_length=512).to("cuda")
                ids, am = enc["input_ids"], enc["attention_mask"]
                lg = model(input_ids=ids, attention_mask=am).logits
                lsm = torch.log_softmax(lg[:, :-1].float(), dim=-1)
                tl = lsm.gather(-1, ids[:, 1:].unsqueeze(-1)).squeeze(-1)
                tl = tl.cpu()
                for j in range(len(texts)):
                    row = []
                    for a, b, isi in occ[i + j]:
                        if a < 1:      # first token has no prediction
                            continue
                        row.append([round(float(tl[j, a - 1:b].sum()), 4),
                                    b - a + 1, 1 if isi else 0])
                    res.append(row)
                if (i // BB) % 40 == 0:
                    print(f"    {i + len(texts)}/{len(items)}", flush=True)
        json.dump(res, open(path, "w"))
        del model
        torch.cuda.empty_cache()
        print(f"  wrote {path}", flush=True)


def report(args):
    """Two estimands, per Matthew: the RAW instrument-position delta (no
    control at all), and the SELF-NORMALISED version -- instrument-position
    delta minus the same segment's full-trace delta, taken from the
    align_ratio run (same 15k segments, same checkpoint pair). No placebo
    word selection is involved in either; the placebo occurrences recorded
    during scoring are deliberately unused, because matched-word constructions
    have repeatedly introduced their own artifacts (F1, the dispersion fix,
    the in-time placebo failure)."""
    items = json.load(open(ITEMS))
    base = json.load(open(f"{OUT}/base_occ_lp.json"))
    inst = json.load(open(f"{OUT}/instruct_occ_lp.json"))
    fb = json.load(open("align_ratio/qwen3_base_lp.json"))
    fi = json.load(open("align_ratio/qwen3_instruct_lp.json"))
    rng = random.Random(23)

    rows = defaultdict(list)
    n_used = 0
    for it, bo, io, (bt, bn), (itt, itn) in zip(items, base, inst, fb, fi):
        di, ni = 0.0, 0
        for (bl, btk, bi), (il, itk, ii) in zip(bo, io):
            if not bi:
                continue                      # placebo positions unused
            di += (il - bl) / max(btk, 1)
            ni += 1
        if not ni:
            continue
        full = (itt - bt) / max(min(bn, itn), 1)
        rows[(it["chamber"], it["era"])].append(
            {"raw": di / ni, "norm": di / ni - full, "turn": it["turn_id"]})
        n_used += 1

    print(f"{n_used:,} segments with >=1 instrument occurrence")
    print("raw  = per-token log P(instruct)-log P(base) AT INSTRUMENT WORDS")
    print("norm = raw minus the same segment's full-trace delta (no word")
    print("       selection; cancels whatever moves the segment as a whole)\n")
    print(f"{'chamber':<8s} {'era':<5s} {'n':>6s} {'raw':>8s} {'norm':>8s}")
    stats = {}
    for k in sorted(rows):
        v = rows[k]
        mr = sum(r["raw"] for r in v) / len(v)
        mn = sum(r["norm"] for r in v) / len(v)
        stats[k] = (mr, mn)
        print(f"{k[0]:<8s} {k[1]:<5s} {len(v):>6d} {mr:>8.4f} {mn:>+8.4f}")

    print("\npre -> post change (clustered bootstrap over speeches, 95% CI):")
    print(f"{'chamber':<7s} {'estimand':<6s} {'change':>9s} {'95% CI':>20s}")
    for ch in ("ie", "ca", "uk", "ush", "uss"):
        pre, post = rows.get((ch, "pre")), rows.get((ch, "post"))
        if not (pre and post):
            continue
        for key in ("raw", "norm"):
            def clus(rs):
                byt = defaultdict(list)
                for r in rs:
                    byt[r["turn"]].append(r[key])
                ks = list(byt)
                o = []
                for _ in range(400):
                    s_ = t_ = 0
                    for _ in range(len(ks)):
                        vv = byt[ks[rng.randrange(len(ks))]]
                        s_ += sum(vv)
                        t_ += len(vv)
                    o.append(s_ / t_)
                return o
            dd = sorted(q - p_ for p_, q in zip(clus(pre), clus(post)))
            ch_ = (stats[(ch, "post")][0 if key == "raw" else 1]
                   - stats[(ch, "pre")][0 if key == "raw" else 1])
            lo, hi = dd[10], dd[-11]
            star = " *" if lo > 0 or hi < 0 else ""
            print(f"{ch:<7s} {key:<6s} {ch_:>+9.4f}  [{lo:+.4f}, {hi:+.4f}]{star}")


def _cells(fam):
    """Per-(chamber, era) mean normalised delta for one model family.

    report() hardcodes the qwen3 full-trace files, so --family=mistral never
    reached them; this reads the right pair for whichever family is asked for.
    """
    occ = {"qwen3": ("base_occ_lp.json", "instruct_occ_lp.json"),
           "mistral": ("mistral_base_occ_lp.json",
                       "mistral_instruct_occ_lp.json")}[fam]
    full = {"qwen3": ("qwen3_base_lp.json", "qwen3_instruct_lp.json"),
            "mistral": ("mistral_base_lp.json",
                        "mistral_instruct_lp.json")}[fam]
    items = json.load(open(os.path.join(_HERE, ITEMS)))
    base = json.load(open(os.path.join(_HERE, OUT, occ[0])))
    inst = json.load(open(os.path.join(_HERE, OUT, occ[1])))
    fb = json.load(open(os.path.join(_HERE, "align_ratio", full[0])))
    fi = json.load(open(os.path.join(_HERE, "align_ratio", full[1])))
    rows = defaultdict(list)
    for it, bo, io, (bt, bn), (itt, itn) in zip(items, base, inst, fb, fi):
        di, ni = 0.0, 0
        for (bl, btk, bi), (il, itk, ii) in zip(bo, io):
            if not bi:
                continue
            di += (il - bl) / max(btk, 1)
            ni += 1
        if not ni:
            continue
        fulld = (itt - bt) / max(min(bn, itn), 1)
        rows[(it["chamber"], it["era"])].append(
            {"norm": di / ni - fulld, "turn": it["turn_id"]})
    return rows


def pooled(args):
    """The number §4.8 actually prints: the two-family, five-chamber pooled
    pre->post change in the normalised instrument-position delta, with a
    clustered bootstrap over speeches and a design-based permutation test.

    Previously this existed only as prose -- report() prints five Qwen3 rows
    and no pooled statistic, so the footnote's invocation could not produce the
    sentence's number. B defaults to 2,000 because at B=400 the 2.5% percentile
    carries about one Monte-Carlo SE of noise, which is the whole width of the
    lower bound's distance from zero; the point estimate and the permutation p
    are stable regardless.
    """
    B = getattr(args, "boot", None) or 2000
    seed = getattr(args, "seed", None) or 6
    rng = random.Random(seed)
    CH = ("ie", "ca", "uk", "ush", "uss")
    fams = ("qwen3", "mistral")
    cells, cellrows = {}, {}
    for fam in fams:
        r = _cells(fam)
        for ch in CH:
            pre, post = r.get((ch, "pre")), r.get((ch, "post"))
            if not (pre and post):
                continue
            mp = sum(x["norm"] for x in pre) / len(pre)
            mq = sum(x["norm"] for x in post) / len(post)
            cells[(fam, ch)] = mq - mp
            cellrows[(fam, ch)] = (pre, post)
    vals = list(cells.values())
    point = sum(vals) / len(vals)
    npos = sum(1 for v in vals if v > 0)
    print(f"pooled over {len(vals)} cells ({len(fams)} families x {len(CH)} "
          f"chambers), normalised estimand")
    print(f"{'cell':<16s}{'change':>10s}")
    for k in sorted(cells):
        print(f"  {k[0]+'/'+k[1]:<14s}{cells[k]:>+10.4f}")
    print(f"\n  POOLED {point:+.4f}   positive in {npos}/{len(vals)} cells")

    def draw():
        tot = 0.0
        for k, (pre, post) in cellrows.items():
            def cl(rs):
                byt = defaultdict(list)
                for r in rs:
                    byt[r["turn"]].append(r["norm"])
                ks = list(byt)
                s_ = t_ = 0
                for _ in range(len(ks)):
                    vv = byt[ks[rng.randrange(len(ks))]]
                    s_ += sum(vv)
                    t_ += len(vv)
                return s_ / t_
            tot += cl(post) - cl(pre)
        return tot / len(cellrows)
    dd = sorted(draw() for _ in range(B))
    lo, hi = dd[int(.025 * B)], dd[int(.975 * B) - 1]
    ple = sum(1 for v in dd if v <= 0) / B
    print(f"  clustered bootstrap B={B}, seed={seed}: 95% CI "
          f"[{lo:+.4f}, {hi:+.4f}], P(<=0) = {ple:.3f}")

    # design-based permutation: shuffle era labels within chamber x family
    perm = 0
    P = 3000
    for _ in range(P):
        tot = 0.0
        for k, (pre, post) in cellrows.items():
            allr = pre + post
            idx = list(range(len(allr)))
            rng.shuffle(idx)
            a = [allr[i] for i in idx[:len(pre)]]
            b = [allr[i] for i in idx[len(pre):]]
            tot += (sum(x["norm"] for x in b) / len(b)
                    - sum(x["norm"] for x in a) / len(a))
        if tot / len(cellrows) >= point:
            perm += 1
    print(f"  permutation test (era labels shuffled within cell, {P} draws): "
          f"one-sided p = {(perm + 1) / (P + 1):.4f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["score", "report", "pooled"])
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--family", default="qwen3")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", default=None, help="output dir (default word_context)")
    ap.add_argument("--items", default=None, help="items.json to score")
    ap.add_argument("--seed", type=int, default=6)
    a = ap.parse_args()
    {"score": score, "report": report, "pooled": pooled}[a.mode](a)
