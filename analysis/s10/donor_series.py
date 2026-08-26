#!/usr/bin/env python3
"""A matched counterfactual for the register series: what would ANY 400 words do?

THE OBJECTION, PRICED

§4.5's level series is the pooled rate of 407 words that were chosen because
they rose in scholarly text after 2022. Projected backwards, such a list rises
by construction: regression alone puts a word picked on a recent high below its
own mean earlier. The right control is not "no words" but "the same words minus
the selection" -- an equally large set of words that look like the style words
in every measurable respect EXCEPT having been picked on a recent rise.

THE DESIGN

For every style word, one donor word is drawn from the non-Kobak vocabulary,
matched on three deciles:

  (i)   2006-2010 mean frequency        -- level; a rare word and a common one
                                           have different backward geometry
  (ii)  dispersion across chambers (CV) -- a word concentrated in one
                                           legislature moves with that
                                           legislature's coverage, not with
                                           register
  (iii) 1994-2010 pre-period log-slope  -- THE ONE THAT MATTERS. Matching on
                                           the pre-period trend means the donor
                                           set was already going where the
                                           style set was going before the
                                           window of interest, so any remaining
                                           gap is not shared drift.

Deciles are cut on the DONOR POOL's own distribution and style words are placed
into those bins, so "decile 7" means the same thing on both sides. Selection is
nearest-available in decile space (Manhattan, tie-broken on standardised
continuous distance then on a seeded shuffle), WITHOUT REPLACEMENT, seed 13, so
one popular donor cell cannot supply half the control set.

Donor pool exclusions: alphabetic, length >= 4, and -- stricter than the
committed placebo in long_trend.py -- not appearing ANYWHERE in
kobak_excess_words.csv, content words and mixed types included, since every
entry on that list was selected the same way.

ONE DELIBERATE DEPARTURE from the committed placebo, which drops the 120
commonest words from its pool. That exclusion is fatal here, because the style
list's own heaviest members are ultra-frequent function words -- `this`,
`their`, `these`, `like` -- and a pool with the commonest words removed cannot
match them at all. Under the committed rule those words fall through
`pool_for`'s neighbourhood search to `max(pool.values(), key=len)`, i.e. to
whichever frequency bucket happens to be largest, so the placebo drawn for
`this` is a far rarer word and the instrument-minus-placebo gap inherits the
difference. The top-N exclusion is therefore off by default here; `--exclude-top
120` reproduces the committed rule, and the count of style words that fall in
the top 120 is reported either way.

Both aggregates are read from vocab_year_counts.json.gz so the two sides get
identical treatment, including that artifact's within-chamber count>=2 prune;
the style aggregate is cross-checked against the exact counts in
word_year_counts.json.gz and the difference reported.

THE ONSET TEST is the committed one from long_trend.py: the turning point is
the argmin year of the annual series, not a fitted curve. It is applied to the
DIFFERENCE series here. The committed interval comes from a bootstrap over
sitting DAYS, which needs day-level data this scan does not carry, so the
interval here is a bootstrap over CHAMBERS (seed 17) -- coarser, and on the
1994-2026 panel it has only three units, which is stated with the result rather
than hidden in it. A two-segment continuous piecewise-linear fit is reported
alongside, because an argmin on a noisy series is a fragile statistic.

Usage: python donor_series.py [--reps 2000]
"""
import argparse
import csv
import gzip
import json
import math
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

VOCAB = os.path.join(HERE, "vocab_year_counts.json.gz")
EXACT = os.path.join(HERE, "word_year_counts.json.gz")
ANGLO3 = ["UK", "US-House", "US-Senate"]
FREQ_WIN = ("2006", "2007", "2008", "2009", "2010")
PRE_WIN = [str(y) for y in range(1994, 2011)]
N_DECILE = 10
SEED_MATCH = 13
SEED_BOOT = 17
MIN_LEN = 4


def kobak_all():
    """Every word on the Kobak list, whatever its type -- all were selected
    on the same post-2022 excess, so none of them can serve as a donor."""
    return {r["word"].lower() for r in
            csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
            if r["word"].isalpha()}


def style_words():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE,
                                                    "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def wls_slope(xs, ys, ws):
    sw = sum(ws)
    if sw <= 0 or len(xs) < 3:
        return None
    mx = sum(w * x for w, x in zip(ws, xs)) / sw
    my = sum(w * y for w, y in zip(ws, ys)) / sw
    den = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    if den <= 0:
        return None
    return sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / den


