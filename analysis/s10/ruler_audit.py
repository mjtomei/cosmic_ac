#!/usr/bin/env python3
"""Is the 1994-96 register onset a property of the corpus, or of the ruler?

THE OBJECTION

§4.5 runs a fixed 407-word Kobak style list backwards as a level series and
dates its rise to 1994-96. The list was selected on the post-2022 jump in
scholarly text. Selection on a recent rise is selection on a trend: a word
picked because it is high now was, on average, below its own long-run mean
earlier, so summing hundreds of such words and looking backwards produces a
rising line by construction. The committed artifacts are chamber-year
aggregates, so the objection has never been priced.

WHAT THIS ASKS, from word_year_counts.json.gz

  1. SLOPE DISTRIBUTION. Every one of the 407 words gets its own 1994-2026
     log-rate slope. If the rise is a broad register shift, the slopes are
     centred above zero and most words carry it. If it is selection, the
     aggregate can rise while the median word does nothing, with the sum
     carried by a handful of steep words. Reported as the fraction positive
     against a 50% null (sign test) and as the slope quantiles.

  2. TRIMMED AGGREGATE. The aggregate recomputed with the 10 words that
     contribute most of the level rise removed. Survival of the onset under
     trimming is the direct answer to "is this ten words or four hundred".

  3. BREADTH. Rate is one number; it moves if a few words get commoner or if
     many do. The breadth series is the RAREFIED count of distinct style words
     expected in a random 1,000-token sample of that chamber-year,
     sum_w [1-(1-p_w)^1000]. It is sample-size invariant by construction, so
     it can be compared across chamber-years of wildly different size, and it
     rises only if the set of words in use widens.

  4. THE OTHER RULER. The same onset test on the second marker set: the
     Wikipedia "signs of AI writing" up-family (tier15_wiki_signs.PATTERNS,
     33 patterns), which was derived by Wikipedia editors from AI-written
     article text -- a different corpus, a different selection route, and no
     dependence on Kobak. It is not exposed to Kobak's selection, so if 1994-96
     is a real register turn it should appear there too, and if it does not,
     the burden falls back on the instrument.

THE ONSET TEST is the committed one, reused: the turning point is the argmin
of the annual series over the years a chamber has (long_trend.py fits no curve;
long_trend_bootstrap.py calls the same argmin the point estimate). The
committed version takes the argmin of the instrument-minus-matched-placebo GAP;
that gap series already exists per chamber-year in occurrence_trends.json and
is read here as the reference point, so the trough this script reproduces can
be checked against the published one. The wiki set has no word-matched placebo
-- its members are multi-word patterns -- so the cross-instrument comparison is
run on RAW rates for both instruments, which is the apples-to-apples form.

PANELS. A pooled series whose chamber composition changes is not a trend
(occurrence_trends.py's doctrine). Three fixed panels are used:

  UK       UK Commons alone, 1985-2026 -- the paper's own §4.5 series
  ANGLO3   UK + US House + US Senate, balanced -- the only fixed panel that
           reaches 1994, and the one the per-word statistics are computed on
  ALL      every chamber, balanced -- 2006 onward only, for breadth checks

Usage: python ruler_audit.py [--min-words 200000]
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SRC = os.path.join(HERE, "word_year_counts.json.gz")
COMMITTED = os.path.join(HERE, "occurrence_trends.json")
ANGLO3 = ["UK", "US-House", "US-Senate"]
PRE = ("1994", "1995", "1996")
POST = ("2024", "2025", "2026")
N_TRIM = 10
RAREFY_N = 1000


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE,
                                                    "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def wls_slope(xs, ys, ws):
    """Weighted least squares slope of ys on xs. None if undetermined."""
    sw = sum(ws)
    if sw <= 0 or len(xs) < 3:
        return None
    mx = sum(w * x for w, x in zip(ws, xs)) / sw
    my = sum(w * y for w, y in zip(ws, ys)) / sw
    den = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    if den <= 0:
        return None
    return sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / den


def trough(series):
    """The committed onset statistic: argmin year of an annual series."""
    return min(series, key=lambda y: series[y])


def panel_years(D, chambers, min_words, lo=None, hi=None):
    """Years in which EVERY named chamber clears min_words."""
    sets = []
    for ch in chambers:
        sets.append({y for y, r in D[ch].items() if r["words"] >= min_words})
    ys = sorted(set.intersection(*sets)) if sets else []
    return [y for y in ys
            if (lo is None or y >= lo) and (hi is None or y <= hi)]


def pooled(D, chambers, years, key):
    """year -> (hits, tokens) pooled over chambers, for a per-year extractor."""
    out = {}
    for y in years:
        h = w = 0
        for ch in chambers:
            r = D[ch][y]
            h += key(r)
            w += r["words"]
        out[y] = (h, w)
    return out


def rate_series(pool):
    return {y: h / w * 1e5 for y, (h, w) in pool.items()}


def mean_over(series, years):
    got = [series[y] for y in years if y in series]
    return sum(got) / len(got) if got else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-words", type=int, default=200_000)
    a = ap.parse_args()
    MW = a.min_words

    style = load_style()
    with gzip.open(SRC, "rt") as fh:
        blob = json.load(fh)
    D = blob["chambers"]
    meta = blob["_meta"]
    print(f"read {os.path.basename(SRC)}: {len(D)} chambers, "
          f"{len(meta['style_words'])} style words, "
          f"{len(meta['wiki_patterns'])} wiki patterns\n")

    uk_years = [y for y in sorted(D["UK"]) if D["UK"][y]["words"] >= MW]
    a3_years = panel_years(D, ANGLO3, MW)
    all_ch = sorted(D)
    all_years = panel_years(D, all_ch, MW)
    if not a3_years:
        raise SystemExit("ANGLO3 panel is empty -- check --min-words")
    print(f"panels:  UK {uk_years[0]}-{uk_years[-1]} ({len(uk_years)} yrs)   "
          f"ANGLO3 {a3_years[0]}-{a3_years[-1]} ({len(a3_years)} yrs)   "
          f"ALL {len(all_ch)} chambers "
          + (f"{all_years[0]}-{all_years[-1]} ({len(all_years)} yrs)"
             if all_years else "no balanced years"))

    # ---------------------------------------------------------------- 0. check
    # The committed gap series lives in occurrence_trends.json. Its trough is
    # the published 1994. Reproducing the raw-rate trough next to it says
    # whether the placebo subtraction is doing the dating work.
    print("\n" + "=" * 78)
    print("0. THE COMMITTED ONSET, AND WHAT THE RAW RATE SAYS")
    print("=" * 78)
    committed = None
    if os.path.exists(COMMITTED):
        C = json.load(open(COMMITTED))
        gap = {str(r["year"]): r["gap"] for r in C["UK"]}
        inst = {str(r["year"]): r["instrument_per100k"] for r in C["UK"]}
        committed = set(C["_META"]["instrument_words"])
        print(f"  occurrence_trends.json  UK gap trough        {trough(gap)}"
              f"   (published 1994-96)")
        print(f"  occurrence_trends.json  UK instrument trough {trough(inst)}")
        print(f"  committed instrument is {len(committed)}"
              f" of the {len(style)} style words -- those present in UK "
              f"{'/'.join(C['_META']['base_years'])}")
        # this scan, restricted to those same 377 words, against the committed
        # series: if the pipelines agree the two columns match to rounding
        mine = rate_series(pooled(
            D, ["UK"], uk_years,
            lambda r: sum(n for w, n in r["style"].items() if w in committed)))
        d = max(abs(mine[y] - inst[y]) for y in uk_years if y in inst)
        print(f"  cross-check: this scan on the same 377 words reproduces the "
              f"committed UK series to {d:.2f} per 100k, worst year "
              f"(1994 {mine['1994']:.1f} vs {inst['1994']:.1f}; "
              f"2026 {mine['2026']:.1f} vs {inst['2026']:.1f})")

    def style_hits(r):
        return sum(r["style"].values())

    uk_raw = rate_series(pooled(D, ["UK"], uk_years, style_hits))
    a3_raw = rate_series(pooled(D, ANGLO3, a3_years, style_hits))
    print(f"\n  this scan, all {len(style)} style words, RAW rate per 100k")
    print(f"    UK      {uk_years[0]}-{uk_years[-1]}  trough {trough(uk_raw)}"
          f"   {uk_years[0]} {uk_raw[uk_years[0]]:.0f} -> "
          f"1994 {uk_raw.get('1994', float('nan')):.0f} -> "
          f"2026 {uk_raw[uk_years[-1]]:.0f}")
    print(f"    ANGLO3  {a3_years[0]}-{a3_years[-1]}  trough {trough(a3_raw)}"
          f"   {a3_years[0]} {a3_raw[a3_years[0]]:.0f} -> "
          f"2026 {a3_raw[a3_years[-1]]:.0f}")

    # -------------------------------------------------------- 1. per-word slope
    print("\n" + "=" * 78)
    print(f"1. PER-WORD LOG-RATE SLOPE, {a3_years[0]}-{a3_years[-1]}, "
          f"ANGLO3 pooled (word-weighted)")
    print("=" * 78)
    def word_slopes(chambers, years):
        """word -> (WLS log-rate slope, total hits) over a fixed panel."""
        out, hits, ser = {}, Counter(), {}
        n_by_y = {y: sum(D[ch][y]["words"] for ch in chambers) for y in years}
        for w in style:
            s = [(int(y), sum(D[ch][y]["style"].get(w, 0) for ch in chambers),
                  n_by_y[y]) for y in years]
            ser[w] = s
            hits[w] = sum(c for _, c, _ in s)
            v = wls_slope([y for y, c, n in s],
                          [math.log((c + 0.5) / n) for y, c, n in s],
                          [c + 0.5 for y, c, n in s])   # Poisson iv on log
            if v is not None:
                out[w] = v
        return out, hits, ser

    slopes, tot, wyear = word_slopes(ANGLO3, a3_years)
    uk_slopes, uk_tot, _ = word_slopes(["UK"], uk_years)
    print(f"  {'panel / subset':<26s} {'n':>4s} {'positive':>9s} {'z':>7s} "
          f"{'p10':>8s} {'median':>8s} {'p90':>8s}   (slope, %/yr)")
    for pname, sl, ht, yrs in (("ANGLO3 " + a3_years[0] + "-" + a3_years[-1],
                                slopes, tot, a3_years),
                               ("UK " + uk_years[0] + "-" + uk_years[-1],
                                uk_slopes, uk_tot, uk_years)):
        for label, ws_ in (("all present", [w for w in sl if ht[w] > 0]),
                           (">=200 hits", [w for w in sl if ht[w] >= 200])):
            n = len(ws_)
            k = sum(1 for w in ws_ if sl[w] > 0)
            z = (k - n / 2) / math.sqrt(n / 4) if n else 0.0
            q = sorted(sl[w] for w in ws_)
            pc = lambda p: (math.exp(q[min(len(q) - 1,
                                           int(p * len(q)))]) - 1) * 100
            print(f"  {pname + ', ' + label:<26s} {n:>4d} "
                  f"{k:>4d} {k/n:>5.1%} {z:>+7.1f} "
                  f"{pc(.10):>+8.2f} {pc(.50):>+8.2f} {pc(.90):>+8.2f}")
    print(f"  style words with zero hits in ANGLO3: "
          f"{sum(1 for w in style if tot[w] == 0)};  in UK: "
          f"{sum(1 for w in style if uk_tot[w] == 0)}")

    # ---------------------------------------------------- 2. trimmed aggregate
    print("\n" + "=" * 78)
    print(f"2. AGGREGATE WITH THE {N_TRIM} LARGEST POSITIVE CONTRIBUTORS "
          f"REMOVED")
    print("=" * 78)
    contrib = {}
    for w in style:
        ser = {str(y): (c, n) for y, c, n in wyear[w]}
        pre = [ser[y][0] / ser[y][1] * 1e5 for y in PRE if y in ser]
        post = [ser[y][0] / ser[y][1] * 1e5 for y in POST if y in ser]
        if pre and post:
            contrib[w] = sum(post) / len(post) - sum(pre) / len(pre)
    top = sorted(contrib, key=lambda w: -contrib[w])[:N_TRIM]
    print(f"  aggregate rise {'/'.join(PRE)} mean -> {'/'.join(POST)} mean: "
          f"{mean_over(a3_raw, POST) - mean_over(a3_raw, PRE):+.1f} per 100k")
    print(f"  {'word':<16s} {'contribution/100k':>18s} {'share of rise':>14s}")
    rise = mean_over(a3_raw, POST) - mean_over(a3_raw, PRE)
    for w in top:
        print(f"  {w:<16s} {contrib[w]:>18.1f} {contrib[w]/rise:>13.1%}")
    print(f"  {'TOP-'+str(N_TRIM):<16s} "
          f"{sum(contrib[w] for w in top):>18.1f} "
          f"{sum(contrib[w] for w in top)/rise:>13.1%}")

    keep = set(style) - set(top)

    def trimmed_hits(r):
        return sum(n for w, n in r["style"].items() if w in keep)

    def top_hits(r):
        return sum(n for w, n in r["style"].items() if w in set(top))

    tl = rate_series(pooled(D, ANGLO3, a3_years, top_hits))
    print(f"\n  those {N_TRIM} words are also most of the LEVEL, not just the "
          f"rise: {tl['1994']/a3_raw['1994']:.1%} of the instrument's rate in "
          f"1994 and {tl['2026']/a3_raw['2026']:.1%} in 2026 "
          f"({N_TRIM/len(style):.1%} of the word list)")

    a3_trim = rate_series(pooled(D, ANGLO3, a3_years, trimmed_hits))
    uk_trim = rate_series(pooled(D, ["UK"], uk_years, trimmed_hits))
    print(f"\n  {'series':<22s} {'trough':>7s} {'1994':>8s} {'2006':>8s} "
          f"{'2019':>8s} {'2026':>8s} {'2026/1994':>10s}")
    for name, s in (("ANGLO3 all 407", a3_raw), ("ANGLO3 minus top-10", a3_trim),
                    ("UK all 407", uk_raw), ("UK minus top-10", uk_trim)):
        f = lambda y: s.get(y, float("nan"))
        r = (f("2026") / f("1994")) if f("1994") == f("1994") else float("nan")
        print(f"  {name:<22s} {trough(s):>7s} {f('1994'):>8.0f} "
              f"{f('2006'):>8.0f} {f('2019'):>8.0f} {f('2026'):>8.0f} "
              f"{r:>10.2f}")

    print(f"\n  UK full series (all 407, raw per 100k) -- the §4.5 shape")
    for y in uk_years:
        bar = "#" * int(round((uk_raw[y] - min(uk_raw.values())) / 20))
        mark = "  <- trough" if y == trough(uk_raw) else ""
        print(f"    {y}  {uk_raw[y]:>7.0f}  {bar}{mark}")

    # ------------------------------------------------------------- 3. breadth
    print("\n" + "=" * 78)
    print(f"3. BREADTH: expected distinct style words per {RAREFY_N} tokens")
    print("=" * 78)

    def breadth(chambers, years):
        out = {}
        for y in years:
            n = sum(D[ch][y]["words"] for ch in chambers)
            c = Counter()
            for ch in chambers:
                c.update(D[ch][y]["style"])
            e = 0.0
            for w, k in c.items():
                p = k / n
                e += -math.expm1(RAREFY_N * math.log1p(-p)) if p < 1 else 1.0
            out[y] = e
        return out

    uk_b = breadth(["UK"], uk_years)
    a3_b = breadth(ANGLO3, a3_years)
    all_b = breadth(all_ch, all_years) if all_years else {}
    print(f"  {'year':<6s} {'UK':>8s} {'ANGLO3':>8s} {'ALL-22':>8s}")
    for y in sorted(set(uk_years) | set(a3_years) | set(all_years)):
        print(f"  {y:<6s} {uk_b.get(y, float('nan')):>8.1f} "
              f"{a3_b.get(y, float('nan')):>8.1f} "
              f"{all_b.get(y, float('nan')):>8.1f}")
    print(f"\n  breadth trough  UK {trough(uk_b)}   ANGLO3 {trough(a3_b)}"
          + (f"   ALL {trough(all_b)}" if all_b else ""))
    print(f"  UK breadth {uk_years[0]} {uk_b[uk_years[0]]:.1f} -> "
          f"1994 {uk_b.get('1994', float('nan')):.1f} -> "
          f"2026 {uk_b[uk_years[-1]]:.1f}"
          f"   (rate over the same span "
          f"x{uk_raw[uk_years[-1]]/uk_raw[uk_years[0]]:.2f})")

    # -------------------------------------------------------- 4. the other ruler
    print("\n" + "=" * 78)
    print("4. THE SAME ONSET TEST ON THE WIKIPEDIA MARKER SET")
    print("=" * 78)

    def wiki_hits(r):
        return r["wiki_total"]

    uk_w = rate_series(pooled(D, ["UK"], uk_years, wiki_hits))
    a3_w = rate_series(pooled(D, ANGLO3, a3_years, wiki_hits))
    print(f"  {'year':<6s} | {'UK kobak':>9s} {'UK wiki':>9s} | "
          f"{'A3 kobak':>9s} {'A3 wiki':>9s}")
    for y in uk_years:
        print(f"  {y:<6s} | {uk_raw[y]:>9.0f} {uk_w[y]:>9.2f} | "
              f"{a3_raw.get(y, float('nan')):>9.0f} "
              f"{a3_w.get(y, float('nan')):>9.2f}")
    print(f"\n  trough year   UK   kobak {trough(uk_raw)}   "
          f"wiki {trough(uk_w)}")
    print(f"  trough year   A3   kobak {trough(a3_raw)}   "
          f"wiki {trough(a3_w)}")

    # chamber-level trough tally, so the UK answer is not the whole answer
    tally_k, tally_w = Counter(), Counter()
    for ch in all_ch:
        ys = [y for y in sorted(D[ch]) if D[ch][y]["words"] >= MW]
        if len(ys) < 8:
            continue
        k = rate_series(pooled(D, [ch], ys, style_hits))
        v = rate_series(pooled(D, [ch], ys, wiki_hits))
        tally_k[trough(k)] += 1
        tally_w[trough(v)] += 1
    print(f"\n  per-chamber trough years (chambers with >=8 usable years)")
    print(f"    kobak: {dict(sorted(tally_k.items()))}")
    print(f"    wiki : {dict(sorted(tally_w.items()))}")

    # pre-ChatGPT log slope on each ruler, so 'rises from 1994-96' is a number
    print(f"\n  pre-ChatGPT (1994-2019) log-rate slope, %/yr")
    print(f"  {'panel':<10s} {'kobak':>10s} {'wiki':>10s}")
    for label, chs, ys in (("UK", ["UK"], uk_years), ("ANGLO3", ANGLO3,
                                                      a3_years)):
        win = [y for y in ys if "1994" <= y <= "2019"]
        out = []
        for key in (style_hits, wiki_hits):
            p = pooled(D, chs, win, key)
            xs = [int(y) for y in win]
            yy = [math.log((h + 0.5) / n) for h, n in (p[y] for y in win)]
            ww = [p[y][0] + 0.5 for y in win]
            s = wls_slope(xs, yy, ww)
            out.append((math.exp(s) - 1) * 100 if s is not None else float("nan"))
        print(f"  {label:<10s} {out[0]:>+10.2f} {out[1]:>+10.2f}")

    # which wiki patterns carry it -- the same trimming question, other ruler
    print(f"\n  wiki patterns by {'/'.join(PRE)} -> {'/'.join(POST)} change "
          f"(ANGLO3, per 100k)")
    pat = {}
    for p in meta["wiki_patterns"]:
        pre = post = None
        vals = {}
        for y in a3_years:
            h = sum(D[ch][y]["wiki"].get(p, 0) for ch in ANGLO3)
            n = sum(D[ch][y]["words"] for ch in ANGLO3)
            vals[y] = h / n * 1e5
        pre = [vals[y] for y in PRE if y in vals]
        post = [vals[y] for y in POST if y in vals]
        if pre and post:
            pat[p] = (sum(pre) / len(pre), sum(post) / len(post))
    for p in sorted(pat, key=lambda p: -(pat[p][1] - pat[p][0]))[:8]:
        print(f"    {p:<22s} {pat[p][0]:>8.3f} -> {pat[p][1]:>8.3f}"
              f"  {pat[p][1]-pat[p][0]:>+8.3f}")
    print(f"    ... {sum(1 for p in pat if pat[p][1] > pat[p][0])} of "
          f"{len(pat)} patterns higher in {'/'.join(POST)} than "
          f"{'/'.join(PRE)}")


if __name__ == "__main__":
    main()
