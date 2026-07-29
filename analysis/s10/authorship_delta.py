#!/usr/bin/env python3
"""S10: authorship trial — Burrows' Delta on NB Hansard speakers (numpy).

Q1 (mechanism): does authorship signal survive Hansard's editing? Test:
leave-one-out closed-set attribution of 1000-word chunks to speaker
profiles by Delta; accuracy far above chance = yes.
Q2 (the study's lever): for speakers present in both 2019 and 2025-26, is
their 2019 writing still closest to their own 2025-26 profile? Rank 1 =
style stable across six years.

Burrows' Delta: mean |z-difference| over the MFW most frequent words.
Usage: python authorship_delta.py
"""
import csv
import json
import re
from collections import Counter, defaultdict

import numpy as np

MFW = 150
CHUNK = 1000
MIN_CHUNKS = 3
CHAIRS = {"Madam Speaker", "Mr. Speaker", "Mr. Deputy Speaker", "Mr. Chair",
          "Madam Chair", ""}
TOKEN_RE = re.compile(r"[a-z']+")


def chunks_by_speaker(segs, era_pred):
    words = defaultdict(list)
    for s in segs:
        if s["speaker"] in CHAIRS or not era_pred(s["date"]):
            continue
        words[s["speaker"]] += TOKEN_RE.findall(s["text"].lower())
    return {sp: [ws[i:i + CHUNK] for i in range(0, len(ws) - CHUNK + 1, CHUNK)]
            for sp, ws in words.items()
            if len(ws) >= CHUNK * MIN_CHUNKS}


def main():
    segs = [json.loads(l) for l in open("segments_all.jsonl")]
    segs = [s for s in segs if s.get("scoreable")]
    docs25 = chunks_by_speaker(segs, lambda d: d[:4] >= "2025")
    docs19 = chunks_by_speaker(segs, lambda d: d.startswith("2019"))

    mfw = [w for w, _ in Counter(
        w for cs in docs25.values() for c in cs for w in c).most_common(MFW)]
    widx = {w: i for i, w in enumerate(mfw)}

    def matrix(chunks):
        X = np.zeros((len(chunks), MFW))
        for r, c in enumerate(chunks):
            n = len(c)
            for w in c:
                i = widx.get(w)
                if i is not None:
                    X[r, i] += 1
            X[r] /= n
        return X

    speakers = sorted(docs25)
    Xs = {sp: matrix(docs25[sp]) for sp in speakers}
    allX = np.vstack([Xs[sp] for sp in speakers])
    mu, sd = allX.mean(0), allX.std(0)
    sd[sd == 0] = 1
    Z = {sp: (Xs[sp] - mu) / sd for sp in speakers}
    sums = {sp: Z[sp].sum(0) for sp in speakers}
    counts = {sp: len(Z[sp]) for sp in speakers}

    rows, correct, total = [], 0, 0
    for sp in speakers:
        for k in range(counts[sp]):
            zv = Z[sp][k]
            best, best_d = None, np.inf
            for sp2 in speakers:
                if sp2 == sp:
                    if counts[sp2] < 2:
                        continue
                    prof = (sums[sp2] - zv) / (counts[sp2] - 1)
                else:
                    prof = sums[sp2] / counts[sp2]
                d = np.abs(zv - prof).mean()
                if d < best_d:
                    best, best_d = sp2, d
            correct += best == sp
            total += 1
            rows.append({"test": f"{sp}#c{k}", "true": sp, "pred": best,
                         "delta": round(float(best_d), 4), "kind": "loo-2025"})
    print(f"Q1 closed-set attribution: {len(speakers)} speakers, "
          f"{total} chunks of {CHUNK} words -> {correct}/{total} = "
          f"{correct/total:.1%} correct (chance {1/len(speakers):.1%})")

    profs = {sp: sums[sp] / counts[sp] for sp in speakers}
    both = sorted(set(speakers) & set(docs19))
    print(f"\nQ2 cross-era ({len(both)} speakers in both 2019 and 2025-26):")
    for sp in both:
        Z19 = (matrix(docs19[sp]) - mu) / sd
        d_all = {o: float(np.abs(Z19[:, None, :] - profs[o][None, None, :])
                          .mean()) for o in speakers}
        d_self = d_all[sp]
        rank = 1 + sum(1 for o, d in d_all.items() if o != sp and d < d_self)
        print(f"  {sp:22s} Δ(2019 self -> 2025 own profile)={d_self:.3f}  "
              f"rank {rank}/{len(speakers)}")
        rows.append({"test": f"{sp}#xera", "true": sp,
                     "pred": sp if rank == 1 else f"rank{rank}",
                     "delta": round(d_self, 4), "kind": "cross-era"})

    with open("authorship_delta.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["test", "true", "pred", "delta", "kind"])
        w.writeheader()
        w.writerows(rows)
        f.write(f"# Burrows Delta MFW={MFW} chunk={CHUNK}w min={MIN_CHUNKS} "
                f"chunks; chairs excluded; profiles from 2025-26\n")


if __name__ == "__main__":
    main()
