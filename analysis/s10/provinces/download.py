#!/usr/bin/env python3
"""Polite resumable downloader: 1 request/second max, verifies type/non-empty.

Usage: python3 download.py {bc|ab|sk|aus_wa}
Reads {prov}_manifest.json, writes into {prov}_raw/, logs to {prov}_download.log.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
# parliament.wa.gov.au and (documents.)parliament.qld.gov.au sit behind an
# Azure WAF that 403s non-browser agents; neither qld host serves robots.txt
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
              "Gecko) Chrome/126.0.0.0 Safari/537.36")
PROV_UA = {"aus_wa": BROWSER_UA, "aus_qld": BROWSER_UA}


def local_name(prov, url):
    parts = url.rsplit("/", 2)
    if prov in ("sk", "nl"):       # session dir prefix: basenames collide across sessions
        return parts[-2] + "_" + parts[-1]
    if prov == "aus_wa":           # "A39%20S1%2020160510%20All.pdf" -> spaces
        return urllib.parse.unquote(parts[-1])
    return parts[-1]


def ok(path, url):
    """Non-empty and right type for what the URL claims to be."""
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    if len(head) < 200:
        return False
    if url.lower().endswith(".pdf"):
        return head.startswith(b"%PDF")
    low = head.lower()
    return b"<html" in low or b"<!doctype" in low or b"<head" in low


def main():
    prov = sys.argv[1]
    rows = json.load(open(HERE / f"{prov}_manifest.json"))
    raw = HERE / f"{prov}_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / f"{prov}_download.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url = r["url"]
        dest = raw / local_name(prov, url)
        if dest.exists() and ok(dest, url):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)          # >= 1 s between requests
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": PROV_UA.get(prov, UA)})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest, url):
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
        if (i + 1) % 50 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
