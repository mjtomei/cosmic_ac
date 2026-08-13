#!/usr/bin/env python3
"""Manitoba 2025+ Hansard downloader (mirrors download.py: polite, resumable).

Reads mb_manifest_2025.json (rows {date, session, urls:[...]}), writes
{date}_{session}_h{vol}.html into mb_raw/ (existing naming convention),
logs to mb_download_2025.log.

Bytes are written UNMODIFIED: gov.mb.ca day pages are Latin-1/cp1252 and
provinces_extract.py reads them as latin-1. Do not transcode.
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")


def ok(path):
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    if len(head) < 200:
        return False
    low = head.lower()
    return b"<html" in low or b"<!doctype" in low or b"<head" in low


def main():
    rows = json.load(open(HERE / "mb_manifest_2025.json"))
    raw = HERE / "mb_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "mb_download_2025.log", "a")
    done = fail = skip = 0
    jobs = [(r["date"], r["session"], u) for r in rows for u in r["urls"]]
    for i, (date, sess, url) in enumerate(jobs):
        dest = raw / f"{date}_{sess}_{url.rsplit('/', 1)[-1]}"
        if dest.exists() and ok(dest):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                dest.write_bytes(data)          # raw bytes, no re-encoding
                if ok(dest):
                    got = True
                    break
                print(f"BADTYPE attempt{attempt} {url}", file=log, flush=True)
            except Exception as e:
                print(f"ERR attempt{attempt} {url} {e}", file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            if dest.exists():
                dest.unlink()
            print(f"FAIL {url}", file=log, flush=True)
        if (i + 1) % 25 == 0:
            print(f"progress {i+1}/{len(jobs)} dl={done} skip={skip} "
                  f"fail={fail}", file=log, flush=True)
    print(f"DONE total={len(jobs)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
