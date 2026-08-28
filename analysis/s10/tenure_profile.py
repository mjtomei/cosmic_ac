#!/usr/bin/env python3
"""Register by length of service — the two honest curves.

Matthew's question (2026-08-28): chart register against tenure. The catch:
within one member, tenure = spoken year − entry year, so tenure and calendar
year are the same clock — a within-member rate-vs-tenure slope is
identically the +0.57/decade calendar rise (lifetime_drift_by_cohort). The
only informative tenure question holds period fixed. So this plots two
curves on one tenure axis:

  RAW (within-member): rate minus each member's own career mean, averaged by
    tenure bin. Rises — the calendar tide ridden inside a career; its slope
    reproduces the committed within-member +0.51 as a check.
  PERIOD-ADJUSTED (cross-sectional): rate minus its chamber x year mean,
    averaged by tenure bin. This asks, at a fixed calendar moment, whether
    longer-serving members use more or less register than their just-arrived
    colleagues. It falls — BUT because tenure = year − entry, longer tenure
    at fixed year means an earlier entry cohort, so this decline is the
    entry-cohort gradient seen sideways, NOT a within-career decline. The
    same fact the −0.95/decade tenure test reported, drawn as a shape.

Entry = a member's first observed year in a chamber; members present in the
chamber's first covered year are left-censored (unknown true entry) and
dropped, mirroring cohort_vs_period's --censor 1. Word-weighted throughout;
member-cluster bootstrap 95% CIs (seed 31). Tenure bins 0-2 / 3-5 / 6-9 /
10-14 / 15-19 / 20-29 / 30+.

Usage: python tenure_profile.py
Writes tenure_profile.csv, .txt, tenure_profile.png.
"""
import os
import random
import statistics
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cohort_vs_period as CVP               # noqa: E402

BINS = [(0, 2), (3, 5), (6, 9), (10, 14), (15, 19), (20, 29), (30, 99)]


def binlabel(t):
    for lo, hi in BINS:
        if lo <= t <= hi:
            return (lo, hi)
    return None


def wmean(pairs):
    W = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / W if W else float("nan")


def wslope(rows):
    """word-weighted OLS slope of value on tenure, x10 (per decade)."""
    W = sum(w for _, _, w in rows)
    mx = sum(t * w for t, _, w in rows) / W
    my = sum(v * w for _, v, w in rows) / W
    den = sum(w * (t - mx) ** 2 for t, _, w in rows)
    num = sum(w * (t - mx) * (v - my) for t, v, w in rows)
    return (num / den) * 10 if den else float("nan")


