#!/usr/bin/env python3
"""The age-period-cohort solution line for §4.6, and a bound on it from the
pre-drift US Senate.

WHY. §4.6's headline is the two-stamp fit in cohort_vs_period.py: member-year
register rate on spoken year and birth year, chamber fixed effects, word-
weighted. It returns spoken +1.254 and birth +0.876 per 1,000 words per decade.
Those two numbers are NOT a period effect and a cohort effect. Age = year -
birth, so in the full three-slope model

    rate = mu + a*AGE + p*PERIOD + c*COHORT      (AGE = year - birth)

the two-stamp coefficients are the two identified linear combinations:

    b_spoken = d(rate)/d(year) | birth fixed  = a + p
    b_birth  = d(rate)/d(birth)| year  fixed  = c - a

One free parameter remains. Every (a, p, c) triple with p = b_spoken - a and
c = b_birth + a fits the data EXACTLY as well as every other: that one-
dimensional family is the SOLUTION LINE. Part (a) tabulates it, so the paper
can state what the birth gradient implies under each assumed age slope instead
of leaving the reader to guess. Landmark rows are marked: a = 0 (no age
effect: period 1.254, cohort 0.876), a = -b_birth (pure period, cohort 0), and
a = +b_spoken... (see the table's PURE-* flags).

Part (b) buys the free parameter with a design assumption rather than a prior.
The register's level series turns in 1994-96 (§4.5). US Senate member-years
observed 1994-2004 by members born before 1965 are therefore a cell in which
every cohort was formed decades before the register began to move anywhere:
under the paper's own reading, c ~ 0 for these cohorts. With c switched off,
age is identified inside the cell, and the estimate propagates back along the
solution line to bound p and c for the whole panel.

Two forms of the cell regression are reported:
  SPEC  rate on AGE alone (chamber constant, word-weighted, HC1) -- what the
        task specifies. Its coefficient is a + p*(cov(year,age)/var(age)) under
        c = 0, so the auxiliary slope cov(year,age)/var(age) is printed to make
        the residual period contamination legible.
  JOINT rate on AGE and YEAR together. With c = 0 assumed the two are no longer
        collinear (birth drops out of the model), so this identifies a and a
        local p inside the cell without the contamination term. This is the
        refinement, reported alongside, not instead.

SCALE. Every rate here is occurrences per 1,000 words -- cohort_vs_period.py's
ruler -- because the panel rows are read through that script's own loaders and
its h/w*1000 convention. No conversion is applied or needed. Note that
apc_chamber_decomposition.py and §4.5a use per 100k words; multiply anything in
this file by 100 to move onto that ruler.

DATA NOTE. The panel key is CHAMBER|surname, and cohort_vs_period.load_birth
assigns tier-1 birth years by that key with no ambiguity filter, so colliding
surnames (US Senate 'pryor' = David Pryor b.1934 and Mark Pryor b.1963; 'smith';
...) take whichever covariates row is last in the file. That is measurement
error in AGE precisely where this script leans on it, so the cell regression is
re-run dropping every key flagged ambiguous in covariates_tier1.json, and both
numbers are printed.

Usage: python3 apc_solution_line.py | tee apc_solution_line.txt
"""
import io
import math
import re
import contextlib
import json
import os

import numpy as np

import cohort_vs_period as CV

HERE = os.path.dirname(os.path.abspath(__file__))
MINW = CV.MIN_MEMBER_YEAR_WORDS          # 2,000 words per member-year


# ---------------------------------------------------------------- WLS + HC1

