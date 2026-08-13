#!/usr/bin/env python3
"""Symlink only the 2025+ raw files into {prov}_raw_2025/ so an extractor can be
re-run over the new period without touching the existing corpus.

Usage: python3 link_2025.py {bc|ab|sk}
Uses the same local-naming rule as download.py (sk prefixes the session dir).
"""
import json
import sys
from pathlib import Path

import download

HERE = Path(__file__).parent


def main():
    prov = sys.argv[1]
    rows = json.load(open(HERE / f"{prov}_manifest_2025.json"))
    src = HERE / f"{prov}_raw"
    dst = HERE / f"{prov}_raw_2025"
    dst.mkdir(exist_ok=True)
    linked = missing = []
    linked, missing = [], []
    for r in rows:
        name = download.local_name(prov, r["url"])
        s = src / name
        if not s.exists():
            missing.append(name)
            continue
        d = dst / name
        if d.is_symlink() or d.exists():
            d.unlink()
        d.symlink_to(s.resolve())
        linked.append(name)
    print(f"{prov}: linked {len(linked)}, missing {len(missing)}")
    for m in missing:
        print("  MISSING", m)


if __name__ == "__main__":
    main()
