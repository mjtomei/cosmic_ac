#!/usr/bin/env python3
"""Enumerate Senedd plenary Record meetings 2020-01-01..2024-12-31 via the
record.senedd.wales Search + SeeMore pager, and write
wales_xml_manifest_fill.json in the same row schema as the XML-era (2016-05-11
onward) rows of wales_manifest.json:

    {"url", "date", "file"}   file = xml_YYYY-MM-DD_<meetingid>.xml

These are the years the study's original two-window download design
(2006-2010, 2015-2019) skipped on the XML side; wales_manifest_build.py with
S10_FILL=1 covers the PDF side (2011-2014).

Same shape as wales_harvest_2025.py -- one MONTH per query because the Search
result set is capped at 100 rows.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
BASE = ("https://record.senedd.wales/Search/SeeMore?type=2&meetingtype=-4"
        "&start={lo}&end={hi}&Page={page}")
MONTHS = [f"{y}-{m:02d}" for y in range(2020, 2025) for m in range(1, 13)]
ROW = re.compile(r"\.\./Meeting/(\d+)")
DATE = re.compile(r"Meeting on (\d{2})/(\d{2})/(\d{4})")
LO, HI = "2020-01-01", "2024-12-31"


def get(url):
    for attempt in range(4):
        time.sleep(1.0 + attempt * 3)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            print(f"  ! {e}", file=sys.stderr)
    raise RuntimeError(url)


def main():
    found = {}
    for ym in MONTHS:
        y, m = int(ym[:4]), int(ym[5:7])
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        lo, hi = f"{ym}-01", f"{ny:04d}-{nm:02d}-01"
        page, got = 1, 0
        while True:
            j = json.loads(get(BASE.format(lo=lo, hi=hi, page=page)))
            res = j.get("Results") or []
            if not res:
                break
            for frag in res:
                mid = ROW.search(frag)
                dm = DATE.search(frag)
                if not mid or not dm:
                    print(f"  ?? unparsed fragment {ym} p{page}", file=sys.stderr)
                    continue
                dd, mm, yyyy = dm.groups()
                date = f"{yyyy}-{mm}-{dd}"
                if not date.startswith(ym):
                    continue          # `end` is inclusive of the next 1st
                found[mid.group(1)] = date
            got += len(res)
            page += 1
            if page > 30:
                break
        print(f"{ym}: {got} rows, total {len(found)}", file=sys.stderr)

    rows = []
    for mid, date in sorted(found.items(), key=lambda kv: (kv[1], kv[0])):
        if not (LO <= date <= HI):
            print(f"  skip out-of-window {date} m={mid}", file=sys.stderr)
            continue
        rows.append({
            "url": ("https://record.senedd.wales/XMLExport/Download?meetingID="
                    f"{mid}&xmlDownloadType=BilingualTranscript"),
            "date": date,
            "file": f"xml_{date}_{mid}.xml",
        })
    json.dump(rows, open(HERE / "wales_xml_manifest_fill.json", "w"), indent=1)

    bymonth = {}
    for r in rows:
        bymonth.setdefault(r["date"][:4], set()).add(r["date"][:7])
    for y in range(2020, 2025):
        got = sorted(bymonth.get(str(y), []))
        missing = [f"{y}-{m:02d}" for m in range(1, 13)
                   if f"{y}-{m:02d}" not in got]
        print(f"[cover] {y}: {len(got)}/12 months; missing={missing}",
              file=sys.stderr)
    print(f"wrote {len(rows)} rows"
          + (f" ({rows[0]['date']} .. {rows[-1]['date']})" if rows else ""))


if __name__ == "__main__":
    main()
