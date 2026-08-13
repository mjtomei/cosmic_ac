#!/usr/bin/env python3
"""S10 bios: lead-section plain prose for matched candidates, mined for the
"(born ... 1957)" birth year and for degree strings the infobox omits."""
import json, time, urllib.parse, urllib.request, os, sys, re

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_harvest_categories import get  # noqa


def wp(params):
    params.update({"format": "json", "formatversion": "2"})
    return get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))


def fetch_extracts(titles):
    """Plain-text lead extract (intro only)."""
    out = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i:i + 20]
        d = wp({"action": "query", "titles": "|".join(chunk), "prop": "extracts",
                "exintro": "1", "explaintext": "1", "redirects": 1})
        if not d or "query" not in d:
            continue
        for pg in d["query"].get("pages", []):
            if "extract" in pg:
                out[pg["title"]] = pg["extract"][:2500]
        if i % 200 == 0:
            print("  %d/%d" % (i, len(titles)))
        time.sleep(0.4)
    return out


def main():
    bios = json.load(open(os.path.join(HERE, "member_bios.json")))
    titles = sorted({r["source_url"].rsplit("/", 1)[-1].replace("_", " ")
                     for r in bios if r.get("source_url")})
    print("matched candidate pages:", len(titles))
    path = os.path.join(HERE, "page_prose.json")
    have = json.load(open(path)) if os.path.exists(path) else {}
    todo = [t for t in titles if t not in have]
    print("todo:", len(todo))
    B = 400
    for i in range(0, len(todo), B):
        have.update(fetch_extracts(todo[i:i + B]))
        json.dump(have, open(path, "w"))
        print("saved", len(have))
    nb = sum(1 for v in have.values()
             if re.search(r"\(born[^)]{0,60}?\b(18\d\d|19\d\d|200\d)\b", v))
    print("prose with a parenthetical birth year:", nb, "/", len(have))


if __name__ == "__main__":
    main()
