#!/usr/bin/env python3
"""Prevalence with the bands recombined, word-weighted first.

WHY WORD-WEIGHTED IS THE HEADLINE

A segment is not a natural unit: `segment.py` packs speaker turns into windows
of at most 360 words, so a long speech becomes three segments and a short
interjection becomes one. Weighting by segments therefore measures our packer
as much as the record. Weighting by words asks "what share of what was said is
machine-drafted", which is the question, and is invariant to how the text was
cut up. Segment-weighted is reported alongside because the sampling frame is
built from segments, never alone.

HOW THE BANDS RECOMBINE

Each band was sampled at the SAME rate from its chamber-era pool, so the
combined sample is self-weighting and no reweighting constants are needed. But
that is only true within a chamber-era: pooling across chambers still has to
respect that chambers differ in size and in how much of their record sits in
each band. So the pooled figure is computed by summing flagged words and total
words across the whole sample, which is the design-based estimator here.

WHAT IS STILL OUTSIDE

Text under 50 words -- 3.5% of the record -- which Pangram refuses outright,
and translated segments. See corpus_audit.py. Those bound any prevalence figure
this study reports and no sampling narrows them.

Usage: python banded_prevalence.py
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLAG = ("AI", "Mixed")

# A FLAGGED SEGMENT IS NOT UNIFORMLY FLAGGED.
#
# Word-weighting fixed "a segment is not a natural unit". It did not fix "a
# flagged segment is not entirely machine-written". A Mixed verdict is Pangram
# reporting that part of the segment is human, and counting all of its words as
# machine over-states the rate by a third: 12.03% against 9.03% pooled.
#
# So every flagged segment is weighted by its own AI fraction. Sources, in
# order of preference:
#   1. the `fraction_ai` column, recorded for the 1,431 API-scored rows;
#   2. fraction_ai_harvested.json, read off the dashboard one result at a time
#      for all 132 Mixed segments the API did not cover;
#   3. AI_CONST for AI verdicts, which are effectively a constant -- 0.9965
#      over 148 API rows and 1.0000 over 19 scraped, lowest value anywhere 0.81.
# Human verdicts are 0.0 exactly in every one of the 1,246 recorded cases.
AI_CONST = 0.9965
_HARVEST = os.path.join(HERE, "fraction_ai_harvested.json")
HARVESTED = json.load(open(_HARVEST)) if os.path.exists(_HARVEST) else {}

# Row ids whose AI fraction had to be imputed. Populated by ai_fraction() as
# load() runs, so it can never drift from what the estimator actually did.
IMPUTED = []


def ai_fraction(row_id, verdict, recorded=None):
    """Share of a segment's words that are machine-written."""
    if recorded not in (None, ""):
        return float(recorded)
    if row_id in HARVESTED:
        return HARVESTED[row_id]
    if verdict == "AI":
        return AI_CONST
    if verdict == "Mixed":
        # UNREACHED. Every Mixed segment in the study carries a measured
        # fraction; `python banded_prevalence.py --imputed` reports 0 and is
        # instrumented from inside load(), so it cannot drift from what the
        # estimator actually did.
        #
        # Kept as a guard rather than an assertion because a new arm will
        # arrive with unharvested rows, and the failure should be a countable
        # number rather than a crash. HOW TO HARVEST, since it is not obvious:
        # the detail panel is reachable at
        #     /history?history=<uuid>
        # and each row's uuid sits in its React fiber, under `historyData`, on
        # the <p> holding the file name. Filter the list to Mixed, walk the
        # fibers, collect the uuids, then navigate straight to each panel.
        # Clicking the rows does not work -- the handler swallows the event
        # roughly two times in three.
        #
        # DO NOT USE `historyData.prediction_prob` AS THE FRACTION. It is the
        # document-level AI probability, not the share of words flagged, and
        # the two diverge badly: caprev013 reads 0.674 there against 75% on
        # the gauge, caprev061 0.518 against 72%. Only the gauge figure is the
        # fraction this estimator wants.
        IMPUTED.append(row_id)
        return 0.4351
    return 0.0


def norm(ch):
    """Chamber labels are not consistent across files: pangram_p4_verdicts.csv
    writes US-HOUSE/US-SENATE, the short-band manifest writes US-House/
    US-Senate. Left unnormalised the US short band silently fails to join and
    both chambers report a banding ratio of exactly 1.0, which looks like a
    finding rather than a bug."""
    return (ch or "").strip().upper()


