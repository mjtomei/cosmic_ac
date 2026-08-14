#!/usr/bin/env python3
"""In-time placebo: run the protocol where the effect CANNOT exist.

THE CHALLENGE (round-2 review, R2-1)

Every significance claim in the lexicon arm rests on the frequency-and-
dispersion-matched placebo null: matched random word sets drift by X, the
instrument drifts by more, therefore something specific happened. That
argument is only sound if the null actually captures how instrument-like
vocabulary drifts over comparable spans of time.

It has never been tested on a period where the answer must be zero. The
round-2 review claims that when you do, the protocol returns large positive
"effects" in windows entirely before ChatGPT existed -- which would mean the
placebo does not control for secular vocabulary drift and the headline is
measuring the passage of time.

TWO TESTS, and they answer different questions.

  1. IN-TIME PLACEBO. Split the pre-LLM era into two windows separated by a
     gap, mirroring the real design's shape (pre-window, gap year, post-window)
     and run the identical v1.1 protocol. Expected under a working null: ~0.
     If it returns the same magnitude as the real comparison, the real result
     is not evidence.

  2. NO-GAP ESTIMATOR CHECK. Split the SAME period into interleaved halves by
     alternating sitting date -- so both halves span identical time and differ
     only by sampling. Expected: ~0 by construction. This separates "the
     estimator is biased" from "there is a real secular trend": if test 2 is
     ~0 and test 1 is large, the estimator is fine and the drift is real.

Usage: python in_time_placebo.py
"""
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
N_PLACEBO = 1000
_HERE = os.path.dirname(os.path.abspath(__file__))

CORPORA = [
    ("UK House of Commons", ["uk/segments_uk.jsonl"]),
    ("Dail Eireann", ["ie/segments_ie_en.jsonl"]),
    ("Canada House of Commons", ["ca/segments_ca_en.jsonl"]),
    ("New Brunswick", ["segments_59th.jsonl", "segments_60th.jsonl",
                       "segments_61s1.jsonl", "segments.jsonl"]),
]

# (label, pre-range, post-range) — all inclusive of year bounds
SPECS = [
    ("REAL  2018-22 vs 2024-26", ("2018", "2022"), ("2024", "2026")),
    ("placebo 2018-19 vs 2021-22", ("2018", "2019"), ("2021", "2022")),
    ("placebo 2018 vs 2020", ("2018", "2018"), ("2020", "2020")),
    ("placebo 2019 vs 2021", ("2019", "2019"), ("2021", "2021")),
]


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5)


def run(style, pre_c, pre_w, post_c, post_w, disp, rng):
    """v1.1 exactly: present-in-both, frequency x dispersion matched placebo."""
    ws = [w for w in style if pre_c[w] > 0 and post_c[w] > 0]
    if len(ws) < 30 or pre_w == 0 or post_w == 0:
        return None

    def cell(w):
        return (int(math.log2(pre_c[w] + 1)), int(math.log2(disp.get(w, 0) + 1)))

    excluded = set(style) | {w for w, _ in pre_c.most_common(120)}
    pool = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha() or post_c[w] == 0:
            continue
        pool[cell(w)].append(w)
    if not pool:
        return None

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

    def lr(w):
        return math.log(((post_c[w] + 0.5) / post_w) / ((pre_c[w] + 0.5) / pre_w))

    real = sum(lr(w) for w in ws) / len(ws)
    pools = [pool_for(cell(w)) for w in ws]
    draws = sorted(sum(lr(rng.choice(p)) for p in pools) / len(pools)
                   for _ in range(N_PLACEBO))
    med = draws[len(draws) // 2]
    ex = sum(1 for d in draws if d >= real)
    return {"n": len(ws), "primary": real, "placebo_median": med,
            "excess": real - med, "p": ex / N_PLACEBO,
            "pre_w": pre_w, "post_w": post_w}


def collect(files, in_pre, in_post):
    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    disp = Counter()
    last = {}
    for path in files:
        for line in open(path):
            s = json.loads(line)
            if not keep(s):
                continue
            d = s["date"]
            t = TOKEN_RE.findall(s["text"].lower())
            if in_pre(d):
                pre_c.update(t)
                pre_w += len(t)
                for w in set(t):
                    if last.get(w) != d:
                        disp[w] += 1
                        last[w] = d
            elif in_post(d):
                post_c.update(t)
                post_w += len(t)
    return pre_c, pre_w, post_c, post_w, disp


def main():
    style = load_style()
    for name, files in CORPORA:
        files = [f for f in files if os.path.exists(f)]
        if not files:
            continue
        print(f"\n=== {name} ===")
        print(f"  {'window pair':<28s} {'pre Mw':>7s} {'post Mw':>8s} "
              f"{'primary':>9s} {'placebo':>9s} {'EXCESS':>9s} {'p':>7s}")
        for label, (a1, a2), (b1, b2) in SPECS:
            rng = random.Random(int(hashlib.sha1(
                (name + label).encode()).hexdigest()[:8], 16))
            r = run(style, *collect(files,
                                    lambda d, a1=a1, a2=a2: a1 <= d[:4] <= a2,
                                    lambda d, b1=b1, b2=b2: b1 <= d[:4] <= b2),
                    rng)
            if not r:
                print(f"  {label:<28s} (insufficient data)")
                continue
            print(f"  {label:<28s} {r['pre_w']/1e6:>7.1f} {r['post_w']/1e6:>8.1f} "
                  f"{r['primary']:>+9.4f} {r['placebo_median']:>+9.4f} "
                  f"{r['excess']:>+9.4f} {r['p']:>7.3f}")

        # estimator check: interleave sitting dates within ONE period, so both
        # halves span identical time and differ only by sampling
        dates = set()
        for path in files:
            for line in open(path):
                s = json.loads(line)
                if keep(s) and "2018" <= s["date"][:4] <= "2022":
                    dates.add(s["date"])
        order = {d: i for i, d in enumerate(sorted(dates))}
        rng = random.Random(int(hashlib.sha1(
            (name + "interleave").encode()).hexdigest()[:8], 16))
        r = run(style, *collect(files,
                                lambda d: d in order and order[d] % 2 == 0,
                                lambda d: d in order and order[d] % 2 == 1), rng)
        if r:
            print(f"  {'ESTIMATOR CHECK (odd/even)':<28s} {r['pre_w']/1e6:>7.1f} "
                  f"{r['post_w']/1e6:>8.1f} {r['primary']:>+9.4f} "
                  f"{r['placebo_median']:>+9.4f} {r['excess']:>+9.4f} {r['p']:>7.3f}")


if __name__ == "__main__":
    main()
