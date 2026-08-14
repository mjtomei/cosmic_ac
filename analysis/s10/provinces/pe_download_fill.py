#!/usr/bin/env python3
"""Download the PEI backfill-year Hansard PDFs in pe_manifest_fill.json.

Same contract as pe_download_2025.py -- rows carry an explicit `local` name
(the DMS URL's basename is "dms", not a filename), 1 request/second, resumable,
every response verified to start with %PDF. Writes into pe_raw_fill/ directly:
these are backfill years, disjoint from pe_raw's 2006-2019, and keeping them in
their own directory is what lets the extractor run on exactly the fill set.
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
RAW = HERE / "pe_raw_fill"
RAW.mkdir(exist_ok=True)

rows = json.load(open(HERE / "pe_manifest_fill.json"))
ok = skip = fail = 0
for r in rows:
    dest = RAW / r["local"]
    if dest.exists() and dest.stat().st_size > 20000:
        skip += 1
        continue
    got = False
    for attempt in range(3):
        time.sleep(1.0 + attempt * 4)
        try:
            req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=180).read()
            if not data.startswith(b"%PDF"):
                raise ValueError(f"not a PDF ({data[:40]!r})")
            dest.write_bytes(data)
            print(f"OK  {r['date']} {r['route']:>12s} {len(data)}", flush=True)
            got = True
            break
        except Exception as e:
            print(f"ERR {r['date']} attempt{attempt}: {e}", flush=True)
    if got:
        ok += 1
    else:
        fail += 1
        print(f"FAIL {r['date']} {r['url'][:90]}", flush=True)
print(f"done ok={ok} skip={skip} fail={fail} of {len(rows)}")
