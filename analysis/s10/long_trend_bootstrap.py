#!/usr/bin/env python3
"""Day-clustered bootstrap of the turning-point year in the UK long series.

long_trend.py prints the raw annual instrument-minus-placebo gap; the trough is
the smallest annual point (1994). It fits no curve, so "minimum of the fitted
series" in footnote r45 was wrong. This gives the trough an honest interval: it
resamples sitting DAYS within each year (with replacement), clustering the
uncertainty at the day level, recomputes the annual gap, and records which year
holds the minimum across resamples.

Placebo construction is copied from long_trend.py (same seed, same
frequency-and-dispersion match on the baseline era). The heavy step -- per-day
placebo hits for 200 sets -- is done once as a (days x vocab) @ (vocab x sets)
matmul, so the bootstrap itself is fast.

Usage: python long_trend_bootstrap.py [--seg uk/segments_uk_deep.jsonl] [--reps 2000]
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

import numpy as np

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
N_PLACEBO = 200
BASE_YEARS = ("2010", "2011", "2012")


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE,
                                                    "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg", default="uk/segments_uk_deep.jsonl")
    ap.add_argument("--label", default="UK House of Commons")
    ap.add_argument("--reps", type=int, default=2000)
    args = ap.parse_args()
    style = load_style()
    sset = set(style)

    # PASS 1: baseline-era counts for placebo matching (no per-segment storage)
    per_year = defaultdict(Counter)
    words = Counter()
    disp = Counter()
    last = {}
    for line in open(args.seg):
        d = json.loads(line)
        if not d.get("scoreable"):
            continue
        y = d["date"][:4]
        t = TOKEN_RE.findall(d["text"].lower())
        per_year[y].update(t)
        words[y] += len(t)
        if y in BASE_YEARS:
            for w in set(t):
                if last.get(w) != d["date"]:
                    disp[w] += 1
                    last[w] = d["date"]

    base = Counter()
    for y in BASE_YEARS:
        base.update(per_year.get(y, Counter()))
    rng = random.Random(int(hashlib.sha1(args.label.encode()).hexdigest()[:8], 16))
    excluded = sset | {w for w, _ in base.most_common(120)}
    pool = defaultdict(list)
    for w, n in base.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        pool[(int(math.log2(n + 1)),
              int(math.log2(disp.get(w, 0) + 1)))].append(w)

    def pool_for(c):
        if pool.get(c):
            return pool[c]
        for r in range(1, 8):
            best = None
            for df in range(-r, r + 1):
                for dd in range(-r, r + 1):
                    if max(abs(df), abs(dd)) != r:
                        continue
                    cd = pool.get((c[0] + df, c[1] + dd))
                    if cd and (best is None or len(cd) > len(best)):
                        best = cd
            if best:
                return best
        return max(pool.values(), key=len)

    present = [w for w in style if base[w] > 0]
    pools = [pool_for((int(math.log2(base[w] + 1)),
                       int(math.log2(disp.get(w, 0) + 1)))) for w in present]
    placebo_sets = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO)]

    # vocab index over every word that matters (instrument + all placebo draws)
    vocab = {}
    for w in present:
        vocab.setdefault(w, len(vocab))
    for ps in placebo_sets:
        for w in ps:
            vocab.setdefault(w, len(vocab))
    R = len(vocab)
    inst_vec = np.zeros(R)
    for w in present:
        inst_vec[vocab[w]] += 1.0
    M = np.zeros((R, N_PLACEBO))          # word -> per-set multiplicity
    for k, ps in enumerate(placebo_sets):
        for w in ps:
            M[vocab[w], k] += 1.0

    years = sorted(y for y in per_year if words[y] > 200_000)
    yset = set(years)
    # PASS 2: per-day count vector over the relevant vocab (re-read the file)
    day_key, day_words = [], []
    key_ix = {}
    counts = defaultdict(lambda: Counter())
    for line in open(args.seg):
        d = json.loads(line)
        if not d.get("scoreable"):
            continue
        y = d["date"][:4]
        if y not in yset:
            continue
        t = TOKEN_RE.findall(d["text"].lower())
        k = (y, d["date"])
        if k not in key_ix:
            key_ix[k] = len(day_key)
            day_key.append(k)
            day_words.append(0)
        i = key_ix[k]
        day_words[i] += len(t)
        c = counts[i]
        for w in t:
            j = vocab.get(w)
            if j is not None:
                c[j] += 1
    D = len(day_key)
    DAY = np.zeros((D, R))
    for i, c in counts.items():
        for j, n in c.items():
            DAY[i, j] = n
    day_words = np.array(day_words, dtype=float)
    day_inst = DAY @ inst_vec               # (D,)
    day_plac = DAY @ M                       # (D, 200)
    rows_by_year = defaultdict(list)
    for k, i in key_ix.items():
        rows_by_year[k[0]].append(i)
    idx_by_year = {y: np.array(rows_by_year[y]) for y in years}

    def argmin_gap(pick):
        best_y, best_gap = None, None
        for y in years:
            ix = pick[y]
            wsum = day_words[ix].sum()
            if wsum == 0:
                continue
            ri = day_inst[ix].sum() / wsum * 1e5
            med = np.median(day_plac[ix].sum(axis=0) / wsum * 1e5)
            gap = ri - med
            if best_gap is None or gap < best_gap:
                best_gap, best_y = gap, y
        return best_y

    point = argmin_gap({y: idx_by_year[y] for y in years})
    print(f"point-estimate trough year: {point}  ({args.seg}, {D} sitting days)")

    rs = np.random.RandomState(20260816)
    tally = Counter()
    for _ in range(args.reps):
        pick = {y: idx_by_year[y][rs.randint(0, len(idx_by_year[y]),
                                             len(idx_by_year[y]))]
                for y in years}
        tally[argmin_gap(pick)] += 1
    print(f"\nday-clustered bootstrap, {args.reps} resamples:")
    for y, c in tally.most_common(6):
        print(f"  {y}: {c/args.reps:6.1%}")


if __name__ == "__main__":
    main()
