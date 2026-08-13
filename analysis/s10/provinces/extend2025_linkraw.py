#!/usr/bin/env python3
"""Symlink only the 2025+ raw files into a scratch dir so the chamber's existing
extractor can be run over the new period without touching the old corpus.

Usage: python3 extend2025_linkraw.py MANIFEST_JSON RAW_DIR LINK_DIR
The manifest rows must carry either "fname" or a "url" whose basename is the
local filename.
"""
import json
import sys
from pathlib import Path


def main():
    man, raw, link = (Path(x) for x in sys.argv[1:4])
    rows = json.loads(man.read_text())
    link.mkdir(exist_ok=True)
    for old in link.iterdir():
        if old.is_symlink():
            old.unlink()
    n = missing = 0
    for r in rows:
        fname = r.get("fname") or r["url"].rsplit("/", 1)[-1]
        src = (raw / fname).resolve()
        if not src.exists():
            missing += 1
            print(f"MISSING {fname}", file=sys.stderr)
            continue
        (link / fname).symlink_to(src)
        n += 1
    print(f"linked {n} files into {link} ({missing} missing)")


if __name__ == "__main__":
    main()
