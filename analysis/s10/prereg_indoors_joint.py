#!/usr/bin/env python3
"""Indoors in the joint model: how much does the office cut add?

Matthew's question (2026-08-24): Indoors is the strongest single occupational
correlate — how much explanatory power does it add to the JOINT model? This
mirrors prereg_covariate_strength.py exactly (same row filter, same blocks,
same HC1) and extends its grand model (ii) — birth decade + EGP + education +
prominence + dir_middle + apex delta — with the Indoors z. Reports the
in-model slope, the adjR2 gained when added, and "adjR2 lost if dropped"
alongside every other block, so the office cut ranks directly against the
existing covariates. Writes prereg_indoors_joint.txt.
"""
import csv, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V30 = "/tmp/onet303/db_30_3_text"
IND = "4.C.2.a.1.a"
EGP = ["I", "II", "IIIab", "IVab", "IVc", "V/VI", "VIIab"]

def hc1(y, X):
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    n, k = X.shape
    V = XtXi @ (X * (e**2)[:, None]).T @ X @ XtXi * (n / (n - k))
    rss = float(e @ e); tss = float(((y - y.mean())**2).sum())
    return b, V, 1 - (rss/(n-k))/(tss/(n-1))

val = {}
with open(os.path.join(V30, "Work Context.txt"), encoding="utf-8", errors="replace") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        if r["Element ID"] == IND and r["Scale ID"] in {"CX", "CT"}:
            val[r["O*NET-SOC Code"]] = float(r["Data Value"])

tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
rows = [r for r in tab if r.get("z") is not None and "comp_U" in r
        and r.get("bd") is not None and r.get("egp") in EGP
        and r.get("edu") and r.get("logdepth") is not None
        and r.get("soc") in val]
edus = sorted({r["edu"] for r in rows})
edus = [e for e in edus if sum(1 for r in rows if r["edu"] == e) >= 50]
rows = [r for r in rows if r["edu"] in edus]
y = np.array([r["z"] for r in rows]); n = len(rows)
print(f"panel n = {n} (covariate-strength panel intersected with Indoors coverage)")

def col_vals(v):
    v = np.asarray(v, float); return (v - v.mean()) / (v.std() or 1)
def col(key): return col_vals([r[key] for r in rows])

scal = {k: col(k) for k in ("bd", "logdepth", "apex_delta", "dir_middle")}
ind = col_vals([val[r["soc"]] for r in rows])
egps = [c for c in EGP if any(r["egp"] == c for r in rows)]
egp_b = [np.array([1.0 if r["egp"] == c else 0.0 for r in rows]) for c in egps[1:]]
edu_b = [np.array([1.0 if r["edu"] == e else 0.0 for r in rows]) for e in edus[1:]]
BLOCKS = {"birthdec": [scal["bd"]], "EGP class": egp_b, "education": edu_b,
          "prominence": [scal["logdepth"]], "dir middle": [scal["dir_middle"]],
          "apex delta": [scal["apex_delta"]]}

def grand(extra, drop=None):
    blocks = dict(BLOCKS); blocks.update(extra)
    cols, names = [np.ones(n)], ["const"]
    for k, vs in blocks.items():
        if k == drop: continue
        for i, v in enumerate(vs):
            cols.append(v); names.append(k if len(vs) == 1 else f"{k}#{i}")
    return hc1(y, np.column_stack(cols)), names

L = []
(b0, V0, adj0), _ = grand({})
L.append(f"grand model (ii), no Indoors:   adjR2 {adj0:.4f}   (n={n})")
(b1, V1, adj1), names = grand({"Indoors": [ind]})
i = names.index("Indoors")
L.append(f"grand model (ii) + Indoors:     adjR2 {adj1:.4f}   gain +{adj1-adj0:.4f}")
L.append(f"Indoors in-model: {b1[i]:+.3f} (t {b1[i]/math.sqrt(V1[i,i]):+.1f}) per sd")
L.append("")
L.append(f"{'block':<12s}{'in-model (strongest term)':>28s}{'adjR2 lost if dropped':>24s}")
for k in list(BLOCKS) + ["Indoors"]:
    (b2, V2, adj_d), _ = grand({"Indoors": [ind]}, drop=k)
    ii = [j for j, nm in enumerate(names) if nm.split("#")[0] == k]
    strongest = max(ii, key=lambda j: abs(b1[j]/math.sqrt(max(V1[j,j],1e-12))))
    cell = f"{b1[strongest]:+.3f} (t {b1[strongest]/math.sqrt(V1[strongest,strongest]):+.1f})"
    L.append(f"{k:<12s}{cell:>28s}{adj1-adj_d:>24.4f}")
print("\n".join(L))
open(os.path.join(HERE, "prereg_indoors_joint.txt"), "w").write(
    "prereg_indoors_joint.py -- run 2026-08-24\n\n" + "\n".join(L) + "\n")
print("\nwrote prereg_indoors_joint.txt")
