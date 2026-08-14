#!/usr/bin/env python3
"""Combine coded occupations into class-origin measures.

WHAT CODES THE STRINGS, AND WHY IT IS NOT THIS FILE

Occupation strings are coded to EGP by a workflow of two independent Claude
passes over a shared rubric, blind to each other, with a third agent
adjudicating every disagreement. The result is checked into the repository at
`provinces/occupation_coding.json`, with a methods note beside it at
`provinces/OCCUPATION_CODING.md` recording the rubric, the raw agreement rate
between the two passes, and any ambiguities the adjudicators flagged.

THIS FILE USED TO CONTAIN A REGEX MATCHER. It was removed 2026-08-13 after a
test pass against 1,071 real strings, and the reasons are worth keeping,
because they are reasons about instruments rather than about regexes:

  IT ONLY REACHED 73%, and the residue was not exotic. "Senior positions in the
  oil and gas industry", "jobs in forestry, tourism, education, communications
  and journalism", "partner in a Cranbrook law firm" -- all obvious to a
  reader, all resistant to patterns. Closing that gap meant adding rules
  indefinitely, and every added rule is a judgement buried where no reviewer
  will find it.

  IT GOT TWO RULES WRONG IN WAYS THE OUTPUT DID NOT SHOW. A `director` pattern
  swept communications directors and associate producers into the higher
  service class, and Erikson's dominance rule -- which combines two SPOUSES --
  was applied within a single person's career list, so anyone who had ever been
  a director was coded as one. Together they returned 81% "professional", which
  is not a credible distribution. Both were found by reading the output against
  the literature, not by any test the coder could run on itself.

  A WRONG CODE IS INVISIBLE DOWNSTREAM. The matcher's failures were silent: a
  miscoded string enters the regression looking exactly like a correct one.
  Claude coding is not free of error either, but two blind passes produce an
  AGREEMENT RATE, which measures the instrument's reliability -- something the
  regex could not produce about itself at all.

So the division is: judgement is made by coders and recorded with rationales;
this file does the arithmetic that follows from it.

THE TWO SCHEMAS

EGP (Erikson, Goldthorpe & Portocarero 1979), seven-class collapse, built on
EMPLOYMENT RELATIONS rather than prestige:

  I     higher service          IVab  petty bourgeoisie
  II    lower service           IVc   farmers and smallholders (PROPRIETORS)
  III   routine non-manual      V/VI  technicians and skilled manual
                                VIIab semi/unskilled manual AND farm labourers

NS-SEC three-class (ONS), the UK operationalization of the same logic and the
measure the Social Mobility Commission and the Government Analysis Function
harmonised standard use for class ORIGIN specifically: professional /
intermediate / working.

COMBINING TWO PARENTS -- three rules, because the standard is contested

  dominance    the higher of the two parental positions. Erikson's own rule
               (Erikson 1984, Sociology 18(4)), devised for EGP.
  main_earner  the parent who earned more -- what the SMC standard actually
               specifies for NS-SEC origin ("the occupation of your main
               household earner when you were about aged 14"). That is an
               INCOME ordering and is NOT the same rule: a self-employed
               tradesman can out-earn a teacher while sitting lower in the
               class ordering. With no earnings data this falls back to
               dominance and is LABELLED AN APPROXIMATION rather than reported
               as the standard measure.
  average      the mean of the two positions on the ordered scale. Thaning &
               Hallsten (2020, European Sociological Review 36(4) 533) tested
               these and found dominance the WEAKEST -- it explained 13.2% of
               the sibling correlation in occupation against 22.6-23.4% for
               averages and single-parent models -- and recommend averages.

All three are reported. If they agree the choice does not matter; if they
disagree, that is a result about this data and belongs in the write-up.

WHAT IS BEING MEASURED. The coding currently covers members' OWN prior
occupations, which is class DESTINATION. Class ORIGIN needs the parental
strings, collected separately; the combination rules sit idle until those land.

Usage:
  python class_origin.py --dist        # distribution of the coded occupations
  python class_origin.py --origin      # parental class origin, once collected
  python class_origin.py --unresolved  # codings the workflow could not settle
"""
import argparse
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CODING = os.path.join(HERE, "provinces", "occupation_coding.json")
PARENTS = os.path.join(HERE, "provinces", "parent_bios.json")
OUT = os.path.join(HERE, "provinces", "class_origin.json")

