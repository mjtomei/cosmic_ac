#!/usr/bin/env python3
"""Alberta Hansard manifest for the backfill years 2011-2014 and 2020-2024.

WHY THESE YEARS ARE MISSING

Nothing was wrong with them. The original harvest (`ab_manifest.json`, 884 rows)
was built as two windows, 2006-2010 and 2015-2019, and `ab_manifest_2025.py`
later added 2025 onwards. The Assembly sits continuously; the gaps are an
artifact of the study's sampling design, not of the source.

WHY THE LIVE SITE AND NOT THE INTERNET ARCHIVE

The plan for this backfill was to build from the Archive, on the strength of a
CDX query showing 4,779 archived Hansard PDFs. That route works, but it turned
out to be unnecessary: assembly.ab.ca's own transcripts-by-type index still
serves the fill years, responds normally to a polite client, and is what
`ab_manifest_2025.py` already uses. Measured side by side, the live index
returns 2011:60 2012:72 2013:74 2014:58 2020:139 2021:121 2022:92 2023:37
2024:66 -- the Archive's counts for the same years are identical except
2021 (124), 2022 (93) and 2024 (67). Preferring the publisher's own copy means
the manifest carries the current corrected transcript rather than whatever
version a crawler happened to catch, and it costs the Archive nothing.

The five-file discrepancy is not waved away. After the live pass this script
runs one CDX query per fill year and adds any sitting-file the Archive holds
and the live index does not, via `/web/<ts>id_/<original>` -- the modifier
matters, since without it the Archive returns its toolbar-wrapped HTML page
about the PDF instead of the PDF. Those rows are marked `"src": "ia"` so a
reader can tell which bytes came from where.

THE URL SCHEME NEEDS A LEGISLATURE, WHICH A DATE DOES NOT GIVE

  .../hansards/han/legislature_26/session_2/20060222_1500_01_han.pdf

Legislature and session cannot be derived from the date -- sessions straddle
calendar years and a general election restarts the numbering mid-year. So the
index is scraped per (legislature, session) and the filename date decides which
rows are kept. `_1500_` is the sitting time: one sitting day can have two or
three files (afternoon and evening), which is why file counts exceed day counts.

Usage:
  python ab_manifest_fill.py                 # writes ab_manifest_fill.json
  python ab_manifest_fill.py --no-ia         # live index only
"""
import argparse
import collections
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
IDX = ("https://www.assembly.ab.ca/assembly-business/transcripts/"
       "transcripts-by-type?legl={l}&session={s}")
HREF = re.compile(r"LADDAR_files[^\"'>\s]*")
CDX = "http://web.archive.org/cdx/search/cdx"
NAME = re.compile(r"^(\d{4})(\d{2})(\d{2})_\d{3,4}_\d+_han\.pdf$", re.I)

FILL = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]
# legislature 27 (2008-12) through 31 (2023- ); sessions run 1..5 in practice,
# 6 is queried to catch a session this harvest does not know about
LEGL = range(27, 32)
SESS = range(1, 7)


def live_rows(years):
    """One index page per (legislature, session); keep fill-year PDFs."""
    rows = {}
    for legl in LEGL:
        for sess in SESS:
            time.sleep(1.2)
            try:
                req = urllib.request.Request(IDX.format(l=legl, s=sess),
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    h = r.read().decode("utf-8", "replace")
            except Exception as e:
                print(f"  legl={legl} sess={sess}: FAILED {type(e).__name__} {e}",
                      flush=True)
                continue
            kept = 0
            for raw in set(HREF.findall(h)):
                path = raw.replace("\\", "/")
                if "/hansards/han/" not in path or not path.lower().endswith(".pdf"):
                    continue
                name = path.rsplit("/", 1)[-1]
                m = NAME.match(name)
                if not m or int(m.group(1)) not in years:
                    continue
                rows[name] = {
                    "date": f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
                    "url": "https://docs.assembly.ab.ca/" + path,
                    "name": name,
                    "legl": legl,
                    "session": sess,
                    "src": "live",
                }
                kept += 1
            if kept:
                print(f"  legl={legl} sess={sess}: {kept} fill-year files", flush=True)
    return rows


def ia_rows(years, have):
    """Archive supplement: one CDX query per year, filtered on filename date.

    The capture timestamp is when the Archive fetched the file, often years
    after the sitting, so the query spans every capture year from the earliest
    fill year forward and the filename decides what a row belongs to. A year
    whose query fails is printed, not silently dropped -- a chamber-year that
    comes back empty because of a 504 looks exactly like one where the Assembly
    never sat.
    """
    best, failed = {}, []
    for cy in range(min(years), 2027):
        q = {"url": "docs.assembly.ab.ca/LADDAR_files/docs/hansards/han/*",
             "output": "json", "filter": "statuscode:200",
             "collapse": "urlkey", "fl": "original,timestamp",
             "from": str(cy), "to": str(cy), "limit": "20000"}
        url = CDX + "?" + urllib.parse.urlencode(q)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=240) as r:
                    got = json.loads(r.read().decode() or "[]")
                rows = got[1:] if got else []
                print(f"  cdx {cy}: {len(rows)} rows", flush=True)
                break
            except Exception as e:
                if attempt == 3:
                    failed.append(cy)
                    rows = []
                    print(f"  cdx {cy}: FAILED {type(e).__name__}", flush=True)
                else:
                    time.sleep(8 * (attempt + 1))
        for orig, ts in rows:
            name = urllib.parse.unquote(orig).split("/")[-1]
            m = NAME.match(name)
            if not m or int(m.group(1)) not in years or name in have:
                continue
            # latest snapshot wins: most likely the final corrected transcript
            if name not in best or ts > best[name][0]:
                best[name] = (ts, orig)
        time.sleep(1.5)
    if failed:
        print(f"  WARNING: CDX gave nothing for capture years {failed}")
    out = {}
    for name, (ts, orig) in best.items():
        m = NAME.match(name)
        legl = sess = None
        p = re.search(r"legislature_(\d+)/session_(\d+)", orig)
        if p:
            legl, sess = int(p.group(1)), int(p.group(2))
        out[name] = {
            "date": f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
            "url": f"https://web.archive.org/web/{ts}id_/{orig}",
            "name": name,
            "legl": legl,
            "session": sess,
            "src": "ia",
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="")
    ap.add_argument("--out", default="ab_manifest_fill.json")
    ap.add_argument("--no-ia", action="store_true")
    a = ap.parse_args()
    years = [int(x) for x in a.years.split(",")] if a.years else FILL

    print("live index:")
    rows = live_rows(years)
    n_live = len(rows)
    if not a.no_ia:
        print("archive supplement:")
        extra = ia_rows(years, set(rows))
        rows.update(extra)
        print(f"  archive added {len(extra)} files the live index lacks")

    out = sorted(rows.values(), key=lambda r: (r["date"], r["name"]))
    json.dump(out, open(HERE / a.out, "w"), indent=1)

    per = collections.Counter(r["date"][:4] for r in out)
    days = collections.defaultdict(set)
    for r in out:
        days[r["date"][:4]].add(r["date"])
    print(f"\n{len(out)} files ({n_live} live, {len(out)-n_live} archive) over "
          f"{len(set(r['date'] for r in out))} sitting days -> {a.out}")
    for y in years:
        y = str(y)
        flag = "   <-- NOTHING FOUND" if not per[y] else ""
        print(f"  {y}: {per[y]:>3d} files, {len(days[y]):>3d} distinct days{flag}")


if __name__ == "__main__":
    main()
