#!/usr/bin/env python3
"""Is the sample rate really uniform across segment lengths, per chamber?

THE CLAIM BEING CHECKED

The study reports one unbanded prevalence rate and says the sample carries the
corpus's own length mix, so no length weights are needed. That claim rests
entirely on the sampling rate being the SAME in every length band within a
chamber. If a band was under-drawn somewhere, the pooled figure quietly becomes
a weighted average with the wrong weights, and the error is invisible in the
output because nothing about a self-weighting estimator announces that it has
stopped being self-weighting.

WHAT COUNTS AS A GAP, AND WHAT DOES NOT

Most chambers have ZERO scored segments over 360 words. That is not
automatically a defect. Over-360 text is 0.4% of segments corpus-wide, so a
chamber drawing 120 long-band segments should draw well under one over-360
segment at the same rate, and zero is then the correct outcome of an honest
draw rather than an omission.

The test is therefore not "did we score any" but "does the number we scored
match what the chamber's own long-band rate implies". This computes, per
chamber and band:

    implied = n_long_scored * (population_in_band / population_in_long)

and flags a gap only where implied is at least 1 and the scored count falls
materially short of it. A chamber whose implied draw is 0.3 and whose scored
count is 0 is correctly sampled.

WHAT REMAINS OUT OF REACH REGARDLESS

Under 50 words: Pangram refuses to score it. Unmeasurable, not unmeasured.
Translated text: excluded by design, since a translator's register is not a
member's. Both are reported here so the reachable share is stated rather than
implied.

Usage: python band_coverage_check.py
"""
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import banded_prevalence as BP              # noqa: E402
import build_pangram_expansion as BX        # noqa: E402

BANDS = ("short", "long", "over")


def band_of(n):
    if 50 <= n < 120:
        return "short"
    if 120 <= n <= 360:
        return "long"
    if n > 360:
        return "over"
    return "under50"


def population():
    """chamber -> band -> segment count, over the 2025-26 prevalence frame."""
    pop = defaultdict(lambda: defaultdict(int))
    unreach = defaultdict(lambda: defaultdict(int))
    # The sixteen provincial/state chambers carry their chamber in `prov`. The
    # other five do not -- UK, Ireland and federal Canada were built by their
    # own extractors with no `prov` field, and the two US chambers say
    # chamber='HOUSE'/'SENATE'. Mapping them by FILE is what makes those five
    # resolvable; keying on `prov` alone silently drops exactly the chambers
    # where the over-360 population is concentrated.
    byfile = {"uk/segments_uk_deep.jsonl": "UK",
              "uk/segments_uk_2023.jsonl": "UK",
              "ie/segments_ie_en.jsonl": "IE",
              "ca/segments_ca2.jsonl": "CA-FED",
              "us/segments_us_house.jsonl": "US-HOUSE",
              "us/segments_us_senate.jsonl": "US-SENATE"}
    files = [(p, None) for p in sorted(glob.glob(
        os.path.join(HERE, "provinces", "segments_*.jsonl")))]
    files += [(os.path.join(HERE, rel), ch) for rel, ch in byfile.items()]
    seen = set()
    for path, forced in files:
        if not os.path.exists(path):
            continue
        for line in open(path):
            d = json.loads(line)
            sid = d.get("seg_id")
            if sid in seen:
                continue
            seen.add(sid)
            if BX.era_of(d["date"]) != "prev":
                continue
            ch = forced or BP.norm(d.get("prov") or "?")
            if ch == "TAS":
                continue
            n = d.get("n_words") or 0
            if d.get("translated"):
                unreach[ch]["translated"] += 1
                continue
            if not d.get("scoreable") or n < 50:
                unreach[ch]["under50"] += 1
                continue
            b = band_of(n)
            if b != "under50":
                pop[ch][b] += 1
    return pop, unreach


