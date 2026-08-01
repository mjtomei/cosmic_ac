#!/usr/bin/env python3
"""Record a batch of Pangram web verdicts into pangram_web_verdicts.csv.

Usage: python record_verdicts.py "nb0186 AI|nb0187 Mixed|nb0188 Human|..."
Then prints the running tally and the next batch of filenames to upload.
"""
import csv
import json
import sys
from collections import Counter

man = json.load(open("pangram_rtf_manifest.json"))
rows = [r for r in csv.DictReader(open("pangram_web_verdicts.csv")) if r.get("pangram")]
have = {r["file"] for r in rows}

added = 0
for item in sys.argv[1].split("|"):
    item = item.strip()
    if not item:
        continue
    f, v = item.split()
    if f in have or f not in man:
        continue
    m = man[f]
    rows.append({"file": f, "seg_id": m["seg_id"], "date": m["date"],
                 "speaker": m["speaker"], "n_words": m["n_words"],
                 "opus_screen": m["opus_screen"], "pangram": v})
    have.add(f)
    added += 1

with open("pangram_web_verdicts.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["file", "seg_id", "date", "speaker",
                                       "n_words", "opus_screen", "pangram"])
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["file"]))

todo = [n for n in sorted(man) if n not in have]
print(f"added {added}; {len(rows)}/643 done; tally "
      f"{dict(Counter(r['pangram'] for r in rows))}")
print(f"remaining {len(todo)}")
if todo:
    nxt = todo[:60]
    print("NEXT_BATCH_PATHS")
    print(",".join(f'"/home/matt/performance_commons/analysis/s10/pangram_rtf/{n}.rtf"'
                   for n in nxt))
