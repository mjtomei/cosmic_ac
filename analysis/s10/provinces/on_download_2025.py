#!/usr/bin/env python3
"""Ontario 2025+ Hansard downloader (mirrors download.py: polite, resumable).

Reads on_manifest_2025.json, writes {date}.html into on_raw/ (the naming the
existing 2006-2019 files use), logs to on_download_2025.log.
ola.org 403s non-browser agents -> desktop Chrome UA (recon_central.json).
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
              "Gecko) Chrome/126.0.0.0 Safari/537.36")


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
    rows = json.load(open(HERE / "on_manifest_2025.json"))
    raw = HERE / "on_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "on_download_2025.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url, dest = r["url"], raw / f"{r['date']}.html"
        if dest.exists() and ok(dest) and dest.stat().st_size > 30000:
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(url,
                                             headers={"User-Agent": BROWSER_UA})
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
        if (i + 1) % 20 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} "
                  f"fail={fail}", file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