def main():
    scored = defaultdict(lambda: defaultdict(int))
    for ch, era, band, nw, fl, fr in BP.load():
        if era == "prev":
            scored[ch][band] += 1

    pop, unreach = population()

    print("SAMPLING RATE BY BAND, per chamber, prevalence frame\n")
    print("  A gap is a band whose IMPLIED draw is >=1 but which was scored")
    print("  materially short. Zero scored against an implied 0.4 is correct.\n")
    print(f"  {'chamber':<10}{'band':>6}{'pop':>9}{'scored':>8}"
          f"{'implied':>9}   {'':<8}")
    gaps = []
    for ch in sorted(scored):
        nl_s, nl_p = scored[ch]["long"], pop[ch]["long"]
        if not nl_p:
            print(f"  {ch:<10}  no population found -- check the file mapping")
            continue
        for b in BANDS:
            imp = nl_s * pop[ch][b] / nl_p
            got = scored[ch][b]
            # 0.8 rather than 0.5. A band drawn at four fifths of its rate is
            # already a weighting error, and the threshold has to be tight
            # enough to catch a shortfall that never reaches zero -- a band
            # scored 101 against an implied 152 is the case this is for, and a
            # half-rate threshold waves it through.
            flag = ""
            if b != "long" and imp >= 1.0 and got < 0.8 * imp:
                flag = "<-- GAP"
                gaps.append((ch, b, got, imp))
            print(f"  {ch:<10}{b:>6}{pop[ch][b]:>9,}{got:>8}{imp:>9.1f}   {flag}")
        print()

    print("=" * 62)
    if gaps:
        print(f"\n{len(gaps)} BAND GAP(S)\n")
        for ch, b, got, imp in gaps:
            print(f"  {ch} {b}: scored {got}, implied {imp:.1f}")
    else:
        print("\nNO BAND GAPS. Every band is scored at or above the rate its")
        print("chamber's own long band implies, so the pooled estimate is")
        print("self-weighting across length and needs no length correction.")

    # ---- the check that does not depend on the sampling rate being right ----
    #
    # Everything above asks whether the draw MATCHED the corpus. This asks what
    # the answer would be if it did not: re-estimate each chamber with each
    # band weighted by its share of the chamber's corpus WORDS rather than by
    # its share of the sample. Where the sample is self-weighting the two
    # agree, and the size of any disagreement is the size of the problem.
    print("\n" + "=" * 62)
    print("\nPOST-STRATIFIED CHECK -- band weights from the corpus, not the sample\n")
    wsum = defaultdict(lambda: defaultdict(float))
    ksum = defaultdict(lambda: defaultdict(float))
    for ch, era, band, nw, fl, fr in BP.load():
        if era != "prev":
            continue
        wsum[ch][band] += nw
        ksum[ch][band] += nw * fr
    # corpus words per band, approximated by population x band midpoint; the
    # midpoint is exact enough because it cancels in the ratio for any band
    # whose sample already matches.
    MID = {"short": 85, "long": 240, "over": 600}
    print(f"  {'chamber':<10}{'as sampled':>12}{'post-strat':>12}{'diff':>8}")
    worst = []
    for ch in sorted(wsum):
        w = sum(wsum[ch][b] for b in BANDS)
        k = sum(ksum[ch][b] for b in BANDS)
        if not w:
            continue
        naive = k / w
        num = den = 0.0
        for b in BANDS:
            if not wsum[ch][b]:
                continue
            cw = pop[ch][b] * MID[b]                 # corpus words in band
            num += cw * (ksum[ch][b] / wsum[ch][b])  # band rate x corpus words
            den += cw
        if not den:
            continue
        ps = num / den
        worst.append((abs(ps - naive), ch, naive, ps))
        print(f"  {ch:<10}{100*naive:>11.2f}%{100*ps:>11.2f}%"
              f"{100*(ps-naive):>+7.2f}")
    worst.sort(reverse=True)
    print(f"\n  largest divergence: {worst[0][1]} "
          f"{100*worst[0][2]:.2f}% -> {100*worst[0][3]:.2f}%")

    tot_p = sum(pop[c][b] for c in pop for b in BANDS)
    tot_u = sum(unreach[c][k] for c in unreach for k in ("under50", "translated"))
    u50 = sum(unreach[c]["under50"] for c in unreach)
    tr = sum(unreach[c]["translated"] for c in unreach)
    print(f"\nOUT OF REACH REGARDLESS: {tot_u:,} of {tot_p + tot_u:,} segments "
          f"({100*tot_u/(tot_p+tot_u):.1f}%)")
    print(f"  under 50 words  {u50:>9,}   Pangram refuses to score it")
    print(f"  translated      {tr:>9,}   excluded by design")


if __name__ == "__main__":
    main()
