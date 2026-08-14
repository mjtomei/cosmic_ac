#!/usr/bin/env python3
"""Redraw Manitoba's Pangram sample from the corrected extraction.

WHY MANITOBA IS BEING RESAMPLED

`provinces_extract.py` matched a speaker prefix inside a single <b> run. From
mid-2018 Manitoba's Word export splits a name across several runs around
inserted TOC anchors, so the prefix did not match, the speech accreted to the
previous turn -- usually the Speaker's -- and was dropped as chair voice. The
live files understated 2019 by 41% and 2025-26 by 65-78%.

The verdicts already recorded are not wrong: they are correct readings of the
text that was scored. What was wrong is the SAMPLING FRAME. Manitoba's sample
was drawn from 58% of its record, and because the shortfall is concentrated
after 2018 it is worse in the prevalence window than in the control window --
which is precisely the asymmetry that would bias a before-and-after comparison.
A frame that is incomplete in an era-correlated way cannot be repaired by
reweighting; it has to be redrawn.

WHY THE WHOLE DESIGN AND NOT JUST THE LONG BAND

Both bands came from the same broken frame, so both are redrawn: 120 prevalence
and 60 control in the long band, and short-band draws sized to the SAME
sampling rate as the long band within each era, which is what keeps the
combined estimate self-weighting (see build_shortband.py). Manitoba's over-360
band draws zero at that rate, so nothing is lost by its absence.

THE BACKFILLED YEARS ARE DELIBERATELY EXCLUDED

The pool is `segments_mb.jsonl` alone -- the corrected extraction of the
original download windows (2006-2010, 2015-2019) plus 2025-26 -- and NOT
`segments_mb_fill.jsonl`. Including the fill would add controls from 2011-14
and 2020-22, and a first draw that did so pulled 30 of its 90 controls from
years no other chamber can draw from.

This redraw fixes ONE thing: a frame that was missing 42% of the text inside
the years already sampled. Widening the year coverage at the same time would
confound the two, and would leave Manitoba's specificity measured on text
averaging years newer than the other nineteen chambers' -- so a difference
between Manitoba and the rest would no longer be attributable to either change.

Recent controls (2020 to mid-2022) are worth having and are now available for
every chamber, which is exactly why they belong to the all-chamber recent
control re-run rather than to Manitoba on its own.

WHAT IS DELIBERATELY NOT REUSED

The old sample's seg_ids. 135 of the 278 no longer exist -- re-extraction
changes turn indices -- and reusing the 143 that survive would be a sample of
the segments that happened to parse identically under both versions of the
extractor, which is not a random draw from anything.

Usage:
  python build_mb_redraw.py            # writes pangram_mb_redraw/mb01..NN.csv
"""
import collections
import csv
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pangram_mb_redraw")
SRC = os.path.join(HERE, "provinces", "segments_mb.jsonl")
FILL = os.path.join(HERE, "provinces", "segments_mb_fill.jsonl")
BATCH = 100          # dashboard cap
N_LONG = {"prev": 120, "ctl": 60}
SEED = 20260813

sys.path.insert(0, HERE)
import build_pangram_expansion as BX      # noqa: E402


def band_of(n):
    if 120 <= n <= 360:
        return "long"
    if 50 <= n < 120:
        return "short"
    if n > 360:
        return "over"
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    pool = collections.defaultdict(list)
    floor = BX.REGIME_FLOOR.get("MB", "")
    for path in (SRC,):          # NOT FILL -- see the docstring
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable") or d.get("translated"):
                continue
            era = BX.era_of(d["date"])
            if not era:
                continue
            # Manitoba changed transcription regime in 2007; controls drawn
            # across that step measure false positives on a text regime that
            # no longer exists (transcript_regime_check.py).
            if era == "ctl" and d["date"] < floor:
                continue
            b = band_of(d["n_words"])
            if b:
                pool[(era, b)].append(d)

    print("pool from the CORRECTED frame")
    for k in sorted(pool):
        print(f"  {k[0]+'/'+k[1]:<12s} {len(pool[k]):>8,}")

    want = dict(N_LONG and {("prev", "long"): 120, ("ctl", "long"): 60})
    for era in ("prev", "ctl"):
        nl = len(pool[(era, "long")]) or 1
        for b in ("short", "over"):
            want[(era, b)] = round(N_LONG[era] * len(pool[(era, b)]) / nl)

    rng = random.Random(SEED)
    picked, credits = [], 0
    print("\ndraw, matched rate across bands")
    for (era, b), k in sorted(want.items()):
        avail = pool[(era, b)]
        k = min(k, len(avail))
        if not k:
            print(f"  {era+'/'+b:<12s} 0 (nothing at this rate)")
            continue
        for d in rng.sample(avail, k):
            picked.append((era, b, d))
        print(f"  {era+'/'+b:<12s} {k:>4d} of {len(avail):,}")

    picked.sort(key=lambda x: x[2]["seg_id"])
    key = {}
    for i, (era, b, d) in enumerate(picked):
        cid = f"mb{i:03d}"
        credits += math.ceil(len(d["text"].split()) / 100)
        key[cid] = {"seg_id": d["seg_id"], "chamber": "MB", "era": era,
                    "band": b, "date": d["date"], "n_words": d["n_words"]}

    nb = 0
    for s in range(0, len(picked), BATCH):
        nb += 1
        p = os.path.join(OUT, f"mb{nb:02d}.csv")
        with open(p, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "text"])
            for i in range(s, min(s + BATCH, len(picked))):
                w.writerow([f"mb{i:03d}", picked[i][2]["text"]])
        print(f"  wrote {os.path.basename(p)}: {min(BATCH, len(picked)-s)} rows")

    json.dump(key, open(os.path.join(OUT, "redraw_key.json"), "w"), indent=1)
    print(f"\n{len(picked)} segments in {nb} batches, ~{credits} credits")


if __name__ == "__main__":
    main()
