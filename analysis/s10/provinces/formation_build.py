#!/usr/bin/env python3
"""S10 formation-location: assemble member_formation.json from the Wikidata
P19/P69 pull (formation_wikidata.json) and the enwiki infobox fallback
(formation_infobox.json + formation_linkqids.json).

One output object per member_bios.json row, keyed by {prov, name}.
Nothing is inferred from the riding or the province served: every field either
has a named source or is null."""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from formation_infobox import LINK, clean_text  # noqa

PROV = {"BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"}
TERR = {"YT", "NT", "NU"}


def load(name, default=None):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else default


# --------------------------------------------------------------- place lookup
class Places:
    def __init__(self, places):
        self.p = places or {}

    def get(self, q):
        return self.p.get(q)

    def country(self, q):
        """(label, iso2) of the country, preferring one with an ISO code."""
        rec = self.p.get(q) or {}
        best = (None, None)
        for lab, iso in rec.get("country", {}).values():
            if iso:
                return (lab, iso)
            best = (lab, None)
        return best

    def subdiv(self, q):
        """(iso-3166-2, label) for the place's subdivision. Where the P131
        chain reaches several (University of Alberta reaches both CA-AB and
        CA-NT), take the one nearest the place in the chain; ties break to the
        subdivision of the nearest country."""
        rec = self.p.get(q) or {}
        sd = rec.get("subdiv", {})
        if not sd:
            return (None, None)
        dep = rec.get("subdiv_depth", {})
        _, iso1 = self.country(q)
        keys = sorted(sd, key=lambda k: (dep.get(k, 99),
                                         0 if iso1 and k.startswith(iso1 + "-") else 1,
                                         len(k), k))
        return (keys[0], sd[keys[0]])

    def city(self, q):
        """Best 'the institution is in <city>' label: the nearest admin parent
        that is not itself the subdivision or the country."""
        rec = self.p.get(q) or {}
        _, sub_lab = self.subdiv(q)
        ctry_lab, _ = self.country(q)
        skip = {sub_lab, ctry_lab, rec.get("label")}
        for a, d, lab in rec.get("chain", [])[1:]:
            if lab and lab not in skip:
                return lab
        return None

    def resolved(self, q):
        rec = self.p.get(q)
        return bool(rec and (rec.get("subdiv") or rec.get("country")))

    def granularity(self, q):
        """settlement / subdivision / country -- an infobox birth_place of
        'England' or 'Manitoba' names no settlement at all, and its P1082 is
        a national or provincial population, not a town size."""
        rec = self.p.get(q) or {}
        if q in (rec.get("country") or {}):
            return "country"
        if (rec.get("subdiv_depth") or {}) and \
                min((rec.get("subdiv_depth") or {}).values()) == 0:
            return "subdivision"
        return "settlement"

    def describe(self, q):
        rec = self.p.get(q) or {}
        iso2, sub = self.subdiv(q)
        cl, ci = self.country(q)
        return {"qid": q, "name": rec.get("label"), "types": rec.get("types") or [],
                "subdivision": sub, "subdivision_iso": iso2,
                "country": cl, "country_iso": ci,
                "granularity": self.granularity(q),
                "population": rec.get("pop")}


def province_code(iso2, country_iso):
    """Normalise to the province codes used in province_covariates.csv."""
    if iso2 and iso2.startswith("CA-"):
        c = iso2[3:]
        if c in PROV:
            return c, None
        if c in TERR:
            return "OTHER_CA", "territory: %s" % iso2
        return "OTHER_CA", "unrecognised Canadian subdivision %s" % iso2
    if country_iso == "CA":
        return None, "born in Canada but no ISO-3166-2 subdivision resolved"
    if country_iso:
        return country_iso, None
    return None, "no country resolved"


# ------------------------------------------------------------ degree ranking
DEG_RANK = [
    (4, r"doctor of philosophy|ph\.?d|doctorate|doctor of science|doctor of education|"
        r"doctor of divinity|d\.?phil"),
    (3, r"doctor of medicine|juris doctor|bachelor of laws|master of laws|"
        r"law degree|degree in law|ll\.?b|ll\.?m|"
        r"doctor of veterinary|doctor of dental|doctor of chiropractic|"
        r"doctor of optometry|pharm\.?d|m\.?d\b"),
    (2, r"master|m\.?a\b|m\.?sc|m\.?b\.?a|mba|m\.?ed|m\.?p\.?a"),
    (1, r"bachelor|b\.?a\b|b\.?sc|b\.?comm|b\.?ed|b\.?eng"),
    (0, r"diploma|certificate|associate"),
]


def degree_rank(label):
    if not label:
        return None
    s = label.lower()
    for r, pat in DEG_RANK:
        if re.search(pat, s):
            return r
    return None


POSTSEC = re.compile(r"universit|college|polytechnic|institute of technology|"
                     r"law school|school of law|medical school|business school|"
                     r"graduate school|nursing school|divinity school|"
                     r"academy of|seminary|cegep|cégep|institut", re.I)

