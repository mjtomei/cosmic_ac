#!/usr/bin/env python3
"""Formation-location test: was the member's register set by where they GREW UP?

THE THIRD ATTEMPT, AND WHY THE FIRST TWO FAILED

A cohort effect on legislative register is established: birth decade +0.93
(t = +12), surviving occupation and education controls that both run the wrong
way, and identified as cohort rather than age because chamber age is flat
while the register rises. Birth cohort is a portmanteau, though — it carries
everything that differs between generations.

Two attempts to isolate ambient computing specifically returned null, and both
used the wrong geography:

  1. district adoption during TENURE (US states, provinces) — but the
     register arrives with new members, so tenure is the wrong window
  2. cohort x SERVICE-province adoption — but a member who grew up in
     Newfoundland and now sits in Alberta is coded Alberta

This uses birth province instead. The design is a within-cohort comparison:
among members born in the SAME years, did those formed in early-adopting
places arrive speaking more of the register?

THE CONSTRAINT THAT SHAPES EVERYTHING

Provincial adoption data begins in 1997 (StatCan 22-10-0034). A member born in
1955 was formed in the 1970s, decades before any adoption series exists, so no
per-member exposure figure is possible for most of the panel. Three
specifications follow from that, in decreasing strength and increasing sample:

  A. DIRECT — restrict to members whose formative window (age 15-25) overlaps
     1997-2003, i.e. born ~1972-1988, and use their birth province's mean
     adoption over the overlap. Small n, but it is the actual hypothesis.
  B. INTERACTION — all cohorts, birth-province adoption (2000 level) x birth
     decade. Assumes the 2000 cross-section ranks provinces the same way
     earlier decades did, which is an assumption, not a measurement.
  C. URBANICITY — birth-settlement population as a proxy for early technology
     exposure, available for every cohort and not dependent on any adoption
     series. Weakest link to computing, widest coverage.

A null in A with adequate n is informative. A null in A with n < 100 is not,
and the script says which it got.

MOVERS ARE THE IDENTIFYING VARIATION. If nearly every member serves their
birth province, birth and service geography are collinear and this test
cannot distinguish itself from the one that already failed. The mover share
is reported first, before any coefficient.

Usage: python formation_exposure.py
"""
import csv
import glob
import json
import math
import os
import re
from collections import defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
TITLE_RE = re.compile(
    r"^(hon\.?|honourable|l'hon\.?|mr\.?|mrs\.?|ms\.?|miss|dr\.?|mme\.?|m\.|"
    r"madame|monsieur|the)\s+", re.I)
ROLE = re.compile(r"^(premier|deputy premier|leader of the (official )?opposition|"
                  r"minister\b|government house leader|opposition house leader|"
                  r"attorney general|speaker|chair)", re.I)
MIN_WORDS = 8000


def norm(s):
    s = (s or "").strip().rstrip(":").strip()
    prev = None
    while prev != s:
        prev = s
        s = TITLE_RE.sub("", s).strip()
    return re.sub(r"\s*\(.*?\)\s*$", "", s).lower()


def ols(Y, X, names):
    n, k = len(Y), len(X[0])
    A = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
         for a in range(k)]
    yv = [sum(X[i][a] * Y[i] for i in range(n)) for a in range(k)]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    M = [r[:] for r in A]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        I[c], I[p] = I[p], I[c]
        d = M[c][c]
        if abs(d) < 1e-12:
            return None
        M[c] = [v / d for v in M[c]]
        I[c] = [v / d for v in I[c]]
        for r in range(k):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(k)]
                I[r] = [I[r][j] - f * I[c][j] for j in range(k)]
    beta = [sum(I[a][b] * yv[b] for b in range(k)) for a in range(k)]
    res = [Y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(X[i][a] * X[i][b] * res[i] ** 2 for i in range(n))
             for b in range(k)] for a in range(k)]
    sc = n / max(n - k, 1)
    V = [[sc * sum(I[a][p] * meat[p][q] * I[b][q]
                   for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0))) for j, nm in enumerate(names)}


def show(fit, keys, label):
    print(f"\n{label}")
    for k in keys:
        if k not in fit:
            continue
        b, se = fit[k]
        t = b / se if se else float("nan")
        print(f"  {k:<26s} {b:+.4f}  se {se:.4f}  t {t:+.2f}"
              f"{'  *' if abs(t) > 1.96 else ''}")


