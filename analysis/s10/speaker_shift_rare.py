#!/usr/bin/env python3
"""Per-speaker shift, measured three ways, because the first way was wrong.

speaker_shift.py measured each member's shift as a POOLED rate ratio over the
whole instrument. That is the statistic the methodology explicitly rejects at
corpus level (METHODOLOGY.md 2.2): pooling is frequency-weighted, so a handful
of common words dominate and can point the opposite way to the equal-weight
statistic that carries the corpus result. Canada is exactly that case -- its
pooled full-list ratio is 0.925, below 1, while its equal-weight excess is
+0.218. So a negative median pooled per-speaker shift in Canada may say
nothing at all about the effect we actually measured.

Three statistics per speaker, all against that speaker's own frequency-matched
placebo, so the reader can see whether the conclusion depends on the choice:

  pooled_all   pooled rate ratio over all 407 instrument words
               (frequency-dominated; reported for continuity)
  pooled_rare  pooled rate ratio over instrument words rarer than 10 per 100k
               in the corpus pre-period -- this is where the corpus effect
               lives, and it is still well defined for a single speaker
  equalweight  mean of per-word log fold-change, restricted to instrument
               words the speaker actually used pre-period, so the number is
               not just the smoothing constant

Usage: python speaker_shift_rare.py
"""
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
MIN_WORDS = 8000          # higher than before: equal-weight needs the text
RARE_PER_100K = 10
N_PLACEBO_SETS = 40
OUT = "permeation"

CORPORA = {
    "ie": ("ie/segments_ie_en.jsonl", "Dail Eireann"),
    "ca": ("ca/segments_ca_en.jsonl", "Canada House of Commons"),
    "uk": ("uk/segments_uk.jsonl", "UK House of Commons"),
}


def load_instrument(path="kobak_excess_words.csv"):
    return sorted({r["word"].lower() for r in csv.DictReader(open(path))
                   if r["type"] == "style" and r["word"].isalpha()})


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5)


def quantile(v, q):
    if not v:
        return float("nan")
    s = sorted(v)
    i = q * (len(s) - 1)
    lo = int(i)
    return s[lo] if lo + 1 >= len(s) else s[lo] + (i - lo) * (s[lo + 1] - s[lo])


def report(name, label, ex, n_top=10):
    if not ex:
        print(f"  {label}: no speakers")
        return
    pos = sum(e > 0 for e in ex)
    n = len(ex)
    top = sorted(ex, reverse=True)
    tot_pos = sum(t for t in top if t > 0) or 1.0
    share = sum(top[:max(1, n // n_top)]) / tot_pos
    print(f"  {label:12s} median {quantile(ex,0.5):+.4f}  "
          f"p25 {quantile(ex,0.25):+.4f}  p75 {quantile(ex,0.75):+.4f}  "
          f"positive {pos}/{n} = {pos/n:5.1%}  top-decile share {share:5.1%}")


def main():
    style = load_instrument()
    os.makedirs(OUT, exist_ok=True)
    summary = {}
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            continue
        rng = random.Random(int(hashlib.sha1(f"{name}rare".encode()).hexdigest()[:8], 16))
        pre, post = defaultdict(Counter), defaultdict(Counter)
        corpus_pre = Counter()
        pre_w = 0
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            if d["date"] <= PRE_MAX:
                tgt, is_pre = pre, True
            elif d["date"] >= POST_MIN:
                tgt, is_pre = post, False
            else:
                continue
            toks = TOKEN_RE.findall(d["text"].lower())
            tgt[d.get("person_id") or d.get("speaker", "")].update(toks)
            if is_pre:
                corpus_pre.update(toks)
                pre_w += len(toks)

        rare = [w for w in style
                if corpus_pre[w] / max(pre_w, 1) * 1e5 < RARE_PER_100K]
        sset, rset = set(style), set(rare)

        excluded = sset | {w for w, _ in corpus_pre.most_common(120)}
        bucket = defaultdict(list)
        for w, c in corpus_pre.items():
            if w in excluded or len(w) < 4 or not w.isalpha():
                continue
            bucket[int(math.log2(c + 1))].append(w)

        def pool_for(b):
            for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
                if bucket.get(b + off):
                    return bucket[b + off]
            return bucket[max(bucket)]

        pools_all = [pool_for(int(math.log2(corpus_pre[w] + 1))) for w in style]
        pools_rare = [pool_for(int(math.log2(corpus_pre[w] + 1))) for w in rare]
        plac_all = [[rng.choice(p) for p in pools_all] for _ in range(N_PLACEBO_SETS)]
        plac_rare = [[rng.choice(p) for p in pools_rare] for _ in range(N_PLACEBO_SETS)]

        def pooled(c, words, tot):
            return (sum(c[w] for w in words) + 0.5) / max(tot, 1)

        def eqw(cpre, cpost, wpre, wpost, words):
            """Mean per-word logFC over words the speaker used pre-period."""
            used = [w for w in words if cpre[w] > 0]
            if len(used) < 20:
                return None
            return sum(math.log(((cpost[w] + 0.5) / wpost) /
                                ((cpre[w] + 0.5) / wpre)) for w in used) / len(used)

        res = {"pooled_all": [], "pooled_rare": [], "equalweight": []}
        for sp in set(pre) & set(post):
            a, b = pre[sp], post[sp]
            wa, wb = sum(a.values()), sum(b.values())
            if wa < MIN_WORDS or wb < MIN_WORDS:
                continue
            for key, words, placs in (("pooled_all", sset, plac_all),
                                      ("pooled_rare", rset, plac_rare)):
                inst = math.log(pooled(b, words, wb) / pooled(a, words, wa))
                pl = sum(math.log(pooled(b, set(P), wb) / pooled(a, set(P), wa))
                         for P in placs) / len(placs)
                res[key].append(inst - pl)
            ei = eqw(a, b, wa, wb, style)
            if ei is not None:
                ep = [eqw(a, b, wa, wb, P) for P in plac_all[:10]]
                ep = [x for x in ep if x is not None]
                if ep:
                    res["equalweight"].append(ei - sum(ep) / len(ep))

        print(f"\n=== {name} ===  {len(res['pooled_all'])} members "
              f">={MIN_WORDS:,} words both windows; {len(rare)}/{len(style)} "
              f"instrument words are rare (<{RARE_PER_100K}/100k)")
        for k in ("pooled_all", "pooled_rare", "equalweight"):
            report(name, k, res[k])
        summary[code] = {k: {"n": len(v), "median": quantile(v, 0.5),
                             "p25": quantile(v, 0.25), "p75": quantile(v, 0.75),
                             "frac_positive": (sum(x > 0 for x in v) / len(v))
                             if v else None} for k, v in res.items()}
        json.dump(res, open(f"{OUT}/{code}_speaker_shift_3way.json", "w"))

    json.dump(summary, open(f"{OUT}/speaker_shift_summary.json", "w"), indent=1)
    print("\nInterpretation guide:")
    print("  broad positive median + low top-decile share -> permeation")
    print("  median at/below zero + high top-decile share -> adoption by a subset")


if __name__ == "__main__":
    main()
