#!/usr/bin/env python3
"""Validation report for a UK devolved-legislature segment corpus.

Usage: python3 uk_validate.py {SCO|WAL|NI} SEGMENTS_JSONL RAW_WORDS OUT_TXT

RAW_WORDS is the denominator printed by the extractor (all words present in the
source documents' speech-bearing text before chair/procedure filtering and
window packing); passing it in keeps this script independent of the very
different raw formats (JSON API / HTML / PDF).
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

WINDOWS = [("2006-2010", range(2006, 2011)), ("2015-2019", range(2015, 2020))]


def main():
    prov = sys.argv[1].upper()
    segs = [json.loads(l) for l in open(sys.argv[2])]
    raw_words = int(sys.argv[3])
    out = open(sys.argv[4], "w")

    def w(s=""):
        print(s, file=out)

    w(f"=== {prov} corpus validation ===")
    w(f"segments: {len(segs)}  scoreable: {sum(s['scoreable'] for s in segs)}")
    w(f"turns: {len(set(s['turn_id'] for s in segs))}")
    w(f"unique sitting dates: {len(set(s['date'] for s in segs))}")
    w(f"unique speakers: {len(set(s['speaker'] for s in segs))}")
    w()

    w("--- segments / words per year (both drift windows) ---")
    per = defaultdict(lambda: [0, 0, 0, set()])
    for s in segs:
        y = s["date"][:4]
        per[y][0] += 1
        per[y][1] += s["n_words"]
        per[y][2] += s["scoreable"]
        per[y][3].add(s["date"])
    w(f"{'year':>5} {'days':>5} {'segs':>8} {'scoreable':>10} {'words':>11}")
    for label, yrs in WINDOWS:
        w(f"  [{label}]")
        tot = [0, 0, 0, 0]
        for y in yrs:
            a, b, c, d = per.get(str(y), [0, 0, 0, set()])
            w(f"{y:>5} {len(d):>5} {a:>8} {c:>10} {b:>11}")
            tot[0] += len(d); tot[1] += a; tot[2] += c; tot[3] += b
        w(f"{'sum':>5} {tot[0]:>5} {tot[1]:>8} {tot[2]:>10} {tot[3]:>11}")
    stray = sorted(y for y in per if not any(int(y) in yrs for _, yrs in WINDOWS))
    if stray:
        w(f"  OUT-OF-WINDOW years present (should be empty): {stray}")
    w()

    w("--- top 10 speakers by words (chair voices already excluded) ---")
    sp = Counter()
    for s in segs:
        sp[s["speaker"]] += s["n_words"]
    for k, v in sp.most_common(10):
        w(f"{v:>10}  {k}")
    w()

    w("--- speakers recorded by OFFICE rather than by name ---")
    off = [s for s in segs if s["speaker"].startswith(("The ", "Y ", "Yr "))]
    ow = sum(s["n_words"] for s in off)
    w(f"{len(off)} segments / {ow} words ({ow/max(sum(s['n_words'] for s in segs),1):.1%})"
      f" carry an office label, not a person")
    if off:
        c = Counter(s["speaker"] for s in off)
        for k, v in c.most_common(5):
            w(f"    {v:>6} segs  {k}")
        w("  These cannot be joined to the same person's other speech. See the")
        w("  per-corpus notes at the foot of this file.")
        yrs = Counter(s["date"][:4] for s in off)
        w(f"  by year: {dict(sorted(yrs.items()))}")
    w()

    if any("lang" in s for s in segs):
        w("--- language mix ---")
        c = Counter(s.get("lang", "?") for s in segs)
        n = sum(c.values())
        for k, v in c.most_common():
            w(f"  {k}: {v} segments ({v/n:.1%})")
        cy = sum(v for k, v in c.items() if k == "cy")
        w(f"  Welsh-majority share of segments: {cy/n:.2%} "
          f"(all marked scoreable:false)")
        w()

    w("--- fraction of raw words surviving ---")
    ew = sum(s["n_words"] for s in segs)
    w(f"raw speech-bearing words in source: {raw_words}")
    w(f"extracted words: {ew}  ({ew/max(raw_words,1):.1%})")
    w(f"(the shortfall is chair/procedural voices, narration, and sub-50-word "
      f"leftovers that packing kept but which stay in the count)")
    w()

    w("--- 3 random scoreable segments (full) ---")
    pool = [s for s in segs if s["scoreable"]]
    random.seed(10)
    for s in random.sample(pool, min(3, len(pool))):
        w(f"[{s['seg_id']}] {s['date']} | {s['speaker']} | {s['n_words']} words")
        w(s["text"])
        w()

    notes = Path(__file__).parent / f"{prov.lower()}_notes.txt"
    if notes.exists():
        w("--- corpus notes ---")
        w(notes.read_text().rstrip())
    out.close()
    print(open(sys.argv[4]).read())


if __name__ == "__main__":
    main()
