#!/usr/bin/env python3
"""Score occupations on the blind-derived corporate-level signatures.

WHY THIS FILE EXISTS

The corporate-levels arm (workflows/element_levels.js, results in
element_levels.json) asked 18 blind coders which O*NET elements mark FREE /
BOTTOM / MIDDLE / TOP of a corporate hierarchy -- multi-label, no prior
results shown. Its pre-committed readout: the "levels are inexpressible"
hypothesis is refuted only if the signatures, joined to per-occupation values
(predictor-side, no register), place known archetypes correctly.

This script is that join. Each level score is the mean of its consensus
elements' standardised values under the consensus sign. Scales per family are
resolved as in instrument_v2_coverage.py, plus two special cases: Work Context
items rated on CT rather than CX (Duration of Typical Work Week), and 3.A.1
Related Work Experience, which is a category distribution (RW scale) collapsed
to its expected category.

--drop-3a1 reruns without 3.A.1: it is a 2/3 element, its file rates 878 of
the occupations (farmers among the missing), and it alone decides whether
farmers -- the FREE archetype -- can be scored at all.

Usage: python level_scores.py [--drop-3a1]
"""
import argparse
import collections
import csv
import json
import os
import statistics as st

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V = "/tmp/onet303/db_30_3_text"


def famscale(e):
    if e.startswith("4.A"): return ("Work Activities.txt", {"IM"})
    if e.startswith("4.C"): return ("Work Context.txt", {"CX", "CT"})
    if e.startswith("1.B.1"): return ("Career Interest Types.txt", {"OI"})
    if e.startswith("1.B.3"): return ("Specific Interest Areas.txt", {"OI"})
    if e.startswith("1.D"): return ("Work Styles.txt", {"WI"})
    if e.startswith("2.A"): return ("Essential Skills.txt", {"IM"})
    if e.startswith("2.B"): return ("Transferable Skills.txt", {"IM"})
    if e.startswith("2.C"): return ("Knowledge.txt", {"IM"})
    return (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-3a1", action="store_true")
    a = ap.parse_args()

    cp = json.load(open(os.path.join(HERE, "element_levels.json")))["consensus_pairs"]
    if a.drop_3a1:
        cp = [p for p in cp if p["id"] != "3.A.1"]
    need = {p["id"] for p in cp}

    val = collections.defaultdict(dict)
    files = collections.defaultdict(set)
    for e in need:
        fn, sc = famscale(e)
        if fn:
            files[(fn, frozenset(sc))].add(e)
    for (fn, scs), els in files.items():
        with open(os.path.join(V, fn), encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["Element ID"] in els and r["Scale ID"] in scs:
                    val[r["Element ID"]][r["O*NET-SOC Code"]] = float(r["Data Value"])
    if "3.A.1" in need:
        acc = collections.defaultdict(float)
        with open(os.path.join(V, "Training and Experience.txt"),
                  encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["Element ID"] == "3.A.1" and r["Scale ID"] == "RW":
                    acc[r["O*NET-SOC Code"]] += (float(r["Category"])
                                                 * float(r["Data Value"]) / 100)
        val["3.A.1"] = dict(acc)

    occ = set.intersection(*(set(val[e]) for e in need))
    print(f"{len(need)} signature elements; {len(occ)} occupations complete"
          f"{'  (3.A.1 dropped)' if a.drop_3a1 else ''}")

    def z(e):
        xs = {o: val[e][o] for o in occ}
        m, s = st.mean(xs.values()), st.pstdev(xs.values()) or 1
        return {o: (v - m) / s for o, v in xs.items()}

    Z = {e: z(e) for e in need}
    sig = collections.defaultdict(list)
    for p in cp:
        sig[p["level"]].append((p["id"], +1 if p["sign"] == "+" else -1))
    S = {lvl: {o: st.mean(sg * Z[e][o] for e, sg in items) for o in occ}
         for lvl, items in sig.items()}

    ks = ["FREE", "BOTTOM", "MIDDLE", "TOP"]
    A = np.array([[S[k][o] for o in sorted(occ)] for k in ks])
    C = np.corrcoef(A)
    print("\nscore correlations:")
    print("        " + "".join(f"{k:>8s}" for k in ks))
    for i, k in enumerate(ks):
        print(f"{k:<8s}" + "".join(f"{C[i, j]:>8.2f}" for j in range(4)))
    am = collections.Counter(max(ks, key=lambda k: S[k][o]) for o in occ)
    print("\nargmax over all occupations:", dict(am))

    show = {"11-1011.00": "Chief Executives", "11-1021.00": "General/Ops Mgrs",
            "11-3031.00": "Financial Mgrs", "11-3121.00": "HR Managers",
            "43-1011.00": "1stLine Sup Office", "25-2031.00": "Secondary Teachers",
            "29-1141.00": "Registered Nurses", "23-1011.00": "Lawyers",
            "23-2011.00": "Paralegals", "43-9021.00": "Data Entry",
            "43-6014.00": "Secretaries", "41-2031.00": "Retail Sales",
            "33-3051.00": "Police Officers", "11-9013.00": "Farmers",
            "47-2061.00": "Construction Laborers", "13-2011.00": "Accountants",
            "45-2092.00": "Farmworkers"}
    tgt = {"Chief Executives": "TOP", "HR Managers": "MIDDLE",
           "Financial Mgrs": "MIDDLE", "Data Entry": "BOTTOM",
           "Paralegals": "BOTTOM", "Secretaries": "BOTTOM", "Farmers": "FREE"}
    print(f"\n{'occupation':<22s}{'FREE':>7s}{'BOTTOM':>8s}{'MIDDLE':>8s}{'TOP':>7s}   argmax")
    hits = tot = 0
    for c, n in show.items():
        if c not in occ:
            print(f"{n:<22s}{'-- not scoreable: missing a signature element --':>34s}")
            continue
        s = {k: S[k][c] for k in ks}
        am1 = max(s, key=s.get)
        t = tgt.get(n, "")
        if t:
            tot += 1
            hits += am1 == t
        mark = ("   <-- " + ("HIT" if am1 == t else f"MISS (wanted {t})")) if t else ""
        print(f"{n:<22s}{s['FREE']:>+7.2f}{s['BOTTOM']:>+8.2f}"
              f"{s['MIDDLE']:>+8.2f}{s['TOP']:>+7.2f}   {am1:<7s}{mark}")
    print(f"\npre-committed archetype targets: {hits}/{tot} hit")

    print("\nface validity — top 8 by FREE score:")
    for o in sorted(occ, key=lambda o: -S["FREE"][o])[:8]:
        ttl = next((n for c, n in show.items() if c == o), o)
        print(f"   {S['FREE'][o]:+.2f}  {ttl}")


if __name__ == "__main__":
    main()
