#!/usr/bin/env python3
"""Is the content-word control passing for the wrong reason?

THE PROBLEM

Kobak's 462 CONTENT words are the study's negative control: if the instrument
measures an LLM register rather than generic post-2023 vocabulary churn, the
style list should rise and the content list should not. Under protocol v1.1
content goes sharply negative in every chamber, which looks like a clean pass.

But Kobak's list spans 2013-2024 excess vocabulary, and their own validation
notes that the 2020-22 excess was almost entirely content -- *coronavirus*,
*lockdown*. Our pre-window is 2018-2022 and contains the pandemic; our
post-window does not. So a large part of the content list was guaranteed to
collapse for reasons that have nothing to do with AI. The steepest UK
declines are coronavirus (-4.63), quarantine (-4.58), omicron (-4.03),
wuhan (-3.54), lockdown (-3.00).

A control that passes because COVID ended is not evidence that the instrument
discriminates.

THE TEST

Split the content list by whether a word's pre-period usage is concentrated in
the pandemic years, using a data-driven rule rather than a hand-picked word
list: compare each word's share of pre-period occurrences falling in 2020-22
against the corpus-wide share. Words well above it are pandemic-era; the rest
are ordinary biomedical vocabulary with no built-in reason to fall.

The control only means what we want it to mean if the NON-pandemic content
words also stay flat or negative while style rises.

Usage: python content_control_covid.py
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
POST_MIN = "2024-01-01"
COVID_YEARS = {"2020", "2021", "2022"}
CONC = 1.5          # x the corpus-wide pandemic-year share -> "pandemic-era"
N_PLACEBO = 1000
_HERE = os.path.dirname(os.path.abspath(__file__))

CORPORA = [
    ("Dail Eireann", ["ie/segments_ie_en.jsonl"]),
    ("Canada House of Commons", ["ca/segments_ca_en.jsonl"]),
    ("UK House of Commons", ["uk/segments_uk.jsonl"]),
    ("US House of Representatives", ["us/segments_us_house.jsonl"]),
]


def load_lists():
    style, content = set(), set()
    for r in csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv"))):
        w = r["word"].lower()
        if w.isalpha():
            (style if r["type"] == "style" else content).add(w)
    return sorted(style), sorted(content)


def main():
    style, content = load_lists()
    for name, files in CORPORA:
        files = [f for f in files if os.path.exists(f)]
        if not files:
            continue
        rng = random.Random(int(hashlib.sha1(
            (name + "covid").encode()).hexdigest()[:8], 16))
        pre, post = Counter(), Counter()
        covid_c = Counter()
        pre_w = post_w = covid_w = 0
        disp = Counter()
        last = {}
        for path in files:
            for line in open(path):
                s = json.loads(line)
                if (not s.get("scoreable") or s.get("translated")
                        or s.get("orig_frac", 1.0) <= 0.5):
                    continue
                d = s["date"]
                t = TOKEN_RE.findall(s["text"].lower())
                if d <= PRE_MAX:
                    pre.update(t)
                    pre_w += len(t)
                    for w in set(t):
                        if last.get(w) != d:
                            disp[w] += 1
                            last[w] = d
                    if d[:4] in COVID_YEARS:
                        covid_c.update(t)
                        covid_w += len(t)
                elif d >= POST_MIN:
                    post.update(t)
                    post_w += len(t)

        base = covid_w / pre_w           # corpus-wide pandemic-year share
        excluded = set(style) | set(content) | {w for w, _ in pre.most_common(120)}

        def cell(w):
            return (int(math.log2(pre[w] + 1)),
                    int(math.log2(disp.get(w, 0) + 1)))

        pool = defaultdict(list)
        for w, n in pre.items():
            if w in excluded or len(w) < 4 or not w.isalpha() or post[w] == 0:
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
            return math.log(((post[w] + 0.5) / post_w) /
                            ((pre[w] + 0.5) / pre_w))

        def arm(ws, label):
            if len(ws) < 25:
                print(f"    {label:<28s} only {len(ws)} words — skipped")
                return
            real = sum(lr(w) for w in ws) / len(ws)
            pools = [pool_for(cell(w)) for w in ws]
            draws = sorted(sum(lr(rng.choice(p)) for p in pools) / len(pools)
                           for _ in range(N_PLACEBO))
            med = draws[len(draws) // 2]
            ex = sum(1 for d in draws if d >= real)
            print(f"    {label:<28s} n={len(ws):>3d}  excess {real-med:>+8.4f}  "
                  f"p={ex/N_PLACEBO:.3f}")
            return real - med

        present_s = [w for w in style if pre[w] > 0 and post[w] > 0]
        present_c = [w for w in content if pre[w] > 0 and post[w] > 0]
        pandemic = [w for w in present_c
                    if pre[w] > 0 and covid_c[w] / pre[w] > base * CONC]
        ordinary = [w for w in present_c if w not in set(pandemic)]

        print(f"\n=== {name} ===")
        print(f"  pandemic-year share of pre-window words: {base:.1%}; "
              f"a content word counts as pandemic-era above {base*CONC:.1%}")
        print(f"  content words present in both periods: {len(present_c)} "
              f"({len(pandemic)} pandemic-era, {len(ordinary)} ordinary)")
        s_ex = arm(present_s, "style (the instrument)")
        arm(present_c, "content, ALL (as reported)")
        arm(pandemic, "content, pandemic-era only")
        o_ex = arm(ordinary, "content, pandemic REMOVED")
        if s_ex is not None and o_ex is not None:
            print(f"    {'-> honest style - content gap':<28s} {s_ex-o_ex:>+8.4f}")


if __name__ == "__main__":
    main()