def main():
    panel = CVP.load_panel()
    rows = []            # (member_key, chamber, year, tenure, rate, words)
    for ch, ms in panel.items():
        first = min(y for m in ms.values() for y in m)
        for m, ys in ms.items():
            entry = min(ys)
            if entry <= first:                 # left-censored, drop
                continue
            for y, (w, h) in ys.items():
                if w >= CVP.MIN_MEMBER_YEAR_WORDS:
                    rows.append((f"{ch}|{m}", ch, y, y - entry,
                                 h / w * 1000, w))
    print(f"{len(rows):,} member-years, "
          f"{len({r[0] for r in rows}):,} members (left-censored dropped)")

    # RAW: within-member demeaned rate
    bym = defaultdict(list)
    for r in rows:
        bym[r[0]].append(r)
    raw = []             # (tenure, demeaned_rate, words, member)
    for m, v in bym.items():
        W = sum(r[5] for r in v)
        mu = sum(r[4] * r[5] for r in v) / W
        for r in v:
            raw.append((r[3], r[4] - mu, r[5], m))
    # PERIOD-ADJ: chamber x year demeaned rate
    bycy = defaultdict(list)
    for r in rows:
        bycy[(r[1], r[2])].append(r)
    padj = []
    cymean = {}
    for k, v in bycy.items():
        W = sum(r[5] for r in v)
        cymean[k] = sum(r[4] * r[5] for r in v) / W
    for r in rows:
        padj.append((r[3], r[4] - cymean[(r[1], r[2])], r[5], r[0]))

    print(f"\nRAW within-member slope vs tenure: "
          f"{wslope([(t, v, w) for t, v, w, _ in raw]):+.3f}/decade "
          f"(= the calendar rise; committed within-member +0.51)")
    print(f"PERIOD-ADJUSTED slope vs tenure:   "
          f"{wslope([(t, v, w) for t, v, w, _ in padj]):+.3f}/decade "
          f"(cross-sectional; the entry-cohort gradient)")

    def curve(points):
        """points: (tenure, value, words, member) -> per-bin wmean + boot CI."""
        out = []
        rng = random.Random(31)
        bins = defaultdict(list)
        for t, v, w, m in points:
            b = binlabel(t)
            if b:
                bins[b].append((t, v, w, m))
        for b in BINS:
            pts = bins.get(b, [])
            if not pts:
                continue
            mem = defaultdict(list)
            for t, v, w, m in pts:
                mem[m].append((v, w))
            val = wmean([(v, w) for _, v, w in
                         [(t, v, w) for t, v, w, _ in pts]])
            keys = list(mem)
            bs = []
            for _ in range(2000):
                samp = [mem[keys[rng.randrange(len(keys))]]
                        for _ in keys]
                flat = [(v, w) for grp in samp for v, w in grp]
                bs.append(wmean(flat))
            bs.sort()
            out.append((b, val, bs[50], bs[1949], len(mem)))
        return out

    rawc = curve(raw)
    padc = curve(padj)

    with open(os.path.join(HERE, "tenure_profile.csv"), "w") as f:
        f.write("series,tenure_lo,tenure_hi,mean,lo,hi,n_members\n")
        for nm, c in (("raw_within_member", rawc), ("period_adjusted", padc)):
            for (lo, hi), v, blo, bhi, n in c:
                f.write(f"{nm},{lo},{hi},{v:.4f},{blo:.4f},{bhi:.4f},{n}\n")

    print("\ntenure bin       RAW within-member      PERIOD-adjusted")
    for i, (lo, hi) in enumerate(BINS):
        rr = next((x for x in rawc if x[0] == (lo, hi)), None)
        pp = next((x for x in padc if x[0] == (lo, hi)), None)
        lbl = f"{lo}-{hi if hi < 99 else '+'}"
        print(f"  {lbl:<8} {rr[1]:+8.2f} [{rr[2]:+.2f},{rr[3]:+.2f}]"
              f"   {pp[1]:+8.2f} [{pp[2]:+.2f},{pp[3]:+.2f}]  n={pp[4]}")

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    xs = [i for i in range(len(BINS))]
    lab = [f"{lo}-{hi if hi < 99 else '+'}" for lo, hi in BINS]
    for name, c, col in (("within-member (rides the calendar tide)", rawc,
                          "#1f77b4"),
                         ("period-adjusted (vs same-year colleagues)", padc,
                          "#D55E00")):
        xi = [i for i, b in enumerate(BINS) if any(x[0] == b for x in c)]
        ys = [next(x for x in c if x[0] == BINS[i])[1] for i in xi]
        lo = [ys[k] - next(x for x in c if x[0] == BINS[i])[2]
              for k, i in enumerate(xi)]
        hi = [next(x for x in c if x[0] == BINS[i])[3] - ys[k]
              for k, i in enumerate(xi)]
        ax.errorbar(xi, ys, yerr=[lo, hi], fmt="o-", color=col, ms=5,
                    lw=1.5, capsize=3, label=name)
    ax.axhline(0, color="0.6", lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels(lab)
    ax.set_xlabel("years of service")
    ax.set_ylabel("register deviation\n(per 1,000 words)")
    ax.set_title("Register by length of service — the two curves cross\n"
                 "within a career register rises with the calendar tide; at "
                 "fixed year, longer-serving\nmembers sit lower — the "
                 "entry-cohort gradient, not a career decline", fontsize=9,
                 loc="left")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(HERE, "tenure_profile.png")
    fig.savefig(out, dpi=150)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
