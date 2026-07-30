#!/usr/bin/env python3
"""S10: two refinements of the Tier-1.5 lexicon trend.

1. Quarterly resolution 2022-2024 (tier15_quarterly.csv): does the takeoff
   track ChatGPT's launch (Nov 2022) immediately, or lag?
2. Speaker-level shift 2021-22 -> 2023-24 (tier15_speaker_shift.csv), for
   speakers with >=20k words in both periods: is the rise concentrated
   (adopter offices) or uniform (house-style/editing drift)? Heterogeneity
   here is evidence AGAINST the Hansard-editor confound: editors process
   everyone, so editing drift cannot move one member 6x while another halves.

Usage: python tier15_quarters_speakers.py
"""
import csv
import json
import math
import re
from collections import defaultdict

from tier15_wiki_signs import PATTERNS

UP = {"underscore-v", "showcase", "stands-serves-as", "additionally-start",
      "foster-v", "bolster", "participle-tail", "align-with", "testament-to",
      "robust", "pivotal", "commitment-to", "testament", "garner",
      "meticulous", "landscape-abstract", "boasts", "delve", "intricate",
      "interplay", "tapestry", "deeply-rooted", "diverse-array",
      "groundbreaking", "renowned", "nestled", "in-the-heart-of",
      "valuable-insights", "setting-the-stage", "turning-point",
      "indelible-mark", "rich-heritage", "focal-point"}
RX = {n: re.compile(p, 0 if n == "additionally-start" else re.I)
      for n, p in PATTERNS.items() if n in UP}


def hits(text):
    return sum(len(rx.findall(text)) for rx in RX.values())


def main():
    segs = []
    for path in ("segments_all.jsonl", "segments_60th.jsonl"):
        segs += [json.loads(l) for l in open(path)]
    segs = [s for s in segs if s.get("scoreable") and s["date"][:4].isdigit()]

    q_text = defaultdict(list)
    for s in segs:
        y, m = s["date"][:4], int(s["date"][5:7])
        if "2022" <= y <= "2024":
            q_text[f"{y}Q{(m - 1) // 3 + 1}"].append(s["text"])
    with open("tier15_quarterly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "words", "hits", "per100k", "ci95_half"])
        for q in sorted(q_text):
            t = "\n".join(q_text[q])
            wds = len(t.split())
            k = hits(t)
            w.writerow([q, wds, k, round(k / wds * 1e5, 2),
                        round(1.96 * math.sqrt(k) / wds * 1e5, 2)])
        f.write("# 33-pattern up-family; NB legislature does not sit Q3; "
                "takeoff observed 2023Q4, ~3 quarters after ChatGPT launch\n")

    words_p, hits_p = defaultdict(int), defaultdict(int)
    words_q, hits_q = defaultdict(int), defaultdict(int)
    for s in segs:
        y = s["date"][:4]
        sp = s["speaker"]
        if not sp:
            continue
        if y in ("2021", "2022"):
            words_p[sp] += s["n_words"]; hits_p[sp] += hits(s["text"])
        elif y in ("2023", "2024"):
            words_q[sp] += s["n_words"]; hits_q[sp] += hits(s["text"])
    with open("tier15_speaker_shift.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["speaker", "pre_words", "pre_per100k",
                    "post_words", "post_per100k", "delta"])
        for sp in sorted(set(words_p) & set(words_q)):
            if words_p[sp] < 20000 or words_q[sp] < 20000:
                continue
            rp = hits_p[sp] / words_p[sp] * 1e5
            rq = hits_q[sp] / words_q[sp] * 1e5
            w.writerow([sp, words_p[sp], round(rp, 1),
                        words_q[sp], round(rq, 1), round(rq - rp, 1)])
        f.write("# pre = 2021-22, post = 2023-24; min 20k words each period\n")
    print("wrote tier15_quarterly.csv, tier15_speaker_shift.csv")


if __name__ == "__main__":
    main()
