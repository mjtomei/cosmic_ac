#!/usr/bin/env python3
"""Manitoba fill-years Hansard downloader (mirrors mb_download_2025.py).

Reads mb_manifest_fill.json (rows {date, session, urls:[...]}), writes
{date}_{session}_h{vol}.html into mb_raw_fill/ -- the same local-name
convention as mb_raw/, which provinces_extract.py needs (it takes the
date from name[:10]).  Downloads into a SEPARATE directory so the
original two-window corpus in mb_raw/ stays untouched.

Bytes written UNMODIFIED (gov.mb.ca pages are cp1252; the extractor
reads latin-1).  Polite: >=1 s between requests, resumable.
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
    if not (b"<html" in low or b"<!doctype" in low or b"<head" in low):
        return False
    # SOFT 404: gov.mb.ca answers a dead volume link with a 302 to
    # manitoba.ca/404.html, an ~11 KB valid HTML page that every check above
    # passes. Stored, it becomes a sitting day with no turns -- which reads
    # as a parliament in recess. Two 43rd_1st calendar links are dead this
    # way (vol_54c, vol_56); their PDFs are missing too.
    if len(head) < 12288 and (b"resource not found" in low
                              or b"could not find the web page" in low):
        return False
    return True


def main():
    rows = json.load(open(HERE / "mb_manifest_fill.json"))
    raw = HERE / "mb_raw_fill"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "mb_download_fill.log", "a")
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
                dest.write_bytes(data)
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
