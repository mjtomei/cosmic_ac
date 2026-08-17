#!/usr/bin/env python3
"""Is the register gradient a ministerial-office artifact?

THE WORRY

Ministers read departmental text: more prepared, more formal, plausibly more of
this register. If later-born members were also likelier to hold office, the
birth-cohort gradient could be office rather than generation.

WHY THE PANEL CANNOT ANSWER IT DIRECTLY

Chambers differ in whether the record marks rank at all. UK Hansard prints
ministers under their own names (0.2% of speaker strings carry a rank marker),
so ministers sit in both groups and no split is possible. The Canadian
provinces print "Hon. <name>" (Ontario: 25.8%), so there the office years are
identifiable. This script therefore tests the provinces that mark rank, which
is the strongest available version of the check, not a universal one.

DESIGN

`formation_window.norm()` strips the honorific, so one member appears both with
and without it across a career (backbench -> ministry -> backbench). Each
(province, member, year) cell is split by whether its words were spoken under a
rank-marked form, giving an office-year flag rather than an office-member flag.
The birth gradient is then re-estimated on non-office member-years only. If the
gradient survives there, office is not carrying it.

Usage: python office_split.py
"""
import glob
import json
import math
import os
import re
from collections import defaultdict

import formation_window as FW

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_RE = re.compile(r"[a-z']+")
RANK_RE = re.compile(
    r"^\s*(the\s+)?(l')?(rt\.?\s+|right\s+)?hon(ourable|orable|\.|\b)|"
    r"^\s*(premier|minister|attorney general|speaker|president of the)",
    re.I)
MIN_CELL_WORDS = 2000
# provinces whose record marks rank; Australian/UK-devolved files are excluded
# because their speaker strings do not carry it (verified by sampling).
MARKING = ("ab", "bc", "mb", "nl", "ns", "on", "pe", "sk")


def main():
    style = {r["word"].lower() for r in
             __import__("csv").DictReader(
                 open(os.path.join(HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    bios = {}
    for b in json.load(open(os.path.join(HERE, "provinces",
                                         "member_bios.json"))):
        if b.get("birth_year") and b.get("prov") and b.get("name"):
            bios[(b["prov"], FW.norm(b["name"]))] = int(b["birth_year"])

    # (prov, member, year, office_flag) -> [words, hits]
    cell = defaultdict(lambda: [0, 0])
    files = [p for p in sorted(glob.glob(os.path.join(HERE, "provinces",
                                                      "segments_*.jsonl")))
             if os.path.basename(p).split("_", 1)[1].split(".")[0]
             .replace("_fill", "") in MARKING]
    print(f"reading {len(files)} rank-marking province files")
    for path in files:
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            raw = d.get("speaker") or ""
            nm = FW.norm(raw)
            if not nm:
                continue
            office = bool(RANK_RE.match(raw))
            t = TOKEN_RE.findall(d["text"].lower())
            c = cell[(d["prov"], nm, d["date"][:4], office)]
            c[0] += len(t)
            c[1] += sum(1 for w in t if w in style)

    rows = []
    for (pv, nm, yr, office), (w, h) in cell.items():
        if w < MIN_CELL_WORDS:
            continue
        b = bios.get((pv, nm))
        if not b:
            continue
        rows.append({"prov": pv, "year": int(yr), "birth": b, "office": office,
                     "rate": h / w * 1000, "words": w})
    off = [r for r in rows if r["office"]]
    non = [r for r in rows if not r["office"]]
    print(f"\nmember-year cells with a birth year: {len(rows):,}")
    print(f"  office-marked: {len(off):,} "
          f"({sum(r['words'] for r in off)/1e6:.1f}M words)")
    print(f"  non-office:    {len(non):,} "
          f"({sum(r['words'] for r in non)/1e6:.1f}M words)")
    if off:
        wo = sum(r["rate"] * r["words"] for r in off) / sum(r["words"] for r in off)
        wn = sum(r["rate"] * r["words"] for r in non) / sum(r["words"] for r in non)
        print(f"\n  raw register rate: office {wo:.2f} vs non-office {wn:.2f} "
              f"per 1,000  (difference {wo-wn:+.2f})")

    print("\nbirth gradient (rate ~ birth + spoken, province FE, word-weighted):")
    for label, sub in (("all cells", rows), ("NON-OFFICE only", non),
                       ("office only", off)):
        _fit(sub, label)


def _fit(sub, label):
    if len(sub) < 300:
        print(f"  {label:<18s} too few cells ({len(sub)})")
        return
    provs = sorted({r["prov"] for r in sub})[1:]
    X, Y, W = [], [], []
    for r in sub:
        X.append([1.0, (r["birth"] - 1955) / 10.0, (r["year"] - 2015) / 10.0] +
                 [1.0 if r["prov"] == p else 0.0 for p in provs])
        Y.append(r["rate"])
        W.append(r["words"])
    names = ["const", "birth", "spoken"] + [f"p_{p}" for p in provs]
    f = _wls(Y, X, names, W)
    if not f:
        print(f"  {label:<18s} singular")
        return
    b, se = f["birth"]
    s, sse = f["spoken"]
    print(f"  {label:<18s} n={len(sub):>6,}  birth {b:+.3f}/decade "
          f"(t {b/se:+.2f})   spoken {s:+.3f} (t {s/sse:+.2f})")


def _wls(y, X, names, w):
    n, k = len(y), len(X[0])
    A = [[sum(w[i] * X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
         for a in range(k)]
    v = [sum(w[i] * X[i][a] * y[i] for i in range(n)) for a in range(k)]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    M = [r[:] for r in A]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        I[c], I[p] = I[p], I[c]
        d = M[c][c]
        if abs(d) < 1e-12:
            return None
        M[c] = [x / d for x in M[c]]
        I[c] = [x / d for x in I[c]]
        for r in range(k):
            if r != c:
                fct = M[r][c]
                M[r] = [M[r][j] - fct * M[c][j] for j in range(k)]
                I[r] = [I[r][j] - fct * I[c][j] for j in range(k)]
    beta = [sum(I[a][b] * v[b] for b in range(k)) for a in range(k)]
    res = [y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(w[i] ** 2 * X[i][a] * X[i][b] * res[i] ** 2 for i in range(n))
             for b in range(k)] for a in range(k)]
    V = [[sum(I[a][p] * meat[p][q] * I[b][q]
              for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0)))
            for j, nm in enumerate(names)}


if __name__ == "__main__":
    main()