def main():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}

    adopt = {}
    for r in csv.DictReader(open(os.path.join(_HERE, "province_covariates.csv"))):
        if r["prov"].startswith("#"):
            continue
        yrs = {y: float(r[f"internet{y}"]) for y in range(1997, 2004)
               if r.get(f"internet{y}")}
        if yrs:
            adopt[r["prov"]] = yrs

    bios = {}
    for b in json.load(open(os.path.join(_HERE, "provinces", "member_bios.json"))):
        if b.get("birth_year") and (b.get("matched_name") or b.get("wikidata_qid")):
            bios[(b["prov"], b["name"])] = b
    fpath = os.path.join(_HERE, "provinces", "member_formation.json")
    if not os.path.exists(fpath):
        raise SystemExit("member_formation.json not present yet")
    form = {}
    for f in json.load(open(fpath)):
        form[(f.get("prov"), f.get("name"))] = f

    cell = defaultdict(lambda: [0, 0])
    for path in sorted(glob.glob(os.path.join(_HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable") or d.get("prov") not in adopt:
                continue
            nm = norm(d.get("speaker", ""))
            if not nm or ROLE.match(nm):
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            c = cell[(d["prov"], nm, d["date"][:4])]
            c[0] += len(t)
            c[1] += sum(1 for x in t if x in style)

    agg = defaultdict(lambda: [0, 0])
    meta = {}
    for (pv, nm, yr), (w, h) in cell.items():
        b = bios.get((pv, nm))
        if not b:
            continue
        pid = b.get("wikidata_qid") or f"{pv}:{nm}"
        agg[(pv, pid, yr)][0] += w
        agg[(pv, pid, yr)][1] += h
        meta[(pv, pid)] = (b, form.get((pv, nm)) or {})

    rows = []
    for (pv, pid, yr), (w, h) in agg.items():
        if w < MIN_WORDS:
            continue
        b, f = meta[(pv, pid)]
        by, y = b["birth_year"], int(yr)
        if not (1925 <= by <= 2000 and 18 <= y - by <= 85):
            continue
        bp = f.get("birth_province_code")
        rows.append({"pv": pv, "pid": pid, "y": y, "by": by,
                     "rate": h / w * 1000, "bp": bp,
                     "pop": f.get("birth_place_population"),
                     "mover": (bp is not None and bp != pv)})

    known = [r for r in rows if r["bp"]]
    movers = [r for r in known if r["mover"]]
    people = {(r["pv"], r["pid"]) for r in rows}
    kp = {(r["pv"], r["pid"]) for r in known}
    mp = {(r["pv"], r["pid"]) for r in movers}
    print(f"{len(rows):,} member-years, {len(people):,} people")
    print(f"birth province known for {len(kp):,} people ({100*len(kp)/len(people):.0f}%)")
    print(f"MOVERS (serve a different province than born): {len(mp):,} "
          f"({100 * len(mp) / max(len(kp), 1):.0f}% of those with birthplace)")
    if len(mp) < 30:
        print("\n** too few movers: birth and service geography are collinear,")
        print("   so this design cannot separate itself from the failed one **")

    provs = sorted({r["pv"] for r in known})[1:]
    years = sorted({r["y"] for r in known})[1:]

    def fe(r):
        return ([1.0 if r["pv"] == p else 0.0 for p in provs] +
                [1.0 if r["y"] == y else 0.0 for y in years])

    fenames = [f"p_{p}" for p in provs] + [f"y_{y}" for y in years]

    # A — direct: formative window overlaps the adoption series
    A = []
    for r in known:
        lo, hi = r["by"] + 15, r["by"] + 25
        ov = [y for y in range(max(lo, 1997), min(hi, 2003) + 1)]
        if not ov or r["bp"] not in adopt:
            continue
        vals = [adopt[r["bp"]][y] for y in ov if y in adopt[r["bp"]]]
        if vals:
            r2 = dict(r)
            r2["exp"] = (sum(vals) / len(vals) - 55.0) / 5.0
            A.append(r2)
    print(f"\nSPEC A (direct, formative window overlaps 1997-2003): "
          f"{len(A):,} member-years, "
          f"{len({(r['pv'], r['pid']) for r in A})} people")
    if len(A) >= 100:
        names = ["const", "formation_adoption", "birth_decade"] + fenames
        X = [[1.0, r["exp"], (r["by"] - 1955) / 10.0] + fe(r) for r in A]
        f1 = ols([r["rate"] for r in A], X, names)
        if f1:
            show(f1, ["formation_adoption", "birth_decade"],
                 "register ~ adoption where they grew up, during their formation:")
    else:
        print("  too few — the cohorts young enough for this are thin")

    # B — interaction across all cohorts
    B = [r for r in known if r["bp"] in adopt]
    if len(B) >= 200:
        names = ["const", "birth_decade", "cohort_x_birthprov_adoption"] + fenames
        X = [[1.0, (r["by"] - 1955) / 10.0,
              (r["by"] - 1955) / 10.0 * ((adopt[r["bp"]][2000] - 51.9) / 5.0)]
             + fe(r) for r in B]
        f2 = ols([r["rate"] for r in B], X, names)
        if f2:
            show(f2, ["birth_decade", "cohort_x_birthprov_adoption"],
                 f"SPEC B (interaction, all cohorts, n={len(B):,}):")

    # C — urbanicity of the birth settlement
    C = [r for r in known if r.get("pop")]
    if len(C) >= 200:
        names = ["const", "birth_decade", "log_birthplace_pop"] + fenames
        X = [[1.0, (r["by"] - 1955) / 10.0,
              (math.log10(max(float(r["pop"]), 1)) - 5.0)] + fe(r) for r in C]
        f3 = ols([r["rate"] for r in C], X, names)
        if f3:
            show(f3, ["birth_decade", "log_birthplace_pop"],
                 f"SPEC C (birth-settlement size, n={len(C):,}):")

    print("\nReading: a positive formation_adoption (A) is the hypothesis —")
    print("members formed in early-adopting places speak more of the register,")
    print("holding birth cohort, service province and year fixed. B and C are")
    print("weaker proxies and should not be read as confirmation if A is null.")


if __name__ == "__main__":
    main()
