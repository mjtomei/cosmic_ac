#!/usr/bin/env python3
"""Build the Tasmanian Hansard manifest from the ISYS search index.

www.parliament.tas.gov.au sits behind a Cloudflare managed challenge, but the
sibling host search.parliament.tas.gov.au (IIS, no Cloudflare) exposes the
Parliament's ISYS / Perceptive Enterprise Search index of the Hansard document
store, and serves the underlying Word files.

Enumeration works like this:
  1. GET /adv/hahansard (and /adv/lchansard) -- an advanced-search form whose
     year checkboxes carry the server-side folder for each calendar year as
     IW_FILTER_PATH, e.g.
       D:\\Data\\Document Publishing\\Hansard\\Archive\\20032017\\House\\2007\\
  2. POST /search/search/ with IW_DATABASE=Hansard, IW_FIELD_IN_AUTHOR=<chamber>,
     IW_FIELD_TEXT=the and that IW_FILTER_PATH -> a result set identified by a
     server-side GUID (the "isysquery" id), 10 hits per page.
  3. GET /search/isysquery/{guid}/1-{N}/list/ -- the whole result set on one page.
     Each row gives the document title ("Thursday 7 June 2007 - Part 1 - Pages
     1 - 24") and the download link
       /search/isysquery/{guid}/{n}/doc/{filename}.docx
     Every document is indexed twice, so dedupe on filename.

The isysquery GUID is session state, so manifest URLs are only good for a while;
aus_tas_download.py re-runs the year query and rewrites them when one goes stale.

Estimates Committee / Government Businesses Scrutiny / Joint Sitting / Address-in-
Reply-of-another-house transcripts live in the same folders and are dropped here:
we want chamber debate only. Sitting days are split into "Part 1/Part 2" files in
most years; both parts of a day are kept and share a date.

Usage: python3 aus_tas_manifest.py
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
BASE = "https://search.parliament.tas.gov.au"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
      "like Gecko) Chrome/128.0.0.0 Safari/537.36")
# The window pair above is the original drift design; the sources
# publish continuously. S10_FILL / S10_SUFFIX backfill the skipped
# years (2011-14, 2020-24) without overwriting the first pass.
YEARS = (list(range(2011, 2015)) + list(range(2020, 2025))
         if os.environ.get("S10_FILL") else
         list(range(2006, 2011)) + list(range(2015, 2020)))
# Legislative Council is the identical pipeline (slug lchansard, author
# "Legislative Council") and works for 2006-2010 + 2015-2017, but the ISYS index
# has NO documents under ...\Archive\20182021\Council\{2018,2019,2020}\ -- those
# three years are simply missing from the Parliament's index, so the LC would
# cover only 3 of the 5 years of the second drift window. LC is therefore left
# out of the corpus; flip BUILD to include it if a partial window is acceptable.
CHAMBERS = {"HA": ("hahansard", "House of Assembly"),
            "LC": ("lchansard", "Legislative Council")}
BUILD = ["HA"]
# the form's 2016 Council checkbox has a typo'd value (Council2016, missing the
# separator); 2016 House is fine. Corrections applied after scraping the form.
PATH_FIX = {("LC", 2016): r"D:\Data\Document Publishing\Hansard\Archive"
                          r"\20032017\Council\2016"}

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}
DATE_RE = re.compile(
    r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September"
    r"|October|November|December)\s+(\d{4})", re.I)
# committee / joint transcripts filed alongside the chamber Hansard
DROP = re.compile(
    r"estimates|scrutiny|joint sitting|select committee|standing committee"
    r"|sub-?committee|public accounts|committee [ab]\b|gbe\b|commission of inquiry"
    r"|index|contents", re.I)

session = requests.Session()
session.headers["User-Agent"] = UA
_last = [0.0]


def get(url, **kw):
    """Never more than one request per second to this host."""
    wait = 1.05 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    r = session.request(kw.pop("method", "GET"), url, timeout=120, **kw)
    _last[0] = time.time()
    r.raise_for_status()
    return r


def year_paths(form_slug):
    """{year: IW_FILTER_PATH} from the advanced-search form's checkboxes."""
    h = get(f"{BASE}/adv/{form_slug}").text
    out = {}
    for m in re.finditer(r'name="IW_FILTER_PATH"\s+value="(D:[^"]*)"[^>]*>\s*'
                         r'(\d{4})', h):
        out.setdefault(int(m.group(2)), m.group(1))
    return out