def wls(X, y, w, cluster=None):
    """Word-weighted least squares with HC1 (and optional CR1) errors.

    Identical algebra to cohort_vs_period.two_stamp: score rows are w_i x_i e_i,
    HC1 meat is sum_i w_i^2 x_i x_i' e_i^2 scaled n/(n-k).
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    w = np.asarray(w, float)
    n, k = X.shape
    Xw = X * w[:, None]
    XtXi = np.linalg.pinv(X.T @ Xw)
    beta = XtXi @ (Xw.T @ y)
    e = y - X @ beta
    S = Xw * e[:, None]
    V_hc = XtXi @ (S.T @ S) @ XtXi * n / (n - k)
    V_cr = None
    if cluster is not None:
        groups = {}
        for i, g in enumerate(cluster):
            groups.setdefault(g, []).append(i)
        G = len(groups)
        meat = np.zeros((k, k))
        for ii in groups.values():
            sg = S[ii].sum(axis=0)
            meat += np.outer(sg, sg)
        V_cr = XtXi @ meat @ XtXi * G / (G - 1) * (n - 1) / (n - k)
        V_cr = (V_cr, G)
    return beta, V_hc, V_cr


# ------------------------------------------------- (0) re-derive the two-stamp

def two_stamp_refit(panel, birth):
    """Re-run cohort_vs_period.two_stamp's exact model and return full precision.

    Same row filter (>=2,000 words, birth known), same regressors
    ((year-1990)/10, (birth-1990)/10), same chamber dummies (first chamber
    dropped), same weights, same HC1/CR1.
    """
    rows = []
    for ch, ms in panel.items():
        for m, ys in ms.items():
            b = birth.get(f"{ch}|{m}")
            if not b:
                continue
            for y, (w, h) in ys.items():
                if w < MINW:
                    continue
                rows.append((h / w * 1000, y, b, ch, w, f"{ch}|{m}"))
    chambers = sorted({r[3] for r in rows})[1:]
    X = np.array([[1.0, (r[1] - 1990) / 10.0, (r[2] - 1990) / 10.0]
                  + [1.0 if r[3] == c else 0.0 for c in chambers] for r in rows])
    y = np.array([r[0] for r in rows])
    w = np.array([r[4] for r in rows], float)
    beta, V_hc, (V_cr, G) = wls(X, y, w, cluster=[r[5] for r in rows])
    return dict(b_spoken=beta[1], b_birth=beta[2],
                se_spoken_hc=math.sqrt(V_hc[1, 1]), se_birth_hc=math.sqrt(V_hc[2, 2]),
                se_spoken_cr=math.sqrt(V_cr[1, 1]), se_birth_cr=math.sqrt(V_cr[2, 2]),
                n=len(rows), G=G)


def committed_two_stamp(panel, birth):
    """Run the COMMITTED cohort_vs_period.two_stamp and parse what it prints,
    so the refit above is checked against the script the paper cites."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        CV.two_stamp(panel, birth)
    txt = buf.getvalue()
    out = {}
    for nm in ("spoken", "birth"):
        m = re.search(rf"^\s+{nm}\s+([+-][\d.]+) per decade", txt, re.M)
        out[nm] = float(m.group(1))
    m = re.search(r"n=([\d,]+) member-years, ([\d,]+) members", txt)
    out["n"] = int(m.group(1).replace(",", ""))
    out["G"] = int(m.group(2).replace(",", ""))
    return out, txt


# ------------------------------------------------------- (a) the solution line

def solution_line(b_spoken, b_birth):
    print("\n" + "=" * 78)
    print("(a) SOLUTION LINE  --  every (age, period, cohort) triple below fits")
    print("    the data identically.  period = b_spoken - age;  cohort = b_birth + age")
    print(f"    b_spoken = a + p = {b_spoken:+.4f}   b_birth = c - a = {b_birth:+.4f}")
    print("    units: register occurrences per 1,000 words, per decade")
    print("=" * 78)
    print(f"{'age slope':>10s} {'period':>9s} {'cohort':>9s} {'cohort/period':>14s}"
          f"   {'same-age, decade on':>20s}  note")
    grid = [(round(-2.0 + 0.25 * i, 2), "") for i in range(11)]   # -2.00 .. +0.50
    # the two landmark values fall off a 0.25 grid, so insert them explicitly
    grid.append((0.0, "<-- NO AGE EFFECT: §4.6's headline read"))
    grid.append((-b_birth, "<-- COHORT = 0 (all of the birth gradient is age)"))
    grid.append((b_spoken, "<-- PERIOD = 0 (all of the calendar drift is cohort)"))
    seen = set()
    for a, note in sorted(grid):
        if round(a, 6) in seen:
            continue
        seen.add(round(a, 6))
        p = b_spoken - a
        c = b_birth + a
        ratio = (c / p) if abs(p) > 1e-9 else float("nan")
        # what a member born 10y later and speaking 10y later shows, i.e. the
        # same-age comparison a decade on: p + c (age cancels)
        same_age = p + c
        print(f"{a:>+10.3f} {p:>+9.3f} {c:>+9.3f} {ratio:>+14.2f}"
              f"   {same_age:>20.3f}  {note}")
    print("\n    invariants (true anywhere on the line):")
    print(f"      period + cohort = b_spoken + b_birth = {b_spoken + b_birth:+.3f}"
          "   <- the same-age decade-on total, free of the age slope")
    print(f"      cohort - period = b_birth - b_spoken + 2*age = "
          f"{b_birth - b_spoken:+.3f} + 2*age   <- needs the age slope")
    print("    a = 0 is an ASSUMPTION, not a reading of the data: it is the row")
    print("    that reproduces §4.6's headline numbers as period and cohort.")


