#!/usr/bin/env python3
"""Composition guard: is the register series measuring speech, or segment length?

WHY THIS IS THE CHEAP GUARD WORTH RUNNING

The register rate is hits per 100k tokens over whatever segments the extractor
produced. Segment length is not constant across the record: Hansard house
style, the extractor's turn-splitting, and what each parliament chose to print
all move it, and they move it on the same decade scale as the claim in §4.5.
Long segments are prepared statements; short ones are interjections and points
of order. Those genres do not carry the register at the same rate, so a series
can rise because members changed how they speak or because the record changed
what a segment is. Nothing committed separates the two.

THE TEST. Direct standardisation. Pool every 1994-2026 chamber-year's
segment-length histogram, cut it into ten strata each holding a tenth of the
pooled SEGMENTS, then recompute every chamber-year's rate as a weighted sum of
its within-stratum rates using the pooled weights, so every year is scored on
the same mix of segment lengths. Two weightings are reported because they
answer different questions:

  token-standardised    strata weighted by pooled TOKEN share. Directly
                        comparable in magnitude to the raw rate, and the one
                        to read against the published numbers.
  segment-standardised  strata weighted equally (a tenth of segments each), as
                        the literal reweighting of segments. It deliberately
                        gives short segments the same say as long ones, so its
                        LEVEL is not comparable to the raw rate -- only its
                        shape is.

Strata are ranges on the length axis, fixed once, so a chamber-year's bin maps
to the same stratum in every year. Where a single length bin straddles a cut
point its tokens and hits are split proportionally between the two strata; bins
are 32-per-octave (~2.2% wide) so the split is a rounding detail.

The verdicts asked of it: does the 1994-96 onset survive (same argmin-of-the-
annual-series statistic long_trend.py uses), and does the post-2022 jump
survive (2024-26 mean over 2018-22 mean)?

Reads word_year_counts.json.gz, whose `lenbins` carry, per chamber-year and
length bin, [segments, tokens, style hits, wiki hits].

Usage: python length_poststrat.py [--min-words 200000]
"""
import argparse
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SRC = os.path.join(HERE, "word_year_counts.json.gz")
ANGLO3 = ["UK", "US-House", "US-Senate"]
STRATA = 10
STD_LO, STD_HI = "1994", "2026"
JUMP_PRE = ("2018", "2019", "2020", "2021", "2022")
JUMP_POST = ("2024", "2025", "2026")


def blen(b):
    """Inverse of build_word_year_counts.lbin: bin index -> token length."""
    return 2.0 ** (b / 32.0)


def trough(series):
    return min(series, key=lambda y: series[y])


