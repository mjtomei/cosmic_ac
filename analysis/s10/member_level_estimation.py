#!/usr/bin/env python3
"""Legislator-level estimation: one member, one vote, chambers on one scale.

WHY THIS SPECIFICATION EXISTS, AND WHY IT IS THE PRIMARY ONE

The panel specification (panel_estimation.py) weights member-years by words
and clusters errors by member. Three problems surfaced in sequence, each
caught by a check Matthew insisted on:

  1. Unclustered member-year inference inflated the provincial results
     (t = 3-4 became t = 1.5-1.8 under clustering) — the study's third
     unclustered-inference incident.
  2. Per-term t-tests then read as disconfirmation what the JOINT Wald showed
     was a real distributed pattern (class terms jointly p = 0.029 pooled).
  3. Word-weighting let a handful of verbose long-servers dominate point
     estimates (IVab's provincial +0.91 fell to +0.01 sigma at equal weight),
     and raw cross-chamber pooling let large-variance, low-covariate-variance
     chambers (the US, where nearly everyone holds a degree) swamp effects
     that exist on a within-chamber scale.

This file is the fix for all three at once: ONE observation per legislator
(career rate over all their words, >= 8,000), EQUAL weight, register
Z-SCORED within each legislature against the member-level mean and sd of its
full population, HC1 errors (valid because members appear once — nothing to
cluster), and the JOINT Wald reported beside every per-term table.

WHAT IT CANNOT DO: no year fixed effects exist at career level, so the
birth-decade coefficient absorbs era-of-service along with cohort and must
NOT be quoted from here. The citable cohort figure remains the member-year
panel's +1.01 (t = 10.96) with year FE. Class/education coefficients here are
controlled for birthdec and are the citable versions of those effects.

RESULTS AS OF 2026-08-16 (n = 3,413 class / 3,496 education / 704 origin):

  CLASS      II +0.094s (t 2.69), VIIab -0.253s (t -2.52), joint p = 0.0009;
             ordering nearly monotone EGP rank with ONE inversion: II above I.
  EDUCATION  ladder +0.057s/rung (t 2.98, academic rungs), joint p = 0.0020;
             z-means rise to a PEAK AT BACHELOR then fall (graduate +0.03,
             professional -0.07) — the same top-tier crossover as class.
  ORIGIN     null under every specification tried (joint p = 0.53): the
             register tracks class DESTINATION, not origin.

The peak-below-the-summit shape in both instruments, with the peak's exact
location unstable across panels, is what a chase-and-flight cycle predicts
(the top tier is furthest along in abandoning the form, and the peak should
migrate downward as flight propagates). Recorded as hypothesis; the
era-resolved peak-location test it implies has not been run.

Usage: python member_level_estimation.py [--arm class|edu|origin|all]
"""
import argparse
import math
import sys
import os
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_estimation as PE               # noqa: E402

LV = PE.LV
MIN_WORDS = 8000


def members():
    code = PE.coding_maps()
    prov = PE.provincial_rows(code)
    t1, dropped = PE.tier1_rows(code)
    mem = {}
    for r in prov + t1:
        m = mem.setdefault(r["member"], {
            "chamber": r["chamber"], "w": 0, "h": 0.0, "egp": r["egp"],
            "edu": r["edu"], "father": r["father"], "mother": r["mother"],
            "birth": r["birth"]})
        m["w"] += r["words"]
        m["h"] += r["rate"] * r["words"] / 1000.0
    out = []
    for k, m in mem.items():
        if m["w"] < MIN_WORDS:
            continue
        b = m["birth"]
        out.append(dict(m, member=k, rate=m["h"] / m["w"] * 1000,
                        bd=((b - 1960) / 10.0) if b and 1925 <= b <= 2000
                        else None))
    return out


def zscore(rows):
    """z against each chamber's FULL member population, not the subsample —
    a covariate-bearing subsample's own mean/sd would absorb signal."""
    by = defaultdict(list)
    for r in rows:
        by[r["chamber"]].append(r["rate"])
    stats = {ch: (float(np.mean(v)), float(np.std(v)))
             for ch, v in by.items() if len(v) >= 10}
    for r in rows:
        s = stats.get(r["chamber"])
        r["z"] = (r["rate"] - s[0]) / s[1] if s and s[1] else None
    return rows


