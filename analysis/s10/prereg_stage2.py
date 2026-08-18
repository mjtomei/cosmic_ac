#!/usr/bin/env python3
"""Stage 2: the specification lattices and the registered permutation test.

Two lattices, per the amended registration:

  A. REGISTERED: the component block (U+L+D+N) beside birthdec, EGP class,
     education and prominence -- 2^5 = 32 specifications. Carries the
     registered four-sign permutation (corporate signs U+ L- D+ N+): shuffle
     register z across members WITHIN CHAMBER, re-run the whole lattice,
     2,000 times; p = share of shuffles matching the observed pattern share
     or better. The pre-revision pattern (U+ L+ D- N+) is tallied beside it,
     labelled descriptive.

  B. AMENDED (Matthew, post-Stage-1, logged in the prereg): the directional
     ladder and the coded ladder as blocks beside the same four covariates --
     2^6 = 64 specifications. middle + and free - declared; top and bottom
     reported unsigned. Where both ladders are present, per-coefficient
     values are unstable (coded MIDDLE/TOP correlate .99); block Wald p
     carries the weight.

Per predictor, over the specifications containing it: median coefficient,
5th-95th range, share in the predicted direction, share nominally significant
(descriptive), and the extreme specifications named. Prediction 1 (the
occupational measures add to EGP) is tested as the registered lattice
contrast: specs with the block vs otherwise-identical specs without it.

Usage: python prereg_stage2.py [--perms 2000] [--seed 20260818]
"""
import argparse
import collections
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = ["comp_U", "comp_L", "comp_D", "comp_N"]
DIR = ["dir_free", "dir_bottom", "dir_middle", "dir_top"]
COD = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]
EGP_CATS = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]
SIGNS_REG = {"comp_U": +1, "comp_L": -1, "comp_D": +1, "comp_N": +1}
SIGNS_OLD = {"comp_U": +1, "comp_L": +1, "comp_D": -1, "comp_N": +1}


def build(rows, blocks):
    cols, names = [np.ones(len(rows))], ["const"]
    for b in blocks:
        for k in b:
            cols.append(np.array([r[k] for r in rows])); names.append(k)
    return np.column_stack(cols), names


