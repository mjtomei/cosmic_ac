#!/usr/bin/env python3
"""Build aus_sa_manifest.json from Internet Archive CDX for SA Hansard.

The live host (hansardsearch.parliament.sa.gov.au) is WAF-blocked from this
network on every path, so the archive is the only route -- see recon_au_sa.json.

Per chamber (lh = House of Assembly, uh = Legislative Council) we enumerate:
  /daily/{ch}/{YYYY-MM-DD}/pdf/download          -> full sitting-day PDF
  /daily/{ch}/{YYYY-MM-DD}/extract/{N}/download  -> per-subject XML fragment
and keep, restricted to 2006-2010 and 2015-2019:
  - the PDF for every day that has one (full-day coverage), else
  - every XML fragment for that day (partial-day coverage).
Some archived captures recorded the WAF 403 page, so rows are filtered to
statuscode 200 AND the expected mimetype; earliest good capture wins.
"""
import json
import os
import re
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
CDX = ("http://web.archive.org/cdx/search/cdx?url=hansardsearch.parliament.sa.gov.au"
       "/daily/{ch}/&matchType=prefix&fl=original,timestamp,mimetype,statuscode"
       "&limit=400000")
CHAMBER = {"lh": "House of Assembly", "uh": "Legislative Council"}
# The window pair above is the original drift design; the sources
# publish continuously. S10_FILL / S10_SUFFIX backfill the skipped
# years (2011-14, 2020-24) without overwriting the first pass.
WINDOWS = (((2011, 2014), (2020, 2024))
           if os.environ.get("S10_FILL") else ((2006, 2010), (2015, 2019)))


def in_window(d):
    y = int(d[:4])
    return any(lo <= y <= hi for lo, hi in WINDOWS)


def fetch_cdx(ch):
    cache = HERE / f"aus_sa_cdx_{ch}.txt"
    if cache.exists() and cache.stat().st_size > 1000:
        return cache.read_text()
    req = urllib.request.Request(CDX.format(ch=ch), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r:
        txt = r.read().decode("utf-8", "replace")
    cache.write_text(txt)
    time.sleep(2)
    return txt


def main():
    rows = []
    for ch in ("lh", "uh"):
        pdf, ext = {}, defaultdict(dict)
        for line in fetch_cdx(ch).splitlines():
            p = line.split()
            if len(p) < 4:
                continue
            url, ts, mime, sc = p
            m = re.search(r"/daily/%s/(\d{4}-\d{2}-\d{2})/(.*)$" % ch, url)
            if not m or sc != "200":
                continue
            date, rest = m.group(1), m.group(2)
            if not in_window(date):
                continue
            if rest == "pdf/download" and mime == "application/pdf":
                if date not in pdf or ts < pdf[date]:
                    pdf[date] = ts
                continue
            fm = re.match(r"extract/(\d+)/download$", rest)
            if fm and mime in ("text/xml", "application/xml"):
                n = int(fm.group(1))
                if n not in ext[date] or ts < ext[date][n]:
                    ext[date][n] = ts

        for date in sorted(pdf):
            rows.append({
                "url": f"https://web.archive.org/web/{pdf[date]}id_/https://"
                       f"hansardsearch.parliament.sa.gov.au/daily/{ch}/{date}/pdf/download",
                "date": date, "chamber": CHAMBER[ch], "ch": ch, "kind": "pdf",
                "local": f"{ch}_{date}.pdf",
            })
        for date in sorted(ext):
            if date in pdf:                       # PDF already covers the whole day
                continue
            for n in sorted(ext[date]):
                rows.append({
                    "url": f"https://web.archive.org/web/{ext[date][n]}id_/https://"
                           f"hansardsearch.parliament.sa.gov.au/daily/{ch}/{date}"
                           f"/extract/{n}/download",
                    "date": date, "chamber": CHAMBER[ch], "ch": ch, "kind": "xml",
                    "local": f"{ch}_{date}_x{n:03d}.xml",
                })

    (HERE / f"aus_sa_manifest{os.environ.get('S10_SUFFIX','')}.json").write_text(json.dumps(rows, indent=1))
    days = {(r["ch"], r["date"]) for r in rows}
    print(f"{len(rows)} files over {len(days)} chamber-days")
    for lo, hi in WINDOWS:
        w = {d for d in days if lo <= int(d[1][:4]) <= hi}
        print(f"  {lo}-{hi}: {len(w)} chamber-days")


if __name__ == "__main__":
    main()
