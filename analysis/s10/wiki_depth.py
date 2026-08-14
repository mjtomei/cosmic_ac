#!/usr/bin/env python3
"""Measure each member's Wikipedia article length, as the notability instrument.

WHY ARTICLE LENGTH AND NOT ARTICLE EXISTENCE

WP:NPOL makes every elected member presumptively notable, so 1,354 of the 1,396
Canadian provincial legislators in this study have an article and existence
discriminates nothing. Depth does: a cabinet minister gets tens of thousands of
characters, a one-term backbencher gets a stub of a few hundred that omits both
education and occupation -- which is exactly the pattern the collection agents
reported, and exactly the bias that makes a Wikipedia-sourced covariate
suspect.

So article length is the instrument for that bias. With it we can ask whether
register tracks how much has been written about a member, and whether
controlling for it changes the education effect. Without it, "notability bias"
stays an argument rather than a variable.

WHY THIS IS DERIVED AND NOT COLLECTED

The per-member search pass was asked to record article length, and did so
unreliably -- 867 of 1,396 values arrived without an evidence entry naming the
field and were dropped by the merge. Length is a mechanical property of a page,
not a judgement, so asking an agent to eyeball it was the wrong design. Here it
comes from the MediaWiki API, which reports page size directly and exactly.

The route is wikidata_qid -> sitelink -> page size, because the QID is already
in member_bios.json for 1,354 members and is a far more reliable key than a
name. Both APIs take 50 ids per request, so the whole corpus costs about sixty
calls.

WHAT THE NUMBER IS. `length` from the MediaWiki API: the size of the page's
wikitext in bytes, including markup, references and infobox. That is not the
same as prose length -- a reference-heavy stub can outweigh a plain longer
article -- but it is monotone with depth over three orders of magnitude, which
is the range that matters here, and it is exact and reproducible where a
character count eyeballed from a rendered page is neither.

Usage:
  python wiki_depth.py            # fetch and write provinces/wiki_depth.json
  python wiki_depth.py --report   # summarise what is already fetched
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.error
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BIOS = os.path.join(HERE, "provinces", "member_bios.json")
OUT = os.path.join(HERE, "provinces", "wiki_depth.json")
UA = "s10-legislative-register-study/1.0 (research; contact via repo)"


def get(url, tries=6):
    """GET with exponential backoff on 429.

    A first run at one request per second was rate-limited from batch 10
    onward. Backing off is the correct response -- the server is stating a
    rate and we honour it. The wrong responses, which this deliberately does
    not do, are rotating identity or parallelising to route around the limit.
    """
    delay = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            wait = float(e.headers.get("Retry-After") or delay)
            print(f"    429; waiting {wait:.0f}s", flush=True)
            time.sleep(wait)
            delay = min(delay * 2, 60)
    raise RuntimeError("unreachable")


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    if a.report:
        if not os.path.exists(OUT):
            raise SystemExit("nothing fetched yet")
        d = json.load(open(OUT))
        vals = sorted(v["length"] for v in d.values() if v.get("length"))
        n = len(vals)
        print(f"WIKIPEDIA ARTICLE DEPTH -- {n} of {len(d)} members resolved\n")
        if n:
            q = lambda p: vals[int(p * (n - 1))]
            print(f"  min {vals[0]:,}   Q1 {q(.25):,}   median {q(.5):,}   "
                  f"Q3 {q(.75):,}   max {vals[-1]:,}")
            print(f"\n  The spread is the point: the top quartile has roughly "
                  f"{q(.75)/max(q(.25),1):.0f}x the")
            print("  wikitext of the bottom, and it is the short ones whose "
                  "education\n  and occupation fields are missing.")
        return

    bios = json.load(open(BIOS))
    qids = {}
    for b in bios:
        q = (b.get("wikidata_qid") or "").strip()
        if q:
            qids.setdefault(q, []).append((b.get("prov"), b.get("name")))
    print(f"{len(qids)} distinct QIDs from {len(bios)} member rows")

    # QID -> English Wikipedia title
    titles = {}
    for i, batch in enumerate(chunks(sorted(qids), 50)):
        url = ("https://www.wikidata.org/w/api.php?action=wbgetentities"
               "&props=sitelinks&sitefilter=enwiki&format=json&ids="
               + "|".join(batch))
        try:
            d = get(url)
        except Exception as e:
            print(f"  batch {i}: {e}")
            continue
        for qid, ent in (d.get("entities") or {}).items():
            sl = (ent.get("sitelinks") or {}).get("enwiki")
            if sl and sl.get("title"):
                titles[qid] = sl["title"]
        print(f"  wikidata batch {i+1}: {len(titles)} titles so far", flush=True)
        time.sleep(2.5)

    # title -> page length in bytes
    lengths = {}
    tlist = sorted(set(titles.values()))
    for i, batch in enumerate(chunks(tlist, 50)):
        url = ("https://en.wikipedia.org/w/api.php?action=query&prop=info"
               "&format=json&titles="
               + urllib.parse.quote("|".join(batch), safe="|"))
        try:
            d = get(url)
        except Exception as e:
            print(f"  batch {i}: {e}")
            continue
        for pg in (d.get("query", {}).get("pages") or {}).values():
            if pg.get("title") and "length" in pg:
                lengths[pg["title"]] = pg["length"]
        print(f"  wikipedia batch {i+1}: {len(lengths)} lengths so far",
              flush=True)
        time.sleep(2.5)

    out = {}
    for qid, members in qids.items():
        t = titles.get(qid)
        for prov, name in members:
            out[f"{prov}|{name}"] = {"qid": qid, "title": t,
                                     "length": lengths.get(t) if t else None}
    json.dump(out, open(OUT, "w"), indent=1)
    got = sum(1 for v in out.values() if v.get("length"))
    print(f"\nwrote {os.path.relpath(OUT, HERE)}: {got} of {len(out)} "
          f"member rows carry a length")


if __name__ == "__main__":
    main()
