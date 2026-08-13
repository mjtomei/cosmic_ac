#!/usr/bin/env python3
"""Polite resumable downloader for the Australian state Hansard manifests.

Same contract as download.py (the Canadian one), with two changes forced by the
Australian hosts:
  - a browser User-Agent, because parliament.qld.gov.au / parliament.wa.gov.au
    sit behind an Azure WAF JS challenge that 403s library user agents;
  - the manifest carries an explicit "fname", because document ids (NSW) and
    per-session paths collide across chambers/years otherwise.

Usage: python3 aus_download.py {nsw|vic|qld|wa|sa|tas} [--delay SECONDS]
Reads aus_{state}_manifest.json, writes into aus_{state}_raw/,
logs to aus_{state}_download.log. Re-running skips files already valid.
"""
import argparse
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
CONTACT = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"


def ok(path, url, fname):
    """Non-empty and the right type for what the URL/filename claims to be."""
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    if len(head) < 400:
        return False
    if fname.lower().endswith(".pdf") or url.lower().endswith(".pdf"):
        return head.startswith(b"%PDF")
    low = head.lower()
    return (b"<html" in low or b"<!doctype" in low or b"<head" in low
            or b"<?xml" in low or low.lstrip().startswith(b"<"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--delay", type=float, default=1.05)
    args = ap.parse_args()
    st = args.state
    rows = json.load(open(HERE / f"aus_{st}_manifest.json"))
    raw = HERE / f"aus_{st}_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / f"aus_{st}_download.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url, fname = r["url"], r["fname"]
        dest = raw / fname
        if dest.exists() and ok(dest, url, fname):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(args.delay + attempt * 4)      # >= 1 s between requests
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": UA,
                    "Accept": "*/*",
                    "Accept-Language": "en-AU,en;q=0.9",
                    "From": CONTACT,
                })
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest, url, fname):
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
