#!/usr/bin/env python3
"""Does a legislator's register track WHEN THEY WERE FORMED, not where they sit?

THE TEST

Two geographic exposure tests came back null (US states, Canadian provinces),
but the within/between decomposition then showed why they had to: the register
climb is compositional. Sitting members did not change; new arrivals enter
speaking more of it (+2.47 per 1,000 in 8/8 provinces), and the UK series
shows that premium GROWING across intakes rather than being a constant
newcomer offset.

So exposure, if it operates, operates during FORMATION — schooling and early
career — not during tenure, and not at the district. That relocates the test:

    register rate  ~  ambient computer immersion when the member was ~20-30

measured within-year and within-province, so era and chamber are held fixed
and only the member's own cohort varies.

The rival hypotheses are compositional too and are tested in the same
regression: occupational selection (communications/law/consulting displacing
trades/farming) and educational expansion. If birth cohort alone carries the
effect, that is generational language change; if occupation adds beyond it,
candidate selection is doing work.

EXPOSURE PROXY. Household internet adoption is only measured from 1997, and
members' formative years span the 1940s-2000s, so a per-member adoption figure
would be extrapolation. Instead birth year enters directly (the cohort test),
and the interpretation is stated in those terms. Members born after ~1975 came
of age with ambient networked computing; those born before ~1955 did not.

DUPLICATE ROWS: Hansard prints the same person under several forms, so rows
are grouped by wikidata_qid where available before analysis, per the bio
collection's own warning. Unmatched/blended rows (surname-only entries that
collapse several members) are dropped.

Usage: python formation_window.py
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


def ols(y, X, names):
    n, k = len(y), len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
           for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    A = [row[:] for row in XtX]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        I[c], I[p] = I[p], I[c]
        d = A[c][c]
        if abs(d) < 1e-12:
            return None
        A[c] = [v / d for v in A[c]]
        I[c] = [v / d for v in I[c]]
        for r in range(k):
            if r != c:
                f = A[r][c]
                A[r] = [A[r][j] - f * A[c][j] for j in range(k)]
                I[r] = [I[r][j] - f * I[c][j] for j in range(k)]
    beta = [sum(I[a][b] * Xty[b] for b in range(k)) for a in range(k)]
    resid = [y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(X[i][a] * X[i][b] * resid[i] ** 2 for i in range(n))
             for b in range(k)] for a in range(k)]
    sc = n / max(n - k, 1)
    V = [[sc * sum(I[a][p] * meat[p][q] * I[b][q]
                   for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0))) for j, nm in enumerate(names)}


def main():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    bios = json.load(open(os.path.join(_HERE, "provinces", "member_bios.json")))
    bio = {}
    for b in bios:
        key = (b.get("prov"), b.get("name"))
        # the collector marks unmatched rows by leaving identity fields null
        if not b.get("matched_name") and not b.get("wikidata_qid"):
            continue
        bio[key] = b

    # per (prov, member, year): words + style hits
    cell = defaultdict(lambda: [0, 0])
    for path in sorted(glob.glob(os.path.join(_HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            nm = norm(d.get("speaker", ""))
            if not nm or ROLE.match(nm):
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            c = cell[(d["prov"], nm, d["date"][:4])]
            c[0] += len(t)
            c[1] += sum(1 for x in t if x in style)

    # collapse duplicate printed forms of the same person via qid
    agg = defaultdict(lambda: [0, 0])
    meta = {}
    for (pv, nm, yr), (w, h) in cell.items():
        b = bio.get((pv, nm))
        if not b or not b.get("birth_year"):
            continue
        pid = b.get("wikidata_qid") or f"{pv}:{nm}"
        agg[(pv, pid, yr)][0] += w
        agg[(pv, pid, yr)][1] += h
        meta[(pv, pid)] = b

    rows = []
    for (pv, pid, yr), (w, h) in agg.items():
        if w < MIN_WORDS:
            continue
        b = meta[(pv, pid)]
        by = b["birth_year"]
        y = int(yr)
        if not (1925 <= by <= 2000) or not (18 <= y - by <= 85):
            continue
        rows.append({"prov": pv, "pid": pid, "year": y, "birth": by,
                     "rate": h / w * 1000, "words": w,
                     "occ": (b.get("occupation_category") or "unknown"),
                     "postsec": b.get("postsecondary_attested"),
                     "gender": b.get("gender") or "?"})
    if len(rows) < 200:
        raise SystemExit(f"only {len(rows)} member-years — check bio join")

    people = {(r["prov"], r["pid"]) for r in rows}
    print(f"{len(rows):,} member-years, {len(people):,} distinct people, "
          f"{len({r['prov'] for r in rows})} provinces")
    bys = sorted(r["birth"] for r in rows)
    print(f"birth years: {bys[0]}–{bys[-1]}, median {bys[len(bys)//2]}\n")

    print("Mean register rate by birth cohort (raw, all years pooled):")
    coh = defaultdict(lambda: [0, 0])
    for r in rows:
        d = coh[(r["birth"] // 10) * 10]
        d[0] += r["rate"] * r["words"]
        d[1] += r["words"]
    for c in sorted(coh):
        if coh[c][1] > 500_000:
            print(f"  born {c}s: {coh[c][0] / coh[c][1]:>6.2f} per 1,000 "
                  f"({coh[c][1] / 1e6:>5.1f}M words)")

    # within year x province: only the member's own cohort varies
    provs = sorted({r["prov"] for r in rows})[1:]
    years = sorted({r["year"] for r in rows})[1:]
    occs = sorted({r["occ"] for r in rows if r["occ"] != "unknown"})[1:]
    names = (["const", "birth_decade"] +
             [f"p_{p}" for p in provs] + [f"y_{y}" for y in years])
    X, Y = [], []
    for r in rows:
        X.append([1.0, (r["birth"] - 1955) / 10.0] +
                 [1.0 if r["prov"] == p else 0.0 for p in provs] +
                 [1.0 if r["year"] == y else 0.0 for y in years])
        Y.append(r["rate"])
    fit = ols(Y, X, names)
    b, se = fit["birth_decade"]
    print(f"\nPRIMARY — register rate on birth decade, province and year fixed:")
    print(f"  birth_decade {b:+.4f} per 1,000 words per decade later "
          f"(se {se:.4f}, t {b / se:+.2f})"
          f"{' *' if abs(b / se) > 1.96 else ''}")

    # add occupation and education
    names2 = names + [f"occ_{o}" for o in occs] + ["postsec"]
    X2 = []
    for i, r in enumerate(rows):
        X2.append(X[i] + [1.0 if r["occ"] == o else 0.0 for o in occs] +
                  [1.0 if r["postsec"] else 0.0])
    fit2 = ols(Y, X2, names2)
    if fit2:
        b2, se2 = fit2["birth_decade"]
        print(f"\nWITH occupation category and post-secondary:")
        print(f"  birth_decade {b2:+.4f} (se {se2:.4f}, t {b2 / se2:+.2f})"
              f"{' *' if abs(b2 / se2) > 1.96 else ''}")
        ps, pse = fit2["postsec"]
        print(f"  postsecondary {ps:+.4f} (se {pse:.4f}, t {ps / pse:+.2f})")
        sig = [(n, fit2[n]) for n in names2 if n.startswith("occ_")
               and abs(fit2[n][0] / (fit2[n][1] or 1)) > 1.96]
        if sig:
            print("  occupation categories differing from baseline:")
            for n, (bb, ss) in sorted(sig, key=lambda x: -abs(x[1][0]))[:6]:
                print(f"    {n[4:]:<28s} {bb:+.3f} (t {bb / ss:+.2f})")
        else:
            print("  no occupation category differs significantly from baseline")

    print("\nReading: a positive birth_decade coefficient means later-born")
    print("members speak more of this register in the SAME year and chamber —")
    print("the formation/cohort account. If it survives adding occupation and")
    print("education, selection on background is not what is driving it.")


if __name__ == "__main__":
    main()
