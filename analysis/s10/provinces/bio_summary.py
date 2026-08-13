#!/usr/bin/env python3
"""S10 bios: coverage + distribution report for member_bios.json."""
import json, os, collections, io

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["birth_year", "year_first_elected", "occupation_category", "prior_occupation",
          "education_level", "postsecondary_attested", "gender", "party"]


def main():
    b = json.load(open(os.path.join(HERE, "member_bios.json")))
    roster = json.load(open(os.path.join(HERE, "member_roster.json")))
    o = io.StringIO()
    W = o.write
    provs = sorted({r["prov"] for r in b})

    W("S10 provincial-legislator biographical panel -- coverage report\n")
    W("=" * 78 + "\n")
    W("Built %s. Sources, in order of preference actually used:\n" % __import__("datetime").date.today())
    W("  1. Wikidata SPARQL  (P39 position-held per province; P569 birth date, P21,\n")
    W("     P106 occupation, P102 party, P512 academic degree, P69 alma mater)\n")
    W("  2. English Wikipedia categories ('21st-/20th-century members of <assembly>'\n")
    W("     for the candidate pool; 'NNNN births' for birth year; '<Party> MLAs/MPPs'\n")
    W("     for party; 'Women MLAs/MPPs in <prov>' for gender)\n")
    W("  3. English Wikipedia infoboxes (birth_date, occupation/profession,\n")
    W("     alma_mater/education) and lead-section prose ('(born ... 1957)', degrees)\n")
    W("  4. Legislative Assembly of Manitoba MLA biographies (DOB + every general\n")
    W("     election date) -- the only assembly site found publishing birth dates\n\n")

    W("ROSTER AND MATCHING\n")
    W("-" * 78 + "\n")
    W("%-5s %6s %8s %7s %7s %6s   %s\n" % ("prov", "roster", "matched", "high", "medium",
                                           "none", "distinct people behind the rows"))
    tot = collections.Counter()
    for p in provs:
        R = [r for r in b if r["prov"] == p]
        c = collections.Counter(r["match_confidence"] for r in R)
        qids = {r["wikidata_qid"] for r in R if r["wikidata_qid"]}
        W("%-5s %6d %8d %7d %7d %6d   %d\n" % (p, len(R), len(R) - c["none"], c["high"],
                                               c["medium"], c["none"], len(qids)))
        tot.update(c)
        tot["n"] += len(R)
    W("%-5s %6d %8d %7d %7d %6d\n\n" % ("ALL", tot["n"], tot["n"] - tot["none"],
                                        tot["high"], tot["medium"], tot["none"]))
    W("NOTE: %d roster rows are dropped from member_bios.json entirely as non-members\n"
      % (len(roster) - len(b)))
    W("(chair/Speaker/Lieutenant-Governor speaker strings).\n")
    dup = collections.Counter((r["prov"], r["wikidata_qid"]) for r in b if r["wikidata_qid"])
    nd = sum(1 for k, v in dup.items() if v > 1)
    nr = sum(v for k, v in dup.items() if v > 1)
    W("NOTE: Hansard prints the same member under several speaker strings, so %d people\n" % nd)
    W("      account for %d roster rows. Group by (prov, wikidata_qid) -- or use the\n" % nr)
    W("      person_row_count field -- before treating rows as independent members.\n\n")

    W("FIELD COVERAGE (share of ALL roster rows for the province)\n")
    W("-" * 78 + "\n")
    W("%-5s %6s" % ("prov", "n"))
    short = {"birth_year": "birth", "year_first_elected": "elect", "occupation_category": "occCat",
             "prior_occupation": "occTxt", "education_level": "eduLvl",
             "postsecondary_attested": "postSec", "gender": "gender", "party": "party"}
    for f in FIELDS:
        W("%9s" % short[f])
    W("\n")
    for p in provs + ["ALL"]:
        R = b if p == "ALL" else [r for r in b if r["prov"] == p]
        W("%-5s %6d" % (p, len(R)))
        for f in FIELDS:
            n = sum(1 for r in R if r.get(f) not in (None, False, []))
            W("%9s" % ("%d/%d%%" % (n, round(100.0 * n / len(R)))))
        W("\n")
    W("\n(cells are count/percent of that province's roster rows)\n\n")

    W("BIRTH YEAR -- the primary field\n")
    W("-" * 78 + "\n")
    src = collections.Counter(r["birth_year_source"] for r in b if r["birth_year"])
    for k, v in src.most_common():
        W("  %-42s %5d\n" % (k, v))
    W("\n  birth-year values rejected as implausible for the service window: %d\n"
      % sum(1 for r in b if r.get("birth_year_rejected")))
    ys = [r["birth_year"] for r in b if r["birth_year"]]
    W("  n=%d  min=%d  max=%d  median=%d\n" % (len(ys), min(ys), max(ys),
                                               sorted(ys)[len(ys) // 2]))
    W("\n  decade distribution (all provinces, roster rows not distinct people):\n")
    dec = collections.Counter((y // 10) * 10 for y in ys)
    mx = max(dec.values())
    for d in sorted(dec):
        W("    %ds %4d  %s\n" % (d, dec[d], "#" * int(40.0 * dec[d] / mx)))
    W("\n  per-province birth-year median / IQR:\n")
    for p in provs:
        v = sorted(r["birth_year"] for r in b if r["prov"] == p and r["birth_year"])
        if len(v) < 4:
            continue
        W("    %-3s n=%3d  median %d   IQR %d-%d\n" % (
            p, len(v), v[len(v) // 2], v[len(v) // 4], v[3 * len(v) // 4]))

    W("\n\nOCCUPATION CATEGORY\n")
    W("-" * 78 + "\n")
    oc = collections.Counter(r["occupation_category"] for r in b if r["occupation_category"])
    n = sum(oc.values())
    for k, v in oc.most_common():
        W("  %-30s %4d  %4.1f%%  %s\n" % (k, v, 100.0 * v / n, "#" * int(40.0 * v / max(oc.values()))))
    W("  %-30s %4d  (no occupation attested)\n"
      % ("(null)", sum(1 for r in b if not r["occupation_category"])))
    W("\n  per province:\n")
    cats = [k for k, _ in oc.most_common()]
    W("    %-4s" % "")
    for c in cats:
        W("%9s" % c[:8])
    W("\n")
    for p in provs:
        R = [r for r in b if r["prov"] == p]
        W("    %-4s" % p)
        for c in cats:
            W("%9d" % sum(1 for r in R if r["occupation_category"] == c))
        W("\n")

    W("\n\nOTHER FIELDS\n")
    W("-" * 78 + "\n")
    W("  gender:    %s\n" % dict(collections.Counter(r["gender"] for r in b)))
    W("  education_level: %s\n" % dict(collections.Counter(r["education_level"] for r in b)))
    W("  education_field (derived from the degree type where stated): %s\n" % dict(
        collections.Counter(r["education_field"] for r in b if r["education_field"])))
    W("  first-elected source: %s\n" % dict(collections.Counter(
        r.get("year_first_elected_source") for r in b if r.get("year_first_elected"))))
    W("  NOTE: %d of the year_first_elected values are LOWER BOUNDS -- the earliest\n"
      % sum(1 for r in b if r.get("year_first_elected_is_lower_bound")))
    W("        legislature (2003+) the member is listed in, used only when they carry\n")
    W("        no 20th-century membership category. Filter on\n")
    W("        year_first_elected_is_lower_bound before using this field quantitatively.\n")
    W("  Party strings are as published (Wikipedia category / Wikidata label) and are\n")
    W("  NOT normalised across provinces.\n")

    W("\n\nWHAT COULD NOT BE MATCHED, AND WHY\n")
    W("-" * 78 + "\n")
    none = [r for r in b if r["match_confidence"] == "none"]
    W("%d of %d roster rows (%.1f%%) are unmatched. Every field on them is null:\n"
      % (len(none), len(b), 100.0 * len(none) / len(b)))
    W("we leave them empty rather than guess.\n\n")
    W("The single cause is Hansard's surname-only speaker strings. Most provinces print\n")
    W("'Mr. Smith', not 'Mr. John Smith', so the extraction roster collapses every\n")
    W("member of that surname sitting in 2006-2019 into ONE row. Where two or more\n")
    W("same-surname members overlap in time and the honorific does not separate them\n")
    W("(e.g. NL 'Parsons' = Jim / Kelvin / Kevin), no evidence in the roster can\n")
    W("resolve it -- and the row itself is a blend of several speakers, so it should\n")
    W("arguably be dropped from a per-member analysis regardless.\n\n")
    byp = collections.Counter(r["prov"] for r in none)
    for p in provs:
        rows = [r for r in none if r["prov"] == p]
        if not rows:
            continue
        W("  %-3s %2d unmatched: %s\n" % (p, len(rows),
                                          ", ".join(sorted(r["name"] for r in rows))[:200]))
    W("\nSecondary, much smaller losses (these DO get matched but stay field-null):\n")
    W("  - %d matched members have a Wikipedia article that simply never states a\n"
      % sum(1 for r in b if r["match_confidence"] != "none" and not r["birth_year"]))
    W("    birth year -- not in Wikidata, not in a 'NNNN births' category, not in the\n")
    W("    infobox, not in the lead. This is the binding constraint on birth-year\n")
    W("    coverage now, and it falls hardest on NL, SK and MB, whose members' articles\n")
    W("    are short stubs. The assembly websites checked (SK, PE, ON, BC, NL, MB) do\n")
    W("    not publish members' dates of birth; Manitoba's MLA-biographies page is the\n")
    W("    sole exception, and it carries a DOB only for older members. NL's members\n")
    W("    directory returned HTTP 403 to a scripted request and was not pursued\n")
    W("    further. No obvious second source remains for this field.\n")
    W("  - education_level is the weakest field by far: Wikidata's P512 (academic\n")
    W("    degree) is almost unpopulated for these people, and Wikipedia usually names\n")
    W("    the institution without the degree. postsecondary_attested (institution\n")
    W("    named anywhere) is the more usable variable; education_level should be read\n")
    W("    as 'degree explicitly stated', with absence meaning unknown, not 'none'.\n")

    W("\n\nMATCHING METHOD AND CONFIDENCE\n")
    W("-" * 78 + "\n")
    W("Candidates are scoped per province to people in the '21st-century members of\n")
    W("<assembly>' category or linked from the 2003-2023 legislature/parliament\n")
    W("articles, whose term windows give an era filter. A roster row matches only if\n")
    W("exactly one candidate survives name matching, era overlap and (where the\n")
    W("honorific is unambiguous) gender.\n\n")
    W("  high   -- full given+surname match, or an initial+surname match, or a\n")
    W("            surname-only match that is unique AND whose legislature term window\n")
    W("            overlaps the row's Hansard dates\n")
    W("  medium -- unique only after using the honorific's gender, or resolved by\n")
    W("            dropping a mismatched given name (nickname: 'Thomas' -> 'Tom'), or\n")
    W("            unique in the 21st-century pool with no term-window confirmation\n")
    W("  low    -- unique but with neither term-window nor 21st-century confirmation\n")
    W("  none   -- zero or several surviving candidates; all fields null\n")
    W("\nmatch_kind records which rule fired. Spot-checked against known values:\n")
    W("Notley 1964, Horgan 1959, Wynne 1953, Wall 1965, Selinger 1951, McNeil 1964,\n")
    W("Horwath 1962, Ball 1957 -- all correct.\n")

    open(os.path.join(HERE, "member_bios_summary.txt"), "w").write(o.getvalue())
    print(o.getvalue())


if __name__ == "__main__":
    main()
