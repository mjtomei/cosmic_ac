#!/usr/bin/env python3
"""S10: assemble the Pangram adjudication batch (Tier 4).

Strata (fixed seed, reproducible):
  A. consensus-hits  — every 2025-26 segment flagged by ALL local detectors
     at the control-calibrated 5% operating point, plus the control's own
     consensus hits (Pangram's FPR on exactly the genre our detectors
     over-flag).
  B. decile-sample   — 12 random 2025-26 segments per falcon-score decile
     (stratified spread for the two-phase estimate).
  C. control-sample  — 60 random 2019 segments (Pangram in-domain FPR).
  D. se-corpus       — synthetic known-AI legislative speech, if
     se_segments.jsonl exists (Pangram in-domain Se).

Output: pangram_batch.jsonl (+ per-stratum counts and word total).
~60k words: fits one $65 Professional month trivially (1.5M words), or a
month of free tier at 2k words/day.

Usage: python make_pangram_batch.py scores_falcon.csv scores_qwen1.7.csv [scores_qwen8.csv ...]
"""
import csv
import json
import random
import sys

random.seed(20260729)


def load_scores(path):
    return {r["seg_id"]: float(r["score"]) for r in csv.DictReader(open(path))}


def pctile(xs, q):
    xs = sorted(xs)
    return xs[max(0, min(len(xs) - 1, int(q * len(xs))))]


def main():
    dets = {p.split("scores_")[-1].replace(".csv", ""): load_scores(p)
            for p in sys.argv[1:]}
    segs = {}
    for line in open("segments_all.jsonl"):
        s = json.loads(line)
        if s.get("scoreable"):
            segs[s["seg_id"]] = s
    ids = sorted(set(segs) & set.intersection(*(set(d) for d in dets.values())))
    ctl = [i for i in ids if i.startswith("2019")]
    new = [i for i in ids if i[:4] >= "2025"]

    thr = {n: pctile([d[i] for i in ctl], 0.05) for n, d in dets.items()}
    consensus = lambda pool: [i for i in pool
                              if all(d[i] < thr[n] for n, d in dets.items())]
    batch = {}
    for i in consensus(new):
        batch[i] = "A-consensus-2025"
    for i in consensus(ctl):
        batch[i] = "A-consensus-ctl"

    fal = dets.get("falcon") or list(dets.values())[0]
    ranked = sorted(new, key=lambda i: fal[i])
    dec = len(ranked) // 10
    for d in range(10):
        pool = [i for i in ranked[d * dec:(d + 1) * dec] if i not in batch]
        for i in random.sample(pool, min(12, len(pool))):
            batch[i] = f"B-decile-{d}"
    for i in random.sample([i for i in ctl if i not in batch], 60):
        batch[i] = "C-control-2019"

    try:
        for line in open("se_segments.jsonl"):
            s = json.loads(line)
            if s.get("scoreable"):
                segs[s["seg_id"]] = s
                batch[s["seg_id"]] = "D-synthetic-se"
    except FileNotFoundError:
        print("(se_segments.jsonl not present yet — stratum D skipped)")

    words = 0
    with open("pangram_batch.jsonl", "w") as f:
        for i, stratum in sorted(batch.items(), key=lambda kv: kv[1]):
            s = segs[i]
            words += s["n_words"]
            f.write(json.dumps({"seg_id": i, "stratum": stratum,
                                "date": s["date"], "speaker": s["speaker"],
                                "n_words": s["n_words"], "text": s["text"]},
                               ensure_ascii=False) + "\n")
    from collections import Counter
    print(Counter(v.split("-")[0] for v in batch.values()))
    print(f"{len(batch)} segments, {words:,} words -> pangram_batch.jsonl")


if __name__ == "__main__":
    main()
