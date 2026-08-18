#!/usr/bin/env python3
"""Are the new occupational covariates stronger than the existing ones?

Matthew's closing question on the run (2026-08-18). Fair comparison needs one
scale, so two metrics are used for every covariate, on the same panel:

  - per-sd coefficient with t, alone and in the grand model (scalars); for
    the categorical blocks (EGP, education) the strongest contrast is shown
    for orientation but comparisons use the block metric;
  - the block metric: adjusted-R2 LOST when the covariate is dropped from the
    grand model -- incremental explanatory power given everything else.

The new measures enter per the never-together rule: the two ladders are
represented by their strongest level (middle -- near-twins across
constructions), plus the apex delta. Grand model (i): existing covariates +
one new measure at a time. Grand model (ii): existing + dir_middle + delta
together, to ask whether the two new effects survive EACH OTHER.

Usage: python prereg_covariate_strength.py
"""
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EGP = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]


def hc1(y, X):
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    n, k = X.shape
    V = (n / max(n - k, 1)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    r2 = 1 - float(e @ e) / float(((y - y.mean())**2).sum())
    adj = 1 - (1 - r2) * (n - 1) / max(n - k, 1)
    return b, V, adj


def main():
    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    rows = [r for r in tab if r.get("z") is not None and "comp_U" in r
            and r.get("bd") is not None and r.get("egp") in EGP
            and r.get("edu") and r.get("logdepth") is not None]
    edus = sorted({r["edu"] for r in rows})
    edus = [e for e in edus if sum(1 for r in rows if r["edu"] == e) >= 50]
    rows = [r for r in rows if r["edu"] in edus]
    y = np.array([r["z"] for r in rows])
    n = len(rows)

    def col(key):
        v = np.array([r[key] for r in rows], float)
        return (v - v.mean()) / (v.std() or 1)

    scal = {k: col(k) for k in ("bd", "logdepth", "apex_delta",
                                "dir_middle", "lvl_MIDDLE")}
    egp_b = [np.array([1.0 if r["egp"] == c else 0.0 for r in rows])
             for c in EGP[1:]]
    edu_b = [np.array([1.0 if r["edu"] == e else 0.0 for r in rows])
             for e in edus[1:]]
    BLOCKS = {"birthdec": [scal["bd"]], "EGP class": egp_b,
              "education": edu_b, "prominence": [scal["logdepth"]]}

    print(f"panel n = {n:,}\n")
    print("1. ALONE (per-sd slope; blocks by adjR2):")
    for nm in ("bd", "logdepth", "apex_delta", "dir_middle", "lvl_MIDDLE"):
        X = np.column_stack([np.ones(n), scal[nm]])
        b, V, adj = hc1(y, X)
        print(f"   {nm:<11s}{b[1]:+.3f} (t {b[1]/math.sqrt(V[1,1]):+.1f})"
              f"   adjR2 {adj:.4f}")
    for nm, blk in (("EGP class", egp_b), ("education", edu_b)):
        X = np.column_stack([np.ones(n)] + blk)
        _, _, adj = hc1(y, X)
        print(f"   {nm:<11s}{'(block)':>7s}          adjR2 {adj:.4f}")

    def grand(extra, drop=None):
        blocks = dict(BLOCKS)
        for k, v in extra.items():
            blocks[k] = [v]
        cols, names = [np.ones(n)], ["const"]
        for k, vs in blocks.items():
            if k == drop:
                continue
            for i, v in enumerate(vs):
                cols.append(v)
                names.append(k if len(vs) == 1 else f"{k}#{i}")
        X = np.column_stack(cols)
        return hc1(y, X), names

    for title, extra in (
            ("2. GRAND MODEL (i): existing + apex delta",
             {"apex delta": scal["apex_delta"]}),
            ("3. GRAND MODEL (i'): existing + dir_middle",
             {"dir middle": scal["dir_middle"]}),
            ("4. GRAND MODEL (ii): existing + dir_middle + apex delta",
             {"dir middle": scal["dir_middle"],
              "apex delta": scal["apex_delta"]})):
        (b, V, adj_full), names = grand(extra)
        print(f"\n{title}   (adjR2 {adj_full:.4f})")
        print(f"   {'covariate':<12s}{'in-model':>16s}{'adjR2 lost if dropped':>24s}")
        for k in list(BLOCKS) + list(extra):
            (b2, V2, adj_d), _ = grand(extra, drop=k)
            ii = [i for i, nmn in enumerate(names) if nmn.split("#")[0] == k]
            if len(ii) == 1:
                i = ii[0]
                cell = f"{b[i]:+.3f} (t {b[i]/math.sqrt(max(V[i,i],1e-12)):+.1f})"
            else:
                cell = "(block)"
            print(f"   {k:<12s}{cell:>16s}{adj_full-adj_d:>18.4f}")


if __name__ == "__main__":
    main()
