#!/usr/bin/env python3
"""WA Hansard manifest from the Internet Archive, for the backfill years.

WHY NOT THE PARLIAMENT DIRECTLY

`aus_wa_manifest.py` reads the Domino lookup views on parliament.wa.gov.au.
As of 2026-08-13 every path under /hansard/ returns "The request is blocked"
from the site's edge WAF -- including the link the parliament's own homepage
points at, clicked in an ordinary browser. The rest of the site serves
normally, so this is the Hansard section specifically, not an outage.

IT IS NOT US. The first guess was an IP-level block earned by the original
harvest's crawling. Matthew checked from a phone on a different network and
Hansard is blocked there too, which rules that out: the section is unavailable
to the public, not to this machine. Worth recording because the two diagnoses
call for opposite responses -- an earned block means back off and wait, while a
public outage means the archive is the only route and always will be for these
years.

Either way the block is not worked around. Rotating user agents, proxying or
otherwise disguising the client to get past a WAF is bot-detection evasion, and
it is not something to do to a parliament's website for a corpus study. The
Internet Archive serves its own copies, adds no load to the parliament, and is
already how `aus_sa_manifest.py` builds South Australia.

WHOLE DAYS ONLY, AND WHAT THAT COSTS

WA publishes each sitting day twice: one whole-day transcript,
"{A|C}{parliament} S{session} {YYYYMMDD} All.pdf", and a few dozen page-range
extracts of the same day ("... p157b-196a.pdf"), one per debate item, which is
what the Hansard search results link to. The Archive crawled the search
results, so the extracts outnumber the whole-day files roughly forty to one:
across the fill years CDX holds 550 whole-day PDFs and at least 13,000
extracts (at least, because the unfiltered per-year queries hit the 20,000-row
CDX cap for 2011 and 2022 and were truncated).

Only the whole-day files are taken. The rest of the WA corpus (2006-2010,
2015-2019) is whole-day transcripts, and per-day word counts are the check
that an extraction worked; a year assembled from extracts would be a
different measurement wearing the same column heading. Reconstructing days
from extracts is possible in principle -- take every extract for a date and
concatenate -- but the extracts overlap, skip the unlinked parts of a day, and
were crawled selectively, so the reconstruction would be neither complete nor
unbiased, and it would cost ~30,000 downloads to find that out.

The price is the earlier fill years. Whole-day coverage measured 2026-08-13,
distinct sitting dates with at least one chamber's transcript, against the
~60-75 days WA sits:

    2011: 46   2012: 22   2013: 18   2014: 10
    2020: 37   2021: 67   2022: 57   2023: 59   2024: 62

Most of those dates hold one chamber, not both: 2011-2014 average 1.2 files
per date against the two the parliament publishes, so even the day count
overstates what is there.

2020-2024 is near-complete apart from 2020. 2011-2014 is not a backfill of
those years; it is a sample of them, 2014 especially (10 days), and any
statistic broken out by year has to say so. The counts printed by this script
are the record -- a thin year is reported thin rather than quietly averaged in.

THE `id_` MODIFIER MATTERS

Wayback URLs of the form /web/<ts>/<original> return the archived page wrapped
in the Archive's own toolbar and rewritten links. `/web/<ts>id_/<original>`
returns the raw stored bytes, which for a PDF is the difference between the
document and an HTML page about the document.

Usage:
  python aus_wa_manifest_ia.py            # writes aus_wa_manifest_fill.json
  python aus_wa_manifest_ia.py --years 2011,2012
"""
import argparse
import collections
import json
import os
import re
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CDX = "http://web.archive.org/cdx/search/cdx"
FILL = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]
CACHE = os.path.join(HERE, "aus_wa_cdx_all.json")
# whole-day transcripts only -- see the docstring on extracts
ALL_PDF = r"original:.*([Aa][Ll][Ll])\.pdf"
DATE8 = re.compile(r"(\d{8})")
# A37/C40 = Assembly/Council + parliament number, S1 = session.  J40 also
# occurs: the rare joint sitting, which neither chamber's daily-transcript
# view lists and which the rest of the corpus therefore does not contain.
HOUSE = re.compile(r"^([ACJ])(\d{2})[ _+]*S(\d)", re.I)


