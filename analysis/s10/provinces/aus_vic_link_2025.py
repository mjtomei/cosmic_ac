#!/usr/bin/env python3
"""Symlink just the 2025+ query-cell files into aus_vic_raw_2025/ so the
existing extractor can be pointed at the new period without touching the
2006-2019 corpus.  Usage: python3 aus_vic_link_2025.py"""
import json
from pathlib import Path

HERE = Path(__file__).parent
src = HERE / "aus_vic_raw"
dst = HERE / "aus_vic_raw_2025"
dst.mkdir(exist_ok=True)
rows = json.load(open(HERE / "aus_vic_manifest_2025.json"))
n = miss = 0
for r in rows:
    s = src / r["name"]
    if not s.exists():
        miss += 1
        continue
    d = dst / r["name"]
    if not d.exists():
        d.symlink_to(s.resolve())
    n += 1
print(f"linked {n} files into {dst} ({miss} manifest rows missing on disk)")