# A wikilink inside an infobox birth_place is only accepted as a birthplace if
# it is not one of these. Electoral districts are the dangerous case: a riding
# name geocodes perfectly well and would smuggle exactly the inference this
# dataset exists to avoid back into the data.
NOT_A_BIRTHPLACE = re.compile(
    r"electoral district|electoral division|\briding\b|constituency|"
    r"legislative|parliament|political part|house of assembly|legislature|"
    r"ministry|academic degree|\boccupation\b|\bprofession\b|"
    r"universit|college|\bschool\b", re.I)

# Entities that are plainly not places at all. Wikidata occasionally points
# P19 at a surname item; we drop those rather than geocode them.
NOT_A_PLACE = re.compile(r"family name|given name|surname|\bhuman\b(?! settlement)|"
                         r"disambiguation|Wikimedia", re.I)

# A wikilink inside education/alma_mater is only accepted as an institution if
# it looks like one (the field often also links the city, or a degree).
IS_INSTITUTION = re.compile(
    r"school|universit|college|polytechnic|institut|academy|seminary|"
    r"cegep|cégep|conservator|academie|académie", re.I)


def _blob(desc):
    return " ".join([desc.get("name") or desc.get("label") or ""] +
                    list(desc.get("types") or []))


def is_postsec(desc):
    blob = " ".join([desc.get("name") or ""] + list(desc.get("types") or []))
    if re.search(r"high school|secondary school|collegiate institute|"
                 r"elementary school", blob, re.I):
        return False
    return bool(POSTSEC.search(blob))


