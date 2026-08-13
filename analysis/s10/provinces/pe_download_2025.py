#!/usr/bin/env python3
"""Download PEI 2025+ Hansard PDFs listed in pe_manifest_2025.json.

objectIds were harvested once through a real browser session (the enumeration
API wdf.princeedwardisland.ca sits behind Radware Bot Manager); the
docs.assembly.pe.ca/download/dms endpoint itself is not bot-protected.
Local name normalised to the existing convention YYYY-MM-DD-hansard.pdf,
which is what pe_extract.py parses the date from. 1 req/s. Resumable."""
import json, time, urllib.request
from pathlib import Path

UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
RAW = Path("pe_raw"); RAW.mkdir(exist_ok=True)
rows = json.load(open("pe_manifest_2025.json"))
ok = skip = fail = 0
for r in rows:
    local = RAW / r["local"]
    if local.exists() and local.stat().st_size > 20000:
        skip += 1; continue
    try:
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=120).read()
        if not data.startswith(b"%PDF"):
            raise ValueError(f"not a PDF ({data[:40]!r})")
        local.write_bytes(data)
        print(f"OK  {r['date']} {len(data)}", flush=True); ok += 1
    except Exception as e:
        print(f"FAIL {r['date']}: {e}", flush=True); fail += 1
    time.sleep(1.0)
print(f"done ok={ok} skip={skip} fail={fail}")
