#!/usr/bin/env python3
"""S10 pilot: summarize Binoculars scores (uncorrected — NOT an AI rate).

Reports score distributions by corpus year and by original-vs-translated
English, naive threshold counts under the reference Falcon thresholds
(explicitly uncalibrated for legislative register), and the lowest-scoring
segments for eyeballing. The 2019 control's flag rate is the first in-domain
look at the false-positive floor (1 - Sp); no Se measurement exists yet, so
no Rogan-Gladen correction is attempted here.

Usage: python analyze_scores.py SCORES_CSV SEGMENTS_ALL_JSONL
"""
import csv
import json
import sys

ACC_THRESH = 0.9015310749276843   # reference, Falcon pair, f1-optimized
FPR_THRESH = 0.8536432310785527   # reference, Falcon pair, low-FPR


def quantiles(xs, qs=(0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)):
    xs = sorted(xs)
    return {q: xs[min(len(xs) - 1, int(q * len(xs)))] for q in qs}


def summarize(name, rows):
    if not rows:
        print(f"{name}: no rows")
        return
    scores = [r["score"] for r in rows]
    qs = quantiles(scores)
    n = len(scores)
    acc = sum(s < ACC_THRESH for s in scores)
    fpr = sum(s < FPR_THRESH for s in scores)
    print(f"{name}: n={n}  median={qs[0.5]:.3f}  "
          f"p1/p5/p25={qs[0.01]:.3f}/{qs[0.05]:.3f}/{qs[0.25]:.3f}  "
          f"p75/p95/p99={qs[0.75]:.3f}/{qs[0.95]:.3f}/{qs[0.99]:.3f}")
    print(f"   below acc-thresh {ACC_THRESH:.3f}: {acc} ({acc/n:.2%})   "
          f"below low-FPR thresh {FPR_THRESH:.3f}: {fpr} ({fpr/n:.2%})")


def main():
    scores_csv, segs_jsonl = sys.argv[1], sys.argv[2]
    rows = []
    with open(scores_csv) as f:
        for r in csv.DictReader(f):
            r["score"] = float(r["score"])
            r["orig_frac"] = float(r["orig_frac"])
            r["year"] = r["date"][:4]
            rows.append(r)
    text_by_id = {json.loads(l)["seg_id"]: json.loads(l)["text"]
                  for l in open(segs_jsonl)}

    print("== Raw Binoculars score distributions (Falcon pair) ==")
    print("Uncorrected instrument readings; thresholds are the reference's,")
    print("NOT calibrated for legislative register. Not an AI rate.\n")

    ctl = [r for r in rows if r["year"] == "2019"]
    new = [r for r in rows if r["year"] >= "2025"]
    summarize("2019 control (pre-ChatGPT)", ctl)
    summarize("2025-26 corpus            ", new)
    print()
    summarize("2025-26, original English (orig_frac>=0.8) ",
              [r for r in new if r["orig_frac"] >= 0.8])
    summarize("2025-26, translated       (orig_frac<=0.2) ",
              [r for r in new if r["orig_frac"] <= 0.2])
    summarize("2019 ctl, original English (orig_frac>=0.8)",
              [r for r in ctl if r["orig_frac"] >= 0.8])
    summarize("2019 ctl, translated       (orig_frac<=0.2)",
              [r for r in ctl if r["orig_frac"] <= 0.2])

    print("\n== 15 lowest-scoring segments (most AI-like reading) ==")
    for r in sorted(rows, key=lambda r: r["score"])[:15]:
        txt = text_by_id.get(r["seg_id"], "")[:180].replace("\n", " ")
        print(f"{r['score']:.3f} | {r['date']} | {r['speaker'][:24]:24s} | "
              f"orig={r['orig_frac']:.2f} | {r['n_words']}w")
        print(f"      {txt}")
    print("\n== 5 highest-scoring segments (most human-like reading) ==")
    for r in sorted(rows, key=lambda r: -r["score"])[:5]:
        print(f"{r['score']:.3f} | {r['date']} | {r['speaker'][:24]:24s} | "
              f"orig={r['orig_frac']:.2f} | {r['n_words']}w")


if __name__ == "__main__":
    main()
