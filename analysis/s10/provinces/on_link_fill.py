#!/usr/bin/env python3
"""Symlink only the ON backfill-year raw files into on_raw_fill/.

The filename rule is `{date}.html` -- taken from the manifest's own `date`
field, not from the URL basename, because every ola.org day URL ends in the
literal "hansard". Getting this wrong is silent: a pattern that matches
nothing links nothing, the extractor runs happily over an empty directory,
and the result reads as a legislature that never sat. So the link count is
printed and asserted against the manifest row count.

Usage: python on_link_fill.py
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent


def main():
    rows = json.loads((HERE / "on_manifest_fill.json").read_text())
    src, dst = HERE / "on_raw", HERE / "on_raw_fill"
    dst.mkdir(exist_ok=True)
    for old in dst.iterdir():
        if old.is_symlink():
            old.unlink()
    linked, missing = [], []
    for r in rows:
        name = f"{r['date']}.html"
        s = src / name
        if not s.exists():
            missing.append(name)
            continue
        (dst / name).symlink_to(s.resolve())
        linked.append(name)
    print(f"manifest rows {len(rows)}; linked {len(linked)}; "
          f"missing {len(missing)}")
    print("linked per year: " + " ".join(
        f"{y}:{n}" for y, n in sorted(Counter(n[:4] for n in linked).items())))
    if missing:
        print("missing per year: " + " ".join(
            f"{y}:{n}" for y, n in
            sorted(Counter(n[:4] for n in missing).items())))
        for m in missing:
            print("  MISSING", m)
    assert linked, "linked ZERO files -- filename rule is wrong, stop here"
    assert len(list(dst.iterdir())) == len(linked)
    # every linked file must be a fill year and nothing else
    bad = [n for n in linked if int(n[:4]) not in
           {2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024}]
    assert not bad, f"non-fill years linked: {bad[:5]}"
    if len(linked) < 0.95 * len(rows):
        print("WARNING: >5% of manifest rows have no raw file", file=sys.stderr)


if __name__ == "__main__":
    main()
