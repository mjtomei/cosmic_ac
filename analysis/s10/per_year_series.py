#!/usr/bin/env python3
"""Per-year primary series — review finding F8.

THE PROBLEM IT FIXES

The headline pools 2024-2026 into a single ratio. Two things make that a bad
estimand. The marker vocabulary is non-stationary inside that window (Geng &
Trotta show *delve* collapsing from early 2024 once the press named it, while
other markers keep rising), and the chambers weight the post years very
differently -- Canada is 49% 2024 by words, Ireland 31%. So the cross-chamber
comparison is computed over different mixtures, and Canada's weak result may
be a mixture artifact rather than anything about Canada.

Each post year is scored against the SAME 2018-2022 baseline, with its own
frequency-matched placebo null, so the years are comparable to each other.

ONE ARTIFACT TO KEEP IN VIEW: splitting the post window shrinks W_post, which
inflates the constant that absent words contribute under +0.5 smoothing. That
pushes later years up mechanically. The v1.1 present-in-both restriction is
therefore applied here, which removes it -- the numbers below are directly
comparable to the v1.1 headline, not to v1.0.

Usage: python per_year_series.py
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
PRE_MAX = "2022-12-31"
N_PLACEBO = 1000
_HERE = os.path.dirname(os.path.abspath(__file__))

CORPORA = [
    ("New Brunswick", ["segments_59th.jsonl", "segments_60th.jsonl",
                       "segments_61s1.jsonl", "segments.jsonl"]),
    ("Dail Eireann", ["ie/segments_ie_en.jsonl"]),
    ("Canada House of Commons", ["ca/segments_ca_en.jsonl"]),
    ("UK House of Commons", ["uk/segments_uk.jsonl"]),
    ("US House of Representatives", ["us/segments_us_house.jsonl"]),
    ("US Senate", ["us/segments_us_senate.jsonl"]),
]


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def main():
    style = load_style()
    out = {}
    for name, files in CORPORA:
        files = [f for f in files if os.path.exists(f)]
        if not files:
            continue
        rng = random.Random(int(hashlib.sha1(
            (name + "peryear").encode()).hexdigest()[:8], 16))
        pre = Counter()
        pre_w = 0
        post = defaultdict(Counter)
        post_w = defaultdict(int)
        disp = Counter()
        last = {}
        for path in files:
            for line in open(path):
                s = json.loads(line)
                if (not s.get("scoreable") or s.get("translated")
                        or s.get("orig_frac", 1.0) <= 0.5):
                    continue
                d = s["date"]
                toks = TOKEN_RE.findall(s["text"].lower())
                if d <= PRE_MAX:
                    pre.update(toks)
                    pre_w += len(toks)
                    for w in set(toks):
                        if last.get(w) != d:
                            disp[w] += 1
                            last[w] = d
                elif d >= "2024-01-01":
                    y = d[:4]
                    post[y].update(toks)
                    post_w[y] += len(toks)
        if not post:
            continue

        excluded = set(style) | {w for w, _ in pre.most_common(120)}
        print(f"\n=== {name} ===  pre {pre_w:,}w")
        print(f"  {'year':<6s} {'words':>12s} {'share':>6s} {'primary':>9s} "
              f"{'placebo':>9s} {'EXCESS':>9s} {'p':>8s}")
        tot = sum(post_w.values())
        res = {}
        for y in sorted(post):
            pw = post_w[y]
            pc = post[y]
            ws = [w for w in style if pre[w] > 0 and pc[w] > 0]

            def cell(w):
                return (int(math.log2(pre[w] + 1)),
                        int(math.log2(disp.get(w, 0) + 1)))

            pool = defaultdict(list)
            for w, n in pre.items():
                if (w in excluded or len(w) < 4 or not w.isalpha()
                        or pc[w] == 0):
                    continue
                pool[cell(w)].append(w)

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
                return math.log(((pc[w] + 0.5) / pw) / ((pre[w] + 0.5) / pre_w))

            real = sum(lr(w) for w in ws) / len(ws)
            pools = [pool_for(cell(w)) for w in ws]
            draws = sorted(sum(lr(rng.choice(p)) for p in pools) / len(pools)
                           for _ in range(N_PLACEBO))
            med = draws[len(draws) // 2]
            ex = sum(1 for d in draws if d >= real)
            print(f"  {y:<6s} {pw:>12,} {pw/tot:>5.0%} {real:>+9.4f} "
                  f"{med:>+9.4f} {real-med:>+9.4f} {ex/N_PLACEBO:>8.3f}")
            res[y] = {"words": pw, "share": pw / tot, "primary": real,
                      "placebo_median": med, "excess": real - med,
                      "p": ex / N_PLACEBO, "n_words": len(ws)}
        out[name] = res
    json.dump(out, open("per_year_series.json", "w"), indent=1)
    print("\nwrote per_year_series.json")


if __name__ == "__main__":
    main()
