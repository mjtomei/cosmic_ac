#!/usr/bin/env python3
"""Which Pangram results were produced by which model tier?

WHY THIS EXISTS

The API's default model is Pangram 3; the web dashboard runs Pangram 4, and the
two are materially different instruments (§3.2). The defect was found on
2026-08-09, after several arms had already been scored, and it is SILENT -- a
defaulted call returns verdicts, they are just not the same instrument.

Tier is therefore a property every verdict file needs and not every verdict
file has. Two claims in this repository turned out to rest on inference rather
than record, and one of them was wrong:

  * `pangram_ch_verdicts.csv` was described as Pangram 3 because its 120
    short-band rows contained no Mixed. That does not follow. P3 does return
    Mixed -- `pangram_p4_verdicts.csv`'s `prior_p3` column holds 8 -- and zero
    Mixed among 120 SHORT segments is what P4 predicts anyway, since the
    matched-rate P4 short band flagged only 9 of 1,648.
  * The same file's LONG band does contain Mixed, which was nearly taken as
    proof of P4. It is not proof either, for the same reason in reverse.

So this script does not guess from verdict distributions. It reports what each
file actually RECORDS, and flags the rest as unrecorded so they can be settled
by evidence rather than by argument.

RESCORING IS CHEAP RELATIVE TO BEING WRONG. A 25-segment verification sample
costs roughly 75 credits against 1,071 for a full arm. Verify first; rescore in
full only where verification disagrees.

BUT CHECK THE DASHBOARD HISTORY BEFORE PAYING FOR ANYTHING. It settled
`pangram_ch_verdicts.csv` on 2026-08-13 for nothing. The history at
pangram.com/history lists dashboard-submitted checks and ONLY those; API
submissions never appear in it. That asymmetry makes it a decisive test, and it
was verified in both directions on one chamber before being relied on:

    ansctl   recorded 4.0 (API)       -> absent from the history
    ansprev  recorded 4.0-web         -> present, Aug 9
    caprev   unrecorded               -> PRESENT, Aug 2  => dashboard => P4

All 660 rows of that file -- the UK, Irish and federal Canadian long bands,
controls and short bands -- are in the history, so the whole arm is Pangram 4
and the 542 credits budgeted to rescore it were not needed. The tier is now
stamped into the file with `version_source` recording how it was established.

The general lesson: an unrecorded tier is not necessarily an unknown one. Look
for a record outside the verdict file before buying a new measurement.

Usage: python tier_audit.py
"""
import csv
import glob
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# What each arm feeds, so an unrecorded tier can be ranked by what it would
# cost the paper to have wrong.
LOAD_BEARING = {
    "pangram_p4_verdicts.csv": "§4.1 calibration, §4.2 prevalence, §4.3 genre",
    "pangram_shortband_verdicts.csv": "§4.2 de-banding, §5.0a",
    "pangram_ch_verdicts.csv": "UK/IE long band -- currently EXCLUDED from §4.2",
    "pangram_verdicts.csv": "New Brunswick pilot (§4.1)",
    "pangram_bypass.csv": "§4.9 bypass",
    "pangram_web_verdicts.csv": "route cross-check (§3.2)",
    "nb_p3_vs_p4.csv": "the tier defect evidence itself",
}


def audit_csv(path):
    try:
        rows = list(csv.DictReader(open(path)))
    except Exception as e:
        return None
    if not rows:
        return None
    cols = set(rows[0])
    if not (cols & {"pangram", "prediction", "verdict"}):
        return None
    vcol = ("pangram" if "pangram" in cols else
            "prediction" if "prediction" in cols else "verdict")
    out = {"n": len(rows), "verdict_col": vcol,
           "verdicts": dict(Counter(r[vcol] for r in rows).most_common(5))}
    if "version" in cols:
        out["recorded_version"] = dict(Counter(r["version"] for r in rows))
    if "prior_p3" in cols:
        out["has_prior_p3"] = sum(1 for r in rows if r.get("prior_p3"))
    return out


def main():
    print("PANGRAM TIER AUDIT\n")
    print("Dashboard = Pangram 4. API defaults to Pangram 3 unless "
          "model='pangram-4' is named.\n")
    need = []
    for path in sorted(glob.glob(os.path.join(HERE, "*.csv"))):
        a = audit_csv(path)
        if not a:
            continue
        name = os.path.basename(path)
        ver = a.get("recorded_version")
        print(f"  {name}")
        print(f"    {a['n']:>6,} rows   verdicts {a['verdicts']}")
        if ver:
            print(f"    VERSION RECORDED: {ver}")
        else:
            print(f"    *** NO VERSION COLUMN -- tier unrecorded ***")
            need.append(name)
        if a.get("has_prior_p3"):
            print(f"    carries prior_p3 on {a['has_prior_p3']} rows "
                  f"(already rescored from P3)")
        if name in LOAD_BEARING:
            print(f"    feeds: {LOAD_BEARING[name]}")
        print()

    print("\nUNRECORDED TIER, RANKED BY WHAT IT WOULD COST TO BE WRONG\n")
    for name in need:
        print(f"  {name:<34s} {LOAD_BEARING.get(name, 'not cited in the draft')}")
    print("\nEvery one of these should be settled by rescoring a sample "
          "through the\nweb dashboard and checking agreement -- not by "
          "reasoning about verdict\ndistributions, which is how the last two "
          "tier claims went wrong.")


if __name__ == "__main__":
    main()
