#!/usr/bin/env python3
"""Per-word diffusion timing: does the top status tier reach a word first?

WHY

§4.6b reads the one movement inside the stable class profile -- the lower
tiers closing on class II -- as compression in the CHASE direction, and says
so about the pooled 407-word instrument. Pooled, that reading is untestable:
a single index cannot distinguish "everyone adopted the same words at the same
time, with different amplitudes" from "the top adopted first and the bottom
followed". Diffusion has a signature the amplitude does not carry -- ORDER, per
word. If status is doing the work, high-status speakers should reach each
word's half-way point before low-status speakers do, and the lag should show
up across words, not in whichever word happens to be biggest.

So this is the lead-lag test done word by word, with the words as the units of
the paired test and each word's own two tiers as the pair.

CORPUS. member_cache_panel.json.gz. The 20 chambers whose stores run 2006-2026
continuously -- 17 provincial/state/devolved chambers plus UK Commons, the US
House and the US Senate. CA-FED and IE are EXCLUDED: their stores begin in
2015 and 2018, so including them would change the denominator's chamber mix
part-way through the very series whose timing is being measured.

RULES, chosen once and applied to every word:

  volume     a word is analysed if it occurs >= 800 times in 2018-2026 across
             those 20 chambers.
  takeoff    a word's takeoff year is the FIRST year in 2010-2026 whose
             3-year centred moving-average rate exceeds TWICE its 2006-2019
             mean rate. Words that never cross are reported as "no takeoff"
             and kept in the timing test anyway -- excluding them would select
             on the outcome.
  crossing   a tier's crossing date for a word is the year at which that
             tier's CUMULATIVE adoption -- the running sum of its yearly
             rate, 2006 forward -- reaches half its 2026 total, linearly
             interpolated inside the crossing year. Cumulating the RATE, not
             the count, keeps a tier whose speaking volume grows from looking
             like a late adopter. Read it as the word's centre of mass in
             time for that tier: earlier = adopted earlier.

TIERS. Two independent codings, both member-level and both already in the
cache:
  EGP     top = class I (higher service); bottom = IVc + V/VI + VIIab pooled
          (farmers, skilled manual, semi- and unskilled), the same pooling
          build_class_by_era.py uses for its tail.
  folk    top = argmax folk-ladder level "top"; bottom = "bottom"
          (prereg_member_table.json's lvl_* posteriors).

TEST. Paired Wilcoxon signed-rank across words on
  d(word) = crossing(bottom) - crossing(top),
one-sided, H1: d > 0 (the top tier precedes). Words are the units. The two
tiers are built from disjoint member sets, so the pairing is by word and not
by member; the member-level dependence that remains -- the same few hundred
people generate every word's curve -- is addressed by a second, member
bootstrap (seed 13) that resamples members inside each tier and re-derives
every word's crossing.

ROBUSTNESS. A level-based crossing (first year the tier's 3-year moving
average exceeds half its 2026 moving average) is reported next to the
cumulative one, because "half of the final level" and "half of the cumulative
total" are different statistics and the conclusion should not depend on which
was meant.

WRITES leadlag.txt (tee'd) and leadlag_words.csv.

Usage: python leadlag.py
"""
import csv
import gzip
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CHAMBERS = ["AB", "BC", "MB", "NL", "NS", "ON", "PE", "SK",          # Canada
            "NSW", "QLD", "SA", "TAS", "VIC", "WA",                  # Australia
            "NI", "SCO", "WAL",                                      # devolved
            "UK", "US-HOUSE", "US-SENATE"]                           # tier-1
Y0, Y1 = 2006, 2026
YEARS = list(range(Y0, Y1 + 1))
BASE = (2006, 2019)
MIN_OCC = 800
BOTTOM_EGP = {"IVc", "V/VI", "VIIab"}
NBOOT = 300
SEED = 13
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def ma3(v):
    """centred 3-year moving average, endpoints averaged over what exists."""
    out = np.empty_like(v)
    for i in range(len(v)):
        lo, hi = max(0, i - 1), min(len(v), i + 2)
        out[i] = v[lo:hi].mean()
    return out


