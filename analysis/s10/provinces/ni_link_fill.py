#!/usr/bin/env python3
"""Symlink ONLY the fill-year (2011-2014, 2020-2024) NI raw files into ni_raw_fill/.

Two on-disk name shapes, both taken from the manifest's own `file` field rather
than reconstructed from the date -- uk_download.py writes exactly that name, and
guessing a name from a date is how a fill run ends up linking zero files and
reporting a parliament that never sat.  ni_extract.py globs arch_*.htm and
api_*.json, so both globs are counted separately and asserted.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
FILL_YEARS = set(range(2011, 2015)) | set(range(2020, 2025))


def main():
    rows = json.load(open(HERE / "ni_manifest_fill.json"))
    raw = HERE / "ni_raw"
    dest = HERE / "ni_raw_fill"
    dest.mkdir(exist_ok=True)
    for old in dest.glob("*"):
        old.unlink()

    want, missing = [], []
    for r in rows:
        assert int(r["date"][:4]) in FILL_YEARS, r
        p = raw / r["file"]
        (want if p.exists() else missing).append((r, p))

    n = 0
    for r, p in want:
        (dest / p.name).symlink_to(p.resolve())
        n += 1

    htm = len(list(dest.glob("arch_*.htm")))
    js = len(list(dest.glob("api_*.json")))
    print(f"rows={len(rows)} present={len(want)} missing={len(missing)} "
          f"symlinked={n} visible_to_extractor={htm + js} "
          f"(arch:{htm} api:{js})")
    for r, p in missing:
        print(f"  MISSING {r['date']} {p.name}")
    assert htm + js == n == len(want) > 0, "link count mismatch / empty link dir"
    if len(missing) > 0.05 * len(rows):
        print("WARNING: >5% of manifest rows failed to download", file=sys.stderr)


if __name__ == "__main__":
    main()
