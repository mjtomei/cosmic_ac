#!/usr/bin/env python3
"""The synthesis check: is the occupational result the class/education U?

Matthew's reading of Stage 1 (2026-08-18): the insulated/exposed split is the
same inverted U that class and education showed -- peak one step below the
summit -- with the corporate-drone-adjacent position as the register's home.

The sharp test is not shape-matching but NESTING: if the class U is this
structure seen coarsely, the insulation gradient (apex delta) must exist
WITHIN class rungs. It does. Two corrections found on the way are recorded
here so they are never quoted as findings:

  - IVc's within-class slope (-1.7, t -12.9) is a DEGENERATE REGRESSOR:
    199 of 200 IVc members are one SOC code (11-9013.00), delta sd 0.006.
  - The four-group display's "exposed-corporate below front-line" leg is
    FARMER-DRIVEN: remove the 199 farmers from the exposed cell and it moves
    -0.091 -> +0.021, above front-line (+0.066, t +1.6). The registered
    farmer-headwind note (prereg prediction 5) anticipated exactly this drag.

What stands after the corrections: delta positive within class I (t 1.6),
within class II itself (t 3.3 -- the class U's own peak carries the
occupational gradient), and +0.066 (t 4.0) with class fixed effects. The
occupational instrument cuts finer than the ladder it explains.

Usage: python prereg_synthesis_check.py
"""
import collections
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = ["prof_free", "prof_front_line", "prof_corporate"]
CATS = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]


def slope(sub, key):
    y = np.array([r["z"] for r in sub])
    x = np.array([r[key] for r in sub])
    X = np.column_stack([np.ones(len(sub)), x])
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    V = (len(y) / max(len(y) - 2, 1)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    return b[1], b[1] / math.sqrt(max(V[1, 1], 1e-12)), len(sub)


def main():
    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    rows = [r for r in tab if r.get("z") is not None and "comp_U" in r]
    v = [r["apex_delta"] for r in rows]
    m, s = float(np.mean(v)), float(np.std(v))
    for r in rows:
        r["d"] = (r["apex_delta"] - m) / s

    print("1. apex-delta slope within each EGP class:")
    for c in CATS:
        sub = [r for r in rows if r.get("egp") == c]
        if len(sub) >= 60:
            b, t, n = slope(sub, "d")
            soc = collections.Counter(r["soc"] for r in sub)
            flag = ("  <- DEGENERATE: one SOC holds "
                    f"{soc.most_common(1)[0][1]}/{n}"
                    if soc.most_common(1)[0][1] > 0.9 * n else "")
            print(f"   {c:<7s}n={n:>5,}  {b:+.3f} (t {t:+.1f}){flag}")
    sub = [r for r in rows if r.get("egp") in CATS]
    y = np.array([r["z"] for r in sub])
    X = np.column_stack(
        [np.ones(len(sub)), [r["d"] for r in sub]]
        + [[1.0 if r["egp"] == c else 0.0 for r in sub] for c in CATS[1:]])
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    V = (len(y) / (len(y) - X.shape[1])) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    print(f"   with class FE: {b[1]:+.3f} (t {b[1]/math.sqrt(V[1,1]):+.1f})  "
          f"n={len(sub):,}   <- the nesting test")

    print("\n2. the exposed cell, with and without farmers:")
    corp = [r for r in rows if max(P, key=lambda k: r[k]) == "prof_corporate"]
    med = float(np.median([r["apex_delta"] for r in corp]))
    grp = collections.defaultdict(list)
    for r in rows:
        g = max(P, key=lambda k: r[k])[5:]
        if g == "corporate":
            g = "corp-insul" if r["apex_delta"] >= med else "corp-expos"
        grp[g].append(r)
    fl = [r["z"] for r in grp["front_line"]]
    for lab, v2 in (
            ("corp-insulated", [r["z"] for r in grp["corp-insul"]]),
            ("corp-exposed, all", [r["z"] for r in grp["corp-expos"]]),
            ("corp-exposed, no farmers",
             [r["z"] for r in grp["corp-expos"] if r.get("egp") != "IVc"]),
            ("front_line", fl)):
        print(f"   {lab:<26s}n={len(v2):>5,}  mean z {np.mean(v2):+.3f}  "
              f"(se {np.std(v2)/math.sqrt(len(v2)):.3f})")
    levels_table(rows)


def levels_table(rows):
    """Section 3: the four-level slopes under BOTH constructions (Matthew).
    Charged ladder = the component-built free/bottom/middle/top from the
    ladder exploration; uncharged = the blind level signatures. Same shape in
    both: middle peak, top below it, free floor, bottom ~0."""
    LAD = {"free": (-1, 0, -1, -1), "bottom": (+1, -1, -1, +1),
           "middle": (+1, -1, +1, +1), "top": (-1, -1, +1, +1)}
    for r in rows:
        for k, w in LAD.items():
            r["lad_" + k] = sum(wi * r["comp_" + c]
                                for wi, c in zip(w, "ULDN")) / 4
    print("\n3. four-level slopes, both constructions (each entered alone):")
    print(f"   {'level':<9s}{'charged':>18s}{'uncharged':>18s}")
    for lv in ("free", "bottom", "middle", "top"):
        out = []
        for key in ("lad_" + lv, "lvl_" + lv.upper()):
            x = np.array([r[key] for r in rows])
            x = (x - x.mean()) / x.std()
            y = np.array([r["z"] for r in rows])
            X = np.column_stack([np.ones(len(y)), x])
            XtXi = np.linalg.pinv(X.T @ X)
            b = XtXi @ (X.T @ y)
            e = y - X @ b
            V = (len(y) / (len(y) - 2)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
            out.append(f"{b[1]:+.3f} (t {b[1]/math.sqrt(V[1,1]):+.1f})")
        print(f"   {lv:<9s}{out[0]:>18s}{out[1]:>18s}")


if __name__ == "__main__":
    main()
