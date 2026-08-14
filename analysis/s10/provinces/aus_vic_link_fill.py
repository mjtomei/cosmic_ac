#!/usr/bin/env python3
"""Symlink just the backfill-window (2011-2014, 2020-2024) query-cell files
into aus_vic_raw_fill/ so the existing extractor can be pointed at the new
years without touching the 2006-2019 corpus in the same raw directory.

Links are driven off aus_vic_manifest_fill.json, not off a filename glob:
the manifest carries the exact name the downloader wrote, so a naming-format
mismatch shows up as "missing on disk" rather than as a silently empty link
set.  Refuses to finish if any fill year links zero files.

Usage: python3 aus_vic_link_fill.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FILL_YEARS = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]
src = HERE / "aus_vic_raw"
dst = HERE / "aus_vic_raw_fill"
dst.mkdir(exist_ok=True)

rows = json.load(open(HERE / "aus_vic_manifest_fill.json"))
linked, miss, small = Counter(), Counter(), Counter()
for r in rows:
    y = int(r["date"][:4])
    s = src / r["name"]
    if not s.exists():
        miss[y] += 1
        continue
    if s.stat().st_size < 8192:
        small[y] += 1
    d = dst / r["name"]
    if not d.exists():
        d.symlink_to(s.resolve())
    linked[y] += 1

on_disk = len(list(dst.iterdir()))
print(f"{'year':6}{'manifest':>10}{'linked':>8}{'missing':>9}{'<8KB':>7}")
bad = []
for y in FILL_YEARS:
    n = sum(1 for r in rows if r["date"][:4] == str(y))
    print(f"{y:<6}{n:>10}{linked[y]:>8}{miss[y]:>9}{small[y]:>7}")
    if linked[y] == 0:
        bad.append(y)
print(f"TOTAL manifest={len(rows)} linked={sum(linked.values())} "
      f"missing={sum(miss.values())} entries_in_dir={on_disk}")
assert sum(linked.values()) > 0, "linked ZERO files -- filename format mismatch"
if bad:
    sys.exit("FATAL: years with zero linked files: %s" % bad)
