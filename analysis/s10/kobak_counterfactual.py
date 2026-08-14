#!/usr/bin/env python3
"""Kobak's estimator: measure the BREAK from each word's own trend, not a level.

WHY

The two-window contrast used until now compares a pre-period mean to a
post-period mean and asks whether the instrument moved more than
frequency-and-dispersion-matched placebo words. That controls level and
burstiness and controls nothing about TREND -- and the in-time placebo showed
this vocabulary has been climbing in UK parliamentary English since at least
2006, steeper before 2017 than after. So the contrast reports a large "effect"
in windows where no LLM existed.

Kobak et al. do not do this. They fit each word's own trajectory and measure
deviation from it:

    q = p(-2) + 2 * max{ p(-2) - p(-3), 0 }        floored: never predicts a fall
    r = p / q                                       excess ratio
    d = p - q                                       excess gap

The year immediately before the target is deliberately skipped, so a
contaminated year cannot set the baseline. A word already rising gets a rising
counterfactual and shows no excess. That is the property we lost.

TWO ESTIMATORS, because 20 years of data supports something better than a
two-point slope:

  kobak   the published formula above, for fidelity
  trend   log-linear regression on all pre-target years, extrapolated forward
          (more stable; uses the full history)

THE VALIDATION THAT IS NOT OPTIONAL

Every target year is also run for PRE-LLM targets, where the answer must be
zero. An estimator that reports excess in 2017 is not measuring LLMs. This is
the check the previous design never had, and it is why the previous design
failed.

Usage: python kobak_counterfactual.py [--seg uk/segments_uk_long.jsonl]
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
N_PLACEBO = 400
MIN_WORDS = 200_000


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

    per = defaultdict(Counter)
    wc = Counter()
    disp = defaultdict(Counter)
    seen = {}
    for line in open(args.seg):
        d = json.loads(line)
        if not d.get("scoreable"):
            continue
        y = d["date"][:4]
        t = TOKEN_RE.findall(d["text"].lower())
        per[y].update(t)
        wc[y] += len(t)
        for w in set(t):
            if seen.get(w) != d["date"]:
                disp[y][w] += 1
                seen[w] = d["date"]

    years = sorted(y for y in per if wc[y] >= MIN_WORDS)
    yi = {y: int(y) for y in years}

    def rate(w, y):
        # 2023 is excluded by protocol, so some anchor years have no data;
        # a counterfactual that needs a missing year is undefined, not zero
        return per[y][w] / wc[y] if wc.get(y, 0) >= MIN_WORDS else None

    def kobak_q(w, t):
        """p(-2) + 2*max{p(-2)-p(-3),0}; the year before t is skipped."""
        a, b = str(t - 2), str(t - 3)
        if a not in per or b not in per:
            return None
        p2, p3 = rate(w, a), rate(w, b)
        if p2 is None or p3 is None:
            return None
        return p2 + 2 * max(p2 - p3, 0)

    def trend_q(w, t, hist):
        """log-linear fit on all available years <= t-2, extrapolated to t."""
        xs, ys = [], []
        for y in hist:
            if yi[y] <= t - 2:
                r_ = rate(w, y)
                if r_ is None:
                    continue
                xs.append(yi[y])
                ys.append(math.log(r_ + 1e-9))
        if len(xs) < 5:
            return None
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        den = sum((x - mx) ** 2 for x in xs)
        if den == 0:
            return None
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
        return math.exp(my + b * (t - mx))

    def arm(target, qfun, instrument, rng):
        t = int(target)
        ws = [w for w in instrument if per[target][w] > 0 and rate(w, target)]
        vals, cf = [], {}
        for w in ws:
            q = qfun(w, t)
            if q and q > 0:
                cf[w] = q
        ws = [w for w in ws if w in cf]
        if len(ws) < 30:
            return None
        real = sum(math.log(rate(w, target) / cf[w]) for w in ws) / len(ws)  # noqa

        # placebo: frequency x dispersion matched on the year that anchors the
        # counterfactual, so controls share the instrument's baseline profile
        anchor = str(t - 2)
        base, dsp = per[anchor], disp[anchor]
        excluded = set(instrument) | {w for w, _ in base.most_common(120)}
        pool = defaultdict(list)
        for w, n in base.items():
            if w in excluded or len(w) < 4 or not w.isalpha() or per[target][w] == 0:
                continue
            pool[(int(math.log2(n + 1)), int(math.log2(dsp.get(w, 0) + 1)))].append(w)
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

        pools = [pool_for((int(math.log2(base[w] + 1)),
                           int(math.log2(dsp.get(w, 0) + 1)))) for w in ws]
        draws = []
        for _ in range(N_PLACEBO):
            tot = k = 0
            for p in pools:
                w = rng.choice(p)
                q = qfun(w, t)
                r_ = rate(w, target)
                if q and q > 0 and r_:
                    tot += math.log(r_ / q)
                    k += 1
            if k > 20:
                draws.append(tot / k)
        if len(draws) < 50:
            return None
        draws.sort()
        med = draws[len(draws) // 2]
        ex = sum(1 for d in draws if d >= real)
        return {"n": len(ws), "excess": real - med, "p": ex / len(draws)}

    # instrument: full style list, and the instruct-preferred third
    META = re.compile(r"\b(this (text|passage|speech|statement|excerpt)|the speaker|"
                      r"appears to be|summary|analysis|here is|sure[,!]|as an ai)\b", re.I)
    B, I = Counter(), Counter()
    bn = inn = 0
    for fam in ("qwen3", "mistral"):
        try:
            b = json.load(open(f"{_HERE}/rlhf_gen/{fam}_base.json"))
            i = json.load(open(f"{_HERE}/rlhf_gen/{fam}_instruct.json"))
        except FileNotFoundError:
            continue
        for k in range(len(i)):
            if META.search(i[k][:300]) or META.search(b[k][:300]):
                continue
            tb = TOKEN_RE.findall(b[k].lower())
            ti = TOKEN_RE.findall(i[k].lower())
            B.update(tb); I.update(ti); bn += len(tb); inn += len(ti)
    ranked = sorted([w for w in style if B[w] + I[w] > 0],
                    key=lambda w: -math.log(((I[w] + .5) / inn) / ((B[w] + .5) / bn)))
    INSTRUMENTS = [("full style list", style)]
    if ranked:
        INSTRUMENTS.append(("instruct-preferred third", sorted(ranked[:len(ranked) // 3])))

    targets = [y for y in years if int(y) >= 2013]
    print(f"=== {args.label} ===  {len(years)} years, {years[0]}–{years[-1]}\n")
    for iname, inst in INSTRUMENTS:
        for qname, qf in (("kobak 2-point", kobak_q),
                          ("log-linear trend", lambda w, t: trend_q(w, t, years))):
            print(f"  {iname}  |  counterfactual: {qname}")
            print(f"    {'target':<8s} {'n':>4s} {'EXCESS':>9s} {'p':>7s}   era")
            for tg in targets:
                rng = random.Random(int(hashlib.sha1(
                    (args.label + iname + qname + tg).encode()).hexdigest()[:8], 16))
                r = arm(tg, qf, inst, rng)
                if not r:
                    continue
                era = "post-LLM" if int(tg) >= 2024 else "PRE-LLM (must be ~0)"
                flag = " *" if r["p"] < 0.05 else ""
                print(f"    {tg:<8s} {r['n']:>4d} {r['excess']:>+9.4f} "
                      f"{r['p']:>7.3f}   {era}{flag}")
            print()


if __name__ == "__main__":
    main()
