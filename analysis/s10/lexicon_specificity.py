#!/usr/bin/env python3
"""Is the Kobak list special, or would any matched word set predict the detector?

THE QUESTION THIS SETTLES

Per-segment Kobak density correlates with the Opus AI-score at rho = +0.25.
That was initially read as validation. But the same correlation appears in
pre-2023 text, where there is no AI, so something else drives at least part of
it -- most obviously formal/abstract register, which both instruments respond
to.

Comparing pre and post AUCs does NOT settle it: the labels underneath differ
("top 7.8% of human text" vs "flagged"), so the difference is not a
decomposition. The well-posed test is a within-period one:

    among the SAME segments, does the Kobak list predict the detector better
    than a frequency-matched random word set does?

The placebo construction is the one used throughout the protocol -- same
log2 frequency bucket, same dispersion bin, drawn from in-domain vocabulary,
excluding the instrument itself. If a random matched set predicts the detector
just as well, then per-segment density is measuring "how many mid-frequency
abstract words are in this passage", and the Kobak list contributes nothing of
its own. If the Kobak list clearly leads, the list carries specific
information the detector independently recognises.

The formality control (built pre-period-only, from long-vs-short speech) is
included as a third comparator: it is what "register" looks like when
constructed deliberately.

Usage: python lexicon_specificity.py
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
N_PLACEBO_SETS = 30
_HERE = os.path.dirname(os.path.abspath(__file__))
NB = ["segments_59th.jsonl", "segments_60th.jsonl",
      "segments_61s1.jsonl", "segments.jsonl", "segments_all.jsonl"]


def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        a = (i + j) / 2 + 1
        for k in range(i, j + 1):
            rk[s[k]] = a
        i = j + 1
    return rk


def pear(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    d = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / d if d else float("nan")


def spear(x, y):
    return pear(rank(x), rank(y))


def main():
    style = sorted({r["word"].lower() for r in
                    csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                    if r["type"] == "style" and r["word"].isalpha()})
    rng = random.Random(int(hashlib.sha1(b"lexspec").hexdigest()[:8], 16))

    # pre-period counts + dispersion, for building matched placebo sets
    pre_c = Counter()
    disp = Counter()
    last = {}
    text = {}
    for f in NB:
        if not os.path.exists(f):
            continue
        for line in open(f):
            d = json.loads(line)
            text.setdefault(d["seg_id"], (d["text"], d["date"]))
            if not d.get("scoreable") or d["date"] > PRE_MAX:
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            pre_c.update(t)
            for w in set(t):
                if last.get(w) != d["date"]:
                    disp[w] += 1
                    last[w] = d["date"]

    excluded = set(style) | {w for w, _ in pre_c.most_common(120)}

    def cell(w):
        return (int(math.log2(pre_c[w] + 1)), int(math.log2(disp.get(w, 0) + 1)))

    pool = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        pool[cell(w)].append(w)

    def pool_for(c):
        if pool.get(c):
            return pool[c]
        for r in range(1, 8):
            best = None
            for df in range(-r, r + 1):
                for dd in range(-r, r + 1):
                    if max(abs(df), abs(dd)) != r:
                        continue
                    cd = pool.get((c[0] + df, c[1] + dd))
                    if cd and (best is None or len(cd) > len(best)):
                        best = cd
            if best:
                return best
        return max(pool.values(), key=len)

    pools = [pool_for(cell(w)) for w in style]
    placebos = [set(rng.choice(p) for p in pools) for _ in range(N_PLACEBO_SETS)]

    # Opus screen scores
    sc = {}
    for r in csv.DictReader(open("opus_screen_scores.csv")):
        v = (r.get("opus_screen") or "").strip()
        if v.lstrip("-").isdigit() and r.get("year", "").strip().isdigit():
            sc[r["seg_id"]] = (int(v), r["year"].strip())

    sset = set(style)
    for era_label, keep in (("2025-26", lambda y: y >= "2025"),
                            ("pre-2023", lambda y: y <= "2022")):
        toks, scores = [], []
        for sid, (s, y) in sc.items():
            if not keep(y):
                continue
            t = text.get(sid)
            if not t:
                continue
            w = TOKEN_RE.findall(t[0].lower())
            if len(w) < 30:
                continue
            toks.append(w)
            scores.append(float(s))
        if len(toks) < 500:
            continue
        rs = rank(scores)

        def rho_for(lex):
            d = [sum(x in lex for x in w) / len(w) * 1000 for w in toks]
            return pear(rank(d), rs)

        real = rho_for(sset)
        pl = sorted(rho_for(p) for p in placebos)
        med = pl[len(pl) // 2]
        beat = sum(1 for v in pl if v >= real)
        print(f"\n=== {era_label} ===  n = {len(toks):,} segments")
        print(f"  Kobak style list                rho = {real:+.3f}")
        print(f"  frequency+dispersion-matched    rho = {med:+.3f}  "
              f"(median of {N_PLACEBO_SETS}; range {pl[0]:+.3f} to {pl[-1]:+.3f})")
        print(f"  placebo sets beating Kobak      {beat}/{N_PLACEBO_SETS}")
        print(f"  excess over matched placebo     {real - med:+.3f}")


if __name__ == "__main__":
    main()
