#!/usr/bin/env python3
"""Symlink ONLY the fill-year raw files named by a fill manifest into {prov}_raw_fill/.

The shared {prov}_raw/ directories also hold the original 2006-2019 and 2025-26
downloads, so selection is driven by the manifest rows -- never by globbing the
directory. Filenames come from the manifest's own filename field, which differs
per chamber (NSW 'fname', TAS/SA 'local'), so no date string is ever reformatted
into a guessed filename. Asserts a non-zero link count for every year present in
the manifest: a year that links zero files would extract as a parliament that
never sat.

Usage: link_fill.py {aus_nsw|aus_tas|aus_sa}
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FNAME_KEY = {"aus_nsw": "fname", "aus_tas": "local", "aus_sa": "local"}

prov = sys.argv[1]
key = FNAME_KEY[prov]
rows = json.load(open(HERE / f"{prov}_manifest_fill.json"))
src = HERE / f"{prov}_raw"
dst = HERE / f"{prov}_raw_fill"
dst.mkdir(exist_ok=True)
for old in dst.iterdir():           # start clean; stale links would leak years
    old.unlink()

linked, missing = Counter(), Counter()
for r in rows:
    y = r["date"][:4]
    f = src / r[key]
    if not f.exists():
        missing[y] += 1
        continue
    (dst / r[key]).symlink_to(f.resolve())
    linked[y] += 1

years = sorted(set(r["date"][:4] for r in rows))
print(f"{prov}: {sum(linked.values())} linked, {sum(missing.values())} missing")
for y in years:
    print(f"  {y}: linked {linked[y]:>4}  missing {missing[y]:>4}")
zero = [y for y in years if linked[y] == 0]
if zero:
    sys.exit(f"ABORT: zero files linked for year(s) {zero}")
