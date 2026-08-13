#!/usr/bin/env python3
"""Polite resumable downloader for the UK devolved-legislature manifests.

Same contract as download.py (1 request/second floor, 3 tries, resumable,
type-checked) but the manifest rows carry an explicit local filename, because
the Scottish route is an API query string and the NI/Wales routes have
basenames that collide across sessions.

Manifest row: {"url": ..., "file": ...}.  Type is inferred from the local
extension: .json must parse, .pdf must start %PDF, anything else must look
like markup.

Usage: python3 uk_download.py {scot|wales|ni}
Reads {prov}_manifest.json, writes {prov}_raw/, appends {prov}_download.log.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
DELAY = 1.0          # seconds between requests; no site states a crawl-delay


def ok(path):
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if len(data) < 200:
        return False
    suf = path.suffix.lower()
    if suf == ".json":
        try:
            j = json.loads(data)
        except Exception:
            return False
        return bool(j)
    if suf == ".pdf":
        return data.startswith(b"%PDF")
    if suf == ".xml":
        return b"<?xml" in data[:200] or b"<" in data[:200]
    low = data[:4096].lower()
    return b"<html" in low or b"<!doctype" in low or b"<head" in low


def main():
    prov = sys.argv[1]
    rows = json.load(open(HERE / f"{prov}_manifest.json"))
    raw = HERE / f"{prov}_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / f"{prov}_download.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        dest = raw / r["file"]
        if dest.exists() and ok(dest):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(DELAY + attempt * 4)
            try:
                req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=600) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest):
                    got = True
                    break
                print(f"BADTYPE attempt{attempt} {r['url']}", file=log, flush=True)
            except Exception as e:
                print(f"ERR attempt{attempt} {r['url']} {e}", file=log, flush=True)
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
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
