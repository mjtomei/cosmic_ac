#!/usr/bin/env python3
"""S10 formation-location fallback: for members whose Wikidata item carries no
P19, scrape the English-Wikipedia infobox `birth_place` (and `education` /
`alma_mater`) from the lead wikitext, then resolve any [[wikilinks]] inside the
birth_place value to QIDs so the normal place pipeline can geocode them.

Writes formation_infobox.json and appends the new place QIDs to
formation_wikidata.json under 'extra_places' (re-run formation_fetch.py after)."""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = ("PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) "
      "legislator-formation-collection")
HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://en.wikipedia.org/w/api.php"
CACHE = os.path.join(HERE, "formation_wikidata.json")
OUT = os.path.join(HERE, "formation_infobox.json")
LEADS = os.path.join(HERE, "formation_leads.json")


def wp(params, tries=4):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            sys.stderr.write("  wp retry %d: %s\n" % (i, e))
            time.sleep(3 * (i + 1))
    return None


FIELDS = ("birth_place", "birth_date", "education", "alma_mater", "residence")


def parse_infobox(wt):
    out = {}
    if not wt:
        return out
    for f in FIELDS:
        m = re.search(r"\n\s*\|\s*%s[ \t]*=[ \t]*(.*?)"
                      r"(?=\n\s*\|\s*[a-zA-Z_0-9 ]+[ \t]*=|\n\s*\}\})" % f,
                      wt, re.S)
        if m:
            v = m.group(1).strip()
            if v:
                out[f] = v[:600]
    return out


LINK = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]")


def clean_text(v):
    """Human-readable rendering of an infobox value."""
    v = re.sub(r"<ref[^>]*>.*?</ref>", "", v, flags=re.S)
    v = re.sub(r"<ref[^>]*/>", "", v)
    v = re.sub(r"<br\s*/?>", ", ", v)
    v = re.sub(r"\{\{[Nn]owrap\|([^}]*)\}\}", r"\1", v)
    v = re.sub(r"\{\{[^}]*\}\}", "", v)
    v = re.sub(r"\[\[([^\]|]+)\|([^\]]*)\]\]", r"\2", v)
    v = re.sub(r"\[\[([^\]]+)\]\]", r"\1", v)
    v = re.sub(r"''+", "", v)
    v = re.sub(r"<[^>]+>", "", v)
    v = re.sub(r"\s+", " ", v).strip().strip(",").strip()
    return v or None


def main():
    bios = json.load(open(os.path.join(HERE, "member_bios.json")))
    cache = json.load(open(CACHE))
    have_p19 = set(cache["birth"])

    # Fetch the lead infobox for EVERY matched row that has an enwiki article:
    # birth_place backs up a missing P19, and alma_mater/education backs up a
    # missing P69 (Wikidata P69 is populated for only ~43% of these people).
    need = {}
    for r in bios:
        url = r.get("source_url")
        if not url:
            continue
        title = urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")
        need[title] = r.get("wikidata_qid")
    titles = sorted(need)
    print("enwiki titles to scrape: %d (%d of their people lack P19)"
          % (len(titles), sum(1 for t, q in need.items()
                              if not q or q not in have_p19)))

    leads = json.load(open(LEADS)) if os.path.exists(LEADS) else {}
    boxes = {}
    todo = [t for t in titles if t not in leads]
    print("todo: %d" % len(todo))
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        d = wp({"action": "query", "titles": "|".join(chunk), "prop": "revisions",
                "rvprop": "content", "rvslots": "main", "rvsection": "0",
                "redirects": 1})
        if not d or "query" not in d:
            continue
        norm = {}
        for k in ("redirects", "normalized"):
            for m in d["query"].get(k, []):
                norm[m["to"]] = m["from"]
        for pg in d["query"].get("pages", []):
            try:
                wt = pg["revisions"][0]["slots"]["main"]["content"]
            except Exception:
                continue
            key = pg["title"]
            while key in norm:
                key = norm[key]
            leads[key] = {"title": pg["title"], "wikitext": wt}
        json.dump(leads, open(LEADS, "w"))
        print("  %d/%d" % (min(i + 20, len(todo)), len(todo)))
        time.sleep(0.5)

    boxes = {k: {"title": v["title"], "infobox": parse_infobox(v["wikitext"])}
             for k, v in leads.items()}
    json.dump(boxes, open(OUT, "w"), indent=1)
    for f in ("birth_place", "education", "alma_mater"):
        print("infoboxes with %-11s %d/%d"
              % (f, sum(1 for v in boxes.values() if v["infobox"].get(f)), len(boxes)))

    # ---- resolve wikilinks inside birth_place / education to QIDs
    link_titles = set()
    for v in boxes.values():
        for f in ("birth_place", "education", "alma_mater"):
            val = v["infobox"].get(f)
            if val:
                for l in LINK.findall(val):
                    link_titles.add(l.strip())
    link_titles = sorted(t for t in link_titles if t and not t.startswith("File:"))
    print("distinct wikilink titles in birth_place/education: %d" % len(link_titles))

    t2q = json.load(open(os.path.join(HERE, "formation_linkqids.json"))) \
        if os.path.exists(os.path.join(HERE, "formation_linkqids.json")) else {}
    todo2 = [t for t in link_titles if t not in t2q]
    for i in range(0, len(todo2), 40):
        chunk = todo2[i:i + 40]
        d = wp({"action": "query", "titles": "|".join(chunk),
                "prop": "pageprops", "ppprop": "wikibase_item", "redirects": 1})
        if not d or "query" not in d:
            continue
        norm = {}
        for k in ("redirects", "normalized"):
            for m in d["query"].get(k, []):
                norm[m["to"]] = m["from"]
        for pg in d["query"].get("pages", []):
            q = pg.get("pageprops", {}).get("wikibase_item")
            key = pg["title"]
            seen = set()
            while key in norm and key not in seen:
                seen.add(key)
                key = norm[key]
            t2q[key] = q
            t2q[pg["title"]] = q
        for t in chunk:
            t2q.setdefault(t, None)
        time.sleep(0.5)
    json.dump(t2q, open(os.path.join(HERE, "formation_linkqids.json"), "w"), indent=1)
    print("resolved %d link titles to QIDs (%d non-null)"
          % (len(t2q), sum(1 for v in t2q.values() if v)))

    extra = set(cache.get("extra_places", []))
    extra |= {v for v in t2q.values() if v}
    cache["extra_places"] = sorted(extra)
    json.dump(cache, open(CACHE, "w"))
    print("extra_places queued: %d  (now re-run formation_fetch.py)" % len(extra))


if __name__ == "__main__":
    main()
