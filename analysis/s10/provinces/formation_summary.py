#!/usr/bin/env python3
"""S10 formation-location: coverage report for member_formation.json."""
import json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROVS = ["AB", "BC", "MB", "NL", "NS", "ON", "PE", "SK"]
L = []


def w(s=""):
    L.append(s)


def bar(n, mx, width=40):
    return "#" * int(round(width * n / mx)) if mx else ""


def main():
    rows = json.load(open(os.path.join(HERE, "member_formation.json")))
    bios = {(r["prov"], r["name"]): r
            for r in json.load(open(os.path.join(HERE, "member_bios.json")))}

    # ---- distinct people (rows share a person via wikidata_qid)
    def person_key(r):
        return r.get("wikidata_qid") or ("row", r["prov"], r["name"])

    people = {}
    for r in rows:
        people.setdefault(person_key(r), r)

    w("S10 provincial-legislator FORMATION-LOCATION panel -- coverage report")
    w("=" * 78)
    w("Built 2026-08-08 from member_bios.json (1,396 Hansard roster rows).")
    w("Purpose: where each member was FORMED (born / educated), as distinct from")
    w("the province they later served, so a cohort effect on speech register can")
    w("be tested against ambient technology exposure during formation rather")
    w("than against the province the member now sits in.")
    w("")
    w("Sources, in the order the pipeline prefers them:")
    w("  1. Wikidata P19 (place of birth) via wbgetentities, resolved up the")
    w("     P131 administrative chain to an ISO-3166-2 subdivision (P300) and an")
    w("     ISO-3166-1 alpha-2 country (P17 -> P297).")
    w("  2. Wikidata P69 (educated at), with the P512 degree qualifier where")
    w("     present, each institution geocoded by the same chain walk (P131,")
    w("     falling back to P159 headquarters location for institutions).")
    w("  3. English-Wikipedia infobox `birth_place` / `education` / `alma_mater`,")
    w("     used ONLY where the Wikidata item is silent. Wikilinks inside those")
    w("     fields are resolved to QIDs and then geocoded identically; a value")
    w("     with no geocodable wikilink is kept as text and left ungeocoded.")
    w("  4. Nothing else. Birthplace is NEVER inferred from the riding or the")
    w("     province served -- that inference is what this dataset exists to")
    w("     avoid. Every populated field carries a *_source string.")
    w("")
    w("NOTE: 227 people are printed under several Hansard speaker strings, so")
    w("      1,396 rows cover %d distinct people (%d with a Wikidata QID)."
      % (len(people), len({r["wikidata_qid"] for r in rows if r["wikidata_qid"]})))
    w("      Group by wikidata_qid before treating rows as independent members.")
    w("")
    w("PIPELINE (in run order, all in analysis/s10/provinces/):")
    w("  formation_fetch.py    P19 + P69 per person (SPARQL, VALUES-batched)")
    w("  formation_infobox.py  enwiki lead wikitext -> infobox fields -> QIDs")
    w("  formation_places.py   place/institution QIDs -> admin chain -> ISO codes")
    w("  formation_build.py    -> member_formation.json")
    w("  formation_summary.py  -> this file")
    w("  caches: formation_wikidata.json, formation_entities.json,")
    w("          formation_leads.json, formation_infobox.json,")
    w("          formation_linkqids.json")
    w("")

    # ---------------------------------------------------------- coverage table
    def has_bp(r):
        return r["birth_place"] is not None

    def has_code(r):
        return r["birth_province_code"] is not None

    def has_pop(r):
        return r["birth_place_population"] is not None

    def has_edu(r):
        return bool(r["educated_at"])

    def has_hi(r):
        return r["highest_institution_location"] is not None

    for scope, data in (("ALL ROSTER ROWS", rows),
                        ("DISTINCT PEOPLE", list(people.values()))):
        w("FIELD COVERAGE -- %s" % scope)
        w("-" * 78)
        w("%-6s %6s %10s %10s %10s %10s %10s"
          % ("prov", "n", "birthplc", "provcode", "pop", "educated", "highestIn"))
        for p in PROVS + ["ALL"]:
            sub = data if p == "ALL" else [r for r in data if r["prov"] == p]
            n = len(sub)
            if not n:
                continue
            f = lambda g: "%4d/%3d%%" % (sum(1 for r in sub if g(r)),
                                         round(100 * sum(1 for r in sub if g(r)) / n))
            w("%-6s %6d %10s %10s %10s %10s %10s"
              % (p, n, f(has_bp), f(has_code), f(has_pop), f(has_edu), f(has_hi)))
        w("")

    # -------------------------------------------------------- source breakdown
    w("SOURCE OF EACH POPULATED FIELD (roster rows)")
    w("-" * 78)
    for field in ("birth_place_source", "educated_at_source"):
        w("  %s:" % field)
        for k, v in Counter(r[field] for r in rows).most_common():
            w("    %-62s %5d" % (k if k else "(null)", v))
    w("  highest_institution_basis:")
    for k, v in Counter(
            (r["highest_institution_basis"] or "(null)").split(" (")[0].split(";")[0]
            for r in rows).most_common():
        w("    %-62s %5d" % (k[:62], v))
    w("")

    # -------------------------------------------- birth province vs served
    w("BIRTH PROVINCE vs PROVINCE SERVED -- the key number")
    w("-" * 78)
    for scope, data in (("roster rows", rows), ("distinct people",
                                                list(people.values()))):
        known = [r for r in data if r["birth_province_code"]]
        moved = [r for r in known if r["moved_province"]]
        w("  %-16s birth province known for %4d of %4d (%2.0f%%);"
          % (scope, len(known), len(data), 100 * len(known) / len(data)))
        w("  %-16s of those, %4d serve a province OTHER than their birth "
          "province = %.1f%%" % ("", len(moved), 100 * len(moved) / len(known)))
        out_ca = [r for r in known if r["birth_in_canada"] is False]
        w("  %-16s   of which %d were born outside Canada and %d in another "
          "province/territory"
          % ("", len(out_ca), len(moved) - len(out_ca)))
    w("")

    # the analysis sample: cohort tests need a birth YEAR as well
    for scope, data in (("roster rows", rows), ("distinct people",
                                                list(people.values()))):
        both = [r for r in data if r["birth_province_code"] and r["birth_year"]]
        mv = [r for r in both if r["moved_province"]]
        w("  ANALYSIS SAMPLE (%s with BOTH a birth year and a birth" % scope)
        w("  province): %d; of those %d (%.1f%%) serve a province other than"
      % (len(both), len(mv), 100 * len(mv) / len(both)))
        w("  their birth province.")
    w("")

    def ocode(r):
        c = r["birth_province_code"]
        return c if r["birth_in_canada"] else "*" + (r["birth_country_iso"] or "??")

    w("  per province served (roster rows with a known birth province);")
    w("  a leading * marks a country of birth outside Canada:")
    w("  %-5s %6s %8s %8s   %s" % ("serve", "known", "same", "moved", "top origins"))
    for p in PROVS:
        sub = [r for r in rows if r["prov"] == p and r["birth_province_code"]]
        if not sub:
            continue
        moved = [r for r in sub if r["moved_province"]]
        origins = Counter(ocode(r) for r in moved).most_common(5)
        w("  %-5s %6d %8d %8s   %s"
          % (p, len(sub), len(sub) - len(moved),
             "%d/%2.0f%%" % (len(moved), 100 * len(moved) / len(sub)),
             ", ".join("%s %d" % (k, v) for k, v in origins)))
    w("")

    w("  cross-tabulation, birth province (rows) x province served (cols),")
    w("  roster rows with a known birth province:")
    codes = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL",
             "OTHER_CA", "outside-CA"]
    tab = defaultdict(Counter)
    for r in rows:
        c = r["birth_province_code"]
        if not c:
            continue
        if r["birth_in_canada"] is False or c not in codes:
            c = "outside-CA"
        tab[c][r["prov"]] += 1
    w("  %-11s %s" % ("born\\serves", " ".join("%4s" % p for p in PROVS)))
    for c in codes:
        if not tab[c]:
            continue
        w("  %-11s %s" % (c, " ".join("%4d" % tab[c][p] for p in PROVS)))
    w("")

    # ------------------------------------------------------- born outside CA
    w("  CODE COLLISION WARNING: birth_province_code carries ISO-3166-1 alpha-2")
    w("  country codes for members born abroad, and 'NL' is BOTH Newfoundland")
    w("  and Labrador and the Netherlands. Always read birth_province_code")
    w("  together with birth_in_canada / birth_country_iso. %d rows in this"
      % sum(1 for r in rows if r["birth_province_code"] == "NL"
            and r["birth_in_canada"] is False))
    w("  panel are affected (Netherlands-born members); their")
    w("  birth_province_code_note says so explicitly.")
    w("")
    w("BORN OUTSIDE CANADA")
    w("-" * 78)
    foreign = [r for r in rows if r["birth_place"] and
               r["birth_place"]["country_iso"] and
               r["birth_place"]["country_iso"] != "CA"]
    fp = [r for r in people.values() if r["birth_place"] and
          r["birth_place"]["country_iso"] and
          r["birth_place"]["country_iso"] != "CA"]
    dom = [r for r in rows if r["birth_place"] and
           r["birth_place"]["country_iso"] == "CA"]
    w("  %d roster rows / %d distinct people born outside Canada" %
      (len(foreign), len(fp)))
    w("  (%d rows / %d people born in Canada; %d rows have a birthplace whose "
      "country did not resolve)"
      % (len(dom), len([r for r in people.values() if r["birth_place"] and
                        r["birth_place"]["country_iso"] == "CA"]),
         len([r for r in rows if r["birth_place"] and
              not r["birth_place"]["country_iso"]])))
    w("")
    w("  country breakdown (roster rows / distinct people):")
    cr = Counter((r["birth_place"]["country_iso"], r["birth_place"]["country"])
                 for r in foreign)
    cp = Counter((r["birth_place"]["country_iso"], r["birth_place"]["country"])
                 for r in fp)
    for (iso, lab), n in cr.most_common():
        w("    %-3s %-28s %4d / %3d" % (iso, lab or "", n, cp[(iso, lab)]))
    w("  ('SU' is the exceptionally-reserved ISO code for the Soviet Union:")
    w("   the member's birth settlement sits in a successor state, but the")
    w("   Wikidata chain terminates at the USSR for the relevant period.)")
    w("")

    # --------------------------------------------------------- urban / rural
    w("BIRTH-SETTLEMENT SIZE (Wikidata P1082, any recent census year)")
    w("-" * 78)
    pops = [r["birth_place_population"] for r in people.values()
            if r["birth_place_population"] is not None]
    gran = Counter(r["birth_place_granularity"] for r in people.values()
                   if r["birth_place"])
    w("  birthplace granularity (distinct people): %s"
      % ", ".join("%s %d" % (k, v) for k, v in gran.most_common()))
    w("  birth_place_population is populated ONLY where the birthplace names a")
    w("  settlement. Where the source names a province or a country instead")
    w("  ('England', 'Manitoba'), the field is null and the entity's own P1082")
    w("  is parked in birth_place_entity_population so it cannot be mistaken")
    w("  for a town size.")
    w("  distinct people with a settlement population figure: %d of %d with a "
      "birthplace" % (len(pops), sum(1 for r in people.values()
                                     if r["birth_place"])))
    if pops:
        bands = [(0, 1000, "<1k"), (1000, 5000, "1k-5k"), (5000, 20000, "5k-20k"),
                 (20000, 100000, "20k-100k"), (100000, 500000, "100k-500k"),
                 (500000, 10 ** 9, ">500k")]
        mx = max(sum(1 for v in pops if lo <= v < hi) for lo, hi, _ in bands)
        for lo, hi, lab in bands:
            n = sum(1 for v in pops if lo <= v < hi)
            w("    %-10s %4d  %s" % (lab, n, bar(n, mx)))
        w("  CAVEAT: P1082 is the settlement's CURRENT population, not its")
        w("  population when the member was a child. It codes urban/rural rank,")
        w("  not the size of the place they actually grew up in.")
    w("")

    # ------------------------------------------------------------- education
    w("EDUCATION LOCATION")
    w("-" * 78)
    ins = [i for r in people.values() for i in r["educated_at"]]
    w("  distinct people with >=1 attested institution: %d"
      % sum(1 for r in people.values() if r["educated_at"]))
    w("  institution-person pairs: %d (%d geocoded to a subdivision)"
      % (len(ins), sum(1 for i in ins if i["subdivision_iso"])))
    w("  with a P512 degree qualifier attached: %d"
      % sum(1 for i in ins if i.get("degree")))
    w("")
    hi = [r for r in people.values() if r["highest_institution_location"]]
    w("  highest_institution_location resolved for %d distinct people" % len(hi))
    same = sum(1 for r in hi
               if r["highest_institution_location"]["province_code"] == r["prov"])
    w("    studied in the province they serve:       %4d" % same)
    w("    studied elsewhere:                        %4d" % (len(hi) - same))
    w("  where they studied (province/country code):")
    for k, v in Counter(r["highest_institution_location"]["province_code"]
                        or "(unresolved)" for r in hi).most_common(15):
        w("    %-12s %4d" % (k, v))
    w("")
    both = [r for r in people.values()
            if r["birth_province_code"] and r["highest_institution_location"]
            and r["highest_institution_location"]["province_code"]]
    if both:
        agree = sum(1 for r in both if r["birth_province_code"] ==
                    r["highest_institution_location"]["province_code"])
        w("  of %d people with BOTH a birth province and a study province,"
          % len(both))
        w("  %d (%.0f%%) studied where they were born -- birth and education"
          % (agree, 100 * agree / len(both)))
        w("  location are highly collinear, so they are not independent")
        w("  exposure measures.")
    w("")

    # ------------------------------------------------------- what is missing
    w("WHAT COULD NOT BE RESOLVED, AND WHY")
    w("-" * 78)
    unres = [r for r in rows if r["unresolved_reason"]]
    w("  %d roster rows carry no person at all: Hansard prints only a surname"
      % len(unres))
    w("  that several sitting members share, so the row is a blend of speakers.")
    w("  These are the same 40 rows flagged in member_bios_summary.txt; every")
    w("  field on them is null and they should be dropped from a per-member")
    w("  analysis regardless.")
    w("")
    nobp = [r for r in people.values()
            if not r["birth_place"] and not r["unresolved_reason"]]
    w("  %d distinct people are matched to a Wikipedia/Wikidata person but no"
      % len(nobp))
    w("  birthplace is stated anywhere: not P19, not the infobox. These are")
    w("  overwhelmingly short stub articles. Per province:")
    for p, n in sorted(Counter(r["prov"] for r in nobp).items()):
        tot = len({person_key(r) for r in rows if r["prov"] == p})
        w("    %-4s %3d of %3d" % (p, n, tot))
    w("")
    txtonly = [r for r in rows if r["birth_place"] is None
               and r["birth_place_text"]]
    w("  %d rows have an infobox birth_place string but no geocodable wikilink"
      % len(txtonly))
    w("  in it (plain text such as 'Nova Scotia, Canada'). The raw string is")
    w("  kept in birth_place_text and left ungeocoded rather than pattern-")
    w("  matched into a province.")
    nocode = [r for r in rows if r["birth_place"] and not r["birth_province_code"]]
    if nocode:
        w("  %d rows have a birthplace entity that would not resolve to an"
          % len(nocode))
        w("  ISO-3166-2 subdivision or a country:")
        for k, v in Counter(r["birth_province_code_note"]
                            for r in nocode).most_common(6):
            w("    %-62s %4d" % (str(k)[:62], v))
    else:
        w("  Every birthplace that resolved to a Wikidata entity also resolved")
        w("  to a subdivision or a country, so birth_place and")
        w("  birth_province_code have identical coverage.")
    w("")
    w("  KNOWN LIMITS OF THIS PANEL, stated plainly:")
    w("  - P19 is place of BIRTH, not place of upbringing. A member born in a")
    w("    hospital town, or born abroad to Canadian parents, is coded to the")
    w("    birth settlement. Wikidata has no 'raised in' property, and we did")
    w("    not substitute residence (P551) for it.")
    w("  - Education is attested, not complete. A null educated_at means no")
    w("    institution is recorded, NOT that the member has no post-secondary")
    w("    education; Wikidata P69 covers only ~40% of these people and the")
    w("    infobox fallback is patchier still for the smaller assemblies.")
    w("  - P512 degree qualifiers are almost absent, so")
    w("    highest_institution_location usually rests on 'all attested")
    w("    institutions are in one subdivision' rather than on an actual")
    w("    ranking of degrees. Where attested institutions straddle two")
    w("    subdivisions and no degree is stated, the field is left null with")
    w("    the reason recorded in highest_institution_basis.")
    w("  - Three rows resolve to an institution that carries a country but no")
    w("    P131 administrative parent (University of Alberta Faculty of Law,")
    w("    Mount Douglas Secondary School). Their province_code is null while")
    w("    country_iso is 'CA'; they are counted as '(unresolved)' above.")
    w("  - Coverage is not missing at random. It tracks Wikipedia article")
    w("    length, which tracks party prominence, cabinet service and recency.")
    w("    NL, SK and PE are the thinnest, exactly as they are for birth year.")

    txt = "\n".join(L) + "\n"
    open(os.path.join(HERE, "member_formation_summary.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
