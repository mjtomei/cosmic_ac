#!/usr/bin/env python3
"""S10 formation-location: resolve every birthplace / institution QID to a
settlement -> subdivision -> country chain using the Wikidata wbgetentities
API (50 ids per request).  WDQS kept 504-ing on the recursive P131 property
path, so we walk the administrative chain ourselves.

Reads seed QIDs from formation_wikidata.json (birth, edu, extra_places),
writes the entity store to formation_entities.json and the flattened place
records back into formation_wikidata.json['places']."""
import json, os, sys, time, urllib.parse, urllib.request

UA = ("PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) "
      "legislator-formation-collection")
HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://www.wikidata.org/w/api.php"
CACHE = os.path.join(HERE, "formation_wikidata.json")
STORE = os.path.join(HERE, "formation_entities.json")

# properties we keep
P_INSTANCE, P_COUNTRY, P_ADMIN, P_POP = "P31", "P17", "P131", "P1082"
P_ISO1, P_ISO2, P_HQ = "P297", "P300", "P159"
KEEP = (P_INSTANCE, P_COUNTRY, P_ADMIN, P_POP, P_ISO1, P_ISO2, P_HQ)
MAX_DEPTH = 8


def api(ids, tries=5):
    params = {"action": "wbgetentities", "ids": "|".join(ids),
              "props": "labels|claims", "languages": "en|fr",
              "format": "json", "formatversion": "2"}
    for i in range(tries):
        try:
            data = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(API, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("  api retry %d: %s\n" % (i, e))
            time.sleep(4 * (i + 1))
    return None


def slim(ent):
    """Keep only the label and the handful of claims we use."""
    labels = ent.get("labels", {})
    lab = (labels.get("en") or labels.get("fr") or {}).get("value")
    out = {"label": lab, "claims": {}}
    for p in KEEP:
        vals = []
        for st in ent.get("claims", {}).get(p, []):
            if st.get("rank") == "deprecated":
                continue
            dv = st.get("mainsnak", {}).get("datavalue")
            if not dv:
                continue
            v = dv.get("value")
            if isinstance(v, dict) and "id" in v:
                vals.append(v["id"])
            elif isinstance(v, dict) and "amount" in v:
                vals.append(v["amount"])
            elif isinstance(v, str):
                vals.append(v)
        if vals:
            out["claims"][p] = vals
    return out


def fetch(qids, store):
    todo = sorted(q for q in qids if q and q not in store and q.startswith("Q"))
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        d = api(chunk)
        if d and "entities" in d:
            for q, ent in d["entities"].items():
                if ent.get("missing") is not None:
                    store[q] = {"label": None, "claims": {}, "missing": True}
                else:
                    store[q] = slim(ent)
        for q in chunk:
            store.setdefault(q, {"label": None, "claims": {}, "missing": True})
        if (i // 50) % 5 == 0:
            print("  entities %d/%d" % (min(i + 50, len(todo)), len(todo)))
            json.dump(store, open(STORE, "w"))
        time.sleep(0.5)
    json.dump(store, open(STORE, "w"))
    return len(todo)


def main():
    cache = json.load(open(CACHE))
    seeds = set(cache.get("extra_places", []))
    for lst in cache.get("birth", {}).values():
        seeds |= {x["qid"] for x in lst if x.get("qid")}
    for lst in cache.get("edu", {}).values():
        seeds |= {x["qid"] for x in lst if x.get("qid")}
    print("seed place/institution QIDs: %d" % len(seeds))

    store = json.load(open(STORE)) if os.path.exists(STORE) else {}
    frontier = set(seeds)
    for depth in range(MAX_DEPTH):
        n = fetch(frontier, store)
        print("depth %d: fetched %d new entities (store=%d)" % (depth, n, len(store)))
        nxt = set()
        for q in frontier:
            c = store.get(q, {}).get("claims", {})
            for p in (P_ADMIN, P_COUNTRY, P_HQ):
                for v in c.get(p, []):
                    if isinstance(v, str) and v.startswith("Q") and v not in store:
                        nxt.add(v)
        # also need P31 labels for the 'types' field
        for q in frontier:
            for v in store.get(q, {}).get("claims", {}).get(P_INSTANCE, []):
                if isinstance(v, str) and v.startswith("Q") and v not in store:
                    nxt.add(v)
        if not nxt:
            print("closure reached at depth %d" % depth)
            break
        frontier = nxt

    # ---------------------------------------------------- flatten to 'places'
    def claims(q, p):
        return store.get(q, {}).get("claims", {}).get(p, [])

    def label(q):
        return store.get(q, {}).get("label")

    def walk(q):
        """Administrative ancestors breadth-first, as (qid, depth) pairs.
        Depth matters: an entity can sit under two subdivisions (University of
        Alberta reaches both CA-AB and CA-NT) and the nearest one is the right
        answer."""
        order, seen, frontier, depth = [], {q}, [q], 0
        order.append((q, 0))
        while frontier and depth < 12:
            depth += 1
            nxt = []
            for a in frontier:
                parents = claims(a, P_ADMIN)
                # institutions often carry only a headquarters location
                if not parents and depth == 1:
                    parents = claims(a, P_HQ)
                for p in parents:
                    if p not in seen:
                        seen.add(p)
                        nxt.append(p)
                        order.append((p, depth))
            frontier = nxt
        return order

    places = {}
    for q in sorted(seeds):
        chain = walk(q)
        subdiv, sub_depth, country = {}, {}, {}
        for a, d in chain:
            for iso2 in claims(a, P_ISO2):
                if iso2 not in subdiv or d < sub_depth[iso2]:
                    subdiv[iso2] = label(a)
                    sub_depth[iso2] = d
        for a, d in chain:
            for c in claims(a, P_COUNTRY):
                if c not in country:
                    iso1 = (claims(c, P_ISO1) or [None])[0]
                    country[c] = [label(c), iso1]
            if country:
                break                       # nearest country wins
        if not any(v[1] for v in country.values()):
            # Either no P17 at all (Jamaica, Denmark are their own country) or
            # the nearest P17 target carries no P297 (Dutch municipalities point
            # at Q55 Netherlands, but the ISO code lives on Q29999 Kingdom of
            # the Netherlands). Scan the chain for the first entity that has
            # an ISO-3166-1 code of its own.
            for a, d in chain:
                iso1 = (claims(a, P_ISO1) or [None])[0]
                if iso1:
                    country[a] = [label(a), iso1]
                    break
            else:
                for a, d in chain:
                    for c in claims(a, P_COUNTRY):
                        iso1 = (claims(c, P_ISO1) or [None])[0]
                        if iso1:
                            country[c] = [label(c), iso1]
                            break
                    if any(v[1] for v in country.values()):
                        break
        pop = None
        for v in claims(q, P_POP):
            try:
                v = int(float(v))
            except (TypeError, ValueError):
                continue
            if pop is None or v > pop:
                pop = v
        parents = {}
        for p in claims(q, P_ADMIN) + claims(q, P_HQ):
            parents[p] = label(p)
        places[q] = {
            "label": label(q),
            "types": [label(t) for t in claims(q, P_INSTANCE) if label(t)],
            "pop": pop, "subdiv": subdiv, "subdiv_depth": sub_depth,
            "country": country, "parents": parents,
            "chain": [[a, d, label(a)] for a, d in chain],
        }
    cache["places"] = places
    json.dump(cache, open(CACHE, "w"))
    n_sub = sum(1 for v in places.values() if v["subdiv"])
    n_ctry = sum(1 for v in places.values() if v["country"])
    print("places: %d, with subdivision %d, with country %d"
          % (len(places), n_sub, n_ctry))


if __name__ == "__main__":
    main()
