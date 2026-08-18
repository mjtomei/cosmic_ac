#!/usr/bin/env python3
"""Stage 1 of the pre-registered occupational study: every registered fit.

Reads prereg_member_table.json (built by prereg_join.py -- the one join step)
and runs the registered Stage-1 battery. One observation per member, register
z-scored within chamber, HC1 (members appear once), occupational predictors
standardised over the analysis sample so slopes are comparable, as registered.

Sections:
  1  components alone (x4) and jointly, each also with birthdec
  2  profiles alone (x3), the ordering bootstrap (2,000 member resamples)
  3  EGP, for scale
  4  the horse race: charged vs uncharged (AIC primary), headline vs headline,
     encompassing F both directions
  5  the apex delta
  6  hierarchy: altitude quadratic in top-tercile E, peak-location bootstrap;
     the rung x ownership arm (no O*NET)
  7  registered subsets and splits: U decomposition, D without 1.B.3.al,
     N writing views, N halves, activity/context-only, M1/M2 instrument splits
  8  autonomy: asymmetry (median split) and nominal vs effective
  9  the four-sign pattern in the joint fit; argmax display counts

Usage: python prereg_stage1.py [--seed 20260818]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = ["comp_U", "comp_L", "comp_D", "comp_N"]
LVL = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]
PROF = ["prof_free", "prof_front_line", "prof_corporate"]
EGP_CATS = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]


def ols(y, X):
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    n, k = X.shape
    V = (n / max(n - k, 1)) * XtXi @ ((X * (e ** 2)[:, None]).T @ X) @ XtXi
    sig2 = float(e @ e) / n
    aic = n * math.log(sig2) + 2 * k
    r2 = 1 - float(e @ e) / float(((y - y.mean()) ** 2).sum())
    adj = 1 - (1 - r2) * (n - 1) / max(n - k, 1)
    return b, V, e, aic, adj


def fit(rows, keys, ybd=False, label="", quiet=False):
    sub = [r for r in rows if all(r.get(k) is not None for k in keys)
           and (r.get("bd") is not None or not ybd)]
    y = [r["z"] for r in sub]
    X = [[1.0] + [r[k] for k in keys] + ([r["bd"]] if ybd else [])
         for r in sub]
    b, V, e, aic, adj = ols(y, X)
    if not quiet:
        cells = "  ".join(f"{k.split('_', 1)[1]} {b[i+1]:+.3f} "
                          f"(t {b[i+1]/math.sqrt(V[i+1, i+1]):+.1f})"
                          for i, k in enumerate(keys))
        print(f"  {label:<26s} n={len(sub):,}  {cells}"
              f"{'  [+bd]' if ybd else ''}")
    return b, V, len(sub), aic, adj


def std(rows, keys):
    for k in keys:
        v = [r[k] for r in rows if r.get(k) is not None]
        m, s = float(np.mean(v)), float(np.std(v)) or 1.0
        for r in rows:
            if r.get(k) is not None:
                r[k] = (r[k] - m) / s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260818)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    rows = [r for r in tab if r.get("z") is not None and "comp_U" in r]
    allkeys = [k for k in rows[0] if k.startswith(
        ("comp_", "prof_", "lvl_", "sub_", "row_", "ac_", "auto_", "apex", "E", "A"))]
    std(rows, allkeys)
    print(f"analysis panel: {len(rows):,} members with z + both instruments\n")

    print("=" * 74)
    print("1. COMPONENTS -- alone, jointly, and cohort-adjusted")
    print("=" * 74)
    for k in COMP:
        fit(rows, [k], label=k)
        fit(rows, [k], ybd=True, label=k)
    print()
    fit(rows, COMP, label="joint U+L+D+N")
    bj, Vj, nj, aic_c, adj_c = fit(rows, COMP, ybd=True, label="joint +bd")

    print("\n" + "=" * 74)
    print("2. PROFILES -- slopes and the registered ordering")
    print("=" * 74)
    betas = {}
    for k in PROF:
        b, V, n, _, _ = fit(rows, [k], label=k)
        betas[k] = b[1]
        fit(rows, [k], ybd=True, label=k)
    order = betas["prof_corporate"] > betas["prof_front_line"] > betas["prof_free"]
    top = betas["prof_corporate"] > max(betas["prof_front_line"], betas["prof_free"])
    print(f"\n  point estimates: corporate {betas['prof_corporate']:+.3f}  "
          f"front-line {betas['prof_front_line']:+.3f}  free {betas['prof_free']:+.3f}")
    print(f"  full ordering holds: {order}   corporate on top: {top}")
    B = 2000
    sub = [r for r in rows if all(r.get(k) is not None for k in PROF)]
    ys = np.array([r["z"] for r in sub])
    Xs = {k: np.array([r[k] for r in sub]) for k in PROF}
    n = len(sub)
    hold = croptop = 0
    for _ in range(B):
        ii = rng.integers(0, n, n)
        bb = {k: float(np.polyfit(Xs[k][ii], ys[ii], 1)[0]) for k in PROF}
        if bb["prof_corporate"] > bb["prof_front_line"] > bb["prof_free"]:
            hold += 1
        if bb["prof_corporate"] > max(bb["prof_front_line"], bb["prof_free"]):
            croptop += 1
    print(f"  bootstrap ({B} member resamples): full ordering {100*hold/B:.1f}%"
          f"   corporate top {100*croptop/B:.1f}%   <- the load-bearing share")

    print("\n" + "=" * 74)
    print("3. THE INCUMBENT, FOR SCALE -- EGP class dummies")
    print("=" * 74)
    sub = [r for r in rows if r.get("egp") in EGP_CATS]
    y = [r["z"] for r in sub]
    X = [[1.0] + [1.0 if r["egp"] == c else 0.0 for c in EGP_CATS[1:]]
         for r in sub]
    b, V, e, aic_e, adj_e = ols(y, X)
    print(f"  n={len(sub):,}  adjR2 {adj_e:.4f}  (baseline I)")
    for i, c in enumerate(EGP_CATS[1:], 1):
        print(f"    {c:<7s}{b[i]:+.3f} (t {b[i]/math.sqrt(max(V[i,i],1e-12)):+.1f})")

    print("\n" + "=" * 74)
    print("4. THE HORSE RACE -- charged vs uncharged, criterion as registered")
    print("=" * 74)
    _, _, n1, aicC, adjC = fit(rows, COMP, label="charged  U+L+D+N", quiet=True)
    _, _, n2, aicU, adjU = fit(rows, LVL, label="uncharged levels", quiet=True)
    print(f"  charged  z ~ U+L+D+N              n={n1:,}  AIC {aicC:,.1f}  adjR2 {adjC:.4f}")
    print(f"  uncharged z ~ FREE+BOT+MID+TOP    n={n2:,}  AIC {aicU:,.1f}  adjR2 {adjU:.4f}")
    print(f"  PRIMARY: {'CHARGED' if aicC < aicU else 'UNCHARGED'} wins by "
          f"{abs(aicC-aicU):.1f} AIC")
    bC, VC, nC, _, _ = fit(rows, ["prof_corporate"], quiet=True)
    bM, VM, nM, _, _ = fit(rows, ["lvl_MIDDLE"], quiet=True)
    print(f"  headline: corporate {bC[1]:+.3f} (t {bC[1]/math.sqrt(VC[1,1]):+.1f})"
          f"   vs MIDDLE {bM[1]:+.3f} (t {bM[1]/math.sqrt(VM[1,1]):+.1f})")
    for lab, base, add in (("levels add to charged?", COMP, LVL),
                           ("charged adds to levels?", LVL, COMP)):
        subb = [r for r in rows if all(r.get(k) is not None
                                       for k in base + add)]
        yb = np.array([r["z"] for r in subb])
        X0 = np.array([[1.0] + [r[k] for k in base] for r in subb])
        X1 = np.array([[1.0] + [r[k] for k in base + add] for r in subb])
        _, _, e0, _, _ = ols(yb, X0)
        _, _, e1, _, _ = ols(yb, X1)
        rss0, rss1 = float(e0 @ e0), float(e1 @ e1)
        q = len(add); dof = len(subb) - X1.shape[1]
        F = ((rss0 - rss1) / q) / (rss1 / dof)
        # Wilson-Hilferty chi2 approx of the F right tail (no scipy on box)
        x = q * F
        zz = ((x / q) ** (1/3) - (1 - 2/(9*q))) / math.sqrt(2/(9*q))
        p = 0.5 * math.erfc(zz / math.sqrt(2))
        print(f"  encompassing -- {lab:<24s} F({q},{dof}) = {F:.2f}  p ~ {p:.4f}")

    print("\n" + "=" * 74)
    print("5. THE APEX DELTA -- insulated command vs exposed command")
    print("=" * 74)
    bD, VD, nD, _, _ = fit(rows, ["apex_delta"], label="apex_delta")
    fit(rows, ["apex_delta"], ybd=True, label="apex_delta")
    print(f"  registered: beta > 0.  observed {bD[1]:+.3f} "
          f"(t {bD[1]/math.sqrt(VD[1,1]):+.1f})")

    print("\n" + "=" * 74)
    print("6. HIERARCHY -- the altitude shape, and the taxonomy arm")
    print("=" * 74)
    subE = sorted([r for r in rows if r.get("E") is not None],
                  key=lambda r: r["E"])
    topE = subE[len(subE)*2//3:]
    yA = np.array([r["z"] for r in topE])
    Araw = np.array([r["A"] for r in topE])
    XA = np.column_stack([np.ones(len(topE)), Araw, Araw**2])
    bA, VA, _, _, _ = ols(yA, XA)
    pk = -bA[1] / (2*bA[2]) if bA[2] != 0 else float("nan")
    lo, hi = Araw.min(), Araw.max()
    print(f"  top-tercile E (n={len(topE):,}): z ~ A + A^2")
    print(f"    A {bA[1]:+.3f} (t {bA[1]/math.sqrt(VA[1,1]):+.1f})   "
          f"A^2 {bA[2]:+.3f} (t {bA[2]/math.sqrt(VA[2,2]):+.1f})")
    print(f"    implied peak A* = {pk:+.2f}   observed A range "
          f"[{lo:+.2f}, {hi:+.2f}]   interior: {lo < pk < hi}")
    inpk = 0
    for _ in range(B):
        ii = rng.integers(0, len(topE), len(topE))
        bb = np.linalg.lstsq(XA[ii], yA[ii], rcond=None)[0]
        if bb[2] != 0:
            p2 = -bb[1] / (2*bb[2])
            if bb[2] < 0 and lo < p2 < hi:
                inpk += 1
    print(f"    bootstrap: concave-with-interior-peak in {100*inpk/B:.1f}% "
          f"of {B} resamples")
    print("\n  rung x ownership (means of z, members appear once):")
    import collections
    cells = collections.defaultdict(list)
    for r in tab:
        if r.get("z") is not None and r.get("rung"):
            cells[(r["rung"], r["ownership"])].append(r["z"])
    for k in sorted(cells):
        v = cells[k]
        print(f"    {k[0]:<12s}{k[1]:<10s}n={len(v):>4d}  "
              f"mean z {np.mean(v):+.3f}  (se {np.std(v)/math.sqrt(len(v)):.3f})")

    print("\n" + "=" * 74)
    print("7. REGISTERED SUBSETS AND SPLITS")
    print("=" * 74)
    for k, lab in (("sub_U_cons", "U: consultation alone"),
                   ("sub_U_disc", "U: discretion (rev) alone"),
                   ("sub_D_noal", "D without 1.B.3.al"),
                   ("sub_N_nowrite", "N without the writing four"),
                   ("sub_writing", "the writing four alone")):
        fit(rows, [k], label=lab)
    print("\n  M1-only and M2-only instrument splits (joint component fits):")
    fit(rows, ["comp_U", "row_L_M1", "row_D_M1", "row_N_M1"],
        label="M1: U+L1+D1+N1")
    fit(rows, ["row_L_M2", "row_D_M2", "row_N_M2"], label="M2: L2+D2+N2")
    print("\n  activity/context-only components:")
    fit(rows, ["ac_U", "ac_L", "ac_D", "ac_N"], label="AC-only joint")

    print("\n" + "=" * 74)
    print("8. AUTONOMY -- asymmetry, and nominal vs effective")
    print("=" * 74)
    auto = [r for r in rows if r.get("sub_U_disc") is not None]
    araw = np.array([-r["sub_U_disc"] for r in auto])   # high = free
    med = float(np.median(araw))
    for side, lab in ((araw >= med, "high-autonomy half"),
                      (araw < med, "low-autonomy half")):
        ys = np.array([r["z"] for r in auto])[side]
        xs = araw[side]
        X = np.column_stack([np.ones(side.sum()), xs])
        b, V, _, _, _ = ols(ys, X)
        print(f"  {lab:<22s} n={int(side.sum()):,}  slope {b[1]:+.3f} "
              f"(t {b[1]/math.sqrt(V[1,1]):+.1f})   "
              f"[registered: high negative, low near-flat]")
    fit(rows, ["auto_nominal"], label="nominal autonomy")
    fit(rows, ["auto_effective"], label="effective autonomy")

    print("\n" + "=" * 74)
    print("9. THE FOUR-SIGN PATTERN, and the display")
    print("=" * 74)
    signs = {"comp_U": +1, "comp_L": -1, "comp_D": +1, "comp_N": +1}
    ok = all(math.copysign(1, bj[i+1]) == signs[k]
             for i, k in enumerate(COMP))
    got = "  ".join(f"{k[5:]}{'+' if bj[i+1] > 0 else '-'}"
                    for i, k in enumerate(COMP))
    print(f"  joint fit signs: {got}   registered U+ L- D+ N+   "
          f"pattern holds: {ok}")
    am = collections.Counter()
    for r in rows:
        if all(r.get(k) is not None for k in PROF):
            am[max(PROF, key=lambda k: r[k])] += 1
    print(f"  argmax display (secondary): "
          + "  ".join(f"{k[5:]} {v:,}" for k, v in am.most_common()))


if __name__ == "__main__":
    main()