# Filled by load(): META[i] is the date and row id of the i-th returned row.
# It is a side table rather than a seventh tuple element because consumers
# unpack positionally and a silent arity change surfaces as a wrong number
# rather than an error. Internally load() carries (tuple, meta) PAIRS so that
# any filtering moves both together -- a first version kept a parallel array
# and the Manitoba replacement dropped rows from one side only, misaligning
# every date after MB.
#
# sample_years.py reads this, so the record of which text is in each sample
# cannot drift from what the estimator actually loaded.
META = []


def load():
    """-> rows of (chamber, era, band, n_words, flagged, ai_fraction)

    Also refills META with {"date", "id"} per row, in the same order.
    """
    recs = []
    p4 = os.path.join(HERE, "pangram_p4_verdicts.csv")
    for r in csv.DictReader(open(p4)):
        if r.get("stratum") not in ("prev", "ctl"):
            continue
        if not r.get("pangram") or not r.get("n_words"):
            continue
        if norm(r.get("chamber")) == "TAS":          # regime-flagged, excluded
            continue
        # Federal Canada's rows in this file are ALL arm='genre' -- 60 each
        # from Statements by Members, Government Orders and Oral Questions.
        # That is a good instrument for the genre question in 4.3 and a bad
        # sample of a chamber: it imposes a genre mix instead of observing
        # one, and it leaves 25.6% of the chamber's in-band record (Private
        # Members' Business, Adjournment Proceedings, Routine Proceedings,
        # the Throne Speech reply) in no stratum at all. The chamber row is
        # taken from the uniform draw below instead; these rows stay where
        # they belong, in 4.3.
        if norm(r.get("chamber")) == "CA-FED":
            continue
        recs.append(((norm(r["chamber"]), r["stratum"], "long",
                      int(r["n_words"]), r["pangram"] in FLAG,
                      ai_fraction(r["file"].split(".")[0], r["pangram"],
                                  r.get("fraction_ai"))),
                     {"date": (r.get("date") or "")[:10], "id": r.get("file")}))
    # UK and Ireland long bands, from the four-chamber arm's dashboard rescore.
    # All 360 agreed 360/360 with the originals.
    ch = os.path.join(HERE, "pangram_ch_p4_verdicts.csv")
    CHMAP = {"UK House of Commons": "UK", "Dail Eireann": "IE"}
    if os.path.exists(ch):
        for r in csv.DictReader(open(ch)):
            k = CHMAP.get(r["chamber"])
            if k:
                recs.append(((k, r["stratum"], "long", int(r["n_words"]),
                              r["pangram"] in FLAG,
                              ai_fraction(r["id"], r["pangram"])),
                             {"date": (r.get("date") or "")[:10],
                              "id": r.get("id")}))

    # Federal Canada's chamber row: the uniform draw from the same
    # four-chamber arm -- 120 prevalence and 60 control at 120-360 words,
    # sampled uniformly at random with no genre stratification, exactly as
    # the other nineteen chambers were. Its short band already matches it:
    # 120 x 15,236/18,029 = 101, and 101 is what was scored.
    #
    # Its tier was unrecorded until 2026-08-13 and is now established from the
    # Pangram dashboard's own history, which lists dashboard-submitted checks
    # and only those. Verified in both directions before being relied on --
    # a known-API file (ansctl) is absent from the history while a known-web
    # file (ansprev) is present, and every caprev/cactl row is present. See
    # tier_audit.py.
    #
    # The UK/IE short-band rows in that same file (uk/ie/cashrt, 40 each) are
    # NOT loaded here: the short band comes from the matched-rate draw in
    # pangram_shortband_verdicts.csv, and adding both would double-count.
    chu = os.path.join(HERE, "pangram_ch_verdicts.csv")
    if os.path.exists(chu):
        for r in csv.DictReader(open(chu)):
            if r["chamber"] != "Canada House of Commons":
                continue
            # cafedctl2* are the seven controls redrawn 2026-08-13 to replace
            # rows dated past the 2022-06-30 era cutoff (build_cafed_ctl_redraw.py).
            if not r["file"].startswith(("caprev", "cactl", "cafedctl2")):
                continue                       # skips the superseded cashrt
            recs.append((("CA-FED", r["stratum"], "long", int(r["n_words"]),
                          r["pangram"] in FLAG,
                          ai_fraction(r["file"], r["pangram"])),
                         {"date": (r.get("date") or "")[:10],
                          "id": r.get("file")}))

    # Manitoba was rescored 2026-08-13 after a speaker-prefix bug was found to
    # have cost its frame 42% of the record. The redraw REPLACES its old rows
    # rather than adding to them -- the old sample is a draw from a different
    # (incomplete) frame and pooling the two would average a biased estimate
    # with an unbiased one.
    mb = os.path.join(HERE, "pangram_mb_redraw_verdicts.csv")
    mb_new = os.path.exists(mb)
    if mb_new:
        # Filtering the PAIRS, not a bare tuple list. An earlier version kept
        # dates in a parallel array and dropped MB from one side only, which
        # silently misaligned every date after Manitoba.
        recs = [x for x in recs if x[0][0] != "MB"]
        for r in csv.DictReader(open(mb)):
            recs.append((("MB", r["era"], r["band"], int(r["n_words"]),
                          r["pangram"] in FLAG,
                          ai_fraction(r["id"], r["pangram"])),
                         {"date": (r.get("date") or "")[:10],
                          "id": r.get("id")}))

    sb = os.path.join(HERE, "pangram_shortband_verdicts.csv")
    if os.path.exists(sb):
        for r in csv.DictReader(open(sb)):
            if norm(r["chamber"]) == "TAS":
                continue
            if mb_new and norm(r["chamber"]) == "MB":
                continue          # superseded by the redraw
            recs.append(((norm(r["chamber"]), r["era"], r["band"],
                          int(r["n_words"]), r["pangram"] in FLAG,
                          ai_fraction(r["id"], r["pangram"])),
                         {"date": (r.get("date") or "")[:10],
                          "id": r.get("id")}))
    META.clear()
    META.extend(m for _, m in recs)
    return [t for t, _ in recs]


