#!/usr/bin/env python3
"""Build aus_wa_manifest_2025.json -- the 2025-01-01..today extension.

Identical route and row schema to aus_wa_manifest.py (Domino views -> day stub
-> whole-day PDF attachment); only the date window differs.  The 42nd
Parliament (2025+) kept the ($lookupDailyTransLAByDate)/($lookupDailyTransLCByDate)
views and the ?opendocument stub, but the attachment BASENAME changed from
"A39 S1 20160510 All.pdf" to "Legislative Assembly_2025_06_18.pdf" (and, from
2026-06, "Legislative Assembly-20260618.pdf").

Usage: python3 aus_wa_manifest_2025.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BASE = "https://www.parliament.wa.gov.au"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
VIEWS = {"Legislative Assembly": "($lookupDailyTransLAByDate)",
         "Legislative Council": "($lookupDailyTransLCByDate)"}
START, END = "20250101", "20260809"
ROW = re.compile(r'>(\d{8})</a>')
REDIR = re.compile(r'window\.location\.replace\("([^"]+)"\)')
CACHE = HERE / "aus_wa_stub_cache_2025.json"


def get(url, tries=3):
    for a in range(tries):
        time.sleep(1.0 + a * 4)                    # >= 1 s between requests
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"  retry {a} {url}: {e}", file=sys.stderr)
    return None


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    rows = []
    for chamber, view in VIEWS.items():
        url = (f"{BASE}/Hansard/hansard.nsf/{urllib.parse.quote(view)}"
               f"?OpenView&Start=1&Count=5000")
        h = get(url)
        dates = sorted({d for d in ROW.findall(h)})
        want = [d for d in dates if START <= d <= END]
        print(f"{chamber}: {len(dates)} sitting days total, {len(want)} in window",
              file=sys.stderr)
        for i, d in enumerate(want):
            key = f"{view}/{d}"
            if key not in cache:
                stub = get(f"{BASE}/Hansard/hansard.nsf/"
                           f"{urllib.parse.quote(view)}/{d}?opendocument")
                m = REDIR.search(stub) if stub else None
                cache[key] = m.group(1) if m else None
                if (i + 1) % 25 == 0:
                    CACHE.write_text(json.dumps(cache))
                    print(f"  {chamber} {i+1}/{len(want)}", file=sys.stderr)
            path = cache[key]
            if not path:
                print(f"  NO PDF for {chamber} {d}", file=sys.stderr)
                continue
            rows.append({"url": urllib.parse.urljoin(BASE, path),
                         "date": f"{d[:4]}-{d[4:6]}-{d[6:]}",
                         "chamber": chamber})
        CACHE.write_text(json.dumps(cache))
    rows.sort(key=lambda r: (r["chamber"], r["date"]))
    (HERE / "aus_wa_manifest_2025.json").write_text(json.dumps(rows, indent=1))
    print(f"manifest: {len(rows)} whole-day PDFs", file=sys.stderr)


if __name__ == "__main__":
    main()
