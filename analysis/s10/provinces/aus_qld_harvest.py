#!/usr/bin/env python3
"""Harvest the Queensland Hansard day-URL manifest from the Sitecore search API.

www.parliament.qld.gov.au exposes its Hansard index through the same JSON
endpoint the advanced-search SPA calls:

    POST /qpsapi/Search/SearchForPhrase
      SearchDataSourceItemGuid=<guid from the search page's hidden input>
      SelectedSearchIndex=qps_hansard_index
      QueryText=<phrase>          (required; empty query returns nothing)
      Years=<YYYY>                (repeatable facet)
      Page=0                      (page 0 carries the whole year; page 1 empty)

The response is a JSON-encoded HTML fragment; every Record of Proceedings for
the year appears as an <a href="https://documents.parliament.qld.gov.au/
events/han/{YYYY}/{YYYY}_{MM}_{DD}_WEEKLY.PDF">. Two different query phrases
are unioned so a stray relevance cut-off cannot silently drop a sitting day.

The same index also carries estimates-committee transcripts
({YYYY}_{MM}_{DD}_EST_{A..G}.PDF, ..._ESTIMATES{XXX}.PDF); those are committee
hearings, not chamber debate, and are filtered out. Despite the name, one
_WEEKLY.PDF is ONE sitting day (verified: 2019_02_12/13/14 all exist, the
Monday does not, and every running header inside a file carries a single date).

Usage: python3 aus_qld_harvest.py            (writes aus_qld_manifest.json)
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
API = "https://www.parliament.qld.gov.au/qpsapi/Search/SearchForPhrase"
GUID = "6bc7b54d-2c4e-469c-bab7-7009a785a4f1"
YEARS = list(range(2006, 2011)) + list(range(2015, 2020))
PHRASES = ["Queensland", "member"]
HREF = re.compile(r'href="(https://documents\.parliament\.qld\.gov\.au/[^"]+)"', re.I)
DATE = re.compile(r"/(\d{4})/(\d{4})_(\d{2})_(\d{2})_WEEKLY\.PDF$", re.I)


def query(phrase, year):
    body = urllib.parse.urlencode([
        ("SearchDataSourceItemGuid", GUID),
        ("SelectedSearchIndex", "qps_hansard_index"),
        ("QueryText", phrase),
        ("Years", str(year)),
        ("Page", "0"),
    ]).encode()
    req = urllib.request.Request(API, data=body, headers={
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.parliament.qld.gov.au/Global/Search?index=qps_hansard_index",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    found = {}
    for year in YEARS:
        for phrase in PHRASES:
            time.sleep(1.2)
            try:
                frag = query(phrase, year)
            except Exception as e:
                print(f"ERR {year} {phrase}: {e}", file=sys.stderr)
                continue
            n = 0
            for url in HREF.findall(frag):
                m = DATE.search(url)
                if not m or m.group(1) != m.group(2):
                    continue
                date = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
                if int(m.group(2)) != year:
                    continue
                found.setdefault(date, url)
                n += 1
            print(f"{year} '{phrase}': {n} hits, running total {len(found)}",
                  file=sys.stderr)

    rows = [{"url": u, "date": d, "prov": "QLD"}
            for d, u in sorted(found.items())]
    (HERE / "aus_qld_manifest.json").write_text(json.dumps(rows, indent=1))
    per = {}
    for r in rows:
        per[r["date"][:4]] = per.get(r["date"][:4], 0) + 1
    print(f"manifest: {len(rows)} sitting days", file=sys.stderr)
    for y in sorted(per):
        print(f"  {y}: {per[y]}", file=sys.stderr)


if __name__ == "__main__":
    main()
