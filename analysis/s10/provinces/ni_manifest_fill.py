#!/usr/bin/env python3
"""Northern Ireland Assembly plenary manifest for the backfill years.

The two windows the original build skipped, 2011-2014 and 2020-2024, straddle
the same platform change ni_extract.py already knows about, so each half is
taken from the source whose format the extractor supports:

  * archive.niassembly.gov.uk static HTML (arch_*.htm), enumerated from the
    per-session index pages hansard_sessionYYYY.htm.  Covers 2011-01-17 to
    2011-12-06, after which the archive site is frozen.
  * data.niassembly.gov.uk's Hansard API (api_*.json), enumerated from
    GetAllHansardReports_JSON.  Its earliest report is 2012-09-10; asking
    GetHansardComponentsByPlenaryDate for anything before that returns a
    308-byte stub, so the API genuinely does not hold the earlier sittings.

WHAT IS NOT HERE

  2011-12-12 .. 2012-09-09.  Between the archive's freeze and the API's first
  report, this script finds nothing.  That window is not a gap in the record,
  only in these two sources: the Assembly's live per-day pages carry the whole
  Official Report inline, in the same Word-export markup the frozen archive
  uses.  ni_manifest_gap.py enumerates those 44 sitting days and
  ni_gap_extract.py parses them into segments_ni_fill2.jsonl.  (This file used
  to record the window as PDF-only and deliberately skipped; that was wrong.
  The PDF exists, but nothing needs it.)

  2018.  Not a gap in the sources.  The Assembly did not sit at all between
  March 2017 and January 2020 (the Stormont collapse); the API lists six 2017
  reports, none for 2018, and one for 2019 (the 21 October recall).  2022-2023
  is thin for the same reason -- the second collapse, February 2022 to
  February 2024 -- and the API's counts (32 reports in 2022, one in 2023) are
  the real sitting record, not a harvest shortfall.

Usage: python ni_manifest_fill.py        # writes ni_manifest_fill.json
"""
import collections
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
ARCH = "https://archive.niassembly.gov.uk/record/"
API = ("https://data.niassembly.gov.uk/hansard.asmx/"
       "GetHansardComponentsByReportId_JSON?reportId=")
ALL_REPORTS = ("https://data.niassembly.gov.uk/hansard.asmx/"
               "GetAllHansardReports_JSON")
FILL = {2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024}
# the session index folder is the SESSION start year, not the document year:
# reports2010/110321.htm is 21 March 2011
SESSIONS = ["2010", "2011"]
# listed in no index but served: the archive was frozen mid-week
EXTRA = [("2011", "111206")]


def get(url, tries=3):
    for attempt in range(tries):
        time.sleep(1.0 + 3 * attempt)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            if attempt == tries - 1:
                raise
            print(f"  retry {type(e).__name__} {url}", flush=True)


def archive_rows():
    seen = {}
    for sess in SESSIONS:
        page = get(ARCH + f"hansard_session{sess}.htm").decode("cp1252", "replace")
        hits = re.findall(rf'href="(reports{sess}/(\d{{6}})\.htm)"', page, re.I)
        print(f"  session{sess} index: {len(set(hits))} report links", flush=True)
        for href, yymmdd in hits:
            seen[yymmdd] = (sess, href)
    for sess, yymmdd in EXTRA:
        seen.setdefault(yymmdd, (sess, f"reports{sess}/{yymmdd}.htm"))

    rows = []
    for yymmdd, (sess, href) in sorted(seen.items()):
        date = f"20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:]}"
        if int(date[:4]) not in FILL:
            continue
        rows.append({"url": ARCH + href, "date": date, "part": "",
                     "file": f"arch_{date}.htm"})
    return rows


def api_rows():
    reports = json.loads(get(ALL_REPORTS))["AllHansardComponentsList"]["HansardComponent"]
    print(f"  GetAllHansardReports: {len(reports)} reports", flush=True)
    rows = []
    for r in reports:
        date = r["PlenaryDate"][:10]
        if int(date[:4]) not in FILL:
            continue
        rid = r["ReportDocId"]
        rows.append({"url": API + rid, "date": date, "part": "",
                     "file": f"api_{date}_{rid}.json"})
    return sorted(rows, key=lambda r: r["date"])


def main():
    rows = archive_rows() + api_rows()
    have = set()
    for prev in ("ni_manifest.json", "ni_manifest_2025.json"):
        p = os.path.join(HERE, prev)
        if os.path.exists(p):
            have |= {r["file"] for r in json.load(open(p))}
    before = len(rows)
    rows = [r for r in rows if r["file"] not in have]
    if before != len(rows):
        print(f"  dropped {before - len(rows)} rows already in the built corpus")

    out = os.path.join(HERE, "ni_manifest_fill.json")
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1)

    per = collections.Counter(r["date"][:4] for r in rows)
    src = collections.Counter((r["date"][:4], r["file"][:4]) for r in rows)
    print(f"{len(rows)} sitting days -> ni_manifest_fill.json")
    for y in sorted(FILL):
        n = per.get(str(y), 0)
        bits = ", ".join(f"{k[1].rstrip('_')}:{v}" for k, v in sorted(src.items())
                         if k[0] == str(y))
        print(f"  {y}: {n:>3d} days  {bits}"
              + ("   <-- NOTHING FOUND" if not n else ""))


if __name__ == "__main__":
    main()
