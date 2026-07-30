#!/usr/bin/env python3
"""S10: mechanism prediction test — does ex-ante AI-preference predict
which words shifted?

For every Kobak style word measurable in the synthetic corpus (>=1
occurrence there; 89 of 407), compute:
  ex-ante preference = log[ rate in synthetic corpus / rate in 2019 control ]
    (both in-domain; involves NO post-2023 chamber data)
  observed shift     = log[ post-2024-26 rate / pre-2018-22 rate ]
and correlate. A positive rank correlation means an independent in-domain
measurement predicts WHICH words rose — mechanism-level corroboration that
list-selection cannot manufacture. Permutation p over 10,000 shuffles of
the preference labels.

Result at freeze (2026-07-30): Spearman +0.548, p < 1e-4.
Usage: python ai_pref_prediction.py   (writes ai_pref_prediction.csv)
"""
import csv
import json
import math
import random
import re
from collections import Counter

random.seed(20260730)
TOKEN_RE = re.compile(r"[a-z']+")
PRE = {"2018", "2019", "2020", "2021", "2022"}
POST = {"2024", "2025", "2026"}


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    return cov / math.sqrt(vx * vy)


def main():
    style = [r["word"].lower() for r in
             csv.DictReader(open("kobak_excess_words.csv"))
             if r["type"] == "style" and r["word"].isalpha()]
    pre_c, post_c, ctl_c, syn_c = Counter(), Counter(), Counter(), Counter()
    pre_w = post_w = ctl_w = syn_w = 0
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "segments_59th.jsonl", "se_segments.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if not s.get("scoreable"):
                continue
            y = s["date"][:4]
            toks = TOKEN_RE.findall(s["text"].lower())
            if s["date"].startswith("synthetic"):
                syn_c.update(toks); syn_w += len(toks)
            if s["date"].startswith("2019"):
                ctl_c.update(toks); ctl_w += len(toks)
            if y in PRE:
                pre_c.update(toks); pre_w += len(toks)
            elif y.isdigit() and y in POST:
                post_c.update(toks); post_w += len(toks)

    cand = [w for w in style if syn_c[w] > 0]
    rows = []
    for w in cand:
        pref = math.log(((syn_c[w] + 0.5) / syn_w) / ((ctl_c[w] + 0.5) / ctl_w))
        shift = math.log(((post_c[w] + 0.5) / post_w) / ((pre_c[w] + 0.5) / pre_w))
        rows.append({"word": w, "syn_n": syn_c[w], "ctl_n": ctl_c[w],
                     "pre_n": pre_c[w], "post_n": post_c[w],
                     "ai_pref": round(pref, 4), "shift": round(shift, 4)})
    pref = [r["ai_pref"] for r in rows]
    shift = [r["shift"] for r in rows]
    rho = spearman(pref, shift)
    N = 10000
    sh = pref[:]
    exceed = 0
    for _ in range(N):
        random.shuffle(sh)
        if spearman(sh, shift) >= rho:
            exceed += 1
    print(f"n={len(cand)} words; Spearman={rho:+.3f}; "
          f"permutation p={exceed/N:.4f}")
    with open("ai_pref_prediction.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -r["ai_pref"]))
        f.write(f"# Spearman {rho:+.4f}, permutation p {exceed/N:.4f} "
                f"({N} shuffles); preference uses synthetic+2019 control "
                f"only (no post-2023 data)\n")


if __name__ == "__main__":
    main()
