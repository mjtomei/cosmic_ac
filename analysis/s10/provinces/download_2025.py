#!/usr/bin/env python3
"""Thin wrapper: run download.py's main() against {prov}_manifest_2025.json.

Usage: python3 download_2025.py {bc|ab|sk}
Downloads into the EXISTING {prov}_raw/ dir with the same local-naming rules,
logs to {prov}_download_2025.log.  Resumable (skips valid existing files).
"""
import json
import sys
from pathlib import Path

import download

HERE = Path(__file__).parent


def main():
    prov = sys.argv[1]
    rows = json.load(open(HERE / f"{prov}_manifest_2025.json"))
    raw = HERE / f"{prov}_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / f"{prov}_download_2025.log", "a")
    import time
    import urllib.request
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url = r["url"]
        dest = raw / download.local_name(prov, url)
        if dest.exists() and download.ok(dest, url):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": download.PROV_UA.get(prov, download.UA)})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if download.ok(dest, url):
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
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