def rate(rows):
    """-> n, flagged, seg rate, words, machine words, WORD RATE.

    The machine-word count weights each segment by its own AI fraction, so a
    Mixed segment at 0.38 contributes 38% of its words and not all of them.
    """
    n = len(rows)
    k = sum(1 for r in rows if r[4])
    w = sum(r[3] for r in rows)
    wk = sum(r[3] * r[5] for r in rows)
    return n, k, (k / n if n else 0), w, wk, (wk / w if w else 0)


def boot_ci(rows, seed=0, n=20000):
    """95% CI for a WORD-WEIGHTED rate, resampling segments.

    A Wilson interval is wrong here twice over: it assumes a binomial on
    segments, and the estimator is a ratio of two random sums (flagged words
    over total words) whose numerator and denominator move together. Resampling
    segments with replacement and recomputing the ratio carries both the
    flag variance and the length variance, which is what makes a chamber whose
    single flagged segment happens to be 900 words show an honestly wider
    interval than one whose flag is 130 words.
    """
    import random
    if not rows:
        return (0.0, 0.0)
    rng = random.Random(seed)
    m = len(rows)
    out = []
    for _ in range(n):
        w = k = 0
        for _ in range(m):
            r = rows[rng.randrange(m)]
            w += r[3]
            k += r[3] * r[5]
        out.append(k / w if w else 0.0)
    out.sort()
    return (out[int(.025 * n)], out[int(.975 * n)])


def table(rows):
    """Per-chamber word-weighted prevalence over every scored band."""
    prev = [r for r in rows if r[1] == "prev"]
    print("\n\nPREVALENCE, WORD-WEIGHTED, ALL SCORED BANDS, 2025-26\n")
    print(f"  {'chamber':<11s} {'flagged w':>11s} {'total w':>10s} "
          f"{'rate':>7s} {'95% CI':>16s} {'segs':>6s}")
    out = []
    for ch in sorted({r[0] for r in prev}):
        c = [r for r in prev if r[0] == ch]
        n, k, sr, w, wk, wr = rate(c)
        lo, hi = boot_ci(c, seed=abs(hash(ch)) % 10000)
        out.append((ch, wr, lo, hi, n, w, wk))
    for ch, wr, lo, hi, n, w, wk in sorted(out, key=lambda x: -x[1]):
        print(f"  {ch:<11s} {wk:>11,.0f} {w:>10,} {100*wr:>6.1f}% "
              f"{'[' + format(100*lo, '.1f') + ', ' + format(100*hi, '.1f') + ']':>16s} "
              f"{n:>6d}")
    # Pool ONLY chambers with every band scored: a chamber missing its
    # highest-rate band is not a low-prevalence chamber, it is an incompletely
    # measured one, and including one adds low-rate short segments with no
    # high-rate long segments behind them. This excluded UK and Ireland until
    # 2026-08-13, costing 0.23pp (11.50% against 11.73%); both now have
    # Pangram 4 long bands and the guard passes them. It is kept because it is
    # derived from the data rather than a hardcoded list, so the next chamber
    # scored out of order cannot slip in half-measured.
    full = {ch for ch in {r[0] for r in prev}
            if any(r[2] == "long" for r in prev if r[0] == ch)}
    part = sorted({r[0] for r in prev} - full)
    pool = [r for r in prev if r[0] in full]
    n, k, sr, w, wk, wr = rate(pool)
    lo, hi = boot_ci(pool, seed=7)
    print(f"\n  POOLED {100*wr:.2f}% [{100*lo:.2f}, {100*hi:.2f}]  "
          f"({wk:,.0f} of {w:,} words, {n:,} segments, {len(full)} chambers)")
    if part:
        print(f"  excluded from the pool, short/over band only: "
              f"{', '.join(part)}")
    return out


