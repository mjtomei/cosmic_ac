#!/usr/bin/env python3
"""Cohort vs period vs generation: which time-stamp does the register track?

Replaces two earlier, weaker cohort measures (the one-shot 2006-10 vs 2015-19
decomposition premium, and the rolling new-vs-incumbent arrival premium). Each
member-year of legislative speech carries three time-stamps:

  spoken year   when the words were said            -> PERIOD (calendar drift)
  entry year    the speaker's first year sitting     -> COHORT (set at entry)
  birth year    when the speaker was born            -> GENERATION (formation)

If the register is a period effect, everyone drifts up together and spoken year
organises it. If it is a cohort effect, later-entering intakes arrive higher and
entry year organises it even holding the calendar fixed. Birth year is the
formation account, distinct from entry (a member can be old and new, or young
and long-serving).

MEASURE. Within each chamber (so chamber baselines never mix), the word-weighted
correlation of the member-year rate with each stamp, and an APC-style regression
putting spoken against entry (and birth) together so period and cohort are read
net of each other. Reported per chamber and pooled (mean of within-chamber
statistics).

LEFT-CENSORING. A member already sitting in a chamber's first covered year has an
unknown true entry year; those members are dropped for the entry-year stamp
(count reported). Provinces begin 2006, tier-1 chambers 1985.

Usage: python cohort_vs_period.py [--censor 1]
"""
import argparse
import json
import math
import os
import statistics
from collections import defaultdict

import formation_window as FW   # reuse norm() for province name matching

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_MEMBER_YEAR_WORDS = 2000


def load_panel():
    panel = defaultdict(lambda: defaultdict(dict))  # ch -> member -> year -> [w,h]
    for f in ("member_year_rates.json", "member_year_rates_t1.json"):
        for k, v in json.load(open(os.path.join(HERE, f))).items():
            ch, member, yr = k.rsplit("|", 2)
            panel[ch][member][int(yr)] = v
    return panel


def load_birth():
    birth = {}
    # tier-1: covariates_tier1.json keyed (chamber, key); panel member is CH|key
    for r in json.load(open(os.path.join(HERE, "covariates_tier1.json"))):
        if r.get("birth_year"):
            birth[f'{r["chamber"]}|{r["key"]}'] = int(r["birth_year"])
    # provinces: member_bios.json keyed (prov, norm(name)); panel member is PROV|nm
    for b in json.load(open(os.path.join(HERE, "provinces", "member_bios.json"))):
        if b.get("birth_year") and b.get("prov") and b.get("name"):
            birth.setdefault(f'{b["prov"]}|{FW.norm(b["name"])}',
                             int(b["birth_year"]))
    return birth


