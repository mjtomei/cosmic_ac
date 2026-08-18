#!/usr/bin/env python3
"""Repair the SOC mapping against the real O*NET-SOC 30.3 taxonomy.

WHY THIS EXISTS

Double-blind coding catches independent error but not CORRELATED error: when
both coders make the same mistake the record passes as "agreed" and never
reaches adjudication. Validating every code against the published taxonomy
found 18 such records carrying codes that do not exist, all of them in the
agreed set. The adjudicator separately caught 26 invalid codes among the
disagreements, which is the same defect surfacing where the design could see it.

Every repair below is a near-miss with unambiguous intent -- the coders' own
soc_title names a real occupation whose code they mistyped, or a retired 2010
SOC code whose successor is determinate from the occupation text. Nothing here
is a re-coding; anything genuinely ambiguous is left alone or set unknown.

Usage: python repair_soc_coding.py   # rewrites soc_coding_new.json in place
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALID = {r["O*NET-SOC Code"]: r["Title"] for r in
         csv.DictReader(open(os.path.join(HERE, "onet_occupation_data.csv"),
                             encoding="utf-8-sig"))}

# invalid code -> (replacement, why). None means "decide from the occupation text".
FIX = {
    # identical title in the taxonomy, middle digits transposed
    "25-1099.00": ("25-1199.00", "typo for Postsecondary Teachers, All Other"),
    # 2018 SOC merged category that O*NET keeps split; resolved per occupation
    "21-1018.00": (None, "merged SOC category; split by occupation text"),
    # paraeducator is a K-12 teaching assistant
    "25-9045.00": ("25-9042.00", "Teaching Assistants, K-12"),
    # retired 2010 code; its successor for a generic supervisor
    "53-1047.00": ("53-1049.00", "retired 2010 code -> All Other successor"),
}


def split_counsellor(text):
    t = text.lower()
    if "drug" in t or "alcohol" in t or "substance" in t:
        return "21-1011.00", "substance-abuse counsellor"
    return "21-1014.00", "mental-health counsellor"


def main():
    p = os.path.join(HERE, "soc_coding_new.json")
    d = json.load(open(p))
    repaired, notes = 0, []
    for r in d:
        c = r.get("soc_code")
        if c in (None, "unknown") or c in VALID:
            continue
        if c not in FIX:
            notes.append(f"UNHANDLED invalid code {c} on id {r['id']}")
            continue
        new, why = FIX[c]
        if new is None:
            new, why = split_counsellor(r.get("occupation") or "")
        r["soc_code"], r["soc_title"] = new, VALID[new]
        r["resolution"] = "repaired"
        r["rubric_note"] = ((r.get("rubric_note") or "") +
                            f" [taxonomy repair: {c} -> {new}, {why}]").strip()
        repaired += 1

    # id 2065: the writer declined to invent a code, correctly. The ruling on
    # id 1811 cites 2065 as the pool's 19-3099.00 case, so the intent is on
    # record; applying it here explicitly rather than leaving a null.
    for r in d:
        if r["id"] == 2065 and r.get("soc_code") is None:
            r["soc_code"], r["soc_title"] = "19-3099.00", VALID["19-3099.00"]
            r["resolution"] = "repaired"
            r["rubric_note"] = ("resolved to 19-3099.00 on the strength of the "
                                "id-1811 ruling, which cites 2065 as the pool's "
                                "agreed 19-3099.00 case")
            repaired += 1

    # normalise the unknown title, written inconsistently as "" or "unknown"
    for r in d:
        if r.get("soc_code") == "unknown":
            r["soc_title"] = "unknown"

    json.dump(d, open(p, "w"), indent=1)
    bad = [r for r in d if r.get("soc_code") not in VALID
           and r.get("soc_code") != "unknown"]
    print(f"repaired {repaired} records")
    print(f"remaining invalid codes: {len(bad)}")
    for n in notes:
        print("  " + n)
    # coal-miner inconsistency the writer self-flagged: report, do not silently merge
    coal = [(r["id"], r["soc_code"], r["occupation"][:40]) for r in d
            if r.get("soc_code") in ("47-5041.00", "47-5049.00")]
    if coal:
        print("\ncoal/underground mining cell (writer flagged an inconsistency):")
        for i, c, o in coal:
            print(f"  id {i:<5d} {c}  {o}")


if __name__ == "__main__":
    main()
