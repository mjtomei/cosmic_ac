#!/usr/bin/env python3
"""Append the standard '2025+ extension' section to a chamber's validation file.

Usage:
  python3 extend2025_validate.py PROV SEGMENTS_JSONL VALIDATION_TXT [--notes FILE]
                                 [--days N] [--raw-files N] [--raw-words N]

PROV is the short chamber tag used in the validation heading (BC, AB, ..., VIC).
Writes, appended to VALIDATION_TXT:
  - header with build date
  - sitting days / segments / words totals for the new period
  - per-MONTH segments and words (the zero-month check)
  - top-5 speakers by words
  - 2 random scoreable segments printed in full
  - optional free-text notes read from --notes
The per-month table is the Victoria-2019 regression check: a month with source
files but zero segments means the extractor missed a markup era.
"""
import argparse
import datetime as dt
import json
import random
from collections import Counter, defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prov")
    ap.add_argument("segments")
    ap.add_argument("validation")
    ap.add_argument("--notes")
    ap.add_argument("--days", type=int, default=None,
                    help="sitting days fetched (source-side count)")
    ap.add_argument("--raw-files", type=int, default=None)
    ap.add_argument("--raw-words", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1010)
    a = ap.parse_args()

    segs = [json.loads(l) for l in open(a.segments)]
    out = open(a.validation, "a")

    def w(s=""):
        print(s, file=out)

    today = dt.date.today().isoformat()
    w()
    w()
    w(f"=== {a.prov} 2025+ extension (built {today}) ===")
    if not segs:
        w("NO SEGMENTS EXTRACTED FOR 2025 ONWARD.  See notes below.")
        if a.notes:
            w()
            w(open(a.notes).read().rstrip())
        out.close()
        print("empty corpus - wrote failure note")
        return

    dates = sorted({s["date"] for s in segs})
    words = sum(s["n_words"] for s in segs)
    scoreable = sum(1 for s in segs if s["scoreable"])
    w(f"period covered: {dates[0]} .. {dates[-1]}")
    if a.raw_files is not None:
        w(f"raw files downloaded: {a.raw_files}")
    if a.days is not None:
        w(f"sitting days fetched (source index): {a.days}")
    w(f"sitting dates with segments: {len(dates)}")
    w(f"segments: {len(segs)}  scoreable: {scoreable} "
      f"({scoreable/len(segs):.0%})  words: {words}")
    ids = [s["seg_id"] for s in segs]
    w(f"unique seg_ids: {len(set(ids))} of {len(ids)}"
      f"{'  (OK)' if len(set(ids)) == len(ids) else '  *** DUPLICATES ***'}")
    if a.raw_words:
        w(f"raw-word survival: {words}/{a.raw_words} = {words/a.raw_words:.1%}")

    w()
    w("--- segments / words per MONTH (zero-month check) ---")
    mseg, mwords, mdays = Counter(), Counter(), defaultdict(set)
    for s in segs:
        m = s["date"][:7]
        mseg[m] += 1
        mwords[m] += s["n_words"]
        mdays[m].add(s["date"])
    first, last = dates[0][:7], dates[-1][:7]
    y, mo = int(first[:4]), int(first[5:7])
    months = []
    while f"{y:04d}-{mo:02d}" <= last:
        months.append(f"{y:04d}-{mo:02d}")
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
    w(f"  {'month':>8}  {'days':>5}  {'segs':>7}  {'words':>10}")
    for m in months:
        flag = "   <-- ZERO" if mseg[m] == 0 else ""
        w(f"  {m:>8}  {len(mdays[m]):>5}  {mseg[m]:>7}  {mwords[m]:>10}{flag}")
    zero = [m for m in months if mseg[m] == 0]
    w(f"  months with zero segments: {len(zero)}"
      + (f"  {zero}" if zero else ""))

    w()
    w("--- segments / words per year ---")
    yseg, ywords, ydays = Counter(), Counter(), defaultdict(set)
    for s in segs:
        yseg[s["date"][:4]] += 1
        ywords[s["date"][:4]] += s["n_words"]
        ydays[s["date"][:4]].add(s["date"])
    for yy in sorted(yseg):
        w(f"  {yy}: {yseg[yy]:>7} segs  {ywords[yy]:>10} words  "
          f"({len(ydays[yy])} sitting days)")

    w()
    w("--- top 5 speakers by word count ---")
    sp = Counter()
    for s in segs:
        sp[s["speaker"]] += s["n_words"]
    for name, n in sp.most_common(5):
        w(f"  {n:>9}  {name}")
    w(f"  distinct speakers: {len(sp)}")

    rng = random.Random(a.seed)
    pool = [s for s in segs if s["scoreable"]]
    for i, s in enumerate(rng.sample(pool, min(2, len(pool))), 1):
        w()
        w(f"--- random scoreable segment {i}: {s['seg_id']} "
          f"({s['speaker']}, {s['n_words']} words, {s['date']}) ---")
        w(s["text"])

    if a.notes:
        w()
        w("--- notes ---")
        w(open(a.notes).read().rstrip())
    out.close()
    print(f"appended {a.prov}: {len(segs)} segs, {words} words, "
          f"{len(dates)} dates, {len(zero)} zero months")


if __name__ == "__main__":
    main()
