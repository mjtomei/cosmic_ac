#!/usr/bin/env python3
"""S10 bios: harvest era-scoped candidate pools (2006-2019) from Wikipedia
legislature articles, resolve to Wikidata QIDs, pull biographical facts."""
import json, time, urllib.parse, urllib.request, os, sys, re

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))

# Legislature/assembly articles covering the 2006-2019 Hansard window
ARTICLES = {
    "ON": ["%dth Parliament of Ontario" % n for n in (38,)] +
          ["39th Parliament of Ontario", "40th Parliament of Ontario",
           "41st Parliament of Ontario", "42nd Parliament of Ontario"],
    "AB": ["26th Alberta Legislature", "27th Alberta Legislature",
           "28th Alberta Legislature", "29th Alberta Legislature",
           "30th Alberta Legislature"],
    "MB": ["38th Manitoba Legislature", "39th Manitoba Legislature",
           "40th Manitoba Legislature", "41st Manitoba Legislature",
           "42nd Manitoba Legislature"],
    "BC": ["38th Parliament of British Columbia", "39th Parliament of British Columbia",
           "40th Parliament of British Columbia", "41st Parliament of British Columbia",
           "42nd Parliament of British Columbia"],
    "NS": ["59th General Assembly of Nova Scotia", "60th General Assembly of Nova Scotia",
           "61st General Assembly of Nova Scotia", "62nd General Assembly of Nova Scotia",
           "63rd General Assembly of Nova Scotia"],
    "NL": ["45th General Assembly of Newfoundland and Labrador",
           "46th General Assembly of Newfoundland and Labrador",
           "47th General Assembly of Newfoundland and Labrador",
           "48th General Assembly of Newfoundland and Labrador",
           "49th General Assembly of Newfoundland and Labrador"],
    "PE": ["62nd General Assembly of Prince Edward Island",
           "63rd General Assembly of Prince Edward Island",
           "64th General Assembly of Prince Edward Island",
           "65th General Assembly of Prince Edward Island",
           "66th General Assembly of Prince Edward Island"],
    "SK": ["25th Saskatchewan Legislature", "26th Saskatchewan Legislature",
           "27th Saskatchewan Legislature", "28th Saskatchewan Legislature",
           "29th Saskatchewan Legislature"],
}


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("retry %d %s: %s\n" % (i, url[:90], e))
            time.sleep(3 * (i + 1))
    return None


def wp(params):
    params.update({"format": "json", "formatversion": "2"})
    return get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))


def page_links(title):
    """All ns-0 links from one article, following continuation."""
    links, cont = [], {}
    while True:
        p = {"action": "query", "titles": title, "prop": "links",
             "pllimit": "max", "plnamespace": 0, "redirects": 1}
        p.update(cont)
        d = wp(p)
        if not d:
            break
        for pg in d.get("query", {}).get("pages", []):
            links += [l["title"] for l in pg.get("links", [])]
        if "continue" in d:
            cont = d["continue"]
            time.sleep(0.5)
        else:
            break
    return links


def titles_to_qids(titles):
    """enwiki title -> QID, 50 at a time."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        d = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({
            "action": "wbgetentities", "sites": "enwiki", "titles": "|".join(chunk),
            "props": "info|sitelinks", "sitefilter": "enwiki", "format": "json"}))
        if not d:
            continue
        for qid, ent in d.get("entities", {}).items():
            if qid.startswith("Q") and "missing" not in ent:
                t = ent.get("sitelinks", {}).get("enwiki", {}).get("title")
                if t:
                    out[t] = qid
        time.sleep(0.5)
    return out


def main():
    pools = {}
    alltitles = {}
    if os.path.exists(os.path.join(HERE, "wikipedia_links_raw.json")):
        alltitles = json.load(open(os.path.join(HERE, "wikipedia_links_raw.json")))
    for prov, arts in ARTICLES.items():
        if prov in alltitles:
            titles = set(alltitles[prov])
            arts = []
        else:
            titles = set()
        for a in arts:
            ls = page_links(a)
            titles.update(ls)
            print("  %s / %s: %d links" % (prov, a, len(ls)))
            time.sleep(0.5)
        titles = sorted(titles)
        alltitles[prov] = titles
        json.dump(alltitles, open(os.path.join(HERE, "wikipedia_links_raw.json"), "w"))
        m = titles_to_qids(titles)
        pools[prov] = m
        print("%s: %d linked titles -> %d qids" % (prov, len(titles), len(m)))
    with open(os.path.join(HERE, "wikipedia_pool_raw.json"), "w") as f:
        json.dump(pools, f, indent=1)


if __name__ == "__main__":
    main()
