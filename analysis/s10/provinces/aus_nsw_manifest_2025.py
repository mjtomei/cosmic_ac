#!/usr/bin/env python3
"""2025+ extension of the NSW Hansard day manifest.

One GET per year against the public unauthenticated year index
    https://api.parliament.nsw.gov.au/api/hansard/search/year/{YYYY}
which returns every sitting date with, per chamber, the PdfDocId of the
whole-day transcript.  Same row schema as aus_nsw_manifest.json:
    {url, date, chamber, doc_id, uncorrected, fname}

Usage: python3 aus_nsw_manifest_2025.py
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
YEAR = "https://api.parliament.nsw.gov.au/api/hansard/search/year/{}"
PDF = "https://api.parliament.nsw.gov.au/api/hansard/search/daily/pdf/{}"
CH = {"Legislative Assembly": "LA", "Legislative Council": "LC"}
START, END = "2025-01-01", "2026-08-09"
# The 2011-14 and 2020-24 years the windowed design skipped. Same public year
# index, so backfilling is a wider year list and a different output file.
import os
FILL_YEARS = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]
if os.environ.get("S10_FILL"):
    START, END = "2011-01-01", "2024-12-31"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    rows = []
    for year in (FILL_YEARS if os.environ.get('S10_FILL') else (2025, 2026)):
        time.sleep(1.1)
        days = get(YEAR.format(year))
        n = 0
        for d in days:
            date = d["date"][:10]
            if not (START <= date <= END):
                continue
            for ev in d.get("Events") or []:
                ch = CH.get(ev.get("Chamber"))
                doc = ev.get("PdfDocId")
                if not ch or not doc:
                    continue
                rows.append({
                    "url": PDF.format(doc),
                    "date": date,
                    "chamber": ch,
                    "doc_id": doc,
                    "uncorrected": bool(ev.get("Uncorrected")),
                    "fname": f"{date}_{ch}_{doc}.pdf",
                })
                n += 1
        print(f"{year}: {len(days)} indexed dates, {n} chamber-days in period")
    rows.sort(key=lambda r: (r["date"], r["chamber"]))
    (HERE / f"aus_nsw_manifest{os.environ.get('S10_SUFFIX', '_2025')}.json").write_text(json.dumps(rows, indent=1))
    unc = sum(1 for r in rows if r["uncorrected"])
    print(f"manifest rows: {len(rows)}  (uncorrected/proof: {unc})")
    per = {}
    for r in rows:
        per.setdefault(r["date"][:4], []).append(r["chamber"])
    for y in sorted(per):
        c = per[y]
        print(f"  {y}: {len(c)} chamber-days "
              f"(LA={c.count('LA')} LC={c.count('LC')}), "
              f"{len({r['date'] for r in rows if r['date'][:4] == y})} dates")


if __name__ == "__main__":
    main()
