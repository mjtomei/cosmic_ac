#!/usr/bin/env python3
"""The full-panel re-estimation: class, education and origin at 13 chambers.

WHAT THIS IS

Every §4.6a regression, re-run on the expanded panel (8 Canadian provinces +
US House + US Senate + UK Commons + federal Canada + Dáil Éireann), with the
one thing the original results lacked and the study committed to before
believing them: CLUSTER-ROBUST STANDARD ERRORS BY MEMBER. The old SEs treated
member-years as independent draws; three prior incidents in this study came
from exactly that class of inference.

JOINS, all deterministic:

  provinces  member_year_rates.json (prov|key|year) x occupation_coding.json
             (v1) via each province file's own speaker key, plus birth years.
  tier-1     member_year_rates_t1.json (CH|key|year) x covariates_tier1.json,
             occupation strings coded via occupation_coding_v2.json. A key
             spanning several people resolves by year in [term_first,
             term_last]; rows flagged ambiguous, or whose year matches no
             person's term, are DROPPED and counted, not guessed.

PARENTAL ORIGIN uses the same v2 string->EGP map on father/mother occupation
strings, combined by Erikson dominance (the EGP convention; the rule choice
is reported alongside in class_origin.py and matters little when only one
parent is coded, which is the modal case here).

CLUSTERED SEs: Liang-Zeger, clusters = distinct members. With G clusters the
usual small-sample factor G/(G-1) * (N-1)/(N-k) is applied.

Usage:
  python panel_estimation.py            # everything
  python panel_estimation.py --arm class|edu|origin
"""
import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402
import covariate_study as CS                # noqa: E402
import class_markedness as CM               # noqa: E402

EGP = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
EGP_RANK = {c: i for i, c in enumerate(EGP)}
LV = ["none", "secondary", "college", "bachelor", "graduate", "professional"]
MIN_WORDS = 8000


def coding_maps():
    m = {}
    for f in ("provinces/occupation_coding.json",
              "provinces/occupation_coding_v2.json"):
        for r in json.load(open(os.path.join(HERE, f))):
            if r.get("egp") in EGP_RANK or r.get("egp") in ("unknown",
                                                            "none-political"):
                m[r["string"]] = r["egp"]
    return m


def provincial_rows(code):
    """member-year rows for the 8 provinces (reuses the v1 join machinery)."""
    cls = CM.member_class()
    by = {}
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_allsource.json"))):
        if r.get("birth_year"):
            by[(r["prov"], FW.norm(r["name"]))] = r["birth_year"]
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_bios.json"))):
        k = (r.get("prov"), FW.norm(r.get("name") or ""))
        if r.get("birth_year") and k not in by:
            by[k] = r["birth_year"]
    edu = CS.load_covariates("official")
    rows = []
    cell = json.load(open(os.path.join(HERE, "member_year_rates.json")))
    agg = defaultdict(lambda: [0, 0])
    for k, (w, h) in cell.items():
        pv, nm, yr = k.split("|")
        agg[(pv, nm, yr)][0] += w
        agg[(pv, nm, yr)][1] += h
    for (pv, nm, yr), (w, h) in agg.items():
        if w < MIN_WORDS:
            continue
        rows.append({
            "chamber": pv, "member": f"{pv}|{nm}", "year": int(yr),
            "words": w, "rate": h / w * 1000,
            "egp": cls.get((pv, nm)),
            "edu": (edu.get(pv, {}).get(nm) or {}).get("edu"),
            "birth": by.get((pv, nm)),
            "father": None, "mother": None,     # provincial parental joined
        })                                       # via allsource below
    pj = {}
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_allsource.json"))):
        k = f"{r['prov']}|{FW.norm(r['name'])}"
        pj[k] = (code.get((r.get("father_occupation") or "").strip()),
                 code.get((r.get("mother_occupation") or "").strip()))
    for r in rows:
        f, m = pj.get(r["member"], (None, None))
        r["father"], r["mother"] = f, m
    return rows


