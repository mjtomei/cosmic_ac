#!/usr/bin/env python3
"""Build aus_wa_manifest.json for the WA Parliament (Domino/HCL Hansard).

Two hops, both polite (<= 1 request/second, resumable via the cache file):
  1. Enumerate sitting days from the Domino views
       /Hansard/hansard.nsf/($lookupDailyTransLAByDate)?OpenView&Start=1&Count=5000
       /Hansard/hansard.nsf/($lookupDailyTransLCByDate)?OpenView&Start=1&Count=5000
     Each row's display value is the sitting date as YYYYMMDD.
  2. For each in-window date fetch the day stub
       /Hansard/hansard.nsf/($lookupDailyTransLAByDate)/{YYYYMMDD}?opendocument
     which contains window.location.replace("<path to the whole-day All.pdf>").

Windows: 2006-2010 and 2015-2019 only.
Requires a browser User-Agent (the site's Azure WAF 403s anything else).

Usage: python3 aus_wa_manifest.py
"""
import json
import os
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
# The window pair above is the original drift design; the sources
# publish continuously. S10_FILL / S10_SUFFIX backfill the skipped
# years (2011-14, 2020-24) without overwriting the first pass.
WINDOWS = (((2011, 2014), (2020, 2024))
           if os.environ.get("S10_FILL") else ((2006, 2010), (2015, 2019)))
ROW = re.compile(r'href="(/Hansard/hansard\.nsf/[0-9a-f]+/[0-9a-f]+\?OpenDocument)"'
                 r'>(\d{8})</a>', re.I)
REDIR = re.compile(r'window\.location\.replace\("([^"]+)"\)')
CACHE = HERE / "aus_wa_stub_cache.json"


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


def in_window(d):
    y = int(d[:4])
    return any(lo <= y <= hi for lo, hi in WINDOWS)


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    rows = []
    for chamber, view in VIEWS.items():
        url = f"{BASE}/Hansard/hansard.nsf/{urllib.parse.quote(view)}?OpenView&Start=1&Count=5000"
        h = get(url)
        dates = sorted({d for _, d in ROW.findall(h)})
        want = [d for d in dates if in_window(d)]
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
    (HERE / f"aus_wa_manifest{os.environ.get('S10_SUFFIX','')}.json").write_text(json.dumps(rows, indent=1))
    print(f"manifest: {len(rows)} whole-day PDFs", file=sys.stderr)


if __name__ == "__main__":
    main()
