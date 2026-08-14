#!/usr/bin/env python3
"""Download the Wales fill-year corpus (2011-2014 PDF, 2020-2024 XML).

Why not the shared download.py: its local_name() derives the local filename
from the URL's last path segment, which for the Senedd's CeConvert2PDF and
XMLExport endpoints is the ASPX handler plus its query string, not a filename.
The wales manifest rows carry an explicit "file" key for exactly that reason,
and its ok() type check keys off a ".pdf" URL suffix these URLs do not have.
This script honours row["file"] and types the check off that name instead.
Same politeness contract as download.py: >= 1 s between requests, 3 tries,
resumable (an already-good file is skipped).

Usage: python3 wales_download_fill.py [manifest.json] [raw_dir]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"


def ok(path, name):
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    if len(head) < 200:
        return False
    if name.endswith(".pdf"):
        return head.startswith(b"%PDF")
    low = head.lower().lstrip()
    return low.startswith(b"<?xml") or b"<xml_" in low or b"<" in low[:1]


def main():
    man = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "wales_manifest_fill.json")
    raw = Path(sys.argv[2] if len(sys.argv) > 2 else HERE / "wales_raw")
    rows = json.load(open(man))
    raw.mkdir(exist_ok=True)
    log = open(HERE / "wales_download_fill.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url, name = r["url"], r["file"]
        dest = raw / name
        if dest.exists() and ok(dest, name):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest, name):
                    got = True
                    break
                print(f"BADTYPE attempt{attempt} {name} {url}", file=log, flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"ERR attempt{attempt} {name} {url} {e}", file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            if dest.exists():
                dest.unlink()
            print(f"FAIL {name} {url}", file=log, flush=True)
        if (i + 1) % 50 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
