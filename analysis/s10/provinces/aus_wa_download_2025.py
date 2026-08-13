#!/usr/bin/env python3
"""Polite resumable downloader for the WA 2025+ whole-day PDFs.

Same contract as download.py (browser UA -- the Azure WAF 403s anything else --
>= 1 s between requests, resumable, %PDF check), reading
aus_wa_manifest_2025.json and writing into the existing aus_wa_raw/.

LOCAL FILENAME.  The 42nd Parliament changed the attachment basename twice
("Legislative Assembly_2025_06_18.pdf", then "Legislative Assembly-20260618.pdf"
from June 2026) and one attachment is mislabelled at source (the Assembly stub
for 2026-03-19 serves a file called "Legislative Council_2026_03_19.pdf", which
would collide with the real Council file).  Local names are therefore
canonicalised from the manifest row itself:

    {Legislative Assembly|Legislative Council}_{YYYY}_{MM}_{DD}.pdf

which is the dominant source convention, still carries house + date (what
aus_wa_extract.py parses), and cannot collide with the 2006-2019 files.

Usage: python3 aus_wa_download_2025.py
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
              "Gecko) Chrome/126.0.0.0 Safari/537.36")


def local_name(row):
    y, m, d = row["date"].split("-")
    return f"{row['chamber']}_{y}_{m}_{d}.pdf"


def ok(path):
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    return len(head) >= 200 and head.startswith(b"%PDF")


def main():
    rows = json.load(open(HERE / "aus_wa_manifest_2025.json"))
    raw = HERE / "aus_wa_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "aus_wa_download_2025.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        dest = raw / local_name(r)
        if dest.exists() and ok(dest):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)          # >= 1 s between requests
            try:
                req = urllib.request.Request(
                    r["url"], headers={"User-Agent": BROWSER_UA})
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest):
                    got = True
                    break
                print(f"BADTYPE a{attempt} {r['url']}", file=log, flush=True)
            except Exception as e:
                print(f"ERR a{attempt} {r['url']} {e}", file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            if dest.exists():
                dest.unlink()
            print(f"FAIL {r['url']}", file=log, flush=True)
        if (i + 1) % 25 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
