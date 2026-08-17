#!/usr/bin/env python3
"""Arrival premium (new members minus incumbents, same year) across ALL chambers.

arrival_premium.py answered this for the UK alone, off the raw segment file.
This computes the same quantity for every chamber in the member-year panels,
which is cheap because those are pre-aggregated ([words, hits] per CH|member|year).

Definition, identical to arrival_premium.py: in probe year Y a member is NEW if
absent from all of Y-1..Y-4, INCUMBENT otherwise; the premium is the
word-weighted register rate of the NEW group minus that of the INCUMBENT group,
both measured in Y. Held fixed by construction: era, chamber, extractor.

Two things are reported:
  1. per-chamber mean premium and its linear trend over probe years
  2. the onset-era series (pre-2005) for the deep-history chambers only --
     provinces begin in 2006 and cannot speak to the ~1994-2000 onset

Usage: python panel_arrival_premium.py
"""
import json
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LOOKBACK = 4
MIN_YEAR_WORDS = 300_000
COUNTRY = {"AB": "Canada", "BC": "Canada", "MB": "Canada", "NL": "Canada",
           "NS": "Canada", "ON": "Canada", "SK": "Canada", "PE": "Canada",
           "CA-FED": "Canada", "NSW": "Australia", "QLD": "Australia",
           "SA": "Australia", "TAS": "Australia", "VIC": "Australia",
           "WA": "Australia", "NI": "UK", "SCO": "UK", "WAL": "UK",
           "UK": "UK", "US-HOUSE": "USA", "US-SENATE": "USA", "IE": "Ireland"}


def load():
    panel = defaultdict(lambda: defaultdict(dict))  # ch -> member -> year -> [w,h]
    for f in ("member_year_rates.json", "member_year_rates_t1.json"):
        d = json.load(open(os.path.join(HERE, f)))
        for k, v in d.items():
            ch, member, yr = k.rsplit("|", 2)
            panel[ch][member][int(yr)] = v
    return panel


def premium_series(members):
    """{year: (premium, n_new, n_inc)} for one chamber."""
    yr_words = defaultdict(int)
    for m, ys in members.items():
        for y, (w, h) in ys.items():
            yr_words[y] += w
    out = {}
    for y in sorted(yr_words):
        if yr_words[y] < MIN_YEAR_WORDS:
            continue
        nw = [0, 0]
        inc = [0, 0]
        for m, ys in members.items():
            if y not in ys:
                continue
            seen = any((y - k) in ys for k in range(1, LOOKBACK + 1))
            w, h = ys[y]
            (inc if seen else nw)[0] += w
            (inc if seen else nw)[1] += h
        if nw[0] == 0 or inc[0] == 0:
            continue
        prem = nw[1] / nw[0] * 1000 - inc[1] / inc[0] * 1000
        out[y] = (prem, nw[0], inc[0])
    return out


def trend(series):
    ys = sorted(series)
    xs = [y for y in ys if y - LOOKBACK >= ys[0]]
    if len(xs) < 3:
        return None
    v = [series[y][0] for y in xs]
    mx = statistics.mean(xs)
    mv = statistics.mean(v)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (val - mv) for x, val in zip(xs, v)) / den if den else None


def main():
    panel = load()
    print(f"{'chamber':<10s} {'yrs':>4s} {'mean prem':>10s} {'trend/yr':>9s} "
          f"{'first':>6s} {'last':>6s}")
    rows = []
    for ch in sorted(panel):
        s = premium_series(panel[ch])
        probe = [y for y in sorted(s) if y - LOOKBACK >= min(s)]
        if len(probe) < 3:
            continue
        prem = [s[y][0] for y in probe]
        mp = statistics.mean(prem)
        tr = trend(s)
        rows.append((ch, mp, tr, probe[0], probe[-1], s))
        print(f"{ch:<10s} {len(probe):>4d} {mp:>+10.2f} "
              f"{(f'{tr:+.3f}' if tr is not None else 'n/a'):>9s} "
              f"{probe[0]:>6d} {probe[-1]:>6d}")

    print("\npooled mean premium (chamber-unweighted): "
          f"{statistics.mean([r[1] for r in rows]):+.2f}  "
          f"positive in {sum(1 for r in rows if r[1] > 0)}/{len(rows)}")
    byc = defaultdict(list)
    for ch, mp, *_ in rows:
        byc[COUNTRY.get(ch, "?")].append(mp)
    for c in sorted(byc):
        print(f"  {c:<10s} {statistics.mean(byc[c]):+.2f}  (n={len(byc[c])})")

    print("\nONSET-ERA series (pre-2006 probe years, deep-history chambers):")
    for ch, mp, tr, y0, y1, s in rows:
        early = [(y, s[y][0]) for y in sorted(s) if y <= 2006 and y - LOOKBACK >= min(s)]
        if len(early) >= 3:
            print(f"  {ch}: " +
                  "  ".join(f"{y}:{p:+.2f}" for y, p in early))


if __name__ == "__main__":
    main()
