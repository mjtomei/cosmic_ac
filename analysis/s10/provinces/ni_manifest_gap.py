#!/usr/bin/env python3
"""Northern Ireland Assembly plenary manifest for the 2011-12/2012-09 gap.

ni_manifest_fill.py closed 2011-2014 and 2020-2024 from two sources whose
formats ni_extract.py already parses -- archive.niassembly.gov.uk static HTML
up to the archive's freeze on 2011-12-06, and data.niassembly.gov.uk's Hansard
API from its first report on 2012-09-10 -- and left the 44 sitting days in
between, recording them as reachable only as PDF.

THAT WAS WRONG, AND THE GAP NEEDS NO PDF.  The live per-day pages,
niassembly.gov.uk/assembly-business/official-report/reports-11-12/
DD-month-YYYY/, are not link-only landing pages: they carry the SAME Word-
export markup as the frozen archive site, class for class -- B1SpeakersName /
B3BodyText / B3BodyTextnoindent / Q1QuoteIndented / Q3Motion / TimePeriod /
OralAnswers-* / H3SubHeading.  ni_extract.py's extract_archive() parses them
unchanged; the only difference is the page encoding (UTF-8 here, cp1252 on the
frozen archive), so the files are named live_*.htm and decoded accordingly.
The gap therefore closes with no third turn-boundary ruleset: 2006-2012-09 is
one parser end to end.

The PDF at globalassets/documents/official-reports/plenary/{YYYY}/{YYYYMMDD}.pdf
is real and has a text layer, but it is the same text one format further
downstream, and six of the 44 days are not even filed under that name
(2012-01-17 lives under .../official-reports/health/2011-2012/, and
2012-01-30, 2012-02-27, 2012-02-28, 2012-03-26 and 2012-03-27 under numeric
stems such as 8219.pdf).  It is not used.

ENUMERATION.  Two independent routes, and they agree:

  1. The Assembly's own per-session index of plenary Official Reports,
     /assembly-business/official-report/reports-11-12/ and reports-12-13/,
     paginated 20 days to a page (?pageNo=N).  Session 11-12 lists 81 sitting
     days from 2011-05-12 to 2012-07-03; session 12-13 opens on 2012-09-10,
     exactly where the API's record begins, so the gap lies entirely inside
     session 11-12.  The site's sitemap.xml lists the same 81 day URLs, and
     the two lists diff clean.
  2. A brute probe of the canonical PDF URL for every weekday in the window
     (a CMS index can lose a day; the document store cannot invent one).  It
     served 38 of the 44 index days and produced no date the index lacks.  The
     six misses are the mis-filed PDFs listed above, all of which have a
     complete live day page.

The window runs from the day after the last archive-HTML sitting (2011-12-06)
to the day before the API's first report (2012-09-10), so the three sources
abut exactly, with no overlap and no gap.  Two days already held in HTML,
2011-12-05 and 2011-12-06, are emitted as well under the OVERLAP flag: they
are downloaded and extracted only so the new route can be diffed against the
frozen archive's own text for the same sitting, and are dropped before the
segments are written.

Usage: python ni_manifest_gap.py        # writes ni_manifest_gap.json
"""
import collections
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
SITE = "https://www.niassembly.gov.uk"
INDEX = SITE + "/assembly-business/official-report/reports-{sess}/"
SESSIONS = ["11-12", "12-13"]
LO, HI = dt.date(2011, 12, 7), dt.date(2012, 9, 9)
# already in segments_ni_fill.jsonl from the frozen archive; taken again here
# purely as a same-sitting control on the new route
OVERLAP = [dt.date(2011, 12, 5), dt.date(2011, 12, 6)]
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}
DAY_HREF = re.compile(r"reports-(\d\d-\d\d)/(\d{2})-([a-z]+)-(\d{4})")


def get(url, tries=3, head=False):
    for attempt in range(tries):
        time.sleep(1.0 + 3 * attempt)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA},
                                         method="HEAD" if head else "GET")
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, (b"" if head else r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            if attempt == tries - 1:
                raise
        except Exception:
            if attempt == tries - 1:
                raise
        print(f"  retry {url}", flush=True)


def index_days():
    """{date: session} for every day link in the paginated session indexes."""
    days = {}
    for sess in SESSIONS:
        base = INDEX.format(sess=sess)
        page, seen = 1, -1
        while True:
            url = base if page == 1 else base + f"?pageNo={page}"
            _, body = get(url)
            for _, d, mon, y in DAY_HREF.findall(body.decode("utf-8", "replace")):
                if mon in MONTHS:
                    days[dt.date(int(y), MONTHS[mon], int(d))] = (sess, mon, d, y)
            if len(days) == seen or page > 12:
                break
            seen, page = len(days), page + 1
        print(f"  session {sess}: {len(days)} cumulative day links", flush=True)
    return days


def main():
    days = index_days()
    wanted = {d: v for d, v in days.items() if LO <= d <= HI or d in OVERLAP}
    print(f"index days in the window (+{len(OVERLAP)} overlap controls): "
          f"{len(wanted)}")

    # independent check: does the document store know a day the index does not?
    pdf = SITE + "/globalassets/documents/official-reports/plenary/{y}/{ymd}.pdf"
    served, day = set(), LO
    while day <= HI:
        if day.weekday() < 5:
            status, _ = get(pdf.format(y=day.year,
                                       ymd=day.strftime("%Y%m%d")), head=True)
            if status == 200:
                served.add(day)
        day += dt.timedelta(days=1)
    idx = {d for d in wanted if d not in OVERLAP}
    print(f"canonical PDF served for {len(served)}/{len(idx)} index days")
    for d in sorted(served - idx):
        print(f"  INDEX-MISS {d} -- PDF served but absent from the index")
    for d in sorted(idx - served):
        print(f"  PDF-MISFILED {d} -- index day with no PDF at the canonical "
              f"name (day page still complete)")

    rows = []
    for d in sorted(wanted):
        sess, mon, dd, y = wanted[d]
        rows.append({"url": INDEX.format(sess=sess) + f"{dd}-{mon}-{y}/",
                     "date": d.isoformat(), "part": "",
                     "overlap": d in OVERLAP,
                     "file": f"live_{d.isoformat()}.htm"})
    with open(os.path.join(HERE, "ni_manifest_gap.json"), "w") as fh:
        json.dump(rows, fh, indent=1)

    per = collections.Counter(r["date"][:4] for r in rows)
    print(f"{len(rows)} day pages -> ni_manifest_gap.json")
    for y in sorted(per):
        print(f"  {y}: {per[y]:>3d} days")


if __name__ == "__main__":
    main()
