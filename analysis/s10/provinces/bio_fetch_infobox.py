#!/usr/bin/env python3
"""S10 bios: fetch lead-section wikitext for every candidate page and parse the
infobox (birth_date, alma_mater, education, occupation/profession, party,
term_start) -- Wikidata is thin on education and occupation for these people."""
import json, time, urllib.parse, urllib.request, os, sys, re

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_harvest_categories import get  # noqa


def wp(params):
    params.update({"format": "json", "formatversion": "2"})
    return get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))


def fetch_lead(titles):
    out = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i:i + 20]
        d = wp({"action": "query", "titles": "|".join(chunk), "prop": "revisions",
                "rvprop": "content", "rvslots": "main", "rvsection": "0", "redirects": 1})
        if not d or "query" not in d:
            continue
        for pg in d["query"].get("pages", []):
            try:
                out[pg["title"]] = pg["revisions"][0]["slots"]["main"]["content"]
            except Exception:
                pass
        if i % 200 == 0:
            print("  lead %d/%d" % (i, len(titles)))
        time.sleep(0.4)
    return out


FIELDS = ("birth_date", "birth_name", "alma_mater", "education", "occupation",
          "profession", "party", "term_start", "assembly", "spouse", "residence")


def parse_infobox(wt):
    """Crude but adequate: pull |field = value lines from the first template."""
    out = {}
    if not wt:
        return out
    # limit to the leading template block
    for f in FIELDS:
        m = re.search(r"\n\s*\|\s*%s\s*=\s*(.*?)(?=\n\s*\|\s*[a-z_0-9]+\s*=|\n\}\})" % f,
                      wt, re.S | re.I)
        if m:
            v = m.group(1).strip()
            if v:
                out[f] = v[:600]
    return out


def main():
    catpool = json.load(open(os.path.join(HERE, "wikipedia_category_pool.json")))
    artpool = json.load(open(os.path.join(HERE, "wikipedia_pool_raw.json")))
    t2q = json.load(open(os.path.join(HERE, "title_qids.json")))
    titles = sorted(set(t2q) & {t for p in catpool for t in catpool[p]} |
                    (set(t2q) & {t for p in artpool for t in artpool[p]}))
    print("candidate titles:", len(titles))
    path = os.path.join(HERE, "page_infoboxes.json")
    have = json.load(open(path)) if os.path.exists(path) else {}
    todo = [t for t in titles if t not in have]
    print("todo:", len(todo))
    B = 400
    for i in range(0, len(todo), B):
        leads = fetch_lead(todo[i:i + B])
        for t, wt in leads.items():
            have[t] = parse_infobox(wt)
        json.dump(have, open(path, "w"))
        print("saved %d" % len(have))
    n = lambda f: sum(1 for v in have.values() if f in v)
    for f in FIELDS:
        print("  %-12s %d/%d" % (f, n(f), len(have)))


if __name__ == "__main__":
    main()