def tier1_rows(code):
    cov = defaultdict(list)
    for r in json.load(open(os.path.join(HERE, "covariates_tier1.json"))):
        cov[(r["chamber"], r["key"])].append(r)
    dropped = Counter()
    rows = []
    cell = json.load(open(os.path.join(HERE, "member_year_rates_t1.json")))
    for k, (w, h) in cell.items():
        ch, nm, yr = k.split("|")
        if w < MIN_WORDS:
            continue
        cands = cov.get((ch, nm))
        if not cands:
            dropped["no covariate"] += 1
            continue
        y = int(yr)
        # resolve key+year -> person by term span; unique hit required
        hits = [c for c in cands
                if (c.get("term_first") or 0) - 1 <= y <= (c.get("term_last")
                                                           or 9999) + 1]
        if len(hits) != 1:
            hits = [c for c in cands if not c.get("ambiguous")] \
                if len(cands) == 1 else hits
        if len(hits) != 1:
            dropped["ambiguous key-year"] += 1
            continue
        c = hits[0]
        if c.get("ambiguous"):
            dropped["flagged ambiguous"] += 1
            continue
        person = f"{ch}|{nm}|{c.get('person_name') or ''}"
        rows.append({
            "chamber": ch, "member": person, "year": y,
            "words": w, "rate": h / w * 1000,
            "egp": code.get((c.get("prior_occupation") or "").strip()),
            "edu": (c.get("education_level") or "").strip().lower() or None,
            "birth": c.get("birth_year"),
            "father": code.get((c.get("father_occupation") or "").strip()),
            "mother": code.get((c.get("mother_occupation") or "").strip()),
        })
    return rows, dropped


def cluster_ols(y, X, names, clusters):
    """OLS with Liang-Zeger cluster-robust SEs."""
    X = np.asarray(X)
    y = np.asarray(y)
    XtX = X.T @ X
    XtXi = np.linalg.pinv(XtX)
    beta = XtXi @ (X.T @ y)
    e = y - X @ beta
    groups = defaultdict(list)
    for i, g in enumerate(clusters):
        groups[g].append(i)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for idx in groups.values():
        Xg = X[idx]
        eg = e[idx]
        s = Xg.T @ eg
        meat += np.outer(s, s)
    G, N, k = len(groups), len(y), X.shape[1]
    adj = (G / max(G - 1, 1)) * ((N - 1) / max(N - k, 1))
    V = adj * XtXi @ meat @ XtXi
    return {nm: (float(beta[j]), math.sqrt(max(float(V[j, j]), 0)))
            for j, nm in enumerate(names)}, G


def design(rows, main_cols, main_names):
    years = sorted({r["year"] for r in rows})[1:]
    chs = sorted({r["chamber"] for r in rows})[1:]
    names = ["const"] + main_names + [f"y{y}" for y in years] + \
            [f"c{c}" for c in chs]
    y, X, cl = [], [], []
    for r in rows:
        sw = math.sqrt(r["words"])
        row = [1.0] + [f(r) for f in main_cols] + \
              [1.0 if r["year"] == yy else 0.0 for yy in years] + \
              [1.0 if r["chamber"] == cc else 0.0 for cc in chs]
        y.append(r["rate"] * sw)
        X.append([v * sw for v in row])
        cl.append(r["member"])
    return y, X, names, cl


