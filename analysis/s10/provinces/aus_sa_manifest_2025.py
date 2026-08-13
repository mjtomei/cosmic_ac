#!/usr/bin/env python3
"""Build aus_sa_manifest_2025.json -- the 2025-01-01..today extension.

Identical logic and row schema to aus_sa_manifest.py; only the date window and
the file names differ.  The live host was RE-TESTED on 2026-08-09 and is still
Azure-Front-Door 403 on every path from this network (root, /search/calendar,
/daily/lh/2025-02-04/pdf/download -- all 1484-byte "The request is blocked."),
so the Internet Archive remains the only route and coverage stays a
non-uniform sample of the true sitting-day population.

CDX is re-fetched into aus_sa_cdx_{ch}_2025plus.txt so the existing cache files
are left untouched.

Usage: python3 aus_sa_manifest_2025.py
"""
import json
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
START, END = "2025-01-01", "2026-08-09"


def fetch_cdx(ch):
    cache = HERE / f"aus_sa_cdx_{ch}_2025plus.txt"
    if cache.exists() and cache.stat().st_size > 1000:
        return cache.read_text()
    req = urllib.request.Request(CDX.format(ch=ch), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=900) as r:
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
            if not (START <= date <= END):
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

    (HERE / "aus_sa_manifest_2025.json").write_text(json.dumps(rows, indent=1))
    days = {(r["ch"], r["date"]) for r in rows}
    pdays = {(r["ch"], r["date"]) for r in rows if r["kind"] == "pdf"}
    print(f"{len(rows)} files over {len(days)} chamber-days "
          f"({len(pdays)} full-day PDFs, {len(days) - len(pdays)} XML-only days)")
    from collections import Counter
    print(sorted(Counter(d[1][:7] for d in days).items()))


if __name__ == "__main__":
    main()
