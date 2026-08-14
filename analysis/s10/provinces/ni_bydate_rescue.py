#!/usr/bin/env python3
"""Refetch the NI sitting days whose reportId 500s, using the by-date endpoint.

Fourteen of the 2012-2014 reports listed by GetAllHansardReports_JSON make
GetHansardComponentsByReportId_JSON return HTTP 500, consistently and on
retry -- a server-side fault on those documents, not a transport error.
GetHansardComponentsByPlenaryDate_JSON serves the same sittings and returns the
identical envelope (AllHansardComponentsList / HansardComponent), so the day is
recoverable; without this the 2013 and 2014 strata would each be missing about
half a dozen sitting days for no stated reason.

The file is written under the same api_YYYY-MM-DD_<reportId>.json name the
manifest already carries, because that is what ni_extract.py parses the date
from and what ni_link_fill.py asserts on. 1 request/second.

Usage: python ni_bydate_rescue.py            # reads ni_manifest_fill.json
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
BYDATE = ("https://data.niassembly.gov.uk/hansard.asmx/"
          "GetHansardComponentsByPlenaryDate_JSON?plenarydate=")
RAW = HERE / "ni_raw"
# a sitting with real speech is hundreds of KB; the empty-day stub is 308 bytes
MIN_BYTES = 5000


def main():
    rows = json.load(open(HERE / "ni_manifest_fill.json"))
    todo = [r for r in rows if not (RAW / r["file"]).exists()
            and r["file"].startswith("api_")]
    print(f"{len(todo)} api rows missing from ni_raw")
    ok = stub = fail = 0
    for r in todo:
        got = None
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(BYDATE + r["date"],
                                             headers={"User-Agent": UA})
                data = urllib.request.urlopen(req, timeout=300).read()
                json.loads(data)          # must parse
                got = data
                break
            except Exception as e:
                print(f"  ERR {r['date']} attempt{attempt}: {e}", flush=True)
        if got is None:
            fail += 1
            print(f"FAIL {r['date']} unreachable by date too", flush=True)
        elif len(got) < MIN_BYTES:
            stub += 1
            print(f"STUB {r['date']} {len(got)}B -- the API has no text for "
                  f"this sitting", flush=True)
        else:
            (RAW / r["file"]).write_bytes(got)
            ok += 1
            print(f"OK   {r['date']} {len(got)}B", flush=True)
    print(f"done ok={ok} stub={stub} fail={fail} of {len(todo)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