EGP = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
EGP_RANK = {c: i for i, c in enumerate(EGP)}

# IVc (farm proprietors) maps to intermediate with the small-employer group,
# which is where ONS puts own-account farmers.
NSSEC3 = {"I": "professional", "II": "professional",
          "III": "intermediate", "IVab": "intermediate", "IVc": "intermediate",
          "V/VI": "working", "VIIab": "working"}
NSSEC_RANK = {"professional": 0, "intermediate": 1, "working": 2}

# Not classes, and kept distinct from each other and from a missing code:
# "unknown" is a gap in the source, "none-political" is a correct statement
# that no pre-political occupation exists. Collapsing them would turn an
# answer into a hole.
NON_CLASS = {"unknown", "none-political"}


def load_coding():
    """occupation string -> coding record, from the checked-in workflow output."""
    if not os.path.exists(CODING):
        raise SystemExit(
            f"no coding at {os.path.relpath(CODING, HERE)}\n"
            "Run the occupation-class-coding workflow first; see "
            "provinces/OCCUPATION_CODING.md.")
    recs = json.load(open(CODING))
    return {r["string"]: r for r in recs if r.get("string")}


def combine(a, b, rule):
    """Two EGP classes -> one, under the named parent-combination rule."""
    xs = [x for x in (a, b) if x and x in EGP_RANK]
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    if rule in ("dominance", "main_earner"):
        return min(xs, key=lambda c: EGP_RANK[c])          # lower rank = higher
    if rule == "average":
        return EGP[round(sum(EGP_RANK[c] for c in xs) / len(xs))]
    raise ValueError(rule)


def dist_report():
    coding = load_coding()
    recs = list(coding.values())
    n = len(recs)
    # Weighted by MEMBERS, not by distinct string: "Lawyer" covers 40 members
    # and a 60-word career description covers one, and an unweighted
    # distribution would treat those as equals.
    byn, byw = Counter(), Counter()
    for r in recs:
        byn[r["egp"]] += 1
        byw[r["egp"]] += r.get("n_members", 1)
    res = Counter(r.get("resolution") for r in recs)
    agreed = res.get("agreed", 0)

    print(f"OCCUPATION CODING -- {n} distinct strings, "
          f"{sum(byw.values())} member records\n")
    print("  INSTRUMENT RELIABILITY")
    print(f"    two blind passes agreed outright   {agreed:>5}  "
          f"{100*agreed/max(n,1):>5.1f}%")
    for k in ("adjudicated", "UNRESOLVED"):
        if res.get(k):
            print(f"    {k:<32}{res[k]:>5}  {100*res[k]/max(n,1):>5.1f}%")
    print("\n  A coder that cannot report an agreement rate cannot be audited.")
    print("  That number is the reason this is not a regex.\n")

    tot = sum(v for k, v in byw.items() if k in EGP_RANK) or 1
    print(f"  {'EGP':<14}{'strings':>8}{'members':>9}{'  % memb':>9}"
          f"  {'NS-SEC':<14}")
    for c in EGP:
        if byn[c] or byw[c]:
            print(f"  {c:<14}{byn[c]:>8}{byw[c]:>9}{100*byw[c]/tot:>8.1f}%"
                  f"  {NSSEC3[c]:<14}")
    for c in sorted(NON_CLASS):
        if byn[c] or byw[c]:
            lab = ("no occupation stated" if c == "unknown"
                   else "political role only")
            print(f"  {c:<14}{byn[c]:>8}{byw[c]:>9}{'':>9}  {lab}")

    ns = Counter()
    for c, v in byw.items():
        if c in NSSEC3:
            ns[NSSEC3[c]] += v
    t = sum(ns.values()) or 1
    print("\n  NS-SEC three-class, member-weighted: " + "  ".join(
        f"{k} {100*v/t:.0f}%" for k, v in
        sorted(ns.items(), key=lambda kv: NSSEC_RANK[kv[0]])))
    print("\n  These are members' OWN occupations -- class DESTINATION.")
    print("  Class ORIGIN needs the parental strings (--origin).")


