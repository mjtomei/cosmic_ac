#!/usr/bin/env python3
"""S10 bios: per-article (era-scoped) link harvest + bulk Wikidata bio pull
for every candidate QID."""
import json, time, urllib.parse, urllib.request, os, sys

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_harvest_wikipedia import ARTICLES, page_links, get  # noqa

# (prov, article) -> approximate term window, for era-scoped disambiguation
TERMS = {
    "ON": {"38th Parliament of Ontario": (2003, 2007), "39th Parliament of Ontario": (2007, 2011),
           "40th Parliament of Ontario": (2011, 2014), "41st Parliament of Ontario": (2014, 2018),
           "42nd Parliament of Ontario": (2018, 2022)},
    "AB": {"26th Alberta Legislature": (2004, 2008), "27th Alberta Legislature": (2008, 2012),
           "28th Alberta Legislature": (2012, 2015), "29th Alberta Legislature": (2015, 2019),
           "30th Alberta Legislature": (2019, 2023)},
    "MB": {"38th Manitoba Legislature": (2003, 2007), "39th Manitoba Legislature": (2007, 2011),
           "40th Manitoba Legislature": (2011, 2016), "41st Manitoba Legislature": (2016, 2019),
           "42nd Manitoba Legislature": (2019, 2023)},
    "BC": {"38th Parliament of British Columbia": (2005, 2009),
           "39th Parliament of British Columbia": (2009, 2013),
           "40th Parliament of British Columbia": (2013, 2017),
           "41st Parliament of British Columbia": (2017, 2020),
           "42nd Parliament of British Columbia": (2020, 2024)},
    "NS": {"59th General Assembly of Nova Scotia": (2003, 2006),
           "60th General Assembly of Nova Scotia": (2006, 2009),
           "61st General Assembly of Nova Scotia": (2009, 2013),
           "62nd General Assembly of Nova Scotia": (2013, 2017),
           "63rd General Assembly of Nova Scotia": (2017, 2021)},
    "NL": {"45th General Assembly of Newfoundland and Labrador": (2003, 2007),
           "46th General Assembly of Newfoundland and Labrador": (2007, 2011),
           "47th General Assembly of Newfoundland and Labrador": (2011, 2015),
           "48th General Assembly of Newfoundland and Labrador": (2015, 2019),
           "49th General Assembly of Newfoundland and Labrador": (2019, 2021)},
    "PE": {"62nd General Assembly of Prince Edward Island": (2003, 2007),
           "63rd General Assembly of Prince Edward Island": (2007, 2011),
           "64th General Assembly of Prince Edward Island": (2011, 2015),
           "65th General Assembly of Prince Edward Island": (2015, 2019),
           "66th General Assembly of Prince Edward Island": (2019, 2023)},
    "SK": {"25th Saskatchewan Legislature": (2003, 2007), "26th Saskatchewan Legislature": (2007, 2011),
           "27th Saskatchewan Legislature": (2011, 2016), "28th Saskatchewan Legislature": (2016, 2020),
           "29th Saskatchewan Legislature": (2020, 2024)},
}

BIO_Q = """
SELECT ?p ?pLabel ?dob ?genderLabel ?article
       (GROUP_CONCAT(DISTINCT ?occLabel; separator="|") AS ?occs)
       (GROUP_CONCAT(DISTINCT ?partyLabel; separator="|") AS ?parties)
       (GROUP_CONCAT(DISTINCT ?degLabel; separator="|") AS ?degrees)
       (GROUP_CONCAT(DISTINCT ?almaLabel; separator="|") AS ?almas)
       (GROUP_CONCAT(DISTINCT ?fieldLabel; separator="|") AS ?fields)
       (GROUP_CONCAT(DISTINCT ?posLabel; separator="|") AS ?positions)
WHERE {
  VALUES ?p { %s }
  ?p wdt:P31 wd:Q5 .
  OPTIONAL { ?p wdt:P569 ?dob }
  OPTIONAL { ?p wdt:P21 ?gender }
  OPTIONAL { ?p wdt:P106 ?occ }
  OPTIONAL { ?p wdt:P102 ?party }
  OPTIONAL { ?p wdt:P512 ?deg }
  OPTIONAL { ?p wdt:P69  ?alma }
  OPTIONAL { ?p wdt:P812 ?field }
  OPTIONAL { ?p wdt:P39  ?pos }
  OPTIONAL { ?article schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en".
    ?gender rdfs:label ?genderLabel . ?occ rdfs:label ?occLabel .
    ?party rdfs:label ?partyLabel . ?deg rdfs:label ?degLabel .
    ?alma rdfs:label ?almaLabel . ?field rdfs:label ?fieldLabel .
    ?pos rdfs:label ?posLabel . ?p rdfs:label ?pLabel }
}
GROUP BY ?p ?pLabel ?dob ?genderLabel ?article
"""


def sparql(q, tries=4):
    for i in range(tries):
        try:
            url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
                {"query": q, "format": "json"})
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("sparql retry %d: %s\n" % (i, e))
            time.sleep(6 * (i + 1))
    return None


def main():
    # 1. per-article links
    pa_path = os.path.join(HERE, "wikipedia_links_by_article.json")
    by_art = json.load(open(pa_path)) if os.path.exists(pa_path) else {}
    for prov, arts in ARTICLES.items():
        for a in arts:
            k = prov + "||" + a
            if k in by_art:
                continue
            by_art[k] = page_links(a)
            print("  %s: %d" % (k, len(by_art[k])))
            json.dump(by_art, open(pa_path, "w"))
            time.sleep(0.5)

    pools = json.load(open(os.path.join(HERE, "wikipedia_pool_raw.json")))
    allq = sorted({q for m in pools.values() for q in m.values()})
    print("total distinct qids:", len(allq))

    bios = {}
    CH = 300
    for i in range(0, len(allq), CH):
        chunk = allq[i:i + CH]
        d = sparql(BIO_Q % " ".join("wd:" + q for q in chunk))
        if not d:
            print("FAILED chunk", i)
            continue
        for b in d["results"]["bindings"]:
            g = lambda k: b[k]["value"] if k in b and b[k]["value"] != "" else None
            qid = g("p").split("/")[-1]
            bios[qid] = {
                "qid": qid, "label": g("pLabel"), "dob": g("dob"),
                "gender": g("genderLabel"), "article": g("article"),
                "occupations": (g("occs") or "").split("|") if g("occs") else [],
                "parties": (g("parties") or "").split("|") if g("parties") else [],
                "degrees": (g("degrees") or "").split("|") if g("degrees") else [],
                "almas": (g("almas") or "").split("|") if g("almas") else [],
                "fields": (g("fields") or "").split("|") if g("fields") else [],
                "positions": (g("positions") or "").split("|") if g("positions") else [],
            }
        print("chunk %d/%d -> %d bios" % (i, len(allq), len(bios)))
        time.sleep(2)
    json.dump(bios, open(os.path.join(HERE, "pool_bios_raw.json"), "w"), indent=1)
    print("humans with dob:", sum(1 for v in bios.values() if v["dob"]))


if __name__ == "__main__":
    main()
