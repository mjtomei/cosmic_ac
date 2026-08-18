#!/usr/bin/env python3
"""Compare the blind corporate-level signatures with the U/L/D/N instrument.

WHY THIS FILE EXISTS

Two independent derivations now exist over the same 295-element universe:
the four-component instrument (instrument_final_cells.json; directional cells,
audit-fixed) and the corporate-level signatures (element_levels.json; FREE /
BOTTOM / MIDDLE / TOP, blind, multi-label). Matthew: how do the new results
compare to the old? This script answers on three axes, predictor-side only:

  1. element overlap -- which signature elements the instrument already holds,
     in which cell, and which are new
  2. score correlations -- the four level scores against the four components
     and the three registered profiles, across all completely-rated occupations
  3. the farmer, under both readings

Usage: python level_vs_instrument.py
"""
import collections
import csv
import json
import os
import statistics as st

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V = "/tmp/onet303/db_30_3_text"
REV = {"4.C.3.a.4", "4.C.3.b.8", "4.A.2.b.4", "4.C.3.a.2.b"}
PROF = {"free": (-1, -1, -1, -1), "front-line": (+1, +1, -1, +1),
        "corporate": (+1, -1, +1, +1)}


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


def load(need):
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
    return val


def main():
    cells = json.load(open(os.path.join(HERE, "instrument_final_cells.json")))
    lvl = json.load(open(os.path.join(HERE, "element_levels.json")))["consensus_pairs"]
    univ = {u["id"]: u["name"]
            for u in json.load(open(os.path.join(HERE, "onet_element_universe.json")))}
    cell_of = {e: c for c, els in cells.items() for e in els}

    # ---- 1. element overlap ------------------------------------------------
    print("=" * 72)
    print("1. ELEMENT OVERLAP — level signatures vs the U/L/D/N instrument")
    print("=" * 72)
    sig = collections.defaultdict(list)
    for p in lvl:
        sig[p["level"]].append((p["id"], +1 if p["sign"] == "+" else -1))
    used = {p["id"] for p in lvl}
    for lv in ("FREE", "BOTTOM", "MIDDLE", "TOP"):
        inn = [(e, s) for e, s in sig[lv] if e in cell_of]
        out = [(e, s) for e, s in sig[lv] if e not in cell_of]
        print(f"\n{lv}: {len(sig[lv])} elements — {len(inn)} in instrument, {len(out)} new")
        cellmix = collections.Counter(f"{cell_of[e]}{'+' if s > 0 else '-'}" for e, s in inn)
        print(f"   from cells: {dict(cellmix)}")
        for e, s in out:
            print(f"   NEW  {'+' if s > 0 else '-'} {e:<13s}{univ.get(e, '?')[:46]}")
    never = [e for e in set().union(*map(set, cells.values())) if e not in used]
    print(f"\ninstrument elements the levels arm never reached 2-of-3 on: {len(never)} of 64")

    # ---- 2. score correlations ---------------------------------------------
    need = used | set().union(*map(set, cells.values()))
    val = load(need)
    occ = sorted(set.intersection(*(set(val[e]) for e in need)))
    print("\n" + "=" * 72)
    print(f"2. SCORE CORRELATIONS over the {len(occ)} occupations complete on everything")
    print("=" * 72)

    def z(e, oo):
        xs = [val[e][o] for o in oo]
        m, s = st.mean(xs), st.pstdev(xs) or 1
        return {o: (val[e][o] - m) / s for o in oo}

    Z = {e: z(e, occ) for e in need}
    comp = {}
    for c, els in cells.items():
        comp[c] = {o: st.mean(Z[e][o] * (-1 if e in REV else 1) for e in els)
                   for o in occ}
    for name, w in PROF.items():
        comp[name] = {o: sum(wi * comp[k][o] for wi, k in zip(w, "ULDN")) / 4
                      for o in occ}
    for lv, items in sig.items():
        comp[lv] = {o: st.mean(s * Z[e][o] for e, s in items) for o in occ}

    rows = ["FREE", "BOTTOM", "MIDDLE", "TOP"]
    colsets = [("components", ["U", "L", "D", "N"]),
               ("profiles", ["free", "front-line", "corporate"])]
    for label, cols in colsets:
        print(f"\n   levels × {label}:")
        print("            " + "".join(f"{c:>12s}" for c in cols))
        for r in rows:
            a = np.array([comp[r][o] for o in occ])
            line = f"   {r:<9s}"
            for c in cols:
                b = np.array([comp[c][o] for o in occ])
                line += f"{np.corrcoef(a, b)[0, 1]:>12.2f}"
            print(line)

    # ---- 3. the farmer -----------------------------------------------------
    print("\n" + "=" * 72)
    print("3. THE FARMER (11-9013.00) under both readings")
    print("=" * 72)
    f = "11-9013.00"
    if f in set(occ):
        for k in ["U", "L", "D", "N", "free", "front-line", "corporate",
                  "FREE", "BOTTOM", "MIDDLE", "TOP"]:
            print(f"   {k:<11s}{comp[k][f]:>+7.2f}")
    else:
        print("   farmers incomplete on the union set (3.A.1); drop it and the")
        print("   component/profile values are unchanged — see level_scores.py --drop-3a1")
        need2 = {e for e in need if e != "3.A.1"}
        occ2 = sorted(set.intersection(*(set(val[e]) for e in need2)))
        Z2 = {e: z(e, occ2) for e in need2}
        for c, els in cells.items():
            comp[c + "'"] = {o: st.mean(Z2[e][o] * (-1 if e in REV else 1) for e in els)
                             for o in occ2}
        for name, w in PROF.items():
            comp[name + "'"] = {o: sum(wi * comp[k + "'"][o]
                                       for wi, k in zip(w, "ULDN")) / 4 for o in occ2}
        for lv, items in sig.items():
            comp[lv + "'"] = {o: st.mean(s * Z2[e][o] for e, s in items if e != "3.A.1")
                              for o in occ2}
        for k in ["U", "L", "D", "N", "free", "front-line", "corporate",
                  "FREE", "BOTTOM", "MIDDLE", "TOP"]:
            print(f"   {k:<11s}{comp[k + chr(39)][f]:>+7.2f}")


if __name__ == "__main__":
    main()
