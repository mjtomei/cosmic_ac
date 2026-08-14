#!/usr/bin/env python3
"""Newfoundland & Labrador Hansard manifest for the backfill years.

WHY THE FILL YEARS ARE MISSING

The original S10 design sampled two windows, 2006-2010 and 2015-2019, so
`nl_manifest.json` (493 rows) has a hole at 2011-2014 and another at
2020-2024. Nothing about those years is harder to get; they were simply never
asked for.

WHY NOT THE INTERNET ARCHIVE (the `_ia` in the name is historical)

This script was scoped as an Archive job, following `aus_wa_manifest_ia.py`,
because Western Australia's Hansard section is behind a WAF that blocks the
public outright. Checked before writing a line of it: assembly.nl.ca serves
Hansard normally to an honest research user-agent -- both the section index and
a 2006 sitting page returned 200. The publisher is therefore the source, and
the Archive is the fallback for individual days the publisher has dropped.

That matters for more than politeness. `nl_manifest.json`'s 493 rows are live
assembly.nl.ca URLs; pulling the fill years from the Archive instead would mean
the corpus's NL panel changed provenance halfway through its own time series,
and any before/after difference would be confounded with that switch.

WHERE THE SITTING DAYS COME FROM

Each General Assembly session has its own directory whose index lists every
sitting day it holds; the section index at /HouseBusiness/Hansard/ lists the
session directories. That is an enumeration of what exists, not a guess from a
date range, so a day the House did not sit and a day whose transcript is
missing are distinguishable. The URL embeds a General Assembly and session
number that a date alone cannot determine, which is exactly why the listing has
to be read rather than constructed.

The Archive's own CDX index is queried afterwards purely as a cross-check: if
it holds a fill-year sitting page the live listing does not, that day is
reported and added from the Archive with `via_ia` set on the row.

SOFT 404s

assembly.nl.ca answers a missing Hansard page with HTTP 200 and a 4,755-byte
"Sorry, this page could not be found!" page, so status code alone cannot tell a
sitting day from a dead link -- and download.py's type check passes it, since it
is valid HTML. The Archive has crawled some of those error pages and stored
them under the sitting-day URL, which is how two of the five days the CDX index
appeared to hold beyond the live listing (2013-03-22, 2020-09-20) turned out
not to exist at all. Every candidate is fetched and checked for the error text
before it enters the manifest; is_error_page() below is also what
`nl_link_fill.py` uses to keep such pages out of the extractor.

FILE NAMING

`download.py`'s local_name() prefixes NL files with their session directory
because basenames collide across sessions (06-02-23.htm recurs), giving
`ga47session1_12-03-05.htm`. Rows here carry `session` so that convention
holds, and the session directory is taken verbatim from the URL that worked --
the site links the same directory as both `ga50session2` and `ga50Session2`,
and normalising the case would produce two prefixes for one session.

WHICH PAGES COUNT

The original manifest is sitting-day transcripts plus two prorogation pages; it
excludes swearing-in ceremonies, which are member-by-member oath recitations
rather than debate. Matched here so the fill years measure the same thing the
sampled years did.

Usage:
  python nl_manifest_ia.py                 # writes nl_manifest_fill.json
  python nl_manifest_ia.py --no-ia-check   # skip the Archive cross-check
"""
import argparse
import collections
import json
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.assembly.nl.ca/HouseBusiness/Hansard/"
CDX = "http://web.archive.org/cdx/search/cdx"
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
FILL = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]

HREF = re.compile(r'href\s*=\s*"([^"]+)"', re.I)
SESSION_DIR = re.compile(r"^(ga\d+session\d+)/?$", re.I)
# YY-MM-DD at the start of the basename, then any suffix before the extension
DAY_FN = re.compile(r"^(\d{2})-(\d{2})-(\d{2})(.*)\.html?$", re.I)
SWEARING = re.compile(r"swear", re.I)


ERROR_MARK = re.compile(r"this page could not be found|NL - Error Page", re.I)


def is_error_page(text):
    """assembly.nl.ca's 200-with-an-error-page response for a missing day."""
    return bool(ERROR_MARK.search(text[:6000]))


def get(url, tries=3):
    for attempt in range(tries):
        time.sleep(1.0 + 3.0 * attempt)          # >= 1 s between requests
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == tries - 1:
                print(f"  GET FAILED {url}: {type(e).__name__} {e}", flush=True)
    return ""


def full_year(yy):
    return 1900 + yy if yy > 50 else 2000 + yy


def parse_day(href):
    """-> (date, session, basename, suffix) or None."""
    href = href.split("#")[0].split("?")[0]
    if "/" in href.strip("/"):
        parts = href.strip("/").split("/")
        sess, base = parts[-2], parts[-1]
    else:
        return None
    m = DAY_FN.match(urllib.parse.unquote(base))
    if not m or not SESSION_DIR.match(sess + "/"):
        return None
    yy, mm, dd, suffix = m.groups()
    return (f"{full_year(int(yy))}-{mm}-{dd}", sess, base, suffix.strip())


def session_dirs():
    """Session directories listed by the Hansard section index."""
    html = get(BASE)
    if not html:
        raise SystemExit("cannot read the Hansard section index -- stopping")
    out = []
    for href in HREF.findall(html):
        m = SESSION_DIR.match(href.strip())
        if m and m.group(1).lower() not in [d.lower() for d in out]:
            out.append(m.group(1))
    return out


