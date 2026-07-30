#!/usr/bin/env python3
"""S10: per-year AI-lexicon trend, 2019 -> 2026.

The decisive shape test for the Tier-1.5 signal: an inflection at 2023
(ChatGPT deployment) says AI-era adoption; a straight line from 2019 says
ordinary vocabulary drift. Aggregates the 33-pattern "up-family" from
tier15_wiki_signs.PATTERNS (Wikipedia:Signs_of_AI_writing) per calendar
year over the 2019 control + 60th Legislature (2020-24) + 61st (2025-26).

Usage: python tier15_trend.py   (writes tier15_trend.csv)
"""
import csv
import json
import math
import re
from collections import defaultdict

from tier15_wiki_signs import PATTERNS

UP_FAMILY = {"underscore-v", "showcase", "stands-serves-as",
             "additionally-start", "foster-v", "bolster", "participle-tail",
             "align-with", "testament-to", "robust", "pivotal",
             "commitment-to", "testament", "garner", "meticulous",
             "landscape-abstract", "boasts", "delve", "intricate",
             "interplay", "tapestry", "deeply-rooted", "diverse-array",
             "groundbreaking", "renowned", "nestled", "in-the-heart-of",
             "valuable-insights", "setting-the-stage", "turning-point",
             "indelible-mark", "rich-heritage", "focal-point"}
COMPILED = {n: re.compile(p, 0 if n == "additionally-start" else re.I)
            for n, p in PATTERNS.items() if n in UP_FAMILY}
MARQUEE = ["delve", "underscore-v", "showcase", "foster-v", "testament",
           "additionally-start", "participle-tail", "meticulous"]


def main():
    texts_by_year = defaultdict(list)
    for path in ("segments_all.jsonl", "segments_60th.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if s.get("scoreable") and s["date"][:4].isdigit():
                texts_by_year[s["date"][:4]].append(s["text"])

    rows = []
    print(f"{'year':6s} {'words':>10s} {'AI-lex/100k':>12s} {'95% CI':>16s}  marquee: " +
          " ".join(f"{m[:6]:>7s}" for m in MARQUEE))
    for year in sorted(texts_by_year):
        joined = "\n".join(texts_by_year[year])
        words = len(joined.split())
        counts = {n: len(rx.findall(joined)) for n, rx in COMPILED.items()}
        k = sum(counts.values())
        rate = k / words * 1e5
        half = 1.96 * math.sqrt(k) / words * 1e5 if k else 1.9
        marq = {m: counts.get(m, 0) / words * 1e5 for m in MARQUEE}
        rows.append({"year": year, "words": words, "ai_lex_hits": k,
                     "per100k": round(rate, 2), "ci_lo": round(rate - half, 2),
                     "ci_hi": round(rate + half, 2),
                     **{f"{m}_per100k": round(marq[m], 2) for m in MARQUEE}})
        print(f"{year:6s} {words:>10,} {rate:>12.1f} "
              f"[{rate-half:>6.1f},{rate+half:>6.1f}]  " +
              " ".join(f"{marq[m]:>7.2f}" for m in MARQUEE))

    with open("tier15_trend.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        f.write("# 33-pattern up-family aggregate from tier15_wiki_signs "
                "(Wikipedia:Signs_of_AI_writing); Poisson 95% CI; "
                "years 2020-24 = 60th Legislature, 2019 = control, "
                "2025-26 = 61st/2\n")


if __name__ == "__main__":
    main()