def cum_crossing(rate):
    """year at which the running sum of `rate` reaches half its final total."""
    c = np.cumsum(rate)
    if c[-1] <= 0:
        return np.nan
    half = c[-1] / 2.0
    i = int(np.searchsorted(c, half))
    if i == 0:
        return float(YEARS[0])
    prev = c[i - 1]
    frac = (half - prev) / (c[i] - prev) if c[i] > prev else 0.0
    return YEARS[i - 1] + frac


def level_crossing(rate):
    """first year the 3-year MA exceeds half its 2026 MA value."""
    m = ma3(rate)
    if m[-1] <= 0:
        return np.nan
    tgt = m[-1] / 2.0
    for i, v in enumerate(m):
        if v >= tgt:
            if i == 0:
                return float(YEARS[0])
            prev = m[i - 1]
            frac = (tgt - prev) / (v - prev) if v > prev else 0.0
            return YEARS[i - 1] + frac
    return np.nan


def main():
    cache = json.load(gzip.open(os.path.join(HERE,
                                             "member_cache_panel.json.gz"), "rt"))
    keep = {k: r for k, r in cache.items() if k.split("|")[0] in CHAMBERS}
    say(f"cache: {len(cache):,} members, {len(keep):,} in the {len(CHAMBERS)} "
        f"continuous-coverage chambers")

    words = sorted({w for r in keep.values() for y in r["years"].values()
                    for w in y["w"]})
    widx = {w: i for i, w in enumerate(words)}
    yidx = {str(y): i for y, i in zip(YEARS, range(len(YEARS)))}

    # member x year tokens and member x word x year counts, float32
    ks = [k for k, r in keep.items()
          if any(y in yidx for y in r["years"])]
    MT = np.zeros((len(ks), len(YEARS)), np.float32)
    MC = np.zeros((len(ks), len(words), len(YEARS)), np.float32)
    egp = [keep[k]["egp"] for k in ks]
    lvl = [keep[k]["lvl"] for k in ks]
    for a, k in enumerate(ks):
        for y, v in keep[k]["years"].items():
            j = yidx.get(y)
            if j is None:
                continue
            MT[a, j] += v["tot"]
            for w, n in v["w"].items():
                MC[a, widx[w], j] += n
    say(f"members with {Y0}-{Y1} speech: {len(ks):,}  "
        f"(counts array {MC.nbytes / 1e6:.0f} MB)")

    ALL_T = MT.sum(0).astype(float)
    ALL_C = MC.sum(0).astype(float)
    occ1826 = ALL_C[:, [i for i, y in enumerate(YEARS) if y >= 2018]].sum(1)
    use = [w for w in words if occ1826[widx[w]] >= MIN_OCC]
    say(f"style words in the cache: {len(words)}; with >= {MIN_OCC} "
        f"occurrences 2018-2026 here: {len(use)}")
    say(f"panel tokens 2006-2026: {ALL_T.sum() / 1e9:.2f}B")

    # ------------------------------------------------------------- takeoff
    rate_all = ALL_C / np.maximum(ALL_T, 1) * 1e6                # per M tokens
    bi = [i for i, y in enumerate(YEARS) if BASE[0] <= y <= BASE[1]]
    takeoff = {}
    for w in use:
        r = rate_all[widx[w]]
        base = r[bi].mean()
        m = ma3(r)
        t = None
        for i, y in enumerate(YEARS):
            if y >= 2010 and base > 0 and m[i] > 2 * base:
                t = y
                break
        takeoff[w] = t
    n_to = sum(1 for w in use if takeoff[w])
    say(f"\ntakeoff (3yr MA > 2x the {BASE[0]}-{BASE[1]} mean, first year "
        f"2010-2026): {n_to}/{len(use)} words cross")
    yrs = [takeoff[w] for w in use if takeoff[w]]
    if yrs:
        say(f"  takeoff years: median {int(np.median(yrs))}, "
            f"{sum(1 for y in yrs if y >= 2023)} of {len(yrs)} in 2023-2026")
        for y in sorted(set(yrs)):
            ws = [w for w in use if takeoff[w] == y]
            say(f"    {y}: {len(ws):>3}  {', '.join(sorted(ws)[:10])}"
                f"{' ...' if len(ws) > 10 else ''}")

    # --------------------------------------------------------------- tiers
    def tier(mask):
        ix = np.flatnonzero(mask)
        return (len(ix), MT[ix].sum(0).astype(float),
                MC[ix].sum(0).astype(float), ix)

    e = np.array(egp, object)
    lv = np.array(lvl, object)
    TIERS = {
        "EGP": (("I (higher service)", tier(e == "I")),
                ("IVc+V/VI+VIIab",
                 tier(np.isin(e, sorted(BOTTOM_EGP))))),
        "folk": (("top", tier(lv == "top")), ("bottom", tier(lv == "bottom"))),
    }

    rows = []
    results = {}
    for coding, ((tn, top), (bn, bot)) in TIERS.items():
        say(f"\n{'=' * 74}\n{coding.upper()} TIERS")
        for lab, t in ((tn, top), (bn, bot)):
            say(f"  {lab:<22} {t[0]:>5,} members  "
                f"{t[1].sum() / 1e6:>8.1f}M tokens 2006-2026")
        rt = top[2] / np.maximum(top[1], 1) * 1e6
        rb = bot[2] / np.maximum(bot[1], 1) * 1e6
        d_cum, d_lvl, kept = [], [], []
        for w in use:
            i = widx[w]
            if top[2][i].sum() < 30 or bot[2][i].sum() < 30:
                continue
            ct, cb = cum_crossing(rt[i]), cum_crossing(rb[i])
            lt, lb = level_crossing(rt[i]), level_crossing(rb[i])
            if not (np.isfinite(ct) and np.isfinite(cb)):
                continue
            kept.append(w)
            d_cum.append(cb - ct)
            d_lvl.append(lb - lt if np.isfinite(lb) and np.isfinite(lt)
                         else np.nan)
            rows.append([coding, w, int(occ1826[i]),
                         takeoff[w] or "", f"{ct:.2f}", f"{cb:.2f}",
                         f"{cb - ct:+.2f}",
                         f"{lt:.2f}" if np.isfinite(lt) else "",
                         f"{lb:.2f}" if np.isfinite(lb) else "",
                         int(top[2][i].sum()), int(bot[2][i].sum())])
        d_cum = np.array(d_cum)
        d_lvl = np.array(d_lvl, float)
        say(f"\n  words tested: {len(kept)} (>= 30 occurrences in BOTH tiers)")
        to_mask = np.array([takeoff[w] is not None for w in kept])

        def report(lab, d):
            if len(d) < 5:
                say(f"  {lab}: too few words ({len(d)})")
                return
            pos, neg = int((d > 0).sum()), int((d < 0).sum())
            ties = len(d) - pos - neg
            w_ = stats.wilcoxon(d, alternative="greater", zero_method="wilcox")
            t_ = stats.ttest_1samp(d, 0, alternative="greater")
            say(f"  {lab}:")
            say(f"    d = bottom - top, in years. mean {d.mean():+.3f}  "
                f"median {np.median(d):+.3f}  sd {d.std(ddof=1):.3f}")
            say(f"    top precedes in {pos} words, bottom in {neg}, "
                f"tied in {ties}  (n = {len(d)})")
            say(f"    Wilcoxon signed-rank, one-sided (top precedes), ties "
                f"dropped: W {w_.statistic:.0f}, p = {w_.pvalue:.4f}")
            say(f"    paired t (same H1): t {t_.statistic:+.2f}, "
                f"p = {t_.pvalue:.4f}")
            results[(coding, lab)] = (d.mean(), np.median(d), w_.pvalue,
                                      len(d), pos)

        report("cumulative half-point, all words", d_cum)
        report(f"cumulative half-point, the {int(to_mask.sum())} words with a "
               f"takeoff", d_cum[to_mask])
        report("level half-of-2026 (many ties: both tiers already above half "
               "in 2006)", d_lvl[np.isfinite(d_lvl)])

        # ---------------------------------------------- member bootstrap
        rng = np.random.default_rng(SEED)
        meds = []
        ki = [widx[w] for w in kept]
        pre = [(MT[t[3]], MC[np.ix_(t[3], ki, range(len(YEARS)))])
               for t in (top, bot)]
        for _ in range(NBOOT):
            rs = []
            for tk, tc in pre:
                c = np.bincount(rng.integers(0, len(tk), len(tk)),
                                minlength=len(tk)).astype(np.float32)
                T = c @ tk
                C = np.tensordot(c, tc, axes=1)
                rs.append(C / np.maximum(T, 1) * 1e6)
            dd = [b - a for a, b in
                  ((cum_crossing(rs[0][i]), cum_crossing(rs[1][i]))
                   for i in range(len(ki)))
                  if np.isfinite(a) and np.isfinite(b)]
            if dd:
                meds.append(np.median(dd))
        if meds:
            lo, hi = np.percentile(meds, [2.5, 97.5])
            say(f"  member bootstrap ({NBOOT} draws, seed {SEED}) on the "
                f"median d: [{lo:+.3f}, {hi:+.3f}]  "
                f"(share > 0: {np.mean(np.array(meds) > 0):.3f})")

        # ------------------------------------ within-chamber, mix-controlled
        # The two tiers sit in different chambers in different proportions,
        # and chambers took off at different dates, so the pooled lead could
        # be a chamber-mix artifact. Redo it inside each chamber that has
        # enough of both tiers, and pool the per-(chamber, word) differences.
        chn = np.array([k.split("|")[0] for k in ks])
        per_ch, ch_rows = [], []
        for c in CHAMBERS:
            it = top[3][chn[top[3]] == c]
            ib = bot[3][chn[bot[3]] == c]
            if len(it) < 20 or len(ib) < 12:
                continue
            r1 = MC[it].sum(0) / np.maximum(MT[it].sum(0), 1) * 1e6
            r2 = MC[ib].sum(0) / np.maximum(MT[ib].sum(0), 1) * 1e6
            dd = []
            for w in kept:
                i = widx[w]
                if MC[it, i].sum() < 20 or MC[ib, i].sum() < 20:
                    continue
                a, b = cum_crossing(r1[i]), cum_crossing(r2[i])
                if np.isfinite(a) and np.isfinite(b):
                    dd.append(b - a)
            if len(dd) >= 20:
                ch_rows.append((c, len(it), len(ib), len(dd),
                                float(np.median(dd))))
                per_ch += dd
        if ch_rows:
            say(f"\n  WITHIN-CHAMBER (chamber mix held fixed): "
                f"{len(ch_rows)} chambers qualify")
            say(f"    {'chamber':<10}{'nTop':>6}{'nBot':>6}{'words':>7}"
                f"{'median d':>10}")
            for c, a, b, n, m in ch_rows:
                say(f"    {c:<10}{a:>6}{b:>6}{n:>7}{m:>+10.3f}")
            pc = np.array(per_ch)
            w_ = stats.wilcoxon(pc, alternative="greater",
                                zero_method="wilcox")
            say(f"    pooled over {len(pc)} chamber-word pairs: "
                f"mean {pc.mean():+.3f}  median {np.median(pc):+.3f}  "
                f"Wilcoxon p = {w_.pvalue:.4f}")
            cm = np.array([r[4] for r in ch_rows])
            say(f"    chambers with a positive median: "
                f"{int((cm > 0).sum())}/{len(cm)}"
                + (f"  (sign test p = "
                   f"{stats.binomtest(int((cm > 0).sum()), len(cm), 0.5, alternative='greater').pvalue:.4f})"
                   if len(cm) >= 5 else ""))

    with open(os.path.join(HERE, "leadlag_words.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["coding", "word", "occ_2018_2026", "takeoff_year",
                    "cross_top", "cross_bottom", "d_bottom_minus_top",
                    "level_cross_top", "level_cross_bottom",
                    "occ_top", "occ_bottom"])
        w.writerows(rows)

    say(f"\n{'=' * 74}\nREADING. d > 0 means the bottom tier's centre of mass "
        f"falls LATER than the")
    say("top tier's -- the top reached the word first, the chase direction. "
        "d < 0")
    say("means the bottom got there first. The test is across words; with a "
        "few")
    say("hundred words and one shared corpus behind both tiers, treat a "
        "p near")
    say("0.05 as suggestive, not as a diffusion measurement.")
    open(os.path.join(HERE, "leadlag.txt"), "w").write("\n".join(OUT) + "\n")
    print("\nwrote leadlag.txt, leadlag_words.csv")


if __name__ == "__main__":
    main()