def hc1(y, X):
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    n, k = X.shape
    V = (n / max(n - k, 1)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    return b, V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260818)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    rows = [r for r in tab if r.get("z") is not None and "comp_U" in r
            and r.get("bd") is not None and r.get("egp") in EGP_CATS
            and r.get("edu") and r.get("logdepth") is not None]
    edus = sorted({r["edu"] for r in rows})
    edus = [e for e in edus
            if sum(1 for r in rows if r["edu"] == e) >= 50]
    rows = [r for r in rows if r["edu"] in edus]
    for r in rows:
        for c in EGP_CATS[1:]:
            r["egp_" + c] = 1.0 if r["egp"] == c else 0.0
        for e in edus[1:]:
            r["edu_" + e] = 1.0 if r["edu"] == e else 0.0
    for k in COMP + DIR + COD + ["bd", "logdepth"]:
        v = np.array([r[k] for r in rows])
        m, s = v.mean(), v.std() or 1
        for r in rows:
            r[k] = (r[k] - m) / s
    y = np.array([r["z"] for r in rows])
    print(f"lattice panel (all covariates present): n = {len(rows):,}; "
          f"education categories kept: {edus}\n")

    egp_b = ["egp_" + c for c in EGP_CATS[1:]]
    edu_b = ["edu_" + e for e in edus[1:]]
    COV = [("birthdec", ["bd"]), ("EGP", egp_b), ("education", edu_b),
           ("prominence", ["logdepth"])]

    # ---------------- lattice A: registered ------------------------------
    print("=" * 74)
    print("LATTICE A (registered): components x {bd, EGP, edu, prominence}")
    print("=" * 74)
    stats = collections.defaultdict(list)
    r2_with, r2_without = [], []
    designs = []
    for occ_on in (0, 1):
        for mask in itertools.product((0, 1), repeat=4):
            blocks = ([COMP] if occ_on else []) + \
                     [b for on, (_, b) in zip(mask, COV) if on]
            X, names = build(rows, blocks)
            designs.append((occ_on, mask, X, names))
            b, V = hc1(y, X)
            e = y - X @ b
            r2 = 1 - float(e @ e) / float(((y - y.mean())**2).sum())
            (r2_with if occ_on else r2_without).append((mask, r2))
            for i, nm in enumerate(names):
                if nm != "const":
                    stats[nm].append((b[i], b[i]/math.sqrt(max(V[i, i], 1e-12)),
                                      occ_on, mask))
    print(f"{'predictor':<12s}{'median':>9s}{'5-95%':>19s}"
          f"{'right-dir':>10s}{'|t|>1.96':>9s}   (n specs)")
    for nm in COMP + ["bd", "egp_II", "egp_IVc", "logdepth"]:
        vv = stats[nm]
        bs = sorted(x[0] for x in vv)
        med = bs[len(bs)//2]
        lo, hi = bs[int(.05*len(bs))], bs[int(.95*len(bs))-1]
        pred = SIGNS_REG.get(nm, +1 if nm != "egp_IVc" else -1)
        rd = sum(1 for x in vv if math.copysign(1, x[0]) == pred)/len(vv)
        sg = sum(1 for x in vv if abs(x[1]) > 1.96)/len(vv)
        print(f"{nm:<12s}{med:>+9.3f}   [{lo:+.3f},{hi:+.3f}]"
              f"{100*rd:>9.0f}%{100*sg:>8.0f}%   ({len(vv)})")

    print("\nprediction 1 -- do the components add to EGP? (paired specs,")
    print("with-block adjR2 minus without, over the 16 covariate masks):")
    dif = []
    for (mw, rw), (mo, ro) in zip(sorted(r2_with), sorted(r2_without)):
        assert mw == mo
        dif.append(rw - ro)
    print(f"  mean ΔR² {np.mean(dif):+.4f}   min {min(dif):+.4f}   "
          f"max {max(dif):+.4f}   positive in {sum(d > 0 for d in dif)}/16")

    # four-sign pattern over pattern-eligible specs (components present)
    def share(yv):
        ok_reg = ok_old = tot = 0
        for occ_on, mask, X, names in designs:
            if not occ_on:
                continue
            b, _ = hc1(yv, X) if yv is not y else (None, None)
            if yv is y:
                b, _ = hc1(y, X)
            ii = {nm: i for i, nm in enumerate(names)}
            tot += 1
            if all(math.copysign(1, b[ii[k]]) == s
                   for k, s in SIGNS_REG.items()):
                ok_reg += 1
            if all(math.copysign(1, b[ii[k]]) == s
                   for k, s in SIGNS_OLD.items()):
                ok_old += 1
        return ok_reg/tot, ok_old/tot, tot

    obs_reg, obs_old, tot = share(y)
    print(f"\nfour-sign pattern, {tot} pattern-eligible specs:")
    print(f"  registered signs (U+ L- D+ N+): {100*obs_reg:.0f}%")
    print(f"  pre-revision signs (U+ L+ D- N+), descriptive: {100*obs_old:.0f}%")

    # permutation: shuffle z within chamber; precompute projectors
    chi = collections.defaultdict(list)
    for i, r in enumerate(rows):
        chi[r["chamber"]].append(i)
    projs = []
    for occ_on, mask, X, names in designs:
        if occ_on:
            projs.append((np.linalg.pinv(X.T @ X) @ X.T,
                          {nm: i for i, nm in enumerate(names)}))
    ge = 0
    for p in range(a.perms):
        yp = y.copy()
        for ii in chi.values():
            ii = np.array(ii)
            yp[ii] = yp[rng.permutation(ii)]
        ok = 0
        for H, idx in projs:
            b = H @ yp
            if all(math.copysign(1, b[idx[k]]) == s
                   for k, s in SIGNS_REG.items()):
                ok += 1
        if ok/len(projs) >= obs_reg:
            ge += 1
    print(f"  permutation ({a.perms} within-chamber shuffles): "
          f"P(pattern share >= observed) = {ge/a.perms:.4f}")

    # ---------------- lattice B: amended ---------------------------------
    # A ladder's levels are contrasts over one space -- the registered
    # never-enter-profiles-together rule applies, so each level is the FOCAL
    # predictor alone, run over the 16 covariate masks. (A first draft entered
    # each ladder as a four-score joint block; the within-block partials were
    # suppression artifacts and that draft is dead, in git history.)
    print("\n" + "=" * 74)
    print("LATTICE B (amended): each ladder level alone x 16 covariate masks")
    print("=" * 74)
    PRED = {"dir_middle": +1, "dir_free": -1, "lvl_MIDDLE": +1,
            "lvl_FREE": -1}
    print(f"{'predictor':<12s}{'median':>9s}{'5-95%':>19s}"
          f"{'right-dir':>10s}{'|t|>1.96':>9s}{'full-covar':>12s}")
    for nm in DIR + COD:
        vv = []
        full = None
        for mask in itertools.product((0, 1), repeat=4):
            blocks = [[nm]] + [b for on, (_, b) in zip(mask, COV) if on]
            X, names = build(rows, blocks)
            b, V = hc1(y, X)
            i = names.index(nm)
            tv = b[i]/math.sqrt(max(V[i, i], 1e-12))
            vv.append((b[i], tv))
            if mask == (1, 1, 1, 1):
                full = (b[i], tv)
        bs = sorted(x[0] for x in vv)
        med = bs[len(bs)//2]
        lo, hi = bs[0], bs[-1]
        if nm in PRED:
            rd = f"{100*sum(1 for x in vv if math.copysign(1, x[0]) == PRED[nm])/len(vv):>9.0f}%"
        else:
            rd = "  unsigned"
        sg = 100*sum(1 for x in vv if abs(x[1]) > 1.96)/len(vv)
        print(f"{nm:<12s}{med:>+9.3f}   [{lo:+.3f},{hi:+.3f}]{rd:>10s}"
              f"{sg:>8.0f}%   {full[0]:+.3f} (t {full[1]:+.1f})")


if __name__ == "__main__":
    main()
