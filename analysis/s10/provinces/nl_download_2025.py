#!/usr/bin/env python3
"""Download NL 2025+ Hansard day pages listed in nl_manifest_2025.json.
Local name convention matches the existing nl_raw/ files: {session}_{url-basename}.
Resumable: skips files already present and non-trivially sized."""
import json, sys, time, urllib.request
from pathlib import Path

UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
RAW = Path("nl_raw"); RAW.mkdir(exist_ok=True)
rows = json.load(open("nl_manifest_2025.json"))
ok = skip = fail = 0
for r in rows:
    local = RAW / f"{r['session']}_{r['url'].rsplit('/',1)[-1]}"
    if local.exists() and local.stat().st_size > 2000:
        skip += 1; continue
    try:
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=90).read()
        local.write_bytes(data)
        print(f"OK  {r['date']} {len(data)} {local.name}", flush=True); ok += 1
    except Exception as e:
        print(f"FAIL {r['date']} {r['url']}: {e}", flush=True); fail += 1
    time.sleep(1.0)
print(f"done ok={ok} skip={skip} fail={fail}")