def report(res, G, keys, label):
    print(f"\n{label}   ({G:,} member clusters)")
    print(f"  {'term':<12}{'coef':>9}{'clust se':>10}{'t':>7}")
    for k in keys:
        b, se = res[k]
        star = " *" if se and abs(b / se) > 1.96 else ""
        print(f"  {k:<12}{b:>+9.3f}{se:>10.3f}{b/se if se else 0:>7.2f}{star}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="all",
                    choices=("all", "class", "edu", "origin"))
    a = ap.parse_args()
    code = coding_maps()
    prov = provincial_rows(code)
    t1, dropped = tier1_rows(code)
    rows = prov + t1
    print(f"PANEL: {len(rows):,} member-years, "
          f"{len({r['member'] for r in rows}):,} members, "
          f"{len({r['chamber'] for r in rows})} chambers")
    print(f"  tier-1 rows dropped at join: {dict(dropped)}")
    for r in rows:
        r["bd"] = ((r["birth"] - 1960) / 10.0) if r["birth"] and \
            1925 <= r["birth"] <= 2000 else None

    if a.arm in ("all", "class"):
        sub = [r for r in rows if r["egp"] in EGP_RANK and
               r["bd"] is not None]
        cats = [c for c in EGP if c != "I"
                and sum(1 for r in sub if r["egp"] == c) > 60]
        mk = lambda c: (lambda r: 1.0 if r["egp"] == c else 0.0)
        y, X, names, cl = design(
            sub, [mk(c) for c in cats] + [lambda r: r["bd"]],
            cats + ["birthdec"])
        res, G = cluster_ols(y, X, names, cl)
        n_c = Counter(r["egp"] for r in sub)
        print("\n" + "=" * 64)
        report(res, G, cats + ["birthdec"],
               f"CLASS (EGP, baseline I), year+chamber FE, birth controlled, "
               f"n={len(sub):,}")
        print("  member-years per class: " +
              "  ".join(f"{c} {n_c[c]}" for c in EGP if n_c[c]))

    if a.arm in ("all", "edu"):
        sub = [r for r in rows if r["edu"] in LV and r["bd"] is not None]
        lad = [r for r in sub if r["edu"] != "professional"]
        for r in lad:
            r["step"] = float(LV.index(r["edu"]))
        y, X, names, cl = design(lad, [lambda r: r["step"],
                                       lambda r: r["bd"]],
                                 ["level", "birthdec"])
        res, G = cluster_ols(y, X, names, cl)
        print("\n" + "=" * 64)
        report(res, G, ["level", "birthdec"],
               f"EDUCATION ladder (prof. excluded), n={len(lad):,}")
        prof = [r for r in sub]
        mkp = lambda r: 1.0 if r["edu"] == "professional" else 0.0
        y, X, names, cl = design(prof, [mkp, lambda r: r["bd"]],
                                 ["professional", "birthdec"])
        res, G = cluster_ols(y, X, names, cl)
        report(res, G, ["professional", "birthdec"],
               f"PROFESSIONAL degree vs all else, n={len(prof):,}")

    if a.arm in ("all", "origin"):
        sub = []
        for r in rows:
            ps = [p for p in (r["father"], r["mother"]) if p in EGP_RANK]
            if not ps or r["bd"] is None:
                continue
            org = min(ps, key=lambda c: EGP_RANK[c])      # dominance
            r2 = dict(r)
            r2["org3"] = ("professional" if org in ("I", "II") else
                          "working" if org in ("V/VI", "VIIab") else
                          "intermediate")
            sub.append(r2)
        n3 = Counter(r["org3"] for r in sub)
        print("\n" + "=" * 64)
        print(f"\nCLASS ORIGIN (parental, dominance) -- "
              f"{len({r['member'] for r in sub}):,} members, "
              f"{len(sub):,} member-years")
        print(f"  origin mix: {dict(n3)}")
        mk3 = lambda g: (lambda r: 1.0 if r["org3"] == g else 0.0)
        y, X, names, cl = design(
            sub, [mk3("intermediate"), mk3("working"), lambda r: r["bd"]],
            ["org_interm", "org_working", "birthdec"])
        res, G = cluster_ols(y, X, names, cl)
        report(res, G, ["org_interm", "org_working", "birthdec"],
               "ORIGIN (baseline professional-origin), year+chamber FE")


if __name__ == "__main__":
    main()
