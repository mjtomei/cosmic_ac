#!/usr/bin/env python3
"""Verify every CREC zip opens and contains mods.xml; re-download the bad ones.

A size check is not enough: a server-side truncation produces a plausible
file that fails only when read. The same failure mode bit the New Brunswick
PDFs (six were truncated at source), so it is checked explicitly here rather
than discovered later as a silent gap in the corpus.

Usage: python verify_zips.py [--dir zips] [--fix]
"""
import argparse
import os
import zipfile

from fetch_us import download


def bad(path):
    try:
        with zipfile.ZipFile(path) as zf:
            if zf.testzip() is not None:
                return "crc"
            if not any(n.endswith("mods.xml") for n in zf.namelist()):
                return "no-mods"
    except Exception as e:
        return type(e).__name__
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="zips")
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.dir) if f.endswith(".zip"))
    broken = []
    for f in files:
        why = bad(os.path.join(args.dir, f))
        if why:
            broken.append((f, why))
            print(f"BAD {f}: {why}")
    print(f"{len(broken)}/{len(files)} bad")

    if broken and args.fix:
        for f, _ in broken:
            day = f.replace("CREC-", "").replace(".zip", "")
            os.remove(os.path.join(args.dir, f))
            ok = download(day, args.dir)
            still = bad(os.path.join(args.dir, f)) if ok else "download-failed"
            print(f"  refetch {day}: {'OK' if ok and not still else still}")


if __name__ == "__main__":
    main()
