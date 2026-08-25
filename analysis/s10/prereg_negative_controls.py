#!/usr/bin/env python3
"""The prereg's registered negative-control check, run late and owed.

PREREG-occupational-accountability.md registered two deliberate negative
controls, planted in the pool "so their selection is interpretable":
  Spend Time Sitting                 4.C.2.d.1.a
  Indoors, Environmentally Controlled 4.C.2.a.1.a
with the registered interpretation rule: "If these predict as well as the
composite, the model has found 'office job' rather than anything about
language."

This was never run (2026-08-24 audit: no script referenced the codes). Run it
now, mirroring prereg_join's element pipeline (same file, same scales, z over
the same occupation set) and prereg_stage1's estimator (OLS, HC1 t):

  1. PARITY GUARD: reproduce stage-1's uncharged MIDDLE slope (+0.028, t 2.0)
     from the committed member table; abort if it does not reproduce.
  2. Each control alone; the two together (the "office job" model).
  3. The registered comparison: office-job fit vs the charged composite
     (U+L+D+N) and the uncharged levels (FREE..TOP), by adjR2 and AIC.
  4. Encompassing: does the instrument add beyond office-job, and vice versa.

Writes prereg_negative_controls.txt.
"""
import csv, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V30 = "/tmp/onet303/db_30_3_text"
SIT, IND = "4.C.2.d.1.a", "4.C.2.a.1.a"

def ols_hc1(y, X):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(x, float) for x in X])
    y = np.asarray(y, float)
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    n, k = X.shape
    meat = (X * (e**2)[:, None]).T @ X * (n / (n - k))
    V = XtXi @ meat @ XtXi
    t = b / np.sqrt(np.diag(V))
    rss = float(e @ e); tss = float(((y - y.mean())**2).sum())
    adjr2 = 1 - (rss/(n-k)) / (tss/(n-1))
    aic = n * math.log(rss / n) + 2 * k
    return b, t, adjr2, aic, n

# --- element values, mirroring prereg_join (Work Context, scales CX/CT) ---
val = {SIT: {}, IND: {}}
with open(os.path.join(V30, "Work Context.txt"), encoding="utf-8",
          errors="replace") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        if r["Element ID"] in val and r["Scale ID"] in {"CX", "CT"}:
            val[r["Element ID"]][r["O*NET-SOC Code"]] = float(r["Data Value"])
print(f"element coverage: Sitting {len(val[SIT])} SOCs, Indoors {len(val[IND])} SOCs")

tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
rows = [r for r in tab if "comp_U" in r and r.get("soc") in val[SIT]
        and r.get("soc") in val[IND]]
print(f"members with instrument + both controls: {len(rows)} "
      f"(instrumented total: {sum(1 for r in tab if 'comp_U' in r)})")

# z-score controls over the occupations present in the joined member set
occ = sorted({r["soc"] for r in rows})
def zmap(e):
    xs = [val[e][o] for o in occ]
    m, s = np.mean(xs), np.std(xs) or 1
    return {o: (val[e][o] - m) / s for o in occ}
Zs, Zi = zmap(SIT), zmap(IND)
for r in rows:
    r["ctl_sit"], r["ctl_ind"] = Zs[r["soc"]], Zi[r["soc"]]

y = [r["z"] for r in rows]
def col(k):
    xs = np.asarray([r[k] for r in rows], float)
    sd = xs.std() or 1
    return ((xs - xs.mean()) / sd).tolist()

L = []
def rep(name, keys):
    b, t, ar2, aic, n = ols_hc1(y, [col(k) for k in keys])
    parts = "  ".join(f"{k} {b[i+1]:+.3f} (t {t[i+1]:+.1f})" for i, k in enumerate(keys))
    line = f"{name:34s} n={n}  adjR2 {ar2:.4f}  AIC {aic:+.1f}   {parts}"
    print(line); L.append(line)
    return b, t, ar2, aic

# 1. parity guard
_, tg, _, _ = rep("PARITY: lvl_MIDDLE alone", ["lvl_MIDDLE"])
b_g, t_g, _, _, _ = ols_hc1(y, [col("lvl_MIDDLE")])
assert abs(b_g[1] - 0.028) < 0.01 and abs(t_g[1] - 2.0) < 0.3, \
    f"parity guard failed: {b_g[1]:+.3f} (t {t_g[1]:+.1f})"
L.append("parity: reproduces stage-1 uncharged MIDDLE (+0.028, t 2.0) -> estimator matches")

# 2-3. the registered comparison
rep("control: Sitting alone", ["ctl_sit"])
rep("control: Indoors alone", ["ctl_ind"])
_, _, ar2_office, aic_office = rep("office-job: Sitting+Indoors", ["ctl_sit", "ctl_ind"])
_, _, ar2_chg, aic_chg = rep("charged composite U+L+D+N", ["comp_U", "comp_L", "comp_D", "comp_N"])
_, _, ar2_lvl, aic_lvl = rep("uncharged FREE+BOT+MID+TOP",
                             ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"])
rep("apex delta alone", ["apex_delta"])

# 4. encompassing
KEYS_I = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]
b1, t1, ar2_both, _ = rep("levels + office-job", KEYS_I + ["ctl_sit", "ctl_ind"])
L.append("")
verdict = ("CONTROLS DO NOT MATCH THE INSTRUMENT" if
           ar2_office < min(ar2_chg, ar2_lvl) else
           "CONTROLS MATCH OR BEAT THE INSTRUMENT -- 'office job' concern stands")
L.append(f"registered rule: office-job adjR2 {ar2_office:.4f} vs charged {ar2_chg:.4f} / "
         f"uncharged {ar2_lvl:.4f} -> {verdict}")
L.append(f"instrument beyond office-job: adjR2 {ar2_lvl:.4f} -> {ar2_both:.4f} with "
         f"controls added; level terms' t in joint model: "
         + "  ".join(f"{k} {t1[i+1]:+.1f}" for i, k in enumerate(KEYS_I)))
print("\n".join(L[-3:]))
open(os.path.join(HERE, "prereg_negative_controls.txt"), "w").write(
    "\n".join(["prereg_negative_controls.py -- registered check, run 2026-08-24", ""] + L) + "\n")
print("\nwrote prereg_negative_controls.txt")
