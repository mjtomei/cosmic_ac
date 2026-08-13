#!/usr/bin/env python3
"""S10 bios: P39 position-held statements with start/end qualifiers for every
candidate QID (source for year_first_elected)."""
import json, time, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_fetch_pool import sparql  # noqa

Q = """
SELECT ?p ?posLabel ?start ?end WHERE {
  VALUES ?p { %s }
  ?p p:P39 ?st . ?st ps:P39 ?pos .
  { ?st pq:P580 ?start } UNION { ?st pq:P582 ?end }
  OPTIONAL { ?st pq:P580 ?start }
  OPTIONAL { ?st pq:P582 ?end }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def main():
    bios = json.load(open(os.path.join(HERE, "pool_bios_raw.json")))
    qids = sorted(bios)
    out = {}
    CH = 250
    for i in range(0, len(qids), CH):
        chunk = qids[i:i + CH]
        d = sparql(Q % " ".join("wd:" + q for q in chunk))
        if not d:
            print("FAILED", i)
            continue
        for b in d["results"]["bindings"]:
            q = b["p"]["value"].split("/")[-1]
            out.setdefault(q, []).append({
                "pos": b.get("posLabel", {}).get("value"),
                "start": b.get("start", {}).get("value"),
                "end": b.get("end", {}).get("value")})
        print("chunk %d/%d -> %d with terms" % (i, len(qids), len(out)))
        time.sleep(2)
    json.dump(out, open(os.path.join(HERE, "pool_terms_raw.json"), "w"))


if __name__ == "__main__":
    main()
