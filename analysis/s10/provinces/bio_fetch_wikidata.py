#!/usr/bin/env python3
"""S10 bios: bulk-pull provincial legislator biographical data from Wikidata."""
import json, time, urllib.parse, urllib.request, sys, os

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
SPARQL = "https://query.wikidata.org/sparql"
HERE = os.path.dirname(os.path.abspath(__file__))

POS = {
    "ON": "Q3305347",
    "AB": "Q15964815",
    "MB": "Q19007867",
    "NS": "Q18239264",
    "BC": "Q19004821",
    "PE": "Q21010685",
    "SK": "Q18675661",
    "NL": "Q19403853",
}

QUERY = """
SELECT ?p ?pLabel ?dob ?dod ?genderLabel ?article
       (GROUP_CONCAT(DISTINCT ?occLabel; separator="|") AS ?occs)
       (GROUP_CONCAT(DISTINCT ?partyLabel; separator="|") AS ?parties)
       (GROUP_CONCAT(DISTINCT ?degLabel; separator="|") AS ?degrees)
       (GROUP_CONCAT(DISTINCT ?almaLabel; separator="|") AS ?almas)
       (GROUP_CONCAT(DISTINCT ?fieldLabel; separator="|") AS ?fields)
       (MIN(?start) AS ?first_start) (MAX(?end) AS ?last_end)
WHERE {
  ?p p:P39 ?st .
  ?st ps:P39 wd:%s .
  OPTIONAL { ?st pq:P580 ?start }
  OPTIONAL { ?st pq:P582 ?end }
  OPTIONAL { ?p wdt:P569 ?dob }
  OPTIONAL { ?p wdt:P570 ?dod }
  OPTIONAL { ?p wdt:P21 ?gender }
  OPTIONAL { ?p wdt:P106 ?occ }
  OPTIONAL { ?p wdt:P102 ?party }
  OPTIONAL { ?p wdt:P512 ?deg }
  OPTIONAL { ?p wdt:P69  ?alma }
  OPTIONAL { ?p wdt:P812 ?field }
  OPTIONAL { ?article schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en".
    ?gender rdfs:label ?genderLabel . ?occ rdfs:label ?occLabel .
    ?party rdfs:label ?partyLabel . ?deg rdfs:label ?degLabel .
    ?alma rdfs:label ?almaLabel . ?field rdfs:label ?fieldLabel . ?p rdfs:label ?pLabel }
}
GROUP BY ?p ?pLabel ?dob ?dod ?genderLabel ?article
"""


def sparql(q, tries=4):
    for i in range(tries):
        try:
            url = SPARQL + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("retry %d: %s\n" % (i, e))
            time.sleep(5 * (i + 1))
    raise RuntimeError("sparql failed")


def main():
    out = {}
    for prov, qid in POS.items():
        d = sparql(QUERY % qid)
        rows = []
        for b in d["results"]["bindings"]:
            g = lambda k: b[k]["value"] if k in b and b[k]["value"] != "" else None
            rows.append({
                "qid": g("p").split("/")[-1],
                "label": g("pLabel"),
                "dob": g("dob"), "dod": g("dod"),
                "gender": g("genderLabel"),
                "article": g("article"),
                "occupations": (g("occs") or "").split("|") if g("occs") else [],
                "parties": (g("parties") or "").split("|") if g("parties") else [],
                "degrees": (g("degrees") or "").split("|") if g("degrees") else [],
                "almas": (g("almas") or "").split("|") if g("almas") else [],
                "fields": (g("fields") or "").split("|") if g("fields") else [],
                "term_start": g("first_start"), "term_end": g("last_end"),
            })
        out[prov] = rows
        n_dob = sum(1 for r in rows if r["dob"])
        print("%s: %d members, %d with DOB" % (prov, len(rows), n_dob))
        time.sleep(2)
    with open(os.path.join(HERE, "wikidata_raw.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
