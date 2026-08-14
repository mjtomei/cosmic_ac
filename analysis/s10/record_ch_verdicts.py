#!/usr/bin/env python3
"""Record per-chamber Pangram verdicts (Ireland / Canada / UK).

Usage: python record_ch_verdicts.py "iectl000 Human|ieprev004 AI|..."
Prints the running tally per chamber/stratum and the next batch of paths.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

DIRS = {"pangram_ch_manifest.json": "pangram_ch",
        "pangram_x_manifest.json": "pangram_x",
        "pangram_genre_manifest.json": "pangram_genre",
        "pangram_ch2_manifest.json": "pangram_ch2"}
man, home = {}, {}
for mf, d in DIRS.items():
    if os.path.exists(mf):
        got = json.load(open(mf))
        man.update(got)
        home.update({k: d for k in got})
PATH = "pangram_ch_verdicts.csv"
FIELDS = ["file", "chamber", "code", "stratum", "seg_id", "date", "speaker",
          "n_words", "pangram"]
rows = []
if os.path.exists(PATH):
    rows = [r for r in csv.DictReader(open(PATH)) if r.get("pangram")]
have = {r["file"] for r in rows}

added = 0
for item in (sys.argv[1] if len(sys.argv) > 1 else "").split("|"):
    item = item.strip()
    if not item:
        continue
    f, v = item.split()
    if f in have or f not in man:
        continue
    m = man[f]
    rows.append({"file": f, "chamber": m["chamber"], "code": m["code"],
                 "stratum": m["stratum"], "seg_id": m["seg_id"],
                 "date": m["date"], "speaker": m["speaker"],
                 "n_words": m["n_words"], "pangram": v})
    have.add(f)
    added += 1

with open(PATH, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["file"]))

tally = defaultdict(Counter)
for r in rows:
    tally[(r["code"], r["stratum"])][r["pangram"]] += 1
print(f"added {added}; {len(rows)}/{len(man)} done")
for k in sorted(tally):
    print(f"  {k[0]}-{k[1]}: {dict(tally[k])}")

todo = [n for n in sorted(man) if n not in have]
print(f"remaining {len(todo)}")
if todo:
    nxt = todo[:60]
    print("NEXT_BATCH_PATHS")
    print(",".join(f'"/home/matt/performance_commons/analysis/s10/'
                   f'{home[n]}/{n}.rtf"' for n in nxt))