def run_query(chamber_name, path):
    """POST the year query; return (guid, n_docs)."""
    r = get(f"{BASE}/search/search/", method="POST", data={
        "IW_DATABASE": "Hansard",
        "IW_SORT": "-date",
        "IW_FIELD_IN_AUTHOR": chamber_name,
        "IW_FIELD_TEXT": "the",
        "IW_FILTER_PATH": path,
    })
    h = r.text
    g = re.search(r"isysquery/([0-9a-f-]{36})", h)
    n = re.search(r"Showing 1 to \d+ of <span[^>]*>(\d+)</span>", h)
    if not g:
        return None, 0
    return g.group(1), int(n.group(1)) if n else 0


def list_docs(guid, n):
    """Whole result set on one page -> [(docnum, title, filename)] deduped."""
    h = get(f"{BASE}/search/isysquery/{guid}/1-{max(n,1)}/list/").text
    seen, rows = set(), []
    for block in re.findall(r"<tr>(.*?)</tr>", h, re.S):
        t = re.search(r'/(\d+)/doc/"[^>]*>(.*?)</a>', block, re.S)
        f = re.search(r'/(\d+)/doc/([^"]+\.\w{3,4})"', block)
        if not (t and f):
            continue
        import html as htmllib
        title = htmllib.unescape(re.sub("<[^>]+>", "", t.group(2))).strip()
        title = re.sub(r"\s+", " ", title)
        fn = htmllib.unescape(f.group(2))
        if fn in seen:
            continue
        seen.add(fn)
        rows.append((int(t.group(1)), title, fn))
    return rows


def main():
    manifest = []
    report = []
    dropped_titles = []
    for code in BUILD:
        slug, author = CHAMBERS[code]
        paths = year_paths(slug)
        for y in YEARS:
            path = PATH_FIX.get((code, y), paths.get(y))
            if not path:
                report.append(f"{code} {y}: NO FILTER PATH")
                continue
            guid, n = run_query(author, path)
            if not guid or not n:
                report.append(f"{code} {y}: query returned nothing")
                continue
            rows = list_docs(guid, n)
            kept = dropped = undated = 0
            for num, title, fn in rows:
                if DROP.search(title):
                    dropped += 1
                    dropped_titles.append(f"{code} {y} {title}")
                    continue
                m = DATE_RE.search(title)
                if not m or int(m.group(3)) != y:
                    undated += 1
                    continue
                date = (f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}"
                        f"-{int(m.group(1)):02d}")
                manifest.append({
                    "url": f"{BASE}/search/isysquery/{guid}/{num}/doc/{fn}",
                    "date": date,
                    "chamber": author,
                    "prov_chamber": code,
                    "year": y,
                    "file": fn,
                    "title": title,
                    "guid": guid,
                    "docnum": num,
                    "filter_path": path,
                    "author": author,
                    "local": f"{code}_{y}_{fn}",
                })
                kept += 1
            report.append(f"{code} {y}: {len(rows)} docs -> keep {kept}, "
                          f"committee/other {dropped}, undated {undated}")
    out = HERE / f"aus_tas_manifest{os.environ.get('S10_SUFFIX','')}.json"
    out.write_text(json.dumps(manifest, indent=1))
    (HERE / "aus_tas_dropped_titles.txt").write_text("\n".join(dropped_titles))
    print("\n".join(report))
    print(f"\n{len(manifest)} files, "
          f"{len({(r['prov_chamber'], r['date']) for r in manifest})} chamber-days "
          f"-> {out}")


if __name__ == "__main__":
    main()
