#!/usr/bin/env python3
"""Ontario Hansard downloader for the backfill years (2011-2014, 2020-2024).

WHY NOT download.py

`download.py on` cannot be used for Ontario. Its local_name() takes the last
path segment, and every ola.org day URL ends in the literal ".../hansard" --
so all 702 days would be written to a single file called `hansard`. The
2006-2019 harvest and the 2025 extension both named files `{date}.html`
(see on_download_2025.py); this script does the same, into the same on_raw/,
so the fill years sit next to the years already there.

Politeness: one request per second minimum, exponential backoff on retry,
plain research User-Agent (ola.org answers it 200 and robots.txt disallows
nothing under /en/legislative-business). Resumable: an existing, well-formed,
large-enough file is skipped.

Usage: python on_download_fill.py   # reads on_manifest_fill.json
"""
import json
import os
import time
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("performance-commons-research/1.0 (academic corpus build; "
      "matthewtomei@gmail.com)")
MIN_BYTES = 30000          # a real sitting day is 100-500 KB; a stub is not


def ok(path):
    try:
        head = path_open(path)
    except OSError:
        return False
    if len(head) < 200:
        return False
    low = head.lower()
    return b"<html" in low or b"<!doctype" in low or b"<head" in low


def path_open(path):
    with open(path, "rb") as fh:
        return fh.read(2048)


def main():
    rows = json.load(open(os.path.join(HERE, "on_manifest_fill.json")))
    raw = os.path.join(HERE, "on_raw")
    os.makedirs(raw, exist_ok=True)
    log = open(os.path.join(HERE, "on_download_fill.log"), "a")
    done = fail = skip = 0
    failed_dates = []
    for i, r in enumerate(rows):
        dest = os.path.join(raw, f"{r['date']}.html")
        if (os.path.exists(dest) and ok(dest)
                and os.path.getsize(dest) > MIN_BYTES):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(r["url"],
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                with open(dest, "wb") as fh:
                    fh.write(data)
                if ok(dest) and os.path.getsize(dest) > MIN_BYTES:
                    got = True
                    break
                print(f"BADTYPE/SMALL attempt{attempt} "
                      f"{os.path.getsize(dest)}B {r['url']}",
                      file=log, flush=True)
            except Exception as e:
                print(f"ERR attempt{attempt} {r['url']} {e}",
                      file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            failed_dates.append(r["date"])
            if os.path.exists(dest):
                os.unlink(dest)
            print(f"FAIL {r['url']}", file=log, flush=True)
        if (i + 1) % 25 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} "
                  f"fail={fail}", file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)
    if failed_dates:
        print("FAILED DATES BY YEAR: " + " ".join(
            f"{y}:{n}" for y, n in
            sorted(Counter(d[:4] for d in failed_dates).items())),
            file=log, flush=True)
        print("FAILED: " + " ".join(failed_dates), file=log, flush=True)


if __name__ == "__main__":
    main()
