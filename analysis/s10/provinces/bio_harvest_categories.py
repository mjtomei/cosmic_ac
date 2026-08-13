#!/usr/bin/env python3
"""S10 bios: harvest the era-scoped enwiki membership categories per province,
then pull each member's category set (birth year / party / gender fallbacks)."""
import json, time, urllib.parse, urllib.request, os, sys, re

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))

BODY = {
    "ON": "members of the Legislative Assembly of Ontario",
    "AB": "members of the Legislative Assembly of Alberta",
    "MB": "members of the Legislative Assembly of Manitoba",
    "BC": "members of the Legislative Assembly of British Columbia",
    "SK": "members of the Legislative Assembly of Saskatchewan",
    "PE": "members of the Legislative Assembly of Prince Edward Island",
    "NS": "members of the Nova Scotia House of Assembly",
    "NL": "members of the Newfoundland and Labrador House of Assembly",
}


def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("retry %d: %s\n" % (i, e))
            time.sleep(3 * (i + 1))
    return None


def wp(params):
    params.update({"format": "json", "formatversion": "2"})
    return get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))


def catmembers(cat):
    out, cont = [], {}
    while True:
        p = {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat,
             "cmlimit": "500", "cmtype": "page"}
        p.update(cont)
        d = wp(p)
        if not d or "query" not in d:
            break
        out += [c["title"] for c in d["query"]["categorymembers"]]
        if "continue" in d:
            cont = d["continue"]
            time.sleep(0.4)
        else:
            break
    return out


def page_categories(titles):
    """title -> [categories], batched with continuation."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        cont = {}
        while True:
            p = {"action": "query", "titles": "|".join(chunk), "prop": "categories",
                 "cllimit": "max", "clshow": "!hidden", "redirects": 1}
            p.update(cont)
            d = wp(p)
            if not d or "query" not in d:
                break
            for pg in d["query"].get("pages", []):
                out.setdefault(pg["title"], [])
                out[pg["title"]] += [c["title"][9:] for c in pg.get("categories", [])]
            if "continue" in d:
                cont = d["continue"]
                time.sleep(0.3)
            else:
                break
        time.sleep(0.3)
        if i % 500 == 0:
            print("    cats %d/%d" % (i, len(titles)))
    return out


def main():
    catpath = os.path.join(HERE, "wikipedia_category_pool.json")
    pool = json.load(open(catpath)) if os.path.exists(catpath) else {}
    for prov, body in BODY.items():
        if prov in pool:
            continue
        titles = set()
        for c in ("21st-century " + body, "20th-century " + body):
            ms = catmembers(c)
            print("  %s / %s: %d" % (prov, c, len(ms)))
            titles.update(ms)
            time.sleep(0.4)
        pool[prov] = sorted(titles)
        json.dump(pool, open(catpath, "w"))
        print("%s pool: %d" % (prov, len(pool[prov])))

    # union with the legislature-article pool
    art_pool = json.load(open(os.path.join(HERE, "wikipedia_pool_raw.json")))
    alltitles = set()
    for p in pool:
        alltitles.update(pool[p])
        alltitles.update(art_pool.get(p, {}).keys())
    alltitles = sorted(alltitles)
    print("distinct titles to categorize:", len(alltitles))

    cpath = os.path.join(HERE, "page_categories.json")
    have = json.load(open(cpath)) if os.path.exists(cpath) else {}
    todo = [t for t in alltitles if t not in have]
    print("todo:", len(todo))
    if todo:
        have.update(page_categories(todo))
        json.dump(have, open(cpath, "w"))
    nb = sum(1 for v in have.values() if any(re.match(r"^\d{4} births$", c) for c in v))
    print("pages with a 'NNNN births' category:", nb, "/", len(have))


if __name__ == "__main__":
    main()
