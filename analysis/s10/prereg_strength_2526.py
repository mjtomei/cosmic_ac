#!/usr/bin/env python3
"""The covariate-strength table on 2025-2026 speech only.

Matthew (2026-08-18): same table, restricted to the era where the class number
spiked. The outcome is rebuilt from member-YEAR rates: each member's words and
style hits over 2025-2026 only, rate per 1,000, z-scored within chamber
against the era-qualifying member population (chambers with >= 10 such
members), word floor 2,000 for the two-year window (the career floor is 8,000
over whole careers; short-window rates below ~2k words are noise). Covariates
and occupational scores join from prereg_member_table.json unchanged --
element scores are member-invariant.

Usage: python prereg_strength_2526.py
"""
import collections
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EGP = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]
FLOOR = 2000


def hc1(y, X):
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    n, k = X.shape
    V = (n / max(n - k, 1)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    r2 = 1 - float(e @ e) / float(((y - y.mean())**2).sum())
    adj = 1 - (1 - r2) * (n - 1) / max(n - k, 1)
    return b, V, adj


def era_rates():
    """member id (as in prereg_member_table) -> era rate. Tier-1 ids carry a
    third component (person name); year cells key on ch|nm, so aggregate on
    the first two parts and join the same way."""
    agg = collections.defaultdict(lambda: [0, 0.0])
    for f in ("member_year_rates.json", "member_year_rates_t1.json"):
        for k, (w, h) in json.load(open(os.path.join(HERE, f))).items():
            ch, nm, yr = k.split("|")
            if int(yr) in (2025, 2026):
                a = agg[(ch, nm)]
                a[0] += w
                a[1] += h
    return {k: (w, h / w * 1000) for k, (w, h) in agg.items() if w >= FLOOR}


def main():
    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    era = era_rates()
    rows = []
    for r in tab:
        key = tuple(r["member"].split("|")[:2])
        if key in era and "comp_U" in r:
            rr = dict(r)
            rr["rate2526"] = era[key][1]
            rows.append(rr)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["chamber"]].append(r["rate2526"])
    stats = {ch: (float(np.mean(v)), float(np.std(v)))
             for ch, v in by.items() if len(v) >= 10}
    rows = [r for r in rows if r["chamber"] in stats
            and stats[r["chamber"]][1] > 0]
    for r in rows:
        m, s = stats[r["chamber"]]
        r["z25"] = (r["rate2526"] - m) / s
    rows = [r for r in rows if r.get("bd") is not None
            and r.get("egp") in EGP and r.get("edu")
            and r.get("logdepth") is not None]
    edus = sorted({r["edu"] for r in rows})
    edus = [e for e in edus if sum(1 for r in rows if r["edu"] == e) >= 30]
    rows = [r for r in rows if r["edu"] in edus]
    y = np.array([r["z25"] for r in rows])
    n = len(rows)
    print(f"2025-2026 panel: n = {n:,} members, "
          f"{len(stats)} chambers, floor {FLOOR} words\n")

    def col(k):
        v = np.array([r[k] for r in rows], float)
        return (v - v.mean()) / (v.std() or 1)

    scal = {k: col(k) for k in ("bd", "logdepth", "apex_delta",
                                "dir_middle", "lvl_MIDDLE")}
    egp_b = [np.array([1.0 if r["egp"] == c else 0.0 for r in rows])
             for c in EGP[1:]]
    edu_b = [np.array([1.0 if r["edu"] == e else 0.0 for r in rows])
             for e in edus[1:]]
    one = [np.ones(n)]
    BLOCKS = {"birthdec": [scal["bd"]], "EGP class": egp_b,
              "education": edu_b, "prominence": [scal["logdepth"]]}

    print("1. ALONE:")
    for nm in ("bd", "logdepth", "apex_delta", "dir_middle", "lvl_MIDDLE"):
        b, V, adj = hc1(y, np.column_stack(one + [scal[nm]]))
        print(f"   {nm:<11s}{b[1]:+.3f} (t {b[1]/math.sqrt(V[1,1]):+.1f})"
              f"   adjR2 {adj:.4f}")
    for nm, blk in (("EGP class", egp_b), ("education", edu_b)):
        _, _, adj = hc1(y, np.column_stack(one + blk))
        print(f"   {nm:<11s}{'(block)':>7s}          adjR2 {adj:.4f}")
    # the class spike check: II vs I contrast alone
    b, V, _ = hc1(y, np.column_stack(one + egp_b))
    print(f"   (egp II contrast in-block: {b[1]:+.3f}, "
          f"t {b[1]/math.sqrt(max(V[1,1],1e-12)):+.1f})")

    def grand(extra, drop=None):
        blocks = dict(BLOCKS)
        for k, v in extra.items():
            blocks[k] = [v]
        cols, names = list(one), ["const"]
        for k, vs in blocks.items():
            if k == drop:
                continue
            for i, v in enumerate(vs):
                cols.append(v)
                names.append(k if len(vs) == 1 else f"{k}#{i}")
        return hc1(y, np.column_stack(cols)), names

    extra = {"apex delta": scal["apex_delta"]}
    (b, V, adj_full), names = grand(extra)
    print(f"\n2. GRAND MODEL: existing + apex delta   (adjR2 {adj_full:.4f})")
    print(f"   {'covariate':<12s}{'in-model':>16s}{'adjR2 lost if dropped':>24s}")
    for k in list(BLOCKS) + list(extra):
        (_, _, adj_d), _ = grand(extra, drop=k)
        ii = [i for i, nmn in enumerate(names) if nmn.split("#")[0] == k]
        cell = ("(block)" if len(ii) != 1 else
                f"{b[ii[0]]:+.3f} (t {b[ii[0]]/math.sqrt(max(V[ii[0],ii[0]],1e-12)):+.1f})")
        print(f"   {k:<12s}{cell:>16s}{adj_full-adj_d:>18.4f}")

    comp = [col("comp_" + c) for c in "ULDN"]
    d = [scal["apex_delta"]]
    print(f"\n3. TOTALS:")
    print(f"   occupational battery alone      adjR2 "
          f"{hc1(y, np.column_stack(one+comp+d))[2]:.4f}")
    print(f"   everything except cohort        adjR2 "
          f"{hc1(y, np.column_stack(one+egp_b+edu_b+[scal['logdepth']]+comp+d))[2]:.4f}")
    print(f"   everything including cohort     adjR2 "
          f"{hc1(y, np.column_stack(one+[scal['bd']]+egp_b+edu_b+[scal['logdepth']]+comp+d))[2]:.4f}")
    print(f"   cohort alone                    adjR2 "
          f"{hc1(y, np.column_stack(one+[scal['bd']]))[2]:.4f}")


if __name__ == "__main__":
    main()