def mean_over(series, years):
    got = [series[y] for y in years if y in series]
    return sum(got) / len(got) if got else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-words", type=int, default=200_000)
    a = ap.parse_args()
    MW = a.min_words

    with gzip.open(SRC, "rt") as fh:
        blob = json.load(fh)
    D = blob["chambers"]
    all_ch = sorted(D)

    def usable(ch):
        return [y for y in sorted(D[ch]) if D[ch][y]["words"] >= MW]

    # -------------------------------------------------- the pooled standard
    pool_seg = Counter()
    pool_tok = Counter()
    for ch in all_ch:
        for y in usable(ch):
            if not (STD_LO <= y <= STD_HI):
                continue
            for b, (s, t, h, w) in D[ch][y]["lenbins"].items():
                pool_seg[int(b)] += s
                pool_tok[int(b)] += t
    bins = sorted(pool_seg)
    tot_seg = sum(pool_seg.values())
    tot_tok = sum(pool_tok.values())
    print(f"pooled standard, {STD_LO}-{STD_HI}, all {len(all_ch)} chambers: "
          f"{tot_seg/1e6:.2f}M segments, {tot_tok/1e9:.3f}B tokens, "
          f"{len(bins)} length bins")

    # split each bin's segment mass across strata, so strata hold exactly a
    # tenth of pooled segments each
    edge = tot_seg / STRATA
    share = defaultdict(dict)       # bin -> stratum -> fraction of the bin
    cum = 0.0
    for b in bins:
        n = pool_seg[b]
        left = n
        while left > 1e-9:
            s = min(STRATA - 1, int(cum / edge))
            room = (s + 1) * edge - cum
            take = min(left, room) if room > 0 else left
            share[b][s] = share[b].get(s, 0.0) + take / n
            cum += take
            left -= take
    w_seg = [0.0] * STRATA
    w_tok = [0.0] * STRATA
    lo = [None] * STRATA
    hi = [None] * STRATA
    for b in bins:
        for s, f in share[b].items():
            w_seg[s] += pool_seg[b] * f
            w_tok[s] += pool_tok[b] * f
            lo[s] = blen(b) if lo[s] is None else min(lo[s], blen(b))
            hi[s] = blen(b) if hi[s] is None else max(hi[s], blen(b))
    w_seg = [x / tot_seg for x in w_seg]
    w_tok = [x / tot_tok for x in w_tok]
    print(f"\n  {'stratum':<8s} {'length range (tokens)':>24s} "
          f"{'segment share':>14s} {'token share':>12s}")
    for s in range(STRATA):
        print(f"  {s:<8d} {f'{lo[s]:.0f} - {hi[s]:.0f}':>24s} "
              f"{w_seg[s]:>14.3f} {w_tok[s]:>12.3f}")

    # ------------------------------------------------------ standardised rates
    # A bin seen only outside 1994-2026 (UK's 1985-93 years) has no pooled
    # weight; it takes the stratum of the nearest bin that does, so a very long
    # 1980s segment is not silently filed with the shortest ones.
    bmin, bmax = bins[0], bins[-1]

    def share_of(b):
        return share.get(b) or share[bmin if b < bmin else bmax]

    def strat(ch, y):
        """[tokens, style hits, wiki hits] per stratum for one chamber-year."""
        out = [[0.0, 0.0, 0.0] for _ in range(STRATA)]
        for b, (sg, t, h, w) in D[ch][y]["lenbins"].items():
            for s, f in share_of(int(b)).items():
                out[s][0] += t * f
                out[s][1] += h * f
                out[s][2] += w * f
        return out

    empty = 0

    def series(chambers, years, col=1):
        raw, tstd, sstd = {}, {}, {}
        nonlocal empty
        for y in years:
            agg = [[0.0, 0.0, 0.0] for _ in range(STRATA)]
            for ch in chambers:
                for s, v in enumerate(strat(ch, y)):
                    for k in range(3):
                        agg[s][k] += v[k]
            tot = sum(v[0] for v in agg)
            raw[y] = sum(v[col] for v in agg) / tot * 1e5
            for name, ws, dst in (("tok", w_tok, tstd), ("seg", w_seg, sstd)):
                num = den = 0.0
                for s in range(STRATA):
                    if agg[s][0] <= 0:
                        empty += 1
                        continue
                    num += ws[s] * agg[s][col] / agg[s][0]
                    den += ws[s]
                dst[y] = num / den * 1e5
        return raw, tstd, sstd

    uk_years = usable("UK")
    a3_years = sorted(set.intersection(*[set(usable(ch)) for ch in ANGLO3]))
    # every chamber with an unbroken 2006-2026 run, the longest window most of
    # the corpus shares; PE, AUS_SA, NI, CA-FED and IE have holes or start late
    span = {str(y) for y in range(2006, 2027)}
    wide_ch = [ch for ch in all_ch if span <= set(usable(ch))]
    wide_years = sorted(span)

    panels = [("UK", ["UK"], uk_years),
              ("ANGLO3", ANGLO3, a3_years),
              (f"WIDE-{len(wide_ch)}", wide_ch, wide_years)]

    for label, chs, ys in panels:
        raw, tstd, sstd = series(chs, ys)
        print("\n" + "=" * 78)
        print(f"{label}  ({', '.join(chs) if len(chs) <= 3 else str(len(chs)) + ' chambers'})"
              f"  {ys[0]}-{ys[-1]}")
        print("=" * 78)
        print(f"  {'year':<6s} {'raw':>9s} {'token-std':>10s} {'seg-std':>9s} "
              f"{'mean seg len':>13s}")
        for y in ys:
            tl = sum(D[ch][y]["words"] for ch in chs)
            sg = sum(D[ch][y]["segs"] for ch in chs)
            print(f"  {y:<6s} {raw[y]:>9.1f} {tstd[y]:>10.1f} "
                  f"{sstd[y]:>9.1f} {tl/max(1,sg):>13.1f}")
        print(f"\n  ONSET (argmin of the annual series, the committed "
              f"statistic)")
        print(f"    raw {trough(raw)}    token-std {trough(tstd)}    "
              f"seg-std {trough(sstd)}")
        print(f"  POST-2022 JUMP ({'/'.join(JUMP_POST)} mean over "
              f"{'/'.join(JUMP_PRE)} mean)")
        for name, s in (("raw", raw), ("token-std", tstd), ("seg-std", sstd)):
            pre = mean_over(s, JUMP_PRE)
            post = mean_over(s, JUMP_POST)
            print(f"    {name:<10s} {pre:>8.1f} -> {post:>8.1f}   "
                  f"x{post/pre:.3f}")
        for tag, lo_, hi_ in (("1994-96 -> 2019", ("1994", "1995", "1996"),
                               ("2019",)),
                              ("1994-96 -> 2026", ("1994", "1995", "1996"),
                               ("2026",))):
            if all(y in raw for y in lo_ + hi_):
                print(f"  {tag}")
                for name, s in (("raw", raw), ("token-std", tstd),
                                ("seg-std", sstd)):
                    print(f"    {name:<10s} {mean_over(s, lo_):>8.1f} -> "
                          f"{mean_over(s, hi_):>8.1f}   "
                          f"x{mean_over(s, hi_)/mean_over(s, lo_):.3f}")

    # the composition drift the guard exists for
    print("\n" + "=" * 78)
    print("WHAT THE GUARD IS GUARDING AGAINST: segment-length drift")
    print("=" * 78)
    print(f"  {'year':<6s} " + " ".join(f"{ch[:8]:>8s}" for ch in ANGLO3)
          + f" {'WIDE mean':>10s} {'WIDE top-decile token share':>28s}")
    for y in sorted(set(uk_years) | set(wide_years)):
        cells = []
        for ch in ANGLO3:
            if y in D[ch] and D[ch][y]["words"] >= MW:
                cells.append(f"{D[ch][y]['words']/max(1,D[ch][y]['segs']):>8.1f}")
            else:
                cells.append(f"{'-':>8s}")
        chs = [c for c in wide_ch if y in D[c] and D[c][y]["words"] >= MW]
        if chs:
            agg = [[0.0, 0.0, 0.0] for _ in range(STRATA)]
            for ch in chs:
                for s, v in enumerate(strat(ch, y)):
                    agg[s][0] += v[0]
            tot = sum(v[0] for v in agg)
            sg = sum(D[ch][y]["segs"] for ch in chs)
            w = sum(D[ch][y]["words"] for ch in chs)
            tail = agg[STRATA - 1][0] / tot
            print(f"  {y:<6s} " + " ".join(cells)
                  + f" {w/max(1,sg):>10.1f} {tail:>28.3f}")
        else:
            print(f"  {y:<6s} " + " ".join(cells))
    if empty:
        print(f"\n  note: {empty} chamber-year strata were empty and their "
              f"weight was renormalised away")


if __name__ == "__main__":
    main()
