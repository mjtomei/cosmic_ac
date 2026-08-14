#!/usr/bin/env python3
"""Symlink ONLY the fill-year (2011-2014, 2020-2024) SK raw PDFs into sk_raw_fill/.

On-disk names follow download.py's local_name() sk rule: the session directory
is prefixed to the basename because basenames collide across sessions
("27L2S_110307Debates.pdf").  Names are computed from the manifest URLs with
that exact rule -- never guessed from the date -- and the link count is
asserted against the number of rows whose file actually downloaded.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
FILL_YEARS = set(range(2011, 2015)) | set(range(2020, 2025))


def local_name(url):
    parts = url.rsplit("/", 2)
    return parts[-2] + "_" + parts[-1]


def main():
    rows = json.load(open(HERE / "sk_manifest_fill.json"))
    raw = HERE / "sk_raw"
    dest = HERE / "sk_raw_fill"
    dest.mkdir(exist_ok=True)
    for old in dest.glob("*"):
        old.unlink()

    want, missing = [], []
    for r in rows:
        assert int(r["date"][:4]) in FILL_YEARS, r
        p = raw / local_name(r["url"])
        (want if p.exists() else missing).append((r, p))

    n = 0
    for r, p in want:
        (dest / p.name).symlink_to(p.resolve())
        n += 1

    linked = len(list(dest.glob("*.pdf")))
    print(f"rows={len(rows)} present={len(want)} missing={len(missing)} "
          f"symlinked={n} visible_to_extractor={linked}")
    for r, p in missing[:40]:
        print(f"  MISSING {r['date']} {p.name}")
    assert linked == len(want) > 0, "link count mismatch / empty link dir"
    # extractor globs *.pdf -- every link must be visible under that glob
    assert linked == n
    if len(missing) > 0.05 * len(rows):
        print("WARNING: >5% of manifest rows failed to download", file=sys.stderr)


if __name__ == "__main__":
    main()