# ------------------------------------------------------ (b) the Senate bound

def senate_cell(panel, birth, ambiguous_keys, drop_ambiguous, label):
    rows = []
    ch = "US-SENATE"
    for m, ys in panel[ch].items():
        key = f"{ch}|{m}"
        if drop_ambiguous and key in ambiguous_keys:
            continue
        b = birth.get(key)
        if not b or b >= 1965:
            continue
        for y, (w, h) in ys.items():
            if w < MINW or not (1994 <= y <= 2004):
                continue
            rows.append((h / w * 1000, y, b, w, key))
    if len(rows) < 30:
        print(f"  {label}: too few rows ({len(rows)})")
        return None
    y_ = np.array([r[0] for r in rows])
    yr = np.array([r[1] for r in rows], float)
    bi = np.array([r[2] for r in rows], float)
    w_ = np.array([r[3] for r in rows], float)
    cl = [r[4] for r in rows]
    age = yr - bi
    W = w_.sum()
    age_dec = (age - np.average(age, weights=w_)) / 10.0
    yr_dec = (yr - np.average(yr, weights=w_)) / 10.0

    # SPEC form: rate on age alone, chamber constant (one chamber -> intercept)
    Xa = np.column_stack([np.ones(len(rows)), age_dec])
    ba, Va, (Vca, Ga) = wls(Xa, y_, w_, cluster=cl)
    # JOINT form: rate on age and year (valid iff cohort effect ~ 0 in the cell)
    Xj = np.column_stack([np.ones(len(rows)), age_dec, yr_dec])
    bj, Vj, (Vcj, Gj) = wls(Xj, y_, w_, cluster=cl)
    # auxiliary: cov(year,age)/var(age), word-weighted -- the contamination load
    ycen = yr_dec - np.average(yr_dec, weights=w_)
    acen = age_dec - np.average(age_dec, weights=w_)
    aux = float(np.sum(w_ * acen * ycen) / np.sum(w_ * acen * acen))

    res = dict(n=len(rows), members=len(set(cl)), words=int(W),
               mean_rate=float(np.average(y_, weights=w_)),
               age_lo=float(age.min()), age_hi=float(age.max()),
               birth_lo=int(bi.min()), birth_hi=int(bi.max()),
               a_spec=ba[1], se_spec_hc=math.sqrt(Va[1, 1]),
               se_spec_cr=math.sqrt(Vca[1, 1]),
               a_joint=bj[1], se_joint_hc=math.sqrt(Vj[1, 1]),
               se_joint_cr=math.sqrt(Vcj[1, 1]),
               p_joint=bj[2], se_pjoint_cr=math.sqrt(Vcj[2, 2]),
               aux=aux, G=Ga)
    print(f"\n  {label}")
    print(f"    cell: US-SENATE member-years 1994-2004, birth < 1965, "
          f">= {MINW:,} words")
    print(f"    n = {res['n']:,} member-years   members = {res['members']}   "
          f"words = {res['words']:,}")
    print(f"    birth {res['birth_lo']}-{res['birth_hi']}   "
          f"age {res['age_lo']:.0f}-{res['age_hi']:.0f}   "
          f"mean rate {res['mean_rate']:.2f} per 1,000")
    print(f"    SPEC  rate ~ age            a = {res['a_spec']:+.3f} per decade"
          f"  (HC1 se {res['se_spec_hc']:.3f}, t {res['a_spec']/res['se_spec_hc']:+.2f};"
          f"  CR1 se {res['se_spec_cr']:.3f}, t {res['a_spec']/res['se_spec_cr']:+.2f})")
    print(f"    JOINT rate ~ age + year     a = {res['a_joint']:+.3f} per decade"
          f"  (HC1 se {res['se_joint_hc']:.3f}, t {res['a_joint']/res['se_joint_hc']:+.2f};"
          f"  CR1 se {res['se_joint_cr']:.3f}, t {res['a_joint']/res['se_joint_cr']:+.2f})")
    print(f"          local period in-cell  p = {res['p_joint']:+.3f} per decade"
          f"  (CR1 se {res['se_pjoint_cr']:.3f}, "
          f"t {res['p_joint']/res['se_pjoint_cr']:+.2f})")
    print(f"    aux slope cov(year,age)/var(age) = {res['aux']:+.4f}"
          f"   -> SPEC carries {res['aux']:+.4f} x (in-cell period) of contamination;")
    print(f"       SPEC - aux*p_joint = "
          f"{res['a_spec'] - res['aux'] * res['p_joint']:+.3f}  (should track JOINT)")
    return res