def harvest(dirs, years):
    """Every sitting-day page each session directory lists, in the fill years."""
    rows, per_dir = {}, {}
    for d in dirs:
        html = get(BASE + d + "/")
        if not html:
            per_dir[d] = None                    # distinct from "listed none"
            continue
        found = 0
        for href in HREF.findall(html):
            p = parse_day(d + "/" + href.strip()) or parse_day(href.strip())
            if not p:
                continue
            date, sess, base, suffix = p
            if int(date[:4]) not in years or SWEARING.search(base):
                continue
            found += 1
            url = BASE + sess + "/" + base
            # the site links one session directory as both ga50session1 and
            # ga50Session1; case-fold the key so that is one day, not two
            key = (date, sess.lower(), base.lower())
            rows[key] = {"date": date, "url": url, "name": base,
                         "session": sess, "suffix": suffix}
        per_dir[d] = found
        print(f"  {d}: {found} fill-year pages", flush=True)
    return rows, per_dir


def ia_dates(years):
    """Fill-year sitting pages the Archive holds -> {date: (ts, original)}.

    One query per year with retries: a single unbounded query for the whole
    Hansard tree returns thousands of rows and CDX answers it with a 504 as
    often as not. The year filter is on CAPTURE date, not sitting date -- the
    Archive routinely fetches a 2012 sitting in 2017 -- so the span queried
    runs to the present and the filename date does the real filtering.
    """
    best = {}
    for y in range(min(years), 2027):
        q = {"url": "assembly.nl.ca/HouseBusiness/Hansard/*", "output": "json",
             "filter": "statuscode:200", "collapse": "urlkey",
             "fl": "original,timestamp", "from": str(y), "to": str(y),
             "limit": "20000"}
        url = CDX + "?" + urllib.parse.urlencode(q)
        rows = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=240) as r:
                    rows = json.loads(r.read().decode() or "[]")
                break
            except Exception:
                time.sleep(8 * (attempt + 1))
        if rows is None:
            print(f"  cdx {y}: FAILED (cross-check incomplete)", flush=True)
            continue
        print(f"  cdx {y}: {max(0, len(rows) - 1)} rows", flush=True)
        for orig, ts in rows[1:]:
            p = parse_day(urllib.parse.unquote(orig))
            if not p:
                continue
            date, sess, base, _ = p
            if int(date[:4]) not in years or SWEARING.search(base):
                continue
            key = (date, sess.lower(), base.lower())
            if key not in best or ts > best[key][0]:
                best[key] = (ts, orig, sess, base)
        time.sleep(1.5)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="nl_manifest_fill.json")
    ap.add_argument("--years", default="")
    ap.add_argument("--no-ia-check", action="store_true")
    a = ap.parse_args()
    years = [int(x) for x in a.years.split(",")] if a.years else FILL

    dirs = session_dirs()
    print(f"{len(dirs)} session directories: {' '.join(dirs)}")
    rows, per_dir = harvest(dirs, years)
    unreadable = [d for d, n in per_dir.items() if n is None]
    if unreadable:
        print(f"  WARNING: could not read {unreadable}")

    if not a.no_ia_check:
        print("Internet Archive cross-check:")
        ia = ia_dates(years)
        extra = sorted(set(ia) - set(rows))
        print(f"  archive holds {len(ia)} fill-year pages; "
              f"{len(extra)} not in the live listing"
              + (f": {[k[0] for k in extra]}" if extra else ""))
        # Each candidate is a day the session index does not link. Try the
        # publisher first anyway (the page can exist unlinked), then the
        # Archive; a candidate that is an error page both places did not
        # happen, and is reported as such rather than dropped in silence.
        for key in extra:
            date, _, _ = key
            ts, orig, sess, base = ia[key]
            live = BASE + sess + "/" + base
            body = get(live)
            if body and not is_error_page(body):
                rows[key] = {"date": date, "url": live, "name": base,
                             "session": sess, "suffix": "",
                             "unlisted": True}
                print(f"    {date} {sess}: unlisted but live -> publisher")
                continue
            snap = f"https://web.archive.org/web/{ts}id_/{orig}"
            body = get(snap)
            if body and not is_error_page(body):
                rows[key] = {"date": date, "url": snap, "name": base,
                             "session": sess, "suffix": "", "via_ia": True}
                print(f"    {date} {sess}: gone from the site -> archive")
            else:
                print(f"    {date} {sess}: DROPPED -- error page live and in "
                      f"the archive; the House did not sit / page never existed")

    out = sorted(rows.values(), key=lambda r: (r["date"], r["session"]))
    with open(os.path.join(HERE, a.out), "w") as fh:
        json.dump(out, fh, indent=1)

    per = collections.Counter(r["date"][:4] for r in out)
    days = collections.defaultdict(set)
    for r in out:
        days[r["date"][:4]].add(r["date"])
    print(f"{len(out)} rows -> {a.out}")
    for y in years:
        n = per.get(str(y), 0)
        flag = "  <-- NO SITTING PAGES FOUND" if not n else ""
        print(f"  {y}: {n:>3d} pages, {len(days[str(y)]):>3d} distinct days{flag}")


if __name__ == "__main__":
    main()
