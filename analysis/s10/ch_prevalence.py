#!/usr/bin/env python3
"""Per-chamber Pangram calibration and prevalence (Ireland / Canada / UK).

Three strata per chamber, all drawn uniformly at random (no screen
stratification, unlike the New Brunswick pilot — so these are plain
design-based estimates with no weighting assumptions):

  ctl   60 segments, pre-2023, 120-360 words   -> specificity
  prev 120 segments, 2025-26,  120-360 words   -> prevalence, long band
  shrt  40 segments, 2025-26,   50-119 words   -> prevalence, short band

The short band exists because the first sample used a 120-word floor that
excludes ~46% of segments, and AI-flag rate rises with segment length. A
combined estimate over the whole >=50-word pool is only defensible once the
excluded band is measured, so it is measured rather than assumed.

Two combined estimates are reported and they answer different questions:
  segment-weighted  - what share of SEGMENTS is AI-flagged
  word-weighted     - what share of SPOKEN WORDS is AI-flagged
The word-weighted figure is the one comparable to a "share of the record"
claim; the segment-weighted one is comparable to the NB pilot.

Usage: python ch_prevalence.py
"""
import collections
import csv
import json
import math
import os

SEG = {"ie": "ie/segments_ie_en.jsonl", "ca": "ca/segments_ca_en.jsonl",
       "uk": "uk/segments_uk.jsonl"}
NAME = {"ie": "Dail Eireann", "ca": "Canada House of Commons",
        "uk": "UK House of Commons"}
POST_MIN = "2025-01-01"
CACHE = "ch_pool_sizes.json"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pool_sizes():
    """Segment and word counts of the post-window pool, split at 120 words.

    These are the stratum weights; they come from the full corpus, not the
    sample, which is what makes a stratified estimate design-based.
    """
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    out = {}
    for code, path in SEG.items():
        acc = {"short_n": 0, "short_w": 0, "long_n": 0, "long_w": 0}
        for line in open(path):
            d = json.loads(line)
            if (d.get("date", "") < POST_MIN or not d.get("scoreable")
                    or d.get("translated")):
                continue
            w = d["n_words"]
            k = "short" if w < 120 else "long"
            acc[k + "_n"] += 1
            acc[k + "_w"] += w
        out[code] = acc
        print(f"  pooled {code}: {acc['short_n']:,} short / "
              f"{acc['long_n']:,} long segments", flush=True)
    json.dump(out, open(CACHE, "w"), indent=1)
    return out


def rate(rows, mixed_counts):
    """Flag rate. mixed_counts decides whether Mixed counts as a hit."""
    if not rows:
        return None
    k = sum(r["pangram"] == "AI" or (mixed_counts and r["pangram"] == "Mixed")
            for r in rows)
    return k, len(rows)


def main():
    rows = [r for r in csv.DictReader(open("pangram_ch_verdicts.csv"))
            if r.get("pangram")]
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["code"], r["stratum"])].append(r)

    print("Stratum pool sizes (weights come from the full corpus):")
    pools = pool_sizes()
    print()

    for code in ("ie", "ca", "uk"):
        ctl, prev, shrt = (by.get((code, s), []) for s in ("ctl", "prev", "shrt"))
        if not (ctl or prev):
            continue
        print(f"=== {NAME[code]} ===")

        if ctl:
            k, n = rate(ctl, True)
            lo, hi = wilson(k, n)
            print(f"  specificity   {n - k}/{n} Human   "
                  f"false-positive rate {k / n:.1%} [{lo:.1%}, {hi:.1%}]")

        for label, sub, band in (("long  120-360w", prev, "long"),
                                 ("short  50-119w", shrt, "short")):
            if not sub:
                print(f"  {label}   not yet measured")
                continue
            for tag, mixed in (("AI     ", False), ("AI+Mixed", True)):
                k, n = rate(sub, mixed)
                lo, hi = wilson(k, n)
                print(f"  {label}  {tag} {k:3d}/{n:3d} = {k / n:6.1%} "
                      f"[{lo:.1%}, {hi:.1%}]")

        # combined over the whole >=50-word pool, both weightings
        if prev and shrt:
            p = pools[code]
            for tag, mixed in (("AI", False), ("AI+Mixed", True)):
                kl, nl = rate(prev, mixed)
                ks, ns = rate(shrt, mixed)
                pl, ps = kl / nl, ks / ns
                for wt, wl, ws in (("segment", p["long_n"], p["short_n"]),
                                   ("word", p["long_w"], p["short_w"])):
                    tot = wl + ws
                    est = (pl * wl + ps * ws) / tot
                    # stratified variance: sum of squared weights times
                    # each stratum's binomial variance
                    var = ((wl / tot) ** 2 * pl * (1 - pl) / nl
                           + (ws / tot) ** 2 * ps * (1 - ps) / ns)
                    se = math.sqrt(var)
                    print(f"  COMBINED {wt:>7s}-weighted {tag:8s} "
                          f"{est:6.1%} +/- {1.96 * se:.1%}")

        if prev:
            byyear = collections.defaultdict(collections.Counter)
            for r in prev + shrt:
                byyear[r["date"][:4]][r["pangram"]] += 1
            for y in sorted(byyear):
                c = byyear[y]
                t = sum(c.values())
                print(f"    {y}: n={t:3d}  AI {c['AI'] / t:5.1%}  "
                      f"AI+Mixed {(c['AI'] + c['Mixed']) / t:5.1%}")
        print()


if __name__ == "__main__":
    main()