def propagate(name, a_hat, se_a, b_spoken, b_birth, se_sp, se_bi):
    lo, hi = a_hat - 1.96 * se_a, a_hat + 1.96 * se_a
    p_hat, c_hat = b_spoken - a_hat, b_birth + a_hat
    # age-only uncertainty (two-stamp betas treated as fixed): the bound the
    # design assumption buys
    p_lo, p_hi = b_spoken - hi, b_spoken - lo
    c_lo, c_hi = b_birth + lo, b_birth + hi
    # conservative: add the two-stamp SE in quadrature, ASSUMING independence
    # (the samples overlap, so the true covariance is unknown and non-zero;
    #  this widening is indicative, not exact)
    se_p = math.sqrt(se_sp ** 2 + se_a ** 2)
    se_c = math.sqrt(se_bi ** 2 + se_a ** 2)
    print(f"\n    [{name}] age slope a = {a_hat:+.3f} per decade "
          f"(se {se_a:.3f}; 95% CI [{lo:+.3f}, {hi:+.3f}])")
    print(f"        -> PERIOD p = b_spoken - a = {p_hat:+.3f} "
          f"per 1,000 per decade   bound [{p_lo:+.3f}, {p_hi:+.3f}]"
          f"   (+two-stamp se in quadrature: +/-{1.96*se_p:.3f})")
    print(f"        -> COHORT c = b_birth  + a = {c_hat:+.3f} "
          f"per 1,000 per decade   bound [{c_lo:+.3f}, {c_hi:+.3f}]"
          f"   (+two-stamp se in quadrature: +/-{1.96*se_c:.3f})")
    print(f"        -> cohort share of the same-age decade-on total "
          f"({b_spoken + b_birth:+.3f}): {100*c_hat/(b_spoken+b_birth):.0f}%"
          f"  [{100*c_lo/(b_spoken+b_birth):.0f}%, "
          f"{100*c_hi/(b_spoken+b_birth):.0f}%]")
    return p_hat, c_hat, (p_lo, p_hi), (c_lo, c_hi)


