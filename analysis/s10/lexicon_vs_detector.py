#!/usr/bin/env python3
"""Does the Kobak lexicon predict what a calibrated detector says, segment by segment?

WHY THIS REPLACES THE CONTENT-WORD CONTROL

The content-word arm asked whether biomedical topic vocabulary moved in a
parliament. It doesn't, but that is a fact about parliamentary topics, not
about our instrument -- orthogonal to whether the style measurement is picking
up AI rather than something else *here*. The frequency-and-dispersion-matched
placebo already controls for in-domain churn, using words that actually occur
in the domain. The content list adds nothing it does not already do.

The validation that bears on the question is: **does lexicon density predict
an independent measurement of the thing we care about?** Two detectors are
available, and neither has any connection to Kobak's word list:

  Pangram      calibrated in-domain (423/423 specificity), but expensive, so
               only ~120 unbiased segments
  Opus screen  AUC 0.951 against Pangram, and run over ALL 37,801 NB segments
               plus 4,800 segments across three other chambers

THE CONTROL THAT MAKES IT MEAN SOMETHING

A naive correlation is confounded by time: both lexicon density and detector
score rise after 2023, so they would correlate even if neither tracked the
other at the segment level. So every correlation here is also computed
WITHIN era. If density still predicts the detector among 2025-26 segments
alone -- where every segment shares the same period -- then the association is
segment-level, not a shared time trend.

Usage: python lexicon_vs_detector.py
"""
import csv
import json
import math
import os
import random
import re
from collections import defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
NB_SEGS = ["segments_59th.jsonl", "segments_60th.jsonl",
           "segments_61s1.jsonl", "segments.jsonl", "segments_all.jsonl"]


def load_style():
    return {r["word"].lower() for r in
            csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
            if r["type"] == "style" and r["word"].isalpha()}


def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            a = (i + j) / 2 + 1
            for k in range(i, j + 1):
                rk[s[k]] = a
            i = j + 1
        return rk
    rx, ry = rank(x), rank(y)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    pos, neg = sorted(pos), sorted(neg)
    tot = 0.0
    for a in pos:
        import bisect
        lo = bisect.bisect_left(neg, a)
        hi = bisect.bisect_right(neg, a)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(pos) * len(neg))


def density(text, lex):
    w = TOKEN_RE.findall(text.lower())
    return (sum(x in lex for x in w) / len(w) * 1000) if w else None


def boot_ci(x, y, rng, n=400):
    out = []
    m = len(x)
    for _ in range(n):
        idx = [rng.randrange(m) for _ in range(m)]
        out.append(spearman([x[i] for i in idx], [y[i] for i in idx]))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n)]


def main():
    lex = load_style()
    rng = random.Random(19)

    # ---------- New Brunswick: corpus-wide Opus screen ----------
    # the CSV carries a trailing comment row; skip anything non-numeric
    scores = {}
    for r in csv.DictReader(open("opus_screen_scores.csv")):
        v = (r.get("opus_screen") or "").strip()
        if v.lstrip("-").isdigit() and r.get("year", "").strip().isdigit():
            scores[r["seg_id"]] = (int(v), r["year"].strip())
    text = {}
    for f in NB_SEGS:
        if not os.path.exists(f):
            continue
        for line in open(f):
            d = json.loads(line)
            text.setdefault(d["seg_id"], d["text"])

    rows = []
    for sid, (sc, yr) in scores.items():
        t = text.get(sid)
        if not t:
            continue
        d = density(t, lex)
        if d is not None:
            rows.append((d, sc, yr))
    print(f"=== New Brunswick, corpus-wide Opus screen ===")
    print(f"  {len(rows):,} segments matched to text\n")

    def block(sub, label):
        if len(sub) < 200:
            print(f"  {label:<26s} n={len(sub):<6d} too few")
            return
        x = [r[0] for r in sub]
        y = [float(r[1]) for r in sub]
        rho = spearman(x, y)
        lo, hi = boot_ci(x, y, rng)
        pos = [r[0] for r in sub if r[1] >= 50]
        neg = [r[0] for r in sub if r[1] < 50]
        a = auc(pos, neg) if pos and neg else float("nan")
        print(f"  {label:<26s} n={len(sub):<6d} rho={rho:+.3f} "
              f"[{lo:+.3f},{hi:+.3f}]  AUC(screen>=50)={a:.3f}  "
              f"flagged={len(pos)}")

    block(rows, "all years (confounded)")
    print("  -- within era, which removes the shared time trend --")
    block([r for r in rows if r[2] <= "2022"], "pre-2023 only")
    block([r for r in rows if r[2] >= "2025"], "2025-26 only")
    for y in ("2025", "2026"):
        block([r for r in rows if r[2] == y], f"{y} only")

    # ---------- other chambers: blinded band screen ----------
    if os.path.exists("band_screen_key.json") and os.path.exists("band_screen_results.json"):
        key = json.load(open("band_screen_key.json"))
        pool = json.load(open("band_screen_pool.json"))
        import glob
        sc = {}

        def absorb(o):
            if isinstance(o, dict):
                if isinstance(o.get("id"), str) and o["id"].startswith("B") \
                        and "ai_guess" in o:
                    sc[o["id"]] = o["ai_guess"]
                else:
                    for v in o.values():
                        absorb(v)
            elif isinstance(o, list):
                for v in o:
                    absorb(v)
        base = ("/home/matt/.claude/projects/-home-matt-performance-commons/"
                "90221613-745b-4ed1-89b6-bc432df3d564/subagents/workflows/"
                "wf_08038a17-7d8")
        for p in glob.glob(f"{base}/*.jsonl"):
            for line in open(p):
                try:
                    absorb(json.loads(line))
                except Exception:
                    pass
        if sc:
            by = defaultdict(list)
            for sid, s in sc.items():
                k = key.get(sid)
                t = pool.get(sid)
                if not k or not t:
                    continue
                d = density(t, lex)
                if d is not None:
                    by[(k["chamber"], k["era"])].append((d, s, k["era"]))
            print(f"\n=== other chambers, blinded Opus band screen ===")
            for ch in ("ie", "ca", "uk"):
                for era in ("pre", "post"):
                    sub = by.get((ch, era), [])
                    if len(sub) >= 200:
                        x = [r[0] for r in sub]
                        y = [float(r[1]) for r in sub]
                        lo, hi = boot_ci(x, y, rng)
                        print(f"  {ch}-{era:<5s} n={len(sub):<5d} "
                              f"rho={spearman(x, y):+.3f} [{lo:+.3f},{hi:+.3f}]")


if __name__ == "__main__":
    main()