def decile_bins(values):
    """Cut points at the 10th..90th percentiles of `values`."""
    v = sorted(values)
    return [v[int(q * len(v) / N_DECILE)] for q in range(1, N_DECILE)]


def to_decile(x, cuts):
    d = 0
    for c in cuts:
        if x >= c:
            d += 1
    return d


def trough(series):
    return min(series, key=lambda y: series[y])


def seg_fit(years, vals):
    """Continuous two-segment fit; returns (breakpoint, slope_before,
    slope_after). Grid search over interior years, least squares."""
    best = None
    xs = [float(y) for y in years]
    for i in range(2, len(years) - 2):
        tau = xs[i]
        A = [[1.0, x, max(0.0, x - tau)] for x in xs]
        # 3x3 normal equations, solved by Gaussian elimination
        M = [[sum(A[k][r] * A[k][c] for k in range(len(xs))) for c in range(3)]
             + [sum(A[k][r] * vals[k] for k in range(len(xs)))]
             for r in range(3)]
        try:
            for c in range(3):
                p = max(range(c, 3), key=lambda r: abs(M[r][c]))
                if abs(M[p][c]) < 1e-12:
                    raise ZeroDivisionError
                M[c], M[p] = M[p], M[c]
                for r in range(3):
                    if r == c:
                        continue
                    f = M[r][c] / M[c][c]
                    for k in range(c, 4):
                        M[r][k] -= f * M[c][k]
            b = [M[r][3] / M[r][r] for r in range(3)]
        except ZeroDivisionError:
            continue
        sse = sum((vals[k] - (b[0] + b[1] * xs[k]
                              + b[2] * max(0.0, xs[k] - tau))) ** 2
                  for k in range(len(xs)))
        if best is None or sse < best[0]:
            best = (sse, years[i], b[1], b[1] + b[2])
    return best[1:] if best else (None, None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-words", type=int, default=200_000)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--exclude-top", type=int, default=0,
                    help="drop the N commonest words from the donor pool; "
                         "120 reproduces the committed placebo rule and "
                         "leaves the heaviest style words unmatchable")
    ap.add_argument("--match-on", default="freq,cv,slope",
                    help="which of freq,cv,slope to match on. The default "
                         "includes the 1994-2010 pre-slope, which by "
                         "construction absorbs any trend starting inside that "
                         "window -- so 'freq,cv' is the run that can still see "
                         "a 1994-96 onset in the difference series")
    a = ap.parse_args()
    MW = a.min_words

    with gzip.open(VOCAB, "rt") as fh:
        V = json.load(fh)
    D = V["chambers"]
    totals = V["totals"]
    with gzip.open(EXACT, "rt") as fh:
        E = json.load(fh)["chambers"]
    print(f"vocab: {len(totals):,} words at >= "
          f"{V['_meta']['min_global_count']} corpus-wide, {len(D)} chambers")

    tokens = {ch: {y: E[ch][y]["words"] for y in E[ch]} for ch in E}
    all_ch = sorted(D)
    a3_years = sorted(set.intersection(*[
        {y for y in tokens[ch] if tokens[ch][y] >= MW} for ch in ANGLO3]))
    print(f"ANGLO3 balanced panel: {a3_years[0]}-{a3_years[-1]} "
          f"({len(a3_years)} years)")

    # ------------------------------------------------------------- features
    freq_ch = [ch for ch in all_ch
               if sum(tokens[ch].get(y, 0) for y in FREQ_WIN) >= 1_000_000]
    print(f"dispersion measured across {len(freq_ch)} chambers with >=1M "
          f"tokens in {FREQ_WIN[0]}-{FREQ_WIN[-1]}: {' '.join(freq_ch)}")
    win_tok = {ch: sum(tokens[ch].get(y, 0) for y in FREQ_WIN)
               for ch in freq_ch}
    tot_win_tok = sum(win_tok.values())

    cnt_win = defaultdict(Counter)              # ch -> word -> count in window
    for ch in freq_ch:
        for y in FREQ_WIN:
            if y in D[ch]:
                cnt_win[ch].update(D[ch][y])
    pre_tok = {y: sum(tokens[ch].get(y, 0) for ch in ANGLO3) for y in PRE_WIN}
    pre_years = [y for y in PRE_WIN if y in a3_years]
    cnt_pre = defaultdict(Counter)              # year -> word -> ANGLO3 count
    for y in pre_years:
        for ch in ANGLO3:
            cnt_pre[y].update(D[ch].get(y, {}))

    def features(w):
        c = sum(cnt_win[ch].get(w, 0) for ch in freq_ch)
        if c < 20:
            return None
        f = math.log10(c / tot_win_tok)
        rates = [cnt_win[ch].get(w, 0) / win_tok[ch] for ch in freq_ch]
        m = statistics.mean(rates)
        if m <= 0:
            return None
        cv = statistics.pstdev(rates) / m
        xs = [int(y) for y in pre_years]
        ys = [math.log((cnt_pre[y].get(w, 0) + 0.5) / pre_tok[y])
              for y in pre_years]
        ws = [cnt_pre[y].get(w, 0) + 0.5 for y in pre_years]
        s = wls_slope(xs, ys, ws)
        if s is None:
            return None
        return (f, cv, s)

    kob = kobak_all()
    style = style_words()
    top120 = {w for w, _ in Counter(totals).most_common(120)}
    common = {w for w, _ in Counter(totals).most_common(a.exclude_top)} \
        if a.exclude_top else set()
    pool_words = [w for w in totals
                  if w not in kob and w.isalpha() and len(w) >= MIN_LEN
                  and w not in common]
    print(f"donor pool before feature screen: {len(pool_words):,} words "
          f"(excluded {len(kob):,} Kobak entries, "
          f"{a.exclude_top} commonest, len<{MIN_LEN})")
    hot = sorted(w for w in style if w in top120)
    print(f"style words inside the corpus-wide top 120 -- the ones the "
          f"committed placebo pool cannot match: {len(hot)}  {hot}")

    F = {}
    for w in pool_words:
        f = features(w)
        if f:
            F[w] = f
    S = {}
    for w in style:
        if w in totals:
            f = features(w)
            if f:
                S[w] = f
    print(f"donor pool with all three features: {len(F):,}")
    print(f"style words carried: {len(S)} of {len(style)}  "
          f"({len(style)-len(S)} dropped: below the corpus-wide floor, "
          f"below 20 hits in {FREQ_WIN[0]}-{FREQ_WIN[-1]}, or no pre-slope)")

    FEATS = ("freq", "cv", "slope")
    IDX = [FEATS.index(n.strip()) for n in a.match_on.split(",") if n.strip()]
    print(f"matching on {', '.join(FEATS[k] for k in IDX)}"
          + ("   (pre-slope EXCLUDED: the difference series is free to show an "
             "onset inside 1994-2010)" if 2 not in IDX else ""))
    cuts = [decile_bins([F[w][k] for w in F]) for k in range(3)]
    Fd = {w: tuple(to_decile(F[w][k], cuts[k]) for k in IDX) for w in F}
    Sd = {w: tuple(to_decile(S[w][k], cuts[k]) for k in IDX) for w in S}
    sd = [statistics.pstdev([F[w][k] for w in F]) or 1.0 for k in range(3)]

    # -------------------------------------------------------------- matching
    # Greedy nearest-available, in a seeded random order so no alphabetical
    # bias decides who gets first pick of a crowded cell. The comparison key is
    # (Manhattan distance in decile space, Euclidean distance in standardised
    # continuous space, seeded tie-break), so within a decile cell the closest
    # actual frequency/CV/slope wins -- which matters, because the top decile
    # of frequency spans two orders of magnitude and holds the style words that
    # carry the aggregate.
    rng = random.Random(SEED_MATCH)
    order = sorted(S)
    rng.shuffle(order)
    jitter = {w: rng.random() for w in F}
    pool = sorted(F)
    Fz = {w: tuple(F[w][k] / sd[k] for k in IDX) for w in pool}
    used = set()
    match = {}
    quality = []
    for w in order:
        want = Sd[w]
        z = tuple(S[w][k] / sd[k] for k in IDX)
        best = None
        for cand in pool:
            if cand in used:
                continue
            c = Fd[cand]
            md = sum(abs(x - y) for x, y in zip(c, want))
            if best is not None and md > best[0]:
                continue
            key = (md, math.dist(Fz[cand], z), jitter[cand])
            if best is None or key < best[:3]:
                best = key + (cand, c)
        if best:
            used.add(best[3])
            match[w] = best[3]
            quality.append((w, best[3], want, best[4], best[0]))

    exact = sum(1 for *_, md in quality if md == 0)
    print(f"\nmatched {len(match)} style words to distinct donors, seed "
          f"{SEED_MATCH}, without replacement")
    print(f"  exact match on every matched decile: {exact} "
          f"({exact/len(match):.1%})")
    for j, k in enumerate(IDX):
        dif = [abs(q[2][j] - q[3][j]) for q in quality]
        print(f"  |decile difference| {FEATS[k]:<10s} mean "
              f"{statistics.mean(dif):.3f}  max {max(dif)}")
    print(f"\n  {'feature':<22s} {'style mean':>11s} {'donor mean':>11s} "
          f"{'style sd':>9s} {'donor sd':>9s}")
    labels = ("log10 freq 2006-10", "chamber CV", "pre-slope 1994-2010 log/yr")
    for k in range(3):
        sv = [S[w][k] for w in match]
        dv = [F[match[w]][k] for w in match]
        print(f"  {labels[k]:<22s} {statistics.mean(sv):>11.4f} "
              f"{statistics.mean(dv):>11.4f} {statistics.pstdev(sv):>9.4f} "
              f"{statistics.pstdev(dv):>9.4f}")
    print("\n  ten pairs (seeded order):")
    for w, d, want, got, md in quality[:10]:
        print(f"    {w:<16s} -> {d:<16s} want {want} got {got}")
    # the heavy end is where a decile match can still hide a big gap, so the
    # ten style words that dominate the aggregate get their pairs printed
    print("\n  the ten commonest style words, where the aggregate lives:")
    print(f"    {'style':<16s} {'donor':<16s} {'log10 f':>9s} "
          f"{'donor log10 f':>14s} {'gap':>7s}")
    for w in sorted(match, key=lambda w: -S[w][0])[:10]:
        d = match[w]
        print(f"    {w:<16s} {d:<16s} {S[w][0]:>9.3f} {F[d][0]:>14.3f} "
              f"{F[d][0]-S[w][0]:>+7.3f}")

    # --------------------------------------------------------------- series
    donors = {match[w] for w in match}
    matched_style = set(match)

    def panel_counts(chambers, years):
        out = {}
        for y in years:
            s = d = n = 0
            for ch in chambers:
                row = D[ch].get(y, {})
                s += sum(row.get(w, 0) for w in matched_style)
                d += sum(row.get(w, 0) for w in donors)
                n += tokens[ch].get(y, 0)
            out[y] = (s, d, n)
        return out

    per_ch = {ch: {y: (sum(D[ch][y].get(w, 0) for w in matched_style),
                        sum(D[ch][y].get(w, 0) for w in donors),
                        tokens[ch][y])
                   for y in D[ch] if tokens[ch].get(y, 0) >= MW}
              for ch in all_ch}

    a3 = panel_counts(ANGLO3, a3_years)
    reg = {y: a3[y][0] / a3[y][2] * 1e5 for y in a3_years}
    don = {y: a3[y][1] / a3[y][2] * 1e5 for y in a3_years}
    dif = {y: reg[y] - don[y] for y in a3_years}
    ratio = {y: reg[y] / don[y] for y in a3_years}

    # what the (b) prune costs the style side
    ex = {y: sum(sum(n for w, n in E[ch][y]["style"].items()
                     if w in matched_style) for ch in ANGLO3) for y in a3_years}
    slip = max(abs(ex[y] - a3[y][0]) / max(1, ex[y]) for y in a3_years)
    print(f"\n  style counts from vocab_year_counts vs exact: worst-year "
          f"shortfall {slip:.2%} (the count>=2 within-chamber prune)")

    print(f"\n  {'year':<6s} {'register':>10s} {'donor':>10s} "
          f"{'difference':>11s} {'ratio':>7s}")
    for y in a3_years:
        mark = ""
        if y == trough(dif):
            mark = "  <- difference trough"
        print(f"  {y:<6s} {reg[y]:>10.1f} {don[y]:>10.1f} {dif[y]:>11.1f} "
              f"{ratio[y]:>7.3f}{mark}")

    print("\n" + "=" * 78)
    print("ONSET TEST ON THE DIFFERENCE SERIES (ANGLO3, "
          f"{a3_years[0]}-{a3_years[-1]})")
    print("=" * 78)
    print(f"  argmin (committed statistic)   register {trough(reg)}   "
          f"donor {trough(don)}   DIFFERENCE {trough(dif)}   "
          f"ratio {trough(ratio)}")
    print(f"  era means of the difference (per 100k):")
    for lo, hi in ((1994, 2005), (2006, 2013), (2014, 2017), (2018, 2022),
                   (2023, 2026)):
        ys = [y for y in a3_years if lo <= int(y) <= hi]
        if ys:
            print(f"    {lo}-{hi}  {sum(dif[y] for y in ys)/len(ys):>+8.1f}"
                  f"   (register/donor ratio "
                  f"{sum(ratio[y] for y in ys)/len(ys):.3f})")
    print(f"  an argmin on a series that is flat-with-noise before the break "
          f"picks the noisiest low year, not an onset; the two-segment fit "
          f"below is the statistic to read.")
    for name, s in (("register", reg), ("donor", don), ("difference", dif)):
        tau, b0, b1 = seg_fit(a3_years, [s[y] for y in a3_years])
        if tau is None:
            print(f"  two-segment fit  {name:<11s} did not resolve")
            continue
        print(f"  two-segment fit  {name:<11s} break {tau}   "
              f"slope before {b0:+.2f}/yr  after {b1:+.2f}/yr")

    # A second, wider panel: every chamber with an unbroken 2006-2026 run --
    # the longest window most of the corpus shares, and the one
    # constant_window_trend.py takes its endpoints from. Seventeen bootstrap
    # units instead of three, at the cost of starting after the onset.
    span = {str(y) for y in range(2006, 2027)}
    wide_ch = [ch for ch in all_ch if span <= set(per_ch[ch])]
    wide_years = sorted(span)
    rs = random.Random(SEED_BOOT)
    panels = [("ANGLO3", ANGLO3, a3_years)]
    if len(wide_years) >= 8:
        panels.append((f"WIDE-{len(wide_ch)}", wide_ch, wide_years))
    for label, chs, ys in panels:
        tal_a, tal_b = Counter(), Counter()
        for _ in range(a.reps):
            pick = [chs[rs.randrange(len(chs))] for _ in chs]
            ser = {}
            for y in ys:
                s = d = n = 0
                for ch in pick:
                    if y not in per_ch[ch]:
                        s = None
                        break
                    q = per_ch[ch][y]
                    s += q[0]
                    d += q[1]
                    n += q[2]
                if s is None:
                    continue
                ser[y] = (s - d) / n * 1e5
            if len(ser) < 8:
                continue
            tal_a[trough(ser)] += 1
            yy = sorted(ser)
            tau = seg_fit(yy, [ser[y] for y in yy])[0]
            if tau is not None:
                tal_b[tau] += 1
        tot = sum(tal_a.values())
        print(f"\n  chamber bootstrap, {tot} usable resamples of "
              f"{len(chs)} chambers, seed {SEED_BOOT}  [{label} "
              f"{ys[0]}-{ys[-1]}]")
        print(f"    difference-series argmin : " + "  ".join(
            f"{y} {c/tot:.1%}" for y, c in tal_a.most_common(5)))
        tot = max(1, sum(tal_b.values()))
        print(f"    two-segment breakpoint   : " + "  ".join(
            f"{y} {c/tot:.1%}" for y, c in tal_b.most_common(5)))
        if len(chs) < 6:
            print(f"    (only {len(chs)} chambers reach {ys[0]}; this interval "
                  f"is coarse by construction, not by choice)")

    # UK alone, the paper's own series, for the record
    uk_years = [y for y in sorted(per_ch["UK"])]
    uk = panel_counts(["UK"], uk_years)
    ureg = {y: uk[y][0] / uk[y][2] * 1e5 for y in uk_years}
    udon = {y: uk[y][1] / uk[y][2] * 1e5 for y in uk_years}
    udif = {y: ureg[y] - udon[y] for y in uk_years}
    print(f"\n  UK alone {uk_years[0]}-{uk_years[-1]}: register trough "
          f"{trough(ureg)}, donor trough {trough(udon)}, difference trough "
          f"{trough(udif)}")
    print(f"  {'year':<6s} {'register':>10s} {'donor':>10s} "
          f"{'difference':>11s}")
    for y in uk_years:
        print(f"  {y:<6s} {ureg[y]:>10.1f} {udon[y]:>10.1f} {udif[y]:>11.1f}")

    # the match set is part of the artifact's identity -- a freq,cv run and a
    # freq,cv,slope run are different counterfactuals and must not overwrite
    # each other
    tag = "" if len(IDX) == 3 else "_" + "".join(FEATS[k][0] for k in IDX)
    out = os.path.join(HERE, f"donor_series{tag}.json")
    json.dump({"match_on": [FEATS[k] for k in IDX], "match": match,
               "anglo3_years": a3_years,
               "register": reg, "donor": don, "difference": dif,
               "uk_register": ureg, "uk_donor": udon, "uk_difference": udif},
              open(out, "w"), indent=1)
    print(f"\nwrote {os.path.basename(out)}")


if __name__ == "__main__":
    main()