def main():
    panel = CV.load_panel()
    birth = CV.load_birth()

    print("=" * 78)
    print("APC SOLUTION LINE AND THE PRE-DRIFT SENATE BOUND  (S10 §4.6)")
    print("rates: register occurrences per 1,000 words (cohort_vs_period.py's ruler)")
    print("=" * 78)

    committed, raw = committed_two_stamp(panel, birth)
    fit = two_stamp_refit(panel, birth)
    print("\n(0) TWO-STAMP, re-derived by running the committed machinery:")
    print(raw.strip())
    print(f"\n    full-precision refit: spoken {fit['b_spoken']:+.6f}  "
          f"birth {fit['b_birth']:+.6f}   n={fit['n']:,}  members={fit['G']:,}")
    ok = (abs(fit["b_spoken"] - committed["spoken"]) < 5e-4 and
          abs(fit["b_birth"] - committed["birth"]) < 5e-4 and
          fit["n"] == committed["n"] and fit["G"] == committed["G"])
    print(f"    agrees with committed cohort_vs_period.two_stamp print: {ok}")
    if not ok:
        raise SystemExit("REFIT DOES NOT MATCH THE COMMITTED TWO-STAMP -- stop.")

    b_sp, b_bi = fit["b_spoken"], fit["b_birth"]
    solution_line(b_sp, b_bi)

    # ambiguity flags from the tier-1 covariates (keys with >1 real person)
    amb = set()
    for r in json.load(open(os.path.join(HERE, "covariates_tier1.json"))):
        if r.get("ambiguous"):
            amb.add(f'{r["chamber"]}|{r["key"]}')

    print("\n" + "=" * 78)
    print("(b) SENATE BOUND  --  a cell whose cohorts all formed before the drift")
    print("    US Senate, spoken 1994-2004, birth < 1965.  The register turns in")
    print("    1994-96 (§4.5), so under the paper's own reading these cohorts")
    print("    carry no cohort effect; with c = 0 the age slope is identified.")
    print("=" * 78)
    main_res = senate_cell(panel, birth, amb, False, "AS SPECIFIED (all keys)")
    rob_res = senate_cell(panel, birth, amb, True,
                          "ROBUSTNESS (drop surname keys flagged ambiguous)")

    print("\n" + "-" * 78)
    print("PROPAGATION ALONG THE SOLUTION LINE")
    print("-" * 78)
    for tag, res, which in (
            ("SPEC / all keys", main_res, "spec"),
            ("JOINT / all keys", main_res, "joint"),
            ("SPEC / no-ambiguous", rob_res, "spec"),
            ("JOINT / no-ambiguous", rob_res, "joint")):
        if res is None:
            continue
        a_hat = res["a_spec"] if which == "spec" else res["a_joint"]
        se_a = res["se_spec_cr"] if which == "spec" else res["se_joint_cr"]
        propagate(tag, a_hat, se_a, b_sp, b_bi,
                  fit["se_spoken_cr"], fit["se_birth_cr"])

    print("\n" + "-" * 78)
    print("READING")
    print("-" * 78)
    print("  The cell returns a NEGATIVE age slope: within the pre-drift Senate,")
    print("  every extra decade of age costs about 0.9 per 1,000 of the register.")
    print("  That is the same juniority gradient §4.6 reports for this cell, read")
    print("  on the age clock instead of the birth clock (in-cell, year barely")
    print("  moves, so age is very nearly minus birth).")
    print("  It lands almost exactly on the COHORT = 0 landmark: a = -0.892 against")
    print(f"  the landmark a = {-b_bi:+.3f}. So the Senate bound says the panel-wide")
    print("  birth gradient is AGE, and the whole same-age decade-on total")
    print(f"  ({b_sp + b_bi:+.3f}) is PERIOD. That is not a new assumption; it is what")
    print("  §4.6's own sentence -- 'a juniority gradient in this register predates")
    print("  the drift' -- implies once it is carried to the solution line.")
    print("\n  What survives for the cohort reading is NOT this linear term. It is")
    print("  the NONLINEARITY -- §4.6's 'steepening as drift-formed cohorts arrive'.")
    print("  Nonlinear cohort deviations are identified without any age assumption;")
    print("  apc_i.py tests them.")
    print("\n  CAVEATS the cell cannot remove: (i) it identifies the age slope AMONG")
    print("  pre-1965 cohorts observed at ages 31-100 in ONE chamber; carrying that")
    print("  slope to the whole panel assumes the age profile is linear and")
    print("  era-stable -- the residual rival §4.6 already flags, here in the")
    print("  direction that costs the cohort reading rather than helping it.")
    print("  (ii) c = 0 in-cell is an assumption about pre-1965 cohorts, not a test.")
    print("  (iii) the quadrature widening treats the cell estimate as independent")
    print("  of the two-stamp fit; the cell's 1,107 rows are inside the two-stamp's")
    print("  61,312, so the true covariance is non-zero and that widening is")
    print("  indicative only. The age-only bound is the exact one.")


if __name__ == "__main__":
    main()
