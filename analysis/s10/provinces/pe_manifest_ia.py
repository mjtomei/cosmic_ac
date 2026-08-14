#!/usr/bin/env python3
r"""PEI Hansard manifest for the backfill years, from third-party web indexes.

TWO SITE GENERATIONS, ONE OF WHICH IS GONE

Until mid-2019 the Legislative Assembly served each sitting day as a static PDF

    http://www.assembly.pe.ca/sittings/{YYYY}{spring|fall}/hansard/{YYYY-MM-DD}-hansard.pdf

which is exactly the naming convention the local corpus uses and that
pe_extract.py parses its date from. Those paths now 404: the Assembly moved to
a Drupal site whose documents live behind

    https://docs.assembly.pe.ca/download/dms?objectId=<uuid>&fileName=<anything>

and the old tree was not kept. So the backfill has to come from web archives.

WHAT IS AND IS NOT REACHABLE ON THE NEW SITE

The document host is a Kong gateway and is NOT bot-protected: given an
objectId it returns the PDF to an ordinary scripted GET. Measured 2026-08-13:

  * objectId + fileName            -> 200 application/pdf
  * objectId + a WRONG fileName    -> 200, same bytes (fileName is cosmetic;
                                      the objectId alone identifies the file)
  * objectId alone, no fileName    -> 500 "Error retrieving file"
  * fileName alone, no objectId    -> 500  (so you cannot address a document
                                      by its date, only by its opaque uuid)

So the whole problem is enumerating objectIds, and the gateway exposes no
route that lists them: /api /search /debates /dms /services /v1
/legislative-assembly all return Kong's "no Route matched with those values";
only /download exists.

The one real enumeration is the debates app's own POST to
wdf.princeedwardisland.ca/legislative-assembly/services/api/workflow, which
sits behind Radware Bot Manager. From a script the second and later requests
come back as bot-manager interstitials (__uzdbm_* variables); through a real
browser the search ran about two dozen queries and then stopped returning
results even for an ordinary hand-driven click, and its gpei-pagination
element renders empty so a query is capped at 20 rows with no paging. That is
how pe_manifest_2025.json was harvested while the browser route still worked.
www.assembly.pe.ca itself is behind the same bot manager: robots.txt answers,
but /jsonapi and even the homepage return the 302 interstitial.

None of that was worked around. Rotating agents, proxying, replaying signed
requests or pacing under a limit we have already been told we exceeded is
bot-detection evasion, and this is a parliament's website.

ROUTES TRIED, AND WHAT EACH RETURNED (2026-08-13)

  Internet Archive CDX, assembly.pe.ca (domain)     ~49k rows. Old-site
      YYYY-MM-DD-hansard.pdf captures for 2011-2014 only. New-site pages are
      an Angular shell: the archived /legislative-business/house-records/
      debates HTML contains gpei-root and the wdf script tags and ZERO
      objectIds, so the index page is worthless as a capture.
  Internet Archive CDX, docs.assembly.pe.ca         ~656 unique URLs, of
      which the dated Hansards below. THIS IS THE PRODUCTIVE ROUTE and the
      earlier pass missed most of it: the previous manifest matched only
      /(\d{4})-(\d{2})-(\d{2})-hansard\.pdf$/, but the new site names files
      "Hansard-4 November 2021.pdf", "Hansard - 2 July 2020.pdf" and
      "11 July 2019-Hansard.pdf", so every post-2019 document was filtered
      out. Parsing all four spellings is what recovers 2020-2024.
  Internet Archive CDX, wdf.princeedwardisland.ca   550 rows: styles.css,
      the Angular bundles, and one capture each of /api/preflight/... .
      The preflight captures are 302 stubs; no workflow response was ever
      archived, so the API's own output cannot be replayed from the Archive.
  Internet Archive CDX, princeedwardisland.ca       60 DMS links across the
      whole gov domain, zero Hansards.
  Common Crawl URL index, all 65 crawls 2019-2026   254 unique DMS URLs, 24
      of them Hansards -- every one already in the Archive set. Independent
      crawler, same link graph, no new days.
  Web search (docs.assembly.pe.ca)                  returns the same dozen
      PDFs the crawlers found, repeatedly; probe queries for specific absent
      dates ("Hansard-23 November 2021", "9 May 2024") return nothing. The
      search index is a subset of the archive set, not a supplement.
  peildo.ca (PEI Legislative Documents Online)      an open Islandora 8
      repository with a full sitemap and OAI-PMH, no bot protection -- and
      historical only: Journals 1894-2011, MLA biographies 1873-1993, images,
      and 800 hours of 1968-1973 audio. No Hansard, no 2020-2024.
  docs.assembly.pe.ca gateway route probe           see above; /download only.
  data.princeedwardisland.ca                        no API, no such dataset.

WHAT THAT LEAVES

Enumeration by objectId is impossible without the bot-protected API, but the
crawlers that did reach the site left a partial index behind, and each
objectId they recorded still resolves. The 2020-2024 stratum in this build is
therefore that recovered set: real transcripts, fetched live from the
Assembly, but a SAMPLE OF OPPORTUNITY rather than a census. The days present
are the days somebody linked to from a crawlable page, which is not a random
draw across a sitting -- treat per-year counts as coverage, not as the
sitting calendar, and do not compute anything that assumes a complete year.
The per-year counts are printed below and reported as they are. Every year in
FILL was non-empty when this was built, so the script now exits non-zero if
any of them comes back empty -- that means a route broke, not that the House
was in recess.

Usage:
  python pe_manifest_ia.py                     # writes pe_manifest_fill.json
  python pe_manifest_ia.py --years 2011,2012
  python pe_manifest_ia.py --no-cc             # skip the Common Crawl sweep
"""
import argparse
import collections
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CDX = "http://web.archive.org/cdx/search/cdx"
CC_COLLINFO = "https://index.commoncrawl.org/collinfo.json"
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
FILL = [2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024]