def origin_report():
    if not os.path.exists(PARENTS):
        raise SystemExit(
            f"no parental data at {os.path.relpath(PARENTS, HERE)} yet.\n"
            "The per-member search collects father_occupation and "
            "mother_occupation; those strings go through the same coding "
            "workflow before this will run.")
    coding = load_coding()
    recs = json.load(open(PARENTS))
    recs = recs if isinstance(recs, list) else recs.get("records", [])
    out, uncoded = [], Counter()

    def code(s):
        r = coding.get((s or "").strip())
        if not r:
            if s:
                uncoded[s] += 1
            return None
        return r["egp"] if r["egp"] in EGP_RANK else None

    for r in recs:
        f = code(r.get("father_occupation"))
        m = code(r.get("mother_occupation"))
        rec = {"name": r.get("name"), "prov": r.get("prov"),
               "egp_father": f, "egp_mother": m}
        for rule in ("dominance", "main_earner", "average"):
            e = combine(f, m, rule)
            rec[f"egp_{rule}"] = e
            rec[f"nssec3_{rule}"] = NSSEC3.get(e) if e else None
        out.append(rec)

    got = sum(1 for r in out if r["egp_dominance"])
    print(f"CLASS ORIGIN -- {len(out)} members with parental data, "
          f"{got} coded ({100*got/max(len(out),1):.0f}%)\n")
    if uncoded:
        print(f"  {sum(uncoded.values())} parental strings "
              f"({len(uncoded)} distinct) are absent from the coding file and")
        print("  were NOT guessed at. Add them to occupation_strings.json and")
        print("  re-run the coding workflow.\n")

    print("DOES THE COMBINATION RULE CHANGE THE ANSWER?\n")
    print("  Thaning & Hallsten 2020 find dominance the weakest of these.")
    print("  main_earner is dominance here -- we have no earnings data.\n")
    for schema, key in (("NS-SEC 3-class", "nssec3"), ("EGP 7-class", "egp")):
        print(f"  {schema}")
        for rule in ("dominance", "main_earner", "average"):
            c = Counter(x[f"{key}_{rule}"] for x in out if x[f"{key}_{rule}"])
            t = sum(c.values()) or 1
            body = "  ".join(f"{k} {100*v/t:.0f}%" for k, v in
                             sorted(c.items(), key=lambda kv: -kv[1]))
            print(f"    {rule:<12s} {body}")
        print()

    by = defaultdict(Counter)
    for x in out:
        if x["nssec3_dominance"]:
            by[x["prov"]][x["nssec3_dominance"]] += 1
    if by:
        print("BY PROVINCE, NS-SEC 3-class, dominance\n")
        print(f"  {'prov':<6}{'n':>5}{'profess':>9}{'interm':>9}{'working':>9}")
        for p in sorted(by):
            c = by[p]
            t = sum(c.values())
            print(f"  {p:<6}{t:>5}" + "".join(
                f"{100*c[k]/t:>8.0f}%" for k in
                ("professional", "intermediate", "working")))

    json.dump(out, open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.relpath(OUT, HERE)}")


def unresolved_report():
    coding = load_coding()
    bad = [r for r in coding.values()
           if r.get("resolution") == "UNRESOLVED" or not r.get("egp")]
    print(f"UNRESOLVED CODINGS: {len(bad)}\n")
    for r in sorted(bad, key=lambda x: -x.get("n_members", 0)):
        print(f"  {r.get('n_members', 0):>3} members  "
              f"A={r.get('coder_a')} B={r.get('coder_b')}  "
              f"{(r.get('string') or '')[:58]}")
    notes, seen = [], set()
    for r in coding.values():
        nt = r.get("rubric_note")
        if nt and nt not in seen:
            seen.add(nt)
            notes.append(nt)
    if notes:
        print(f"\nRUBRIC AMBIGUITIES flagged by adjudicators ({len(notes)}):\n")
        for nt in notes:
            print(f"  - {nt}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", action="store_true")
    ap.add_argument("--origin", action="store_true")
    ap.add_argument("--unresolved", action="store_true")
    a = ap.parse_args()
    if a.origin:
        return origin_report()
    if a.unresolved:
        return unresolved_report()
    return dist_report()


if __name__ == "__main__":
    main()
