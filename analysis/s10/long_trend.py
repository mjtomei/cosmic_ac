#!/usr/bin/env python3
"""When did the trend start? A 20-year series against transformer-era landmarks.

THE QUESTION

The in-time placebo showed that Kobak-style vocabulary was already rising in
parliamentary English before ChatGPT, which broke every significance claim
resting on a two-window contrast. But "before ChatGPT" is not the same as "not
AI". Writing assistance predates the chat interface by years:

    2017-06  Attention Is All You Need
    2018-05  Gmail Smart Compose (predictive completion, mass deployment)
    2019-02  GPT-2
    2020-06  GPT-3 API
    2021-06  GitHub Copilot
    2022-11  ChatGPT

So the shape of the curve matters more than its slope. Three hypotheses make
different predictions about a long series:

  LONG DRIFT     rising steadily since well before 2017 -> ordinary register
                 change, nothing to do with machines
  EARLY AI       flat, then a break somewhere in 2018-2021 -> consistent with
                 predictive-text and pre-chat model influence
  CHATGPT        flat until 2022-23, then a break -> the study's original claim

The instrument is measured against TWO baselines so the answer is not an
artifact of overall vocabulary change: a frequency-and-dispersion-matched
placebo set drawn the same way as in the protocol, and the raw corpus size.
If the instrument and its matched placebo rise together, nothing specific is
happening; the gap between them is the quantity of interest.

Rates are per 100k words, computed per calendar year, so no window boundaries
are involved and no counterfactual is assumed -- this is descriptive, and
deliberately so.

Usage: python long_trend.py [--seg uk/segments_uk_long.jsonl]
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

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
N_PLACEBO = 200
BASE_YEARS = ("2010", "2011", "2012")     # anchor era, pre-transformer


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg", default="uk/segments_uk_long.jsonl")
    ap.add_argument("--label", default="UK House of Commons")
    args = ap.parse_args()
    style = load_style()
    sset = set(style)

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

    years = sorted(y for y in per_year if words[y] > 200_000)
    base = Counter()
    base_w = 0
    for y in BASE_YEARS:
        base.update(per_year.get(y, Counter()))
        base_w += words.get(y, 0)
    if base_w == 0:
        raise SystemExit("no baseline-era data; check the segment file")

    # matched placebo sets, drawn on the BASELINE era so nothing later informs them
    rng = random.Random(int(hashlib.sha1(args.label.encode()).hexdigest()[:8], 16))
    excluded = sset | {w for w, _ in base.most_common(120)}
    pool = defaultdict(list)
    for w, n in base.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        pool[(int(math.log2(n + 1)), int(math.log2(disp.get(w, 0) + 1)))].append(w)

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

    def rate(ws, y):
        return sum(per_year[y][w] for w in ws) / words[y] * 1e5

    print(f"=== {args.label} ===  instrument = {len(present)} Kobak style words "
          f"present in {'/'.join(BASE_YEARS)}")
    print(f"  baseline era {'/'.join(BASE_YEARS)}: {base_w:,} words\n")
    print(f"  {'year':<6s} {'Mwords':>7s} {'instrument':>11s} {'placebo':>9s} "
          f"{'GAP':>8s} {'gap vs base':>12s}")
    b_inst = rate(present, BASE_YEARS[0])
    rows = []
    for y in years:
        ri = rate(present, y)
        rp = sorted(rate(p, y) for p in placebo_sets)
        med = rp[len(rp) // 2]
        rows.append((y, ri, med, ri - med))
    gap_base = sum(r[3] for r in rows if r[0] in BASE_YEARS) / \
        max(1, sum(1 for r in rows if r[0] in BASE_YEARS))
    marks = {"2017": "  <- Attention Is All You Need (Jun)",
             "2018": "  <- Gmail Smart Compose (May)",
             "2019": "  <- GPT-2 (Feb)",
             "2020": "  <- GPT-3 API (Jun)",
             "2021": "  <- Copilot (Jun)",
             "2022": "  <- ChatGPT (Nov)"}
    for y, ri, med, gap in rows:
        print(f"  {y:<6s} {words[y]/1e6:>7.1f} {ri:>11.1f} {med:>9.1f} "
              f"{gap:>8.1f} {gap-gap_base:>+12.1f}{marks.get(y,'')}")

    json.dump([{"year": y, "words": words[y], "instrument_per100k": ri,
                "placebo_per100k": med, "gap": g} for y, ri, med, g in rows],
              open(f"long_trend_{args.label.split()[0].lower()}.json", "w"), indent=1)
    print(f"\n  gap is instrument minus matched-placebo rate; the final column")
    print(f"  re-bases it on {'/'.join(BASE_YEARS)}, so it reads as change since")
    print(f"  before the transformer era.")


if __name__ == "__main__":
    main()
