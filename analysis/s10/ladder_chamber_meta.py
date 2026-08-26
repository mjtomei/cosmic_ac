#!/usr/bin/env python3
"""The folk ladder's per-chamber meta — the crossover-meta's twin.

The class arm's II-over-I claim carries a within-chamber meta-analysis
(each legislature its own control, inverse-variance pooled). The measure
that absorbs class gets the same test: within each chamber, the member-level
slope of the register (z within chamber) on the FREE level score (per sd
within that chamber's members), pooled across chambers by inverse variance.
Also reported: the same meta for the apex delta (MIDDLE - TOP), and the
FREE slope split by chamber group (the eight provinces / the five tier-1
chambers / the nine 2026-08 additions) — the replication read.

Usage: python ladder_chamber_meta.py
"""
import json
import math
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import member_level_estimation as MLE              # noqa: E402

T1 = {"us-house", "us-senate", "uk", "ca-fed", "ie"}
M9 = {"nsw", "vic", "qld", "wa", "sa", "tas", "sco", "wal", "ni"}


def slope(pairs):
    """OLS slope of y on x with HC1 se; x standardised on these pairs."""
    n = len(pairs)
    xs = [x for x, _ in pairs]
    mx = statistics.mean(xs)
    sx = statistics.pstdev(xs) or 1.0
    xs = [(x - mx) / sx for x in xs]
    ys = [y for _, y in pairs]
    my = statistics.mean(ys)
    sxx = sum(x * x for x in xs)
    b = sum(x * (y - my) for x, y in zip(xs, ys)) / sxx
    e2 = [(y - my - b * x) ** 2 for x, y in zip(xs, ys)]
    se = math.sqrt(sum(ei * x * x for ei, x in zip(e2, xs)) / sxx ** 2
                   * n / max(n - 2, 1))
    return b, se, n


def meta(cells):
    w = [1 / se ** 2 for _, se, _ in cells]
    W = sum(w)
    m = sum(wi * b for wi, (b, _, _) in zip(w, cells)) / W
    return m, math.sqrt(1 / W)


def main():
    rows = MLE.zscore(MLE.members())
    scores = {}
    for r in json.load(open(os.path.join(HERE, "prereg_member_table.json"))):
        if r.get("lvl_MIDDLE") is not None:
            k = "|".join(r["member"].split("|")[:2])
            scores[k] = (r["lvl_FREE"], r["lvl_MIDDLE"], r["lvl_TOP"])
    by_ch = defaultdict(list)
    for r in rows:
        if r.get("z") is None:
            continue
        sc = scores.get("|".join(r["member"].split("|")[:2]))
        if sc:
            by_ch[r["chamber"]].append((sc, r["z"]))

    free_cells, apex_cells = [], []
    groups = defaultdict(list)
    print(f"{'chamber':<10} {'n':>5} {'FREE slope':>12} {'t':>6}")
    for ch in sorted(by_ch):
        pairs = by_ch[ch]
        if len(pairs) < 30:
            continue
        bf, sef, n = slope([(sc[0], z) for sc, z in pairs])
        ba, sea, _ = slope([(sc[1] - sc[2], z) for sc, z in pairs])
        free_cells.append((bf, sef, ch))
        apex_cells.append((ba, sea, ch))
        g = ("tier-1" if ch.lower() in T1 else
             "2026-additions" if ch.lower() in M9 else "provinces")
        groups[g].append((bf, sef, ch))
        star = " *" if abs(bf / sef) > 1.96 else ""
        print(f"{ch:<10} {n:>5} {bf:>+12.3f} {bf/sef:>+6.2f}{star}")

    neg = sum(1 for b, _, _ in free_cells if b < 0)
    sig = sum(1 for b, se, _ in free_cells if b / se < -1.96)
    m, se = meta(free_cells)
    print(f"\nFREE, {len(free_cells)} chambers: negative in {neg}, "
          f"individually significant in {sig}")
    print(f"  inverse-variance meta: {m:+.4f} per sd  (z = {m/se:+.2f})")
    ma, sea = meta(apex_cells)
    print(f"apex delta (MIDDLE − TOP) meta: {ma:+.4f} per sd  (z = {ma/sea:+.2f})")
    print("\nFREE by chamber group:")
    for g, cells in sorted(groups.items()):
        mg, seg = meta(cells)
        ng = sum(1 for b, _, _ in cells if b < 0)
        print(f"  {g:<16} {len(cells):>2} chambers, {ng} negative, "
              f"meta {mg:+.4f} (z {mg/seg:+.2f})")


if __name__ == "__main__":
    main()
