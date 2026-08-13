#!/usr/bin/env python3
"""Download NS 2025+ Hansard HTML day pages (ns_manifest_2025.json).
robots.txt on nslegislature.ca declares Crawl-delay: 10 -> 10 s between requests.
Local name matches the existing modern-era ns_raw/ files: {date}_{slug}.html.
Resumable."""
import json, time, urllib.request
from pathlib import Path

UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
DELAY = 10.0
RAW = Path("ns_raw"); RAW.mkdir(exist_ok=True)
rows = json.load(open("ns_manifest_2025.json"))
ok = skip = fail = 0
for r in rows:
    slug = r["html_url"].rsplit("/", 1)[-1]
    local = RAW / f"{r['date']}_{slug}.html"
    if local.exists() and local.stat().st_size > 20000:
        skip += 1; continue
    try:
        req = urllib.request.Request(r["html_url"], headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=120).read()
        local.write_bytes(data)
        print(f"OK  {r['date']} {len(data)} {local.name}", flush=True); ok += 1
    except Exception as e:
        print(f"FAIL {r['date']} {r['html_url']}: {e}", flush=True); fail += 1
    time.sleep(DELAY)
print(f"done ok={ok} skip={skip} fail={fail}")
