#!/usr/bin/env python3
"""Short-band sample: remove the 120-word floor from the prevalence design.

WHY

Every prevalence and control segment in the study is 120-360 words, and the
flag rate rises steeply with length -- 7.4% at 120-179 against 14.5% at
300-360, a gradient that survives chamber fixed effects. So the headline 12.4%
is a long-band rate reported as a corpus rate.

The study found this once already. METHODOLOGY.md §5.0a measured short bands
for four chambers on 2026-08-02 and corrected Canada from 17.5% to 10.6%
segment-weighted. The 19-chamber expansion a week later measured no short band
and applied no weights.

TWO REASONS TO REDO IT RATHER THAN REUSE §5.0a

Its short-band verdicts are 119 Human and 1 AI across 120 segments, with NOT
ONE Mixed. That is the Pangram 3 signature: the tier defect was not found
until 2026-08-09, a week after those scores, and P3 never returns Mixed at all
(it called Human on 3 of 8 P4-AI segments and 5 of 6 P4-Mixed in the route
check). None of those 120 were ever rescored on Pangram 4 -- verified against
pangram_p4_verdicts.csv. If the short-band rate was measured with a model that
undercounts, §5.0a's correction is too large, not too small.

And it sampled a fixed 40 per chamber, then applied corpus weights afterwards.

THIS DESIGN: MATCHED SAMPLING RATE, SO THE COMBINED SAMPLE IS SELF-WEIGHTING

Each chamber's short-band sample is sized to the same sampling fraction as its
existing long-band sample:

    n_short = n_long * (pool_short / pool_long)

with n_long = 120 for prevalence and 60 for control. Pooling short and long
then gives the corpus rate directly, with no reweighting assumptions -- which
is what §5.0a's post-hoc weighting could not offer.

THE OTHER EXCLUDED BAND: ABOVE 360 WORDS

Also sampled here, at the same matched rate. The packer in segment.py (and in
us_extract.py -- they share the logic) never splits a PARAGRAPH: it appends
whole paragraphs and flushes only once the buffer holds MIN_WORDS, so a single
600-word paragraph arriving at an empty buffer becomes an oversized segment.
Corpus-wide that is 1.7% of words, but it is concentrated almost entirely in
the United States -- 11.4% of US Senate words, 7.7% of US House, under 1%
everywhere else -- because the Congressional Record prints speech in long
unbroken blocks where Hansard breaks it up. Median segment: 277 words in the
Senate, 91 in UK Commons.

This matters because it biases the OPPOSITE WAY from the short band. Short text
is low-rate, so excluding it biases up; the longest text is the highest-rate, so
excluding it biases down. US Senate reports the study's lowest prevalence, 3.3%,
with a tenth of its record in the band most likely to be flagged.

Matched rate gives only ~6 prevalence segments for each US chamber, and their
intervals will be visibly wide. That is deliberate and it is the point:
matched-rate sampling is unbiased by construction and keeps the pooled estimate
self-weighting. Oversampling this stratum because we expect it to be
interesting would break self-weighting, require reweighting across the whole
design, and leave the US chambers non-comparable to the other nineteen. A wide
interval is the honest report of what the exclusion cost; the remedy is more
sampling at matched rate throughout.

Below 50 words remains genuinely unreachable: Pangram refuses text that short,
so those 3.5% of words cannot be scored by any sampling design.

COST: ceil(words/100) credits per segment. Short segments are mostly 1 credit
but 27% run 101-119 words and cost 2, so the short band alone is ~2,068 rather
than the 1,631 its segment count suggests. Over-360 segments average ~660
words and cost ~7 each, but there are few of them at matched rate.

Usage:
  python build_shortband.py --plan     # sample sizes per chamber
  python build_shortband.py --build    # write upload CSVs + manifest
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pangram_shortband")
MANIFEST = os.path.join(HERE, "pangram_shortband_manifest.json")
BATCH = 100          # dashboard hard cap: "Only the first 100 will be processed"
SHORT_MIN, SHORT_MAX = 50, 120
OVER_MIN = 361        # the other excluded band; see the docstring
N_PREV, N_CTL = 120, 60

sys.path.insert(0, HERE)
import build_pangram_expansion as BX      # noqa: E402  (era_of, usable, CODES)


def prefix(ch):
    """Short id prefix, distinct per chamber.

    BX.CODES has no entry for the non-province chambers, and the old fallback
    of ch[:3] mapped BOTH 'US-House' and 'US-Senate' to 'us-', so their ids
    collided and whichever was written second silently overwrote the first.
    Caught after it had already cost US-House 13 short-band and 8 over-band
    segments in the manifest.
    """
    code = BX.CODES.get(ch)
    if code:
        return code.lower()
    # Only the US pair collided; every other fallback prefix is already in use
    # by scored segments, so it is preserved rather than tidied.
    return {"US-House": "usho", "US-Senate": "usse"}.get(ch, ch[:3].lower())

SOURCES = (
    [(p, None) for p in sorted(glob.glob(os.path.join(HERE, "provinces",
                                                      "segments_*.jsonl")))]
    + [(os.path.join(HERE, "us", "segments_us_house.jsonl"), "US-House"),
       (os.path.join(HERE, "us", "segments_us_senate.jsonl"), "US-Senate"),
       (os.path.join(HERE, "ca", "segments_ca2.jsonl"), "CA-FED"),
       (os.path.join(HERE, "uk", "segments_uk.jsonl"), "UK"),
       (os.path.join(HERE, "ie", "segments_ie_en.jsonl"), "IE")]
)


def is_short(d):
    return (d.get("scoreable") and not d.get("translated")
            and (d.get("orig_frac") or 1.0) > 0.5
            and SHORT_MIN <= d["n_words"] < SHORT_MAX)


def is_over(d):
    """The other excluded band. The packer never splits a paragraph, so a
    single paragraph over MAX_WORDS becomes an oversized segment; that is
    almost entirely a US phenomenon (11.4% of Senate words, 7.7% of House,
    under 1% elsewhere) because the Congressional Record prints speech in long
    unbroken blocks. Sampled at the SAME matched rate as every other band --
    which yields very few segments for most chambers, and that is correct:
    matched rate keeps the pooled estimate self-weighting. Oversampling this
    stratum because we expect it to be high-rate would break that."""
    return (d.get("scoreable") and not d.get("translated")
            and (d.get("orig_frac") or 1.0) > 0.5
            and d["n_words"] >= OVER_MIN)


def collect():
    """-> {chamber: {era: {'long': int, 'short': [segments]}}}"""
    pools = {}
    for path, fixed in SOURCES:
        if not os.path.exists(path):
            continue
        for line in open(path):
            d = json.loads(line)
            ch = fixed or d.get("prov")
            if ch is None or (fixed is None and ch not in BX.CODES):
                continue
            era = BX.era_of(d["date"])
            if not era:
                continue
            if era == "ctl" and d["date"] < BX.REGIME_FLOOR.get(ch, ""):
                continue
            p = pools.setdefault(ch, {
                "ctl": {"long": 0, "short": [], "over": []},
                "prev": {"long": 0, "short": [], "over": []}})
            if BX.usable(d):
                p[era]["long"] += 1
            elif is_short(d):
                p[era]["short"].append(d)
            elif is_over(d):
                p[era]["over"].append(d)
    return pools


def sizes(pools):
    """Matched-rate sample size per chamber-era, largest banding gap first."""
    rows = []
    for ch, p in pools.items():
        if p["prev"]["long"] < 300 or p["ctl"]["long"] < 200:
            continue
        n_prev = round(N_PREV * len(p["prev"]["short"]) / p["prev"]["long"])
        n_ctl = round(N_CTL * len(p["ctl"]["short"]) / p["ctl"]["long"])
        n_prev = min(n_prev, len(p["prev"]["short"]))
        n_ctl = min(n_ctl, len(p["ctl"]["short"]))
        o_prev = min(round(N_PREV * len(p["prev"]["over"]) / p["prev"]["long"]),
                     len(p["prev"]["over"]))
        o_ctl = min(round(N_CTL * len(p["ctl"]["over"]) / p["ctl"]["long"]),
                    len(p["ctl"]["over"]))
        share = len(p["prev"]["short"]) / (len(p["prev"]["short"])
                                           + p["prev"]["long"])
        rows.append({"chamber": ch, "n_prev": n_prev, "n_ctl": n_ctl,
                     "o_prev": o_prev, "o_ctl": o_ctl,
                     "short_share": share,
                     "pool_prev": len(p["prev"]["short"]),
                     "pool_ctl": len(p["ctl"]["short"]),
                     "long_prev": p["prev"]["long"],
                     "long_ctl": p["ctl"]["long"]})
    # order by how much of the chamber the band was hiding: a partial run
    # then answers the worst cases first
    rows.sort(key=lambda r: -r["short_share"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--append-over", action="store_true",
                    help="add the over-360 stratum to an EXISTING manifest "
                         "and write new CSVs after the last one, so batches "
                         "already scored keep their ids")
    args = ap.parse_args()

    pools = collect()
    rows = sizes(pools)
    tot = sum(r["n_prev"] + r["n_ctl"] for r in rows)

    print(f"{'chamber':<10s} {'short%':>7s} {'prev':>6s} {'ctl':>5s} "
          f"{'total':>6s}")
    for r in rows:
        print(f"{r['chamber']:<10s} {100*r['short_share']:>6.1f}% "
              f"{r['n_prev']:>6d} {r['n_ctl']:>5d} "
              f"{r['n_prev']+r['n_ctl']:>6d}")
    print(f"\n{len(rows)} chambers, {tot:,} segments, {tot:,} credits "
          f"(1 each), {-(-tot // BATCH)} upload CSVs")
    if not (args.build or args.append_over):
        return

    if args.append_over:
        man = json.load(open(MANIFEST))
        bi = 1 + max((int(f[2:4]) for f in os.listdir(OUT)
                      if f.startswith("sb") and f.endswith(".csv")),
                     default=-1)
        batch, n = [], 0
        print(f"\nappending over-360 stratum; existing manifest has "
              f"{len(man)} segments, next CSV is sb{bi:02d}.csv\n")
        for r in rows:
            ch = r["chamber"]
            for era, k in (("prev", r["o_prev"]), ("ctl", r["o_ctl"])):
                if not k:
                    continue
                pool = pools[ch][era]["over"]
                rng = random.Random(int(hashlib.sha1(
                    f"{ch}{era}overband".encode()).hexdigest()[:8], 16))
                for i, d in enumerate(rng.sample(pool, k)):
                    sid = f"ov{prefix(ch)}{era[0]}{i:03d}"
                    man[sid] = {"chamber": ch, "era": era,
                                "seg_id": d["seg_id"], "date": d["date"],
                                "speaker": d.get("speaker", ""),
                                "n_words": d["n_words"], "band": "over"}
                    batch.append((sid, " ".join(d["text"].split())))
                    n += 1
                    if len(batch) == BATCH:
                        write(batch, bi); bi += 1; batch = []
        if batch:
            write(batch, bi); bi += 1
        json.dump(man, open(MANIFEST, "w"), indent=1)
        cred = sum(max(1, -(-man[k]["n_words"] // 100)) for k in man
                   if man[k].get("band") == "over")
        print(f"added {n} over-360 segments (~{cred:,} credits); "
              f"manifest now {len(man)}")
        for r in rows:
            if r["o_prev"] or r["o_ctl"]:
                print(f"    {r['chamber']:<10s} prev {r['o_prev']:>3d}  "
                      f"ctl {r['o_ctl']:>3d}")
        return

    os.makedirs(OUT, exist_ok=True)
    man, batch, bi, n = {}, [], 0, 0
    for r in rows:
        ch = r["chamber"]
        for era, k in (("prev", r["n_prev"]), ("ctl", r["n_ctl"])):
            if not k:
                continue
            pool = pools[ch][era]["short"]
            rng = random.Random(int(hashlib.sha1(
                f"{ch}{era}shortband".encode()).hexdigest()[:8], 16))
            for i, d in enumerate(rng.sample(pool, k)):
                sid = f"sb{prefix(ch)}{era[0]}{i:03d}"
                man[sid] = {"chamber": ch, "era": era, "seg_id": d["seg_id"],
                            "date": d["date"], "speaker": d.get("speaker", ""),
                            "n_words": d["n_words"], "band": "short"}
                batch.append((sid, " ".join(d["text"].split())))
                n += 1
                if len(batch) == BATCH:
                    write(batch, bi); bi += 1; batch = []
    if batch:
        write(batch, bi); bi += 1
    json.dump(man, open(MANIFEST, "w"), indent=1)
    print(f"\nwrote {bi} CSVs to {os.path.basename(OUT)}/ and "
          f"{os.path.basename(MANIFEST)} ({n:,} segments)")
    print("upload each CSV to the dashboard; the id column is the tag that")
    print("carries attribution into the results, per record_web_verdicts.py")


def write(batch, i):
    p = os.path.join(OUT, f"sb{i:02d}.csv")
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "text"])
        w.writerows(batch)


if __name__ == "__main__":
    main()