def wcorr(xyw):
    """word-weighted Pearson r between x and rate, and weighted slope."""
    W = sum(w for _, _, w in xyw)
    if W == 0:
        return None, None, 0
    mx = sum(x * w for x, _, w in xyw) / W
    my = sum(y * w for _, y, w in xyw) / W
    sxy = sum(w * (x - mx) * (y - my) for x, y, w in xyw)
    sxx = sum(w * (x - mx) ** 2 for x, _, w in xyw)
    syy = sum(w * (y - my) ** 2 for _, y, w in xyw)
    if sxx == 0 or syy == 0:
        return None, None, W
    return sxy / math.sqrt(sxx * syy), sxy / sxx, W


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--censor", type=int, default=1,
                    help="drop members entering within this many years of the "
                         "chamber's first covered year (unknown true entry)")
    a = ap.parse_args()
    panel = load_panel()
    birth = load_birth()

    print(f"{'chamber':<10s} {'obs':>6s} {'r_spoken':>9s} {'r_entry':>9s} "
          f"{'r_birth':>9s}   {'nbirth':>6s}")
    agg = defaultdict(list)   # stamp -> list of (chamber r, weight=n_members)
    reg_rows = []             # pooled APC rows: (rate, spoken, entry, birth, ch)
    censored_total = 0
    for ch in sorted(panel):
        first = min(y for m in panel[ch].values() for y in m)
        entry = {m: min(ys) for m, ys in panel[ch].items()}
        sp, en, bi = [], [], []
        for m, ys in panel[ch].items():
            e = entry[m]
            b = birth.get(f"{ch}|{m}")
            for y, (w, h) in ys.items():
                if w < MIN_MEMBER_YEAR_WORDS:
                    continue
                r = h / w * 1000
                sp.append((y, r, w))
                if e > first + (a.censor - 1):        # entry known
                    en.append((e, r, w))
                    reg_rows.append((r, y, e, b, ch, w))
                if b:
                    bi.append((b, r, w))
        censored_total += sum(1 for m in panel[ch] if entry[m] <= first + a.censor - 1)
        rs, _, _ = wcorr(sp)
        re, _, _ = wcorr(en)
        rb, _, _ = wcorr(bi) if bi else (None, None, 0)
        n = len(panel[ch])
        if rs is None:
            continue
        agg["spoken"].append((rs, n))
        if re is not None:
            agg["entry"].append((re, n))
        if rb is not None:
            agg["birth"].append((rb, n))
        print(f"{ch:<10s} {len(sp):>6d} {rs:>+9.3f} "
              f"{(f'{re:+.3f}' if re is not None else 'n/a'):>9s} "
              f"{(f'{rb:+.3f}' if rb is not None else 'n/a'):>9s}   "
              f"{sum(1 for _ in bi):>6d}")

    print(f"\nmembers dropped to entry-year censoring (entry <= first+{a.censor-1}): "
          f"{censored_total}")

    def pooled(stamp):
        v = agg[stamp]
        if not v:
            return None
        W = sum(n for _, n in v)
        return sum(r * n for r, n in v) / W, len(v)

    print("\nPOOLED within-chamber correlation (member-weighted mean across chambers):")
    for s in ("spoken", "entry", "birth"):
        p = pooled(s)
        if p:
            print(f"  r_{s:<7s} = {p[0]:+.3f}   (over {p[1]} chambers)")

    # APC-style regression, chamber fixed effects, rate on the stamps together.
    # spoken, entry and tenure=spoken-entry are collinear, so only spoken+entry
    # go in as the period/cohort pair; birth enters as an independent 4th axis.
    print("\nAPC regression (chamber FE; period vs cohort net of each other):")
    _apc(reg_rows, ["spoken", "entry"], "period vs cohort")
    _apc([r for r in reg_rows if r[3]], ["spoken", "entry", "birth"],
         "period vs cohort vs generation (birth known)")


def _apc(rows, stamps, label):
    if len(rows) < 500:
        print(f"  {label}: too few rows ({len(rows)})")
        return
    chambers = sorted({r[4] for r in rows})[1:]
    idx = {"spoken": 1, "entry": 2, "birth": 3}
    names = stamps + [f"ch_{c}" for c in chambers]
    X, Y, Wt = [], [], []
    for r in rows:
        row = [(r[idx[s]] - 1990) / 10.0 for s in stamps] + \
              [1.0 if r[4] == c else 0.0 for c in chambers]
        X.append([1.0] + row)
        Y.append(r[0])
        Wt.append(r[5])
    fit = _wls(Y, X, ["const"] + names, Wt)
    if not fit:
        print(f"  {label}: singular")
        return
    print(f"  {label}  (n={len(rows):,}):")
    for s in stamps:
        b, se = fit[s]
        print(f"    {s:<8s} {b:+.3f} per decade  (se {se:.3f}, t {b/se:+.2f})"
              f"{' *' if abs(b/se) > 1.96 else ''}")


def _wls(y, X, names, w):
    n, k = len(y), len(X[0])
    XtX = [[sum(w[i] * X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
           for a in range(k)]
    Xty = [sum(w[i] * X[i][a] * y[i] for i in range(n)) for a in range(k)]
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
    beta = [sum(I[aa][bb] * Xty[bb] for bb in range(k)) for aa in range(k)]
    resid = [y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(w[i] ** 2 * X[i][aa] * X[i][bb] * resid[i] ** 2
                 for i in range(n)) for bb in range(k)] for aa in range(k)]
    V = [[sum(I[aa][p] * meat[p][q] * I[bb][q]
              for p in range(k) for q in range(k))
          for bb in range(k)] for aa in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0)))
            for j, nm in enumerate(names)}


if __name__ == "__main__":
    main()
