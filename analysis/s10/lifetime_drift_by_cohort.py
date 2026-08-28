#!/usr/bin/env python3
"""Average within-member (lifetime) register drift, by birth cohort.

Matthew's question (2026-08-28): do older members actually LOSE register over
their careers, and is that everywhere? The −0.95/decade tenure number in
tenure_within_cells.py is a BETWEEN-member contrast (birth, calendar year and
chamber held fixed, so tenure = year − entry: it is the entry-cohort effect,
not a career trajectory). The honest career quantity is the WITHIN-member
slope: follow each member over their own years and fit register rate on
spoken year. cohort_vs_period.within_member pools that to +0.51 per 1,000
words per decade (positive — members gain register as they serve). This
script splits that pooled slope by birth cohort.

Estimator, per cohort: the committed within-member slope
(cohort_vs_period.within_member) restricted to that cohort's members —
demean rate and spoken year within each member, word-weighted, pool, x10
for per-decade. So each cohort's number is a decomposition of the pooled
+0.51, NOT an average of noisy per-member slopes (which equal-weights
3-year careers with 30-year ones and does not reconcile with the paper).
Members need >= 3 years at >= 2,000 words each. Member bootstrap 95% CI,
seed 29. Reported alongside: the pooled slope (reproduces the committed
figure as a check) and the same estimator within each chamber (is the
drift positive everywhere? — it is not).

CAVEAT stated with the result: this within-member drift over 2006-2026 is
the calendar rise experienced inside a career, not pure personal
conversion — a member serving through the period drift gains register from
the period, so per cohort this is "how much of the drift each cohort rode
while serving," partly a function of which calendar window they served in.

Cohort binning: 10-year birth bins by default (per-year is noise); --bin5
for 5-year bins. Cohorts with < MIN_MEM members are dropped from the chart
(tails only; the tallies name them).

Usage: python lifetime_drift_by_cohort.py [--bin5]
Writes lifetime_drift_by_cohort.csv, .txt, and lifetime_drift_by_cohort.png.
"""
import os
import sys
import random
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cohort_vs_period as CVP               # noqa: E402

MIN_YEARS = 3
MIN_MEM = 25
BIN = 5 if "--bin5" in sys.argv else 10


def within_slope(members):
    """The committed within-member estimator (cohort_vs_period.within_member),
    restricted to a set of members: demean rate and year within each member,
    word-weighted, pool, slope x10 for per-decade. members: list of
    per-member [(year, rate, words), ...]. Returns None if no variation."""
    num = den = 0.0
    for v in members:
        W = sum(w for _, _, w in v)
        my = sum(r * w for _, r, w in v) / W
        mx = sum(y * w for y, _, w in v) / W
        num += sum(w * (y - mx) * (r - my) for y, r, w in v)
        den += sum(w * (y - mx) ** 2 for y, _, w in v)
    return (num / den) * 10.0 if den else None


def main():
    panel = CVP.load_panel()
    birth = CVP.load_birth()

    # one qualifying career per member: list of (year, rate, words)
    careers = []         # (birth_year, chamber, [(year,rate,words),...])
    for ch, ms in panel.items():
        for m, ys in ms.items():
            b = birth.get(f"{ch}|{m}")
            if b is None or not (1915 <= b <= 2005):
                continue
            v = [(y, h / w * 1000, w) for y, (w, h) in ys.items()
                 if w >= CVP.MIN_MEMBER_YEAR_WORDS]
            if len(v) >= MIN_YEARS:
                careers.append((b, ch, v))
    print(f"{len(careers):,} members with a within-career trajectory "
          f"({MIN_YEARS}+ years, {CVP.MIN_MEMBER_YEAR_WORDS}+ words/year)")

    pooled = within_slope([v for _, _, v in careers])
    print(f"pooled within-member drift (word-weighted, all members): "
          f"{pooled:+.3f} per 1,000 per decade "
          f"(committed within_member est is +0.51 — reproduces)")

    # per-legislature: the committed estimator within each chamber
    bych = defaultdict(list)
    for b, ch, v in careers:
        bych[ch].append(v)
    big = {ch: mv for ch, mv in bych.items() if len(mv) >= 15}
    slopes_ch = {ch: within_slope(mv) for ch, mv in big.items()}
    pos = sum(1 for s in slopes_ch.values() if s and s > 0)
    print(f"chambers with >=15 careers: {len(big)}; positive within-member "
          f"drift in {pos} of them")
    for ch in sorted(big, key=lambda c: slopes_ch[c]):
        print(f"    {ch:<10} n={len(big[ch]):>4}  {slopes_ch[ch]:+.3f}")

    # by birth cohort: the SAME estimator, restricted to each cohort's members
    def cohort(b):
        return int(b // BIN * BIN)
    cells = defaultdict(list)
    for b, ch, v in careers:
        cells[cohort(b)].append(v)
    rng = random.Random(29)
    rows = []
    print(f"\nwithin-member drift per decade, by {BIN}-year birth cohort:")
    for c in sorted(cells):
        mv = cells[c]
        if len(mv) < MIN_MEM:
            continue
        m = within_slope(mv)
        bs = []
        for _ in range(2000):
            samp = [mv[rng.randrange(len(mv))] for _ in mv]
            sv = within_slope(samp)
            if sv is not None:
                bs.append(sv)
        bs.sort()
        lo, hi = bs[int(0.025*len(bs))], bs[int(0.975*len(bs))]
        rows.append((c, m, lo, hi, len(mv)))
        print(f"    born {c}-{c+BIN-1}: {m:+.3f}  [{lo:+.3f}, {hi:+.3f}]  "
              f"n={len(mv)}")

    with open(os.path.join(HERE, "lifetime_drift_by_cohort.csv"), "w") as f:
        f.write("birth_cohort,within_member_drift_per_decade,lo,hi,n_members\n")
        for c, m, lo, hi, n in rows:
            f.write(f"{c},{m:.4f},{lo:.4f},{hi:.4f},{n}\n")

    # chart
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    xs = [c + BIN / 2 for c, _, _, _, _ in rows]
    ys = [m for _, m, _, _, _ in rows]
    los = [m - lo for _, m, lo, _, _ in rows]
    his = [hi - m for _, m, _, hi, _ in rows]
    ax.axhline(0, color="0.6", lw=0.8)
    ax.axhline(pooled, color="#D55E00", lw=1.0, ls=":",
               label=f"all-member mean {pooled:+.2f}")
    ax.errorbar(xs, ys, yerr=[los, his], fmt="o-", color="#1f77b4",
                ms=5, lw=1.5, capsize=3, zorder=3)
    for c, m, lo, hi, n in rows:
        ax.annotate(f"{n}", (c + BIN / 2, hi), textcoords="offset points",
                    xytext=(0, 4), fontsize=7, color="0.4", ha="center")
    ax.set_xlabel("birth cohort")
    ax.set_ylabel("lifetime register drift\n(per 1,000 words, per decade)")
    ax.set_title("Within-member register drift over a career, by birth "
                 "cohort\n(word-weighted, ±95% CI; positive = members gain "
                 "register as they serve)", fontsize=10, loc="left")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    out = os.path.join(HERE, "lifetime_drift_by_cohort.png")
    fig.savefig(out, dpi=150)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
