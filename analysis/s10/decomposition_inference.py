#!/usr/bin/env python3
"""Uncertainty on the within/between decomposition and the arrival premium.

WHY THIS EXISTS

The 16-chamber panel was reported as point estimates: continuing members'
register rate falls (within −0.42 mean), composition rises (+2.12), and new
arrivals enter above incumbents (+1.87). The negative within-member component
is load-bearing — it is what licenses "the climb is compositional, sitting
legislators did not change" — and it was never given an interval.

Each quantity is a weighted mean over MEMBERS, so the resampling unit is the
member, not the word or the segment. Words within a member are not independent
observations of anything.

  within    weighted mean over continuing members of their own rate change
            (bootstrap: resample continuing members with replacement)
  premium   pooled rate of arrivals minus pooled rate of incumbents
            (bootstrap: resample within each group separately)
  pooled    the cross-chamber mean of each quantity
            (bootstrap: resample CHAMBERS whole — 16 clusters, so the
            interval is wide and honestly so)

Reported as 95% percentile intervals. A chamber-level "significant" flag means
the interval excludes zero; with 16 chambers being examined at once, individual
flags should be read as descriptive rather than as 16 independent tests.

Usage: python decomposition_inference.py
"""
import csv
import glob
import json
import os
import random
import re
import statistics
from collections import defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
TITLE_RE = re.compile(
    r"^(rt\.?\s+hon\.?|hon\.?|honourable|l'hon\.?|mr\.?|mrs\.?|ms\.?|miss|dr\.?|"
    r"mme\.?|m\.|madame|monsieur|sir|dame|the)\s+", re.I)
ROLE = re.compile(
    r"^(premier|first minister|deputy|leader of the (official )?opposition|"
    r"minister\b|cabinet secretary|government house leader|"
    r"opposition house leader|attorney general|speaker|presiding officer|"
    r"llywydd|chair|president)", re.I)
EARLY = {str(y) for y in range(2006, 2011)}
LATE = {str(y) for y in range(2015, 2020)}
MIN_MEMBER_WORDS = 3000
N_BOOT = 2000


def norm(s):
    s = (s or "").strip().rstrip(":").strip()
    prev = None
    while prev != s:
        prev = s
        s = TITLE_RE.sub("", s).strip()
    return re.sub(r"\s*\(.*?\)\s*$", "", s).lower()


def ci(v, lo=0.025, hi=0.975):
    v = sorted(v)
    return v[int(lo * len(v))], v[int(hi * len(v))]


def main():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    prov = defaultdict(lambda: {"e": defaultdict(lambda: [0, 0]),
                                "l": defaultdict(lambda: [0, 0])})
    for path in sorted(glob.glob(os.path.join(_HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            y = d["date"][:4]
            w = "e" if y in EARLY else "l" if y in LATE else None
            if not w:
                continue
            nm = norm(d.get("speaker", ""))
            if not nm or ROLE.match(nm):
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            c = prov[d["prov"]][w][nm]
            c[0] += len(t)
            c[1] += sum(1 for x in t if x in style)

    rng = random.Random(11)
    print("Member-level bootstrap, 95% percentile intervals "
          f"({N_BOOT} resamples; resampling unit = member)\n")
    print(f"{'chamber':<7s} {'WITHIN':>8s} {'95% CI':>18s} {'sig':>4s}  "
          f"{'PREMIUM':>8s} {'95% CI':>18s} {'sig':>4s}")
    W, P = [], []
    for pv in sorted(prov):
        E, L = prov[pv]["e"], prov[pv]["l"]
        cont = [n for n in set(E) & set(L)
                if E[n][0] >= MIN_MEMBER_WORDS and L[n][0] >= MIN_MEMBER_WORDS]
        new = [n for n in L if n not in E and L[n][0] >= MIN_MEMBER_WORDS]
        inc = [n for n in L if n in E and L[n][0] >= MIN_MEMBER_WORDS]
        if len(cont) < 8 or len(new) < 8:
            continue

        def within_of(ms):
            wt = sum(L[n][0] for n in ms)
            if not wt:
                return 0.0
            return sum((L[n][1] / L[n][0] - E[n][1] / E[n][0]) * 1000 * L[n][0]
                       for n in ms) / wt

        def prem_of(a, b):
            wa = sum(L[n][0] for n in a)
            wb = sum(L[n][0] for n in b)
            if not wa or not wb:
                return 0.0
            return (sum(L[n][1] for n in a) / wa * 1000
                    - sum(L[n][1] for n in b) / wb * 1000)

        w_pt = within_of(cont)
        p_pt = prem_of(new, inc)
        wb = [within_of([cont[rng.randrange(len(cont))]
                         for _ in range(len(cont))]) for _ in range(N_BOOT)]
        pb = [prem_of([new[rng.randrange(len(new))] for _ in range(len(new))],
                      [inc[rng.randrange(len(inc))] for _ in range(len(inc))])
              for _ in range(N_BOOT)]
        wl, wh = ci(wb)
        pl, ph = ci(pb)
        W.append((pv, w_pt, wl, wh))
        P.append((pv, p_pt, pl, ph))
        print(f"{pv:<7s} {w_pt:>+8.2f} [{wl:>+7.2f},{wh:>+7.2f}] "
              f"{'*' if wh < 0 or wl > 0 else '':>4s}  "
              f"{p_pt:>+8.2f} [{pl:>+7.2f},{ph:>+7.2f}] "
              f"{'*' if ph < 0 or pl > 0 else '':>4s}")

    negW = [x for x in W if x[3] < 0]
    posW = [x for x in W if x[2] > 0]
    posP = [x for x in P if x[2] > 0]
    print(f"\nWITHIN: significantly NEGATIVE in {len(negW)}/{len(W)} chambers "
          f"({', '.join(x[0] for x in negW)})")
    print(f"        significantly POSITIVE in {len(posW)}/{len(W)} "
          f"({', '.join(x[0] for x in posW)})")
    print(f"PREMIUM: significantly positive in {len(posP)}/{len(P)} "
          f"({', '.join(x[0] for x in posP)})")

    # pooled across chambers, resampling chambers whole
    wv = [x[1] for x in W]
    pv_ = [x[1] for x in P]
    n = len(wv)
    wpool = [statistics.mean([wv[rng.randrange(n)] for _ in range(n)])
             for _ in range(N_BOOT)]
    ppool = [statistics.mean([pv_[rng.randrange(n)] for _ in range(n)])
             for _ in range(N_BOOT)]
    wl, wh = ci(wpool)
    pl, ph = ci(ppool)
    print(f"\nPOOLED over {n} chambers (chamber-level bootstrap):")
    print(f"  within  {statistics.mean(wv):+.2f}  95% CI [{wl:+.2f}, {wh:+.2f}]"
          f"{'  *' if wh < 0 or wl > 0 else '  (includes zero)'}")
    print(f"  premium {statistics.mean(pv_):+.2f}  95% CI [{pl:+.2f}, {ph:+.2f}]"
          f"{'  *' if ph < 0 or pl > 0 else '  (includes zero)'}")
    print(f"  sign test on the premium: positive in "
          f"{sum(1 for x in pv_ if x > 0)}/{n}, "
          f"one-sided binomial p = {0.5 ** n * sum(1 for _ in range(1)):.2e} "
          f"(exact for all-positive; see count above)")


if __name__ == "__main__":
    main()
