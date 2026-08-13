#!/usr/bin/env python3
"""S10 formation-location, step 1: pull P19 (place of birth) and P69 (educated
at) for every legislator QID in member_bios.json.  Cached to
formation_wikidata.json under 'birth' and 'edu'.

NOTE: the place-resolution pass at the bottom of this file is SUPERSEDED by
formation_places.py.  WDQS repeatedly 504'd on the recursive P131 property
path (and returned 366 MB cross-product responses when the OPTIONALs were
combined), so the administrative chain is now walked client-side over the
wbgetentities API.  This file is kept because its per-person P19/P69 queries
are cheap and reliable; run formation_places.py for step 3."""
import json, os, sys, time, urllib.parse, urllib.request

UA = ("PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) "
      "legislator-formation-collection")
SPARQL = "https://query.wikidata.org/sparql"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "formation_wikidata.json")


def sparql(q, tries=5, timeout=300, backoff=8):
    last = None
    for i in range(tries):
        try:
            data = urllib.parse.urlencode({"query": q, "format": "json"}).encode()
            req = urllib.request.Request(
                SPARQL, data=data,
                headers={"User-Agent": UA,
                         "Accept": "application/sparql-results+json",
                         "Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode("utf-8", "replace")
            # a handful of Wikidata labels carry raw control characters that
            # break strict JSON parsing; scrub them rather than lose the batch
            txt = "".join(ch for ch in txt if ch >= " " or ch in "\t\r\n")
            return json.loads(txt)
        except Exception as e:
            last = e
            sys.stderr.write("  retry %d: %s\n" % (i, e))
            time.sleep(backoff * (i + 1))
    raise RuntimeError("sparql failed: %s" % last)


FAILED = []


def sparql_split(tmpl, chunk, tries=2):
    """Run tmpl over a list of QIDs; on timeout bisect until it succeeds.
    Entities that fail even alone are recorded in FAILED and skipped."""
    vals = " ".join("wd:" + q for q in chunk)
    try:
        return sparql(tmpl % vals, tries=tries, timeout=75,
                      backoff=4)["results"]["bindings"]
    except RuntimeError:
        if len(chunk) == 1:
            FAILED.append(chunk[0])
            sys.stderr.write("  GIVING UP on %s\n" % chunk[0])
            return []
        h = len(chunk) // 2
        return (sparql_split(tmpl, chunk[:h], tries) +
                sparql_split(tmpl, chunk[h:], tries))


def val(b, k):
    return b[k]["value"] if k in b and b[k]["value"] != "" else None


def qid(u):
    return u.rsplit("/", 1)[-1] if u else None


# ---------------------------------------------------------------- person pass
Q_BIRTH = """
SELECT ?p ?pob ?pobLabel WHERE {
  VALUES ?p { %s }
  ?p wdt:P19 ?pob .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""

Q_EDU = """
SELECT ?p ?inst ?instLabel ?deg ?degLabel ?start ?end WHERE {
  VALUES ?p { %s }
  ?p p:P69 ?st . ?st ps:P69 ?inst .
  OPTIONAL { ?st pq:P512 ?deg }
  OPTIONAL { ?st pq:P580 ?start }
  OPTIONAL { ?st pq:P582 ?end }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""

# ----------------------------------------------------------------- place pass
# P300 = ISO 3166-2 code (provinces / states / regions); P297 = ISO 3166-1 a2.
# NOTE: these are deliberately FIVE separate queries with no top-level OPTIONAL.
# A single combined query with three OPTIONALs makes Blazegraph materialise a
# cross product (we got 366 MB responses / 504s before splitting it).
Q_LABEL = """
SELECT ?x ?xLabel ?instLabel WHERE {
  VALUES ?x { %s }
  OPTIONAL { ?x wdt:P31 ?inst }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""
Q_POP = """
SELECT ?x ?pop WHERE { VALUES ?x { %s } ?x wdt:P1082 ?pop }
"""
Q_SUBDIV = """
SELECT ?x ?adm ?admLabel ?iso2 WHERE {
  VALUES ?x { %s }
  ?x (wdt:P131*|wdt:P159/wdt:P131*) ?adm . ?adm wdt:P300 ?iso2 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""
Q_COUNTRY = """
SELECT ?x ?country ?countryLabel ?iso1 WHERE {
  VALUES ?x { %s }
  ?x (wdt:P17|wdt:P159/wdt:P17) ?country .
  OPTIONAL { ?country wdt:P297 ?iso1 }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""
Q_PARENT = """
SELECT ?x ?parent ?parentLabel WHERE {
  VALUES ?x { %s }
  ?x (wdt:P131|wdt:P159) ?parent .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr". }
}
"""


def batched(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def run(query, qids, batch, label):
    rows = []
    todo = list(qids)
    for j, chunk in enumerate(batched(todo, batch)):
        vals = " ".join("wd:" + q for q in chunk)
        d = sparql(query % vals)
        rows.extend(d["results"]["bindings"])
        print("  %s batch %d/%d (%d rows)" %
              (label, j + 1, (len(todo) + batch - 1) // batch, len(rows)))
        time.sleep(0.6)
    return rows


def main():
    bios = json.load(open(os.path.join(HERE, "member_bios.json")))
    people = sorted({r["wikidata_qid"] for r in bios if r.get("wikidata_qid")})
    print("distinct person QIDs: %d" % len(people))

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    if "birth" not in cache:
        rows = run(Q_BIRTH, people, 250, "P19")
        birth = {}
        for b in rows:
            birth.setdefault(qid(val(b, "p")), []).append(
                {"qid": qid(val(b, "pob")), "label": val(b, "pobLabel")})
        cache["birth"] = birth
        json.dump(cache, open(CACHE, "w"))
        print("P19: %d people with a birthplace" % len(birth))

    if "edu" not in cache:
        rows = run(Q_EDU, people, 250, "P69")
        edu = {}
        for b in rows:
            edu.setdefault(qid(val(b, "p")), []).append(
                {"qid": qid(val(b, "inst")), "label": val(b, "instLabel"),
                 "degree": val(b, "degLabel"), "degree_qid": qid(val(b, "deg")),
                 "start": val(b, "start"), "end": val(b, "end")})
        cache["edu"] = edu
        json.dump(cache, open(CACHE, "w"))
        print("P69: %d people with >=1 institution" % len(edu))

    # ---- places: birthplaces + institutions (+ any extra QIDs queued by the
    #      Wikipedia-infobox fallback pass, stored under cache['extra_places'])
    need = set()
    for lst in cache["birth"].values():
        need |= {x["qid"] for x in lst if x["qid"]}
    for lst in cache["edu"].values():
        need |= {x["qid"] for x in lst if x["qid"]}
    need |= set(cache.get("extra_places", []))
    have = set(cache.get("places", {}))
    todo = sorted(need - have)
    print("places needed %d, already resolved %d, todo %d"
          % (len(need), len(have & need), len(todo)))

    if todo:
        places = cache.get("places", {})
        B = 50
        nb = (len(todo) + B - 1) // B
        for j, chunk in enumerate(batched(todo, B)):
            blank = lambda: {"label": None, "types": [], "pop": None, "subdiv": {},
                             "country": {}, "parents": {}}
            for q in chunk:
                places.setdefault(q, blank())

            for b in sparql_split(Q_LABEL, chunk):
                p = places[qid(val(b, "x"))]
                p["label"] = p["label"] or val(b, "xLabel")
                t = val(b, "instLabel")
                if t and t not in p["types"]:
                    p["types"].append(t)
            time.sleep(0.4)

            for b in sparql_split(Q_POP, chunk):
                p = places[qid(val(b, "x"))]
                try:
                    v = int(float(val(b, "pop")))
                except (TypeError, ValueError):
                    continue
                if p["pop"] is None or v > p["pop"]:
                    p["pop"] = v
            time.sleep(0.4)

            for b in sparql_split(Q_SUBDIV, chunk):
                places[qid(val(b, "x"))]["subdiv"][val(b, "iso2")] = val(b, "admLabel")
            time.sleep(0.4)

            for b in sparql_split(Q_COUNTRY, chunk):
                places[qid(val(b, "x"))]["country"][qid(val(b, "country"))] = \
                    [val(b, "countryLabel"), val(b, "iso1")]
            time.sleep(0.4)

            for b in sparql_split(Q_PARENT, chunk):
                places[qid(val(b, "x"))]["parents"][qid(val(b, "parent"))] = \
                    val(b, "parentLabel")
            time.sleep(0.4)

            cache["places"] = places
            json.dump(cache, open(CACHE, "w"))
            print("  place batch %d/%d (%d resolved)" % (j + 1, nb, len(places)))

    json.dump(cache, open(CACHE, "w"))
    print("done. birth=%d edu=%d places=%d"
          % (len(cache["birth"]), len(cache["edu"]), len(cache.get("places", {}))))


if __name__ == "__main__":
    main()