# 2011-04-12-hansard.pdf -- the old scheme, where the date is the name.
OLDNAME = re.compile(r"(\d{4})-(\d{2})-(\d{2})-hansard\.pdf$", re.I)
MONTHS = {m.lower(): i + 1 for i, m in enumerate(
    "January February March April May June July August September October "
    "November December".split())}
# Every spelling the DMS actually uses, confirmed by listing all 552 distinct
# fileName values seen across the archives:
#   Hansard-4 November 2021.pdf   Hansard-24-November 2020.pdf
#   Hansard - 2 July 2020.pdf     Hansard -7 July 2020-1.pdf
#   11 July 2019-Hansard.pdf      2014-05-13-hansard.pdf
DMY = re.compile(r"(\d{1,2})\s*[-\s]\s*([A-Za-z]+)\s*[-\s,]?\s*(\d{4})")


def parse_date(fn):
    """Sitting date out of a DMS fileName, in any of its four spellings."""
    fn = urllib.parse.unquote(fn).replace("+", " ").replace("ﬁ", "fi")
    m = OLDNAME.search(fn)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = DMY.search(fn)
    if m and m.group(2).lower() in MONTHS:
        return (f"{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}"
                f"-{int(m.group(1)):02d}")
    return None


def get(url, timeout=300, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""          # Common Crawl says "no captures" with a 404
            if attempt == tries - 1:
                raise
        except Exception:
            if attempt == tries - 1:
                raise
        time.sleep(8 * (attempt + 1))
    return ""


def cdx_rows(spans, host):
    """One query per capture year, with retries.

    A single unbounded query over the domain 504s as often as it answers; a
    year that fails outright is reported rather than quietly contributing
    nothing, because a missing chamber-year and a recess look identical
    downstream.
    """
    out, failed = [], []
    for y in spans:
        q = {"url": host, "matchType": "domain",
             "output": "json", "filter": "statuscode:200",
             "collapse": "urlkey", "fl": "original,timestamp",
             "from": str(y), "to": str(y), "limit": "40000"}
        try:
            rows = json.loads(get(CDX + "?" + urllib.parse.urlencode(q)) or "[]")
            out += rows[1:] if rows else []
            print(f"  cdx {host} {y}: {max(0, len(rows) - 1)} rows", flush=True)
        except Exception as e:
            failed.append(y)
            print(f"  cdx {host} {y}: FAILED {type(e).__name__}", flush=True)
        time.sleep(1.5)
    if failed:
        print(f"  WARNING: no data for capture years {failed} -- rerun")
    return out


def cc_rows(min_year):
    """Common Crawl's URL index, every crawl from min_year on.

    An index built by a different crawler on a different schedule. It has
    never yet added a Hansard the Archive did not also have -- both are
    following the same handful of leaked links -- but it costs a minute and
    it is the only independent check that the Archive set is the whole of
    what escaped the site.
    """
    out = []
    try:
        crawls = [c["id"] for c in json.loads(get(CC_COLLINFO, timeout=90))]
    except Exception as e:
        print(f"  cc: collinfo FAILED {type(e).__name__}; skipping")
        return out
    crawls = [c for c in crawls if int(c.split("-")[2]) >= min_year]
    for c in crawls:
        q = urllib.parse.urlencode({"url": "docs.assembly.pe.ca/*",
                                    "output": "json"})
        try:
            body = get(f"https://index.commoncrawl.org/{c}-index?{q}",
                       timeout=240, tries=3)
        except Exception as e:
            print(f"  cc {c}: FAILED {type(e).__name__}", flush=True)
            time.sleep(1.2)
            continue
        rows = [json.loads(l) for l in body.splitlines() if l.strip()]
        out += [r["url"] for r in rows if r.get("url")]
        time.sleep(1.2)
    print(f"  cc: {len(crawls)} crawls, {len(out)} urls", flush=True)
    return out


def dms_hits(urls, years):
    """date -> objectId, over anything that looks like a DMS download link."""
    hits = {}
    for u in urls:
        du = urllib.parse.unquote(u).replace("ﬁ", "fi")
        if "download/dms" not in du:
            continue
        oid = re.search(r"objectId=([0-9a-fA-F-]{36})", du)
        fn = re.search(r"fileName=([^&]*)", du)
        if not oid or not fn or "hansard" not in fn.group(1).lower():
            continue
        date = parse_date(fn.group(1))
        if date and int(date[:4]) in years:
            hits.setdefault(date, oid.group(1))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="")
    ap.add_argument("--out", default="pe_manifest_fill.json")
    ap.add_argument("--no-cc", action="store_true")
    a = ap.parse_args()
    years = [int(x) for x in a.years.split(",")] if a.years else FILL
    yset = set(years)

    # The capture timestamp is when the Archive fetched the file, which for a
    # 2011 sitting is anywhere from 2011 to the day the old tree disappeared.
    # Ask wide, then filter on the DATE IN THE FILENAME.
    span = list(range(min(years), 2027))

    # Route 1: old-site static PDFs, replayed from the Archive (2011-2014).
    best = {}
    for orig, ts in cdx_rows(span, "assembly.pe.ca"):
        fn = urllib.parse.unquote(orig).split("/")[-1].split("?")[0]
        m = OLDNAME.match(fn)
        if not m or int(m.group(1)) not in yset:
            continue
        date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        # prefer the latest capture: most likely the final corrected transcript
        if date not in best or ts > best[date][0]:
            best[date] = (ts, orig)

    rows = [{"url": f"https://web.archive.org/web/{ts}id_/{orig}",
             "date": date, "prov": "pe", "local": f"{date}-hansard.pdf",
             "route": "ia-oldsite"}
            for date, (ts, orig) in sorted(best.items())]

    # Route 2: objectIds harvested from whatever crawlers recorded, then
    # fetched LIVE from the Assembly rather than from an archive -- a current,
    # complete PDF instead of whatever a crawler happened to store, and the
    # only way any 2020-2024 day is reachable at all.
    seen = [r[0] for r in cdx_rows(span, "docs.assembly.pe.ca")]
    if not a.no_cc:
        seen += cc_rows(max(2019, min(years)))
    dms = dms_hits(seen, yset)

    have = {r["date"] for r in rows}
    for date, oid in sorted(dms.items()):
        if date in have:
            continue
        rows.append({
            "url": ("https://docs.assembly.pe.ca/download/dms?objectId=" + oid
                    + f"&fileName={date}-hansard.pdf"),
            "date": date, "prov": "pe", "local": f"{date}-hansard.pdf",
            "object_id": oid, "route": "dms-objectid"})
    rows.sort(key=lambda r: r["date"])
    with open(os.path.join(HERE, a.out), "w") as fh:
        json.dump(rows, fh, indent=1)

    per = collections.Counter(r["date"][:4] for r in rows)
    route = collections.Counter((r["date"][:4], r["route"]) for r in rows)
    print(f"{len(rows)} sitting days -> {a.out}")
    for y in years:
        bits = ", ".join(f"{k[1]}:{v}" for k, v in sorted(route.items())
                         if k[0] == str(y))
        print(f"  {y}: {per.get(str(y), 0):>3d} days  {bits}"
              + ("   <-- NOTHING FOUND" if not per.get(str(y)) else ""))

    # Every year in FILL is known to be recoverable -- each one was actually
    # built on 2026-08-13. So an empty year now is a broken route, not a quiet
    # recess, and it must not pass silently: a missing chamber-year and a
    # chamber that did not sit look identical downstream. The manifest is
    # still written, so the counts above are there to debug from.
    empty = [y for y in years if y in FILL and not per.get(str(y))]
    if empty:
        raise SystemExit(
            f"FAILED: no links for {empty}; these years were non-empty when "
            "this manifest was first built, so a route has broken (most "
            "likely the Archive CDX timing out -- rerun before concluding "
            "anything). pe_manifest_fill.json was written anyway.")


if __name__ == "__main__":
    main()