def imputed_report():
    """Which Mixed segments the ESTIMATOR imputes, and what it costs.

    Scoped to what load() actually consumes. An earlier version globbed every
    verdict file and reported 127, which swept in the New Brunswick route
    cross-check and the superseded UK/Irish rows -- neither of which the
    estimator reads. A fallback that is never inspected becomes an assumption;
    one that is inspected against the wrong denominator is worse.
    """
    load()                       # populates IMPUTED as a side effect
    print(f"MIXED SEGMENTS THE ESTIMATOR IMPUTES: {len(IMPUTED)}\n")
    for rid in sorted(set(IMPUTED)):
        print(f"  {rid}")
    meas = [v for k, v in HARVESTED.items() if k.startswith("caprev")]
    if IMPUTED and meas:
        print(f"\n  Imputed at 0.4351. The {len(meas)} measured caprev "
              f"fractions average {sum(meas)/len(meas):.3f}, so the "
              f"imputation is conservative.")


def main():
    if "--imputed" in sys.argv:
        return imputed_report()
    rows = load()
    print("PREVALENCE BY BAND, 2025-26 window (TAS excluded)\n")
    print(f"  {'band':<8s} {'segments':>9s} {'flagged':>8s} {'seg-wtd':>9s} "
          f"{'words':>11s} {'WORD-WTD':>10s}")
    prev = [r for r in rows if r[1] == "prev"]
    for band in ("short", "long", "over"):
        s = [r for r in prev if r[2] == band]
        if not s:
            print(f"  {band:<8s} {'not yet scored':>38s}")
            continue
        n, k, sr, w, wk, wr = rate(s)
        print(f"  {band:<8s} {n:>9,} {k:>8d} {100*sr:>8.2f}% {w:>11,} "
              f"{100*wr:>9.2f}%")
    n, k, sr, w, wk, wr = rate(prev)
    print(f"  {'ALL':<8s} {n:>9,} {k:>8d} {100*sr:>8.2f}% {w:>11,} "
          f"{100*wr:>9.2f}%")

    ctl = [r for r in rows if r[1] == "ctl"]
    cn, ck_, csr, cw, cwk, cwr = rate(ctl)
    print(f"\n  pre-AI controls: {ck_}/{cn:,} segments, "
          f"{cwk:,.0f}/{cw:,} machine words")

    print("\n\nTHE BANDING CORRECTION, WORD-WEIGHTED\n")
    lo = [r for r in prev if r[2] == "long"]
    _, _, _, lw, lwk, lwr = rate(lo)
    _, _, _, aw, awk, awr = rate(prev)
    print(f"  long band alone (what the study reported): {100*lwr:.2f}%")
    print(f"  all scored bands combined:                 {100*awr:.2f}%")
    if lwr:
        print(f"  -> the reported figure is {lwr/awr:.2f}x the combined one")

    print("\n\nPER CHAMBER, WORD-WEIGHTED, 2025-26\n")
    print(f"  {'chamber':<10s} {'long only':>10s} {'combined':>10s} "
          f"{'ratio':>7s} {'short % of sampled words':>26s}")
    chs = sorted({r[0] for r in prev})
    for ch in chs:
        c = [r for r in prev if r[0] == ch]
        cl = [r for r in c if r[2] == "long"]
        cs = [r for r in c if r[2] != "long"]
        if not cl:
            _, _, _, ws, ks, rs = rate(cs)
            print(f"  {ch:<10s} {'--':>9s}  {100*rs:>8.2f}% {'n/a':>7s} "
                  f"{'short band only -- no Pangram 4 long band':>25s}")
            continue
        _, _, _, w1, k1, r1 = rate(cl)
        _, _, _, w2, k2, r2 = rate(c)
        sw = sum(r[3] for r in cs)
        ratio = f"{r1/r2:.1f}x" if r2 else "inf"
        print(f"  {ch:<10s} {100*r1:>9.2f}% {100*r2:>9.2f}% {ratio:>7s} "
              f"{100*sw/w2:>25.1f}%")


if __name__ == "__main__":
    main()