def ols_hc1(y, X):
    X = np.asarray(X)
    y = np.asarray(y)
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ (X.T @ y)
    e = y - X @ beta
    N, k = X.shape
    V = (N / max(N - k, 1)) * XtXi @ ((X * (e ** 2)[:, None]).T @ X) @ XtXi
    return beta, V


def wald(beta, V, ii):
    b = beta[ii]
    Vs = V[np.ix_(ii, ii)]
    W = float(b @ np.linalg.pinv(Vs) @ b)
    k = len(ii)
    z = ((W / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    return W, k, 0.5 * math.erfc(z / math.sqrt(2))


def table(rows, cat_of, cats, base, label):
    """Both specifications, A (z, no FE) and B (raw, chamber FE)."""
    for ykey, chfe, tag in (("z", False, "A. z within legislature"),
                            ("rate", True, "B. raw + chamber FE")):
        sub = [r for r in rows if r.get(ykey) is not None]
        chs = sorted({r["chamber"] for r in sub})[1:] if chfe else []
        y, X = [], []
        for r in sub:
            y.append(r[ykey])
            X.append([1.0] + [1.0 if cat_of(r) == c else 0.0 for c in cats]
                     + [r["bd"]]
                     + [1.0 if r["chamber"] == cc else 0.0 for cc in chs])
        beta, V = ols_hc1(y, X)
        print(f"\n{label} — {tag}   n={len(sub):,}  (baseline {base})")
        for j, c in enumerate(cats, start=1):
            b, se = beta[j], math.sqrt(V[j, j])
            star = " *" if se and abs(b / se) > 1.96 else ""
            print(f"  {c:<14}{b:>+9.3f}  se {se:.3f}  t {b/se:+.2f}{star}")
        b, se = beta[len(cats) + 1], math.sqrt(V[len(cats) + 1,
                                                 len(cats) + 1])
        print(f"  {'birthdec':<14}{b:>+9.3f}  se {se:.3f}  t {b/se:+.2f} "
              f"(absorbs era; do not quote)")
        W, k, p = wald(beta, V, list(range(1, len(cats) + 1)))
        print(f"  JOINT Wald: chi2={W:.1f}, df={k}, p={p:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="all",
                    choices=("all", "class", "edu", "origin"))
    a = ap.parse_args()
    rows = zscore(members())
    ok = [r for r in rows if r["bd"] is not None]
    print(f"{len(ok):,} legislators with birth year, "
          f"{len({r['chamber'] for r in ok})} chambers")

    if a.arm in ("all", "class"):
        sub = [r for r in ok if r["egp"] in PE.EGP_RANK]
        cats = [c for c in PE.EGP if c != "I"
                and sum(1 for r in sub if r["egp"] == c) > 25]
        print(f"\nclass n by category: "
              f"{dict(Counter(r['egp'] for r in sub))}")
        table(sub, lambda r: r["egp"], cats, "class I", "CLASS (EGP)")

    if a.arm in ("all", "edu"):
        sub = [r for r in ok if r["edu"] in LV]
        cats = [l for l in LV if l != "bachelor"
                and sum(1 for r in sub if r["edu"] == l) > 25]
        table(sub, lambda r: r["edu"], cats, "bachelor", "EDUCATION")
        lad = [r for r in sub if r["edu"] != "professional" and
               r.get("z") is not None]
        y = [r["z"] for r in lad]
        X = [[1.0, float(LV.index(r["edu"])), r["bd"]] for r in lad]
        beta, V = ols_hc1(y, X)
        b, se = beta[1], math.sqrt(V[1, 1])
        print(f"\n  ladder (academic rungs, z): {b:+.3f}s/rung "
              f"(se {se:.3f}, t {b/se:+.2f}), n={len(lad):,}")

    if a.arm in ("all", "origin"):
        sub = []
        for r in ok:
            ps = [p for p in (r["father"], r["mother"]) if p in PE.EGP_RANK]
            if not ps:
                continue
            org = min(ps, key=lambda c: PE.EGP_RANK[c])
            r2 = dict(r)
            r2["org3"] = ("professional" if org in ("I", "II") else
                          "working" if org in ("V/VI", "VIIab") else
                          "intermediate")
            sub.append(r2)
        print(f"\norigin mix: {dict(Counter(r['org3'] for r in sub))}")
        table(sub, lambda r: r["org3"], ["intermediate", "working"],
              "professional-origin", "CLASS ORIGIN (parental, dominance)")


if __name__ == "__main__":
    main()
