#!/usr/bin/env python3
"""Per-year segment/word/day stats for a segments jsonl. Usage: fill_stats.py FILE [FILE...]"""
import json
import sys
from collections import defaultdict

for path in sys.argv[1:]:
    seg = defaultdict(int)
    wrd = defaultdict(int)
    days = defaultdict(set)
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)
            y = r["date"][:4]
            seg[y] += 1
            wrd[y] += r["n_words"]
            days[y].add((r.get("chamber", ""), r["date"]))
    print(f"=== {path}")
    print(f"{'year':>6} {'segs':>9} {'words':>12} {'ch-days':>8} {'words/day':>10}")
    for y in sorted(seg):
        d = len(days[y])
        print(f"{y:>6} {seg[y]:>9,} {wrd[y]:>12,} {d:>8} {wrd[y]//max(d,1):>10,}")
