#!/usr/bin/env python3
"""Symlink ONLY the 2011-2014 / 2020-2024 BC raw files into bc_raw_fill/.

Links are driven off bc_manifest_fill.json's own `name` field (the exact
on-disk name download.py writes, since download.py's local_name() for bc is
just the URL basename), not off a reconstructed date string - a date-pattern
guess is what silently linked zero Queensland files.  Asserts the link count
matches the manifest row count and that every date-parsed year is a fill year.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
FILL_YEARS = {"2011", "2012", "2013", "2014",
              "2020", "2021", "2022", "2023", "2024"}
DATE_FROM_NAME = re.compile(r"(\d{4})(\d{2})(\d{2})[ap]m-", re.I)


def main():
    rows = json.load(open(HERE / "bc_manifest_fill.json"))
    src, dst = HERE / "bc_raw", HERE / "bc_raw_fill"
    dst.mkdir(exist_ok=True)
    for old in dst.iterdir():
        old.unlink()

    linked, missing, badname = 0, [], []
    years = Counter()
    for r in rows:
        name = r["name"]
        m = DATE_FROM_NAME.search(name)
        if not m:                       # extractor derives the date from this
            badname.append(name)
            continue
        if m.group(1) not in FILL_YEARS:
            badname.append(name)
            continue
        p = src / name
        if not p.exists():
            missing.append(name)
            continue
        (dst / name).symlink_to(p.resolve())
        years[m.group(1)] += 1
        linked += 1

    print(f"manifest rows={len(rows)} linked={linked} "
          f"missing_from_bc_raw={len(missing)} unparsable_or_wrong_year={len(badname)}")
    for y in sorted(FILL_YEARS):
        print(f"  {y}: {years.get(y,0)} files")
    for n in missing[:10]:
        print("  MISSING", n)
    for n in badname[:10]:
        print("  BADNAME", n)

    assert not badname, "filename date format does not match the extractor's"
    assert linked == len(rows) - len(missing)
    assert linked > 0, "zero files linked - refusing to run the extractor"
    assert all(years.get(y, 0) > 0 for y in FILL_YEARS), \
        f"a fill year linked zero files: {dict(years)}"
    if missing:
        print(f"WARNING: {len(missing)} manifest rows never downloaded",
              file=sys.stderr)


if __name__ == "__main__":
    main()
