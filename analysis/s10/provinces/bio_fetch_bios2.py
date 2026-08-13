#!/usr/bin/env python3
"""S10 bios: resolve the category pool to QIDs and pull Wikidata bios for every
candidate whose surname appears in the Hansard roster for that province."""
import json, time, os, sys, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_harvest_wikipedia import titles_to_qids  # noqa
from bio_fetch_pool import sparql, BIO_Q  # noqa


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("-", " ").replace("'", " ").replace("’", " ").replace(".", " ")
    return re.sub(r"\s+", " ", s).strip()


def strip_paren(t):
    return re.sub(r"\s*\(.*\)$", "", t)


def main():
    roster = json.load(open(os.path.join(HERE, "member_roster.json")))
    surn = {}
    for m in roster:
        surn.setdefault(m["prov"], set()).add(norm(m["name"]).split()[-1])

    catpool = json.load(open(os.path.join(HERE, "wikipedia_category_pool.json")))
    artpool = json.load(open(os.path.join(HERE, "wikipedia_pool_raw.json")))

    want = {}          # prov -> set(titles)
    for p in catpool:
        s = set(catpool[p]) | set(artpool.get(p, {}).keys())
        want[p] = {t for t in s
                   if norm(strip_paren(t)).split()
                   and norm(strip_paren(t)).split()[-1] in surn.get(p, set())}
        print(p, "candidate titles (surname-hit):", len(want[p]))

    qpath = os.path.join(HERE, "title_qids.json")
    t2q = json.load(open(qpath)) if os.path.exists(qpath) else {}
    # seed from earlier article-pool resolution
    for p in artpool:
        t2q.update(artpool[p])
    todo = sorted({t for p in want for t in want[p]} - set(t2q))
    print("titles needing qid resolution:", len(todo))
    if todo:
        t2q.update(titles_to_qids(todo))
        json.dump(t2q, open(qpath, "w"))

    bpath = os.path.join(HERE, "pool_bios_raw.json")
    bios = json.load(open(bpath))
    need = sorted({t2q[t] for p in want for t in want[p] if t in t2q} - set(bios))
    print("qids needing bios:", len(need))
    CH = 300
    for i in range(0, len(need), CH):
        chunk = need[i:i + CH]
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
        print("chunk %d/%d -> %d total bios" % (i, len(need), len(bios)))
        json.dump(bios, open(bpath, "w"))
        time.sleep(2)
    print("bios with dob:", sum(1 for v in bios.values() if v["dob"]))


if __name__ == "__main__":
    main()