# ---------------------------------------------------------------------- main
def main():
    bios = load("member_bios.json")
    cache = load("formation_wikidata.json", {})
    boxes = load("formation_infobox.json", {})
    linkq = load("formation_linkqids.json", {})
    P = Places(cache.get("places", {}))
    birth = cache.get("birth", {})
    edu = cache.get("edu", {})

    # infobox is keyed by the requested title; index by it
    def title_of(url):
        if not url:
            return None
        import urllib.parse
        return urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")

    def links_of(text):
        out = []
        for l in LINK.findall(text or ""):
            q = linkq.get(l.strip())
            if q:
                out.append((l.strip(), q))
        return out

    out = []
    for r in bios:
        qid = r.get("wikidata_qid")
        title = title_of(r.get("source_url"))
        box = (boxes.get(title) or {}).get("infobox", {}) if title else {}

        rec = {
            "prov": r["prov"], "name": r["name"],
            "matched_name": r.get("matched_name"),
            "wikidata_qid": qid,
            "person_row_count": r.get("person_row_count"),
            "birth_year": r.get("birth_year"),
            "birth_place": None,
            "birth_place_text": None,
            "birth_place_source": None,
            "birth_province_code": None,
            "birth_province_code_note": None,
            "birth_country_iso": None,
            "birth_in_canada": None,
            "birth_place_granularity": None,
            "birth_place_population": None,
            "birth_place_population_source": None,
            "birth_place_entity_population": None,
            "educated_at": [],
            "educated_at_source": None,
            "highest_institution_location": None,
            "highest_institution_basis": None,
            "moved_province": None,
            "moved_province_source": None,
            "unresolved_reason": None,
        }
        if not qid and not title:
            rec["unresolved_reason"] = (
                "row unmatched to any person: Hansard prints a blended "
                "surname-only speaker string (see member_bios_summary.txt)")
            out.append(rec)
            continue

        # ---------------------------------------------------------- birthplace
        bp_qid = None
        if qid and qid in birth:
            cands = [b for b in birth[qid] if b.get("qid")
                     and not NOT_A_PLACE.search(_blob(P.describe(b["qid"])))]
            # if several P19 values, prefer the one that resolves to a subdivision
            cands.sort(key=lambda b: (0 if P.subdiv(b["qid"])[0] else 1))
            if cands:
                bp_qid = cands[0]["qid"]
                rec["birth_place_source"] = "wikidata:P19"
                rec["birth_place_text"] = cands[0].get("label")
        if bp_qid is None and box.get("birth_place"):
            raw = box["birth_place"]
            rec["birth_place_text"] = clean_text(raw)
            rejected = []
            for lab, lq in links_of(raw):
                if not (P.subdiv(lq)[0] or P.country(lq)[1]):
                    continue
                blob = _blob(P.describe(lq))
                if NOT_A_BIRTHPLACE.search(blob + " " + lab) or \
                        NOT_A_PLACE.search(blob):
                    rejected.append(lab)
                    continue
                bp_qid = lq
                rec["birth_place_source"] = "enwiki:infobox birth_place"
                break
            if bp_qid is None:
                rec["birth_place_source"] = (
                    "enwiki:infobox birth_place (text only, no geocodable "
                    "wikilink)")
                if rejected:
                    rec["birth_place_source"] += \
                        "; rejected non-place link(s): " + ", ".join(rejected[:3])

        if bp_qid:
            d = P.describe(bp_qid)
            rec["birth_place"] = d
            code, note = province_code(d["subdivision_iso"], d["country_iso"])
            rec["birth_province_code"] = code
            rec["birth_province_code_note"] = note
            rec["birth_country_iso"] = d["country_iso"]
            rec["birth_in_canada"] = (None if not d["country_iso"]
                                      else d["country_iso"] == "CA")
            if code == "NL" and d["country_iso"] != "CA":
                rec["birth_province_code_note"] = (
                    "CODE COLLISION: ISO-3166-1 'NL' is the Netherlands here, "
                    "not Newfoundland and Labrador -- read with "
                    "birth_country_iso")
            rec["birth_place_granularity"] = d["granularity"]
            rec["birth_place_entity_population"] = d["population"]
            if d["population"] is not None and d["granularity"] == "settlement":
                rec["birth_place_population"] = d["population"]
                rec["birth_place_population_source"] = "wikidata:P1082 (%s)" % bp_qid
            elif d["population"] is not None:
                rec["birth_place_population_source"] = (
                    "not set: the birthplace named is a %s, not a settlement; "
                    "its P1082 is in birth_place_entity_population"
                    % d["granularity"])

        # ----------------------------------------------------------- education
        insts, src = [], None
        if qid and qid in edu:
            src = "wikidata:P69"
            for e in edu[qid]:
                if not e.get("qid"):
                    continue
                d = P.describe(e["qid"])
                d["label"] = e.get("label") or d["name"]
                d["degree"] = e.get("degree")
                d["degree_rank"] = degree_rank(e.get("degree"))
                d["city"] = P.city(e["qid"])
                d["postsecondary"] = is_postsec(d)
                d["source"] = "wikidata:P69"
                insts.append(d)
        if not insts:
            got = []
            for f in ("education", "alma_mater"):
                if box.get(f):
                    for lab, lq in links_of(box[f]):
                        if not P.resolved(lq):
                            continue          # degree names etc. have no country
                        if any(g["qid"] == lq for g in got):
                            continue
                        d = P.describe(lq)
                        if not IS_INSTITUTION.search(_blob(d) + " " + lab):
                            continue          # the field often links the city too
                        d["label"] = d["name"] or lab
                        d["degree"] = None
                        d["degree_rank"] = None
                        d["city"] = P.city(lq)
                        d["postsecondary"] = is_postsec(d)
                        d["source"] = "enwiki:infobox %s" % f
                        got.append(d)
            if got:
                insts, src = got, "enwiki:infobox education/alma_mater"
        rec["educated_at"] = insts
        rec["educated_at_source"] = src

        # ------------------------------------------- highest attested location
        loc = lambda d: (d["subdivision_iso"] or (d["country_iso"] and
                                                  "country:" + d["country_iso"]))
        ranked = [d for d in insts if d.get("degree_rank") is not None and loc(d)]
        placed = [d for d in insts if loc(d)]
        ps = [d for d in placed if d["postsecondary"]] or placed
        if ranked:
            top = max(d["degree_rank"] for d in ranked)
            tops = [d for d in ranked if d["degree_rank"] == top]
            # an institution with no degree qualifier could be the more
            # advanced one, so only trust the ranking when every other placed
            # post-secondary institution sits in the same subdivision anyway
            others = [d for d in ps if d.get("degree_rank") is None]
            if len({loc(d) for d in tops}) == 1 and \
                    all(loc(d) == loc(tops[0]) for d in others):
                rec["highest_institution_location"] = _loc_obj(tops[0])
                rec["highest_institution_basis"] = (
                    "wikidata P69 statement carrying the most advanced P512 "
                    "degree qualifier (%s)" % (tops[0]["degree"],))
        if rec["highest_institution_location"] is None and ps:
            if len({loc(d) for d in ps}) == 1:
                rec["highest_institution_location"] = _loc_obj(ps[0])
                rec["highest_institution_basis"] = (
                    "all %d attested post-secondary institution(s) are in one "
                    "subdivision; no degree qualifiers to rank them" % len(ps))
            else:
                rec["highest_institution_basis"] = (
                    "indeterminate: %d attested institutions in %d different "
                    "subdivisions and no P512 degree qualifiers to rank them"
                    % (len(ps), len({loc(d) for d in ps})))
        elif rec["highest_institution_location"] is None and not insts:
            rec["highest_institution_basis"] = "no institution attested"

        # -------------------------------------------------------------- moved
        if rec["birth_province_code"]:
            rec["moved_province"] = rec["birth_province_code"] != r["prov"]
            rec["moved_province_source"] = (
                "birth_province_code (%s) vs province served (%s)"
                % (rec["birth_province_code"], r["prov"]))

        out.append(rec)

    json.dump(out, open(os.path.join(HERE, "member_formation.json"), "w"), indent=1)
    print("wrote member_formation.json (%d rows)" % len(out))
    return out


def _loc_obj(d):
    return {"institution": d.get("label"), "qid": d.get("qid"),
            "city": d.get("city"), "subdivision": d.get("subdivision"),
            "subdivision_iso": d.get("subdivision_iso"),
            "country": d.get("country"), "country_iso": d.get("country_iso"),
            "province_code": province_code(d.get("subdivision_iso"),
                                           d.get("country_iso"))[0],
            "source": d.get("source")}


if __name__ == "__main__":
    main()
