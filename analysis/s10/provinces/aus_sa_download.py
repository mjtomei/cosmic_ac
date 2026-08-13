#!/usr/bin/env python3
"""Polite resumable downloader for the SA Hansard archive fetch.

Same contract as download.py, but every URL is a web.archive.org replay of a
hansardsearch.parliament.sa.gov.au document (the live host is WAF-blocked --
see recon_au_sa.json), and the manifest carries an explicit `local` filename
because the archive URLs all end in /download.

Reads aus_sa_manifest.json, writes into aus_sa_raw/, logs aus_sa_download.log.
Rejects the archived WAF 403 page ("The request is blocked.") as a bad body.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
DELAY = 1.05          # >= 1 s between requests to web.archive.org


def ok(path, kind):
    try:
        head = path.open("rb").read(4096)
    except OSError:
        return False
    if len(head) < 400:
        return False
    if b"The request is blocked" in head or b"Service unavailable" in head:
        return False
    if kind == "pdf":
        return head.startswith(b"%PDF")
    return b"<hansard" in head


def main():
    rows = json.load(open(HERE / "aus_sa_manifest.json"))
    raw = HERE / "aus_sa_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "aus_sa_download.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        dest = raw / r["local"]
        if dest.exists() and ok(dest, r["kind"]):
            skip += 1
            continue
        got = False
        for attempt in range(4):
            time.sleep(DELAY + attempt * 6)
            try:
                req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest, r["kind"]):
                    got = True
                    break
                print(f"BADBODY a{attempt} {r['url']}", file=log, flush=True)
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
