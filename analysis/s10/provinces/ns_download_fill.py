#!/usr/bin/env python3
"""Nova Scotia fill-years Hansard downloader (mirrors ns_download_2025.py).

Reads ns_manifest_fill.json, writes {date}_{slug}.html into ns_raw_fill/ --
same local-name convention as ns_raw/ (provinces_extract.py takes the date
from name[:10]).  Separate directory so the original two-window corpus in
ns_raw/ stays untouched.

robots.txt on nslegislature.ca declares Crawl-delay: 10 -> 10 s between
requests.  Resumable.
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
DELAY = 10.0


def main():
    raw = HERE / "ns_raw_fill"
    raw.mkdir(exist_ok=True)
    rows = json.load(open(HERE / "ns_manifest_fill.json"))
    log = open(HERE / "ns_download_fill.log", "a")
    ok = skip = fail = 0
    for r in rows:
        slug = r["html_url"].rsplit("/", 1)[-1]
        local = raw / f"{r['date']}_{slug}.html"
        if local.exists() and local.stat().st_size > 20000:
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(DELAY + 10 * attempt)
            try:
                req = urllib.request.Request(
                    r["html_url"], headers={"User-Agent": UA})
                data = urllib.request.urlopen(req, timeout=120).read()
                if len(data) < 20000 or b"<html" not in data[:2048].lower():
                    print(f"BADTYPE attempt{attempt} {r['html_url']} "
                          f"{len(data)}", file=log, flush=True)
                    continue
                local.write_bytes(data)
                got = True
                break
            except Exception as e:
                print(f"ERR attempt{attempt} {r['html_url']}: {e}",
                      file=log, flush=True)
        if got:
            ok += 1
            print(f"OK  {r['date']} {local.name}", file=log, flush=True)
        else:
            fail += 1
            if local.exists():
                local.unlink()
            print(f"FAIL {r['date']} {r['html_url']}", file=log, flush=True)
    print(f"DONE total={len(rows)} ok={ok} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