def cdx_rows(years):
    """One query per capture year, cached on disk, with retries.

    A single unbounded query for the whole site returns tens of thousands of
    rows and CDX answers it with a 504 as often as not. Per-year queries are
    small enough to succeed, and a year that fails is reported rather than
    silently contributing nothing -- an empty chamber-year that looks like a
    parliament in recess is the failure mode worth avoiding here.

    Results are cached per capture year because the regex filter makes CDX
    walk the whole index for the host: the full sweep takes about twenty
    minutes, and rebuilding the manifest should not repeat it.
    """
    import time
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE))
    out, failed = [], []
    for y in years:
        if cache.get(str(y)) is not None:
            out += cache[str(y)]
            print(f"  cdx {y}: {len(cache[str(y)])} rows (cached)", flush=True)
            continue
        q = [("url", "parliament.wa.gov.au/Hansard/hansard.nsf/*"),
             ("output", "json"), ("filter", "statuscode:200"),
             ("filter", ALL_PDF), ("collapse", "urlkey"),
             ("fl", "original,timestamp"),
             ("from", str(y)), ("to", str(y)), ("limit", "20000")]
        url = CDX + "?" + urllib.parse.urlencode(q)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=300) as r:
                    rows = json.loads(r.read().decode() or "[]")
                cache[str(y)] = rows[1:] if rows else []
                out += cache[str(y)]
                print(f"  cdx {y}: {len(cache[str(y)])} rows", flush=True)
                break
            except Exception as e:
                if attempt == 3:
                    failed.append(y)
                    cache[str(y)] = None
                    print(f"  cdx {y}: FAILED {type(e).__name__}", flush=True)
                else:
                    time.sleep(8 * (attempt + 1))
        json.dump(cache, open(CACHE, "w"))
        time.sleep(1.5)
    json.dump(cache, open(CACHE, "w"))
    if failed:
        print(f"  WARNING: no data for {failed} -- rerun for those years")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="")
    ap.add_argument("--out", default="aus_wa_manifest_fill.json")
    a = ap.parse_args()
    years = ([int(x) for x in a.years.split(",")] if a.years else FILL)

    best = {}
    skipped = collections.Counter()
    # A capture's timestamp is when the Archive fetched it, which can be years
    # after the sitting; the year filter above is on capture date, so ask for a
    # wider span than the sitting years wanted and filter on the filename date.
    span = list(range(min(years), 2027))
    for orig, ts in cdx_rows(span):
        # '+' is a space in these paths, and unquote() does not decode it
        fn = urllib.parse.unquote(orig).split("/")[-1].replace("+", " ")
        if not fn.lower().endswith(" all.pdf"):
            continue                               # page-range extract
        m = DATE8.search(fn)
        if not m:
            continue
        d = m.group(1)
        if not (d[:4].isdigit() and int(d[:4]) in years):
            continue
        h = HOUSE.match(fn)
        if not h:
            skipped["unparsed house"] += 1
            continue
        house = h.group(1).upper()
        if house == "J":
            skipped["joint sitting"] += 1
            continue
        chamber = "LA" if house == "A" else "LC"
        date = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        key = (date, chamber)
        # one capture per sitting day and house; prefer the latest snapshot,
        # which is the one most likely to be the final corrected version
        if key not in best or ts > best[key][0]:
            best[key] = (ts, orig)

    rows = [{"url": f"https://web.archive.org/web/{ts}id_/{orig}",
             "date": date, "chamber": chamber, "prov": "aus_wa"}
            for (date, chamber), (ts, orig) in sorted(best.items())]
    with open(os.path.join(HERE, a.out), "w") as fh:
        json.dump(rows, fh, indent=1)

    per = collections.Counter(r["date"][:4] for r in rows)
    days = collections.defaultdict(set)
    both = collections.defaultdict(collections.Counter)
    for r in rows:
        days[r["date"][:4]].add(r["date"])
        both[r["date"][:4]][r["date"]] += 1
    print(f"{len(rows)} whole-day files over "
          f"{len(set(r['date'] for r in rows))} sitting days -> {a.out}")
    for k, v in sorted(skipped.items()):
        print(f"  skipped {v} ({k})")
    for y in sorted(per):
        n2 = sum(1 for c in both[y].values() if c == 2)
        print(f"  {y}: {per[y]:>3d} files, {len(days[y]):>3d} distinct days "
              f"({n2} with both chambers)")


if __name__ == "__main__":
    main()
