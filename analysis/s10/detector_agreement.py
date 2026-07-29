#!/usr/bin/env python3
"""S10 pilot: agreement between the Falcon-7B and Qwen3-1.7B Binoculars pairs.

The two-phase design needs the free detector only to be *correlated* with
truth; detector-detector correlation is the cheapest available proxy and
also tells us whether the small pair can stand in for the big one as the
Phase-1 stratifier. Reports Pearson/Spearman on scores and the cross-tab of
bottom-decile flags.

Usage: python detector_agreement.py scores_falcon.csv scores_qwen1.7.csv
"""
import csv
import math
import sys


def load(path):
    return {r["seg_id"]: float(r["score"]) for r in csv.DictReader(open(path))}


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    for rank, i in enumerate(order):
        r[i] = rank
    return r


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    ids = sorted(set(a) & set(b))
    xs = [a[i] for i in ids]
    ys = [b[i] for i in ids]
    print(f"n={len(ids)} shared segments")
    print(f"Pearson  r = {pearson(xs, ys):.3f}")
    print(f"Spearman ρ = {pearson(ranks(xs), ranks(ys)):.3f}")
    # bottom-decile cross-tab (the 'flag' end)
    k = len(ids) // 10
    fa = set(sorted(ids, key=lambda i: a[i])[:k])
    fb = set(sorted(ids, key=lambda i: b[i])[:k])
    inter = len(fa & fb)
    print(f"bottom-decile overlap: {inter}/{k} = {inter/k:.1%} "
          f"(chance would be 10%)")


if __name__ == "__main__":
    main()
