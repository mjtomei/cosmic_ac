#!/usr/bin/env python3
"""Deployed Opus screen vs Pangram, and the six-detector comparison, under P4.

WHY THIS EXISTS

The write-up's headline "the Opus screen tracks Pangram at AUC X" is the
*deployed* screen -- opus_screen_full.js, 473 batches of 40, run over all
37,801 NB segments -- not the smaller lean validation run (opus_lean_screen.js,
25 batches of 10) whose number the A/B experiment uses. The two differ in
score LEVEL (mean 26.5 lean vs 34.3 deployed) but not in discrimination. This
script reports the deployed screen's own AUC so the headline cites the config
that actually ran.

All labels are Pangram 4 (pangram_p4_verdicts.csv), the study's canonical
oracle per METHODOLOGY 3.2 -- NOT the P3 group field baked into
fable_judge_v2_scores.csv, which predates the rescore. Segment id join is
deployed seg_id -> Pangram seg_id directly; the six-detector files are keyed by
blind_id and joined seg-wise through fable_judge_v2_scores.csv's blind_id->sid.

Prints:
  1. deployed screen AUC on the 618-segment Pangram overlap
  2. the same restricting negatives to 2023+ (contemporary human text only),
     which is LOWER -- contemporary speech is harder to separate, corroborating
     the permeation finding rather than flattering the screen
  3. the six prompt-detector configurations, all under P4

Usage: python opus_screen_auc.py
"""
import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))


def auc(pairs):
    pos = [s for s, y in pairs if y]
    neg = [s for s, y in pairs if not y]
    if not pos or not neg:
        return None
    w = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return w / (len(pos) * len(neg))


def ci(pairs, n=4000, seed=7):
    rng = random.Random(seed)
    v = []
    for _ in range(n):
        s = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        a = auc(s)
        if a is not None:
            v.append(a)
    v.sort()
    return v[int(0.025 * len(v))], v[int(0.975 * len(v))]


def p(f):
    return os.path.join(HERE, f)


def num(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def load_p4():
    lab = {}
    for r in csv.DictReader(open(p("pangram_p4_verdicts.csv"))):
        v = r.get("pangram")
        lab[r["seg_id"]] = 1 if v in ("AI", "Mixed") else 0 if v == "Human" else None
    return lab


def load_sidmap():
    """blind_id -> sid, over the labelled A/B pool."""
    sid = {}
    for r in csv.DictReader(open(p("fable_judge_v2_scores.csv"))):
        g = r["group"]
        if g.endswith("_ai") or g.endswith("_human") or g == "ctl2019":
            sid[r["blind_id"]] = r["sid"]
    return sid


def main():
    p4 = load_p4()

    # 1-2. deployed screen
    dep, yr = {}, {}
    for r in csv.DictReader(open(p("opus_screen_scores.csv"))):
        s = num(r["opus_screen"])
        if s is not None:
            dep[r["seg_id"]] = s
            yr[r["seg_id"]] = r.get("year")
    ov = [s for s in dep if p4.get(s) is not None]
    full = [(dep[s], p4[s]) for s in ov]
    a = auc(full)
    lo, hi = ci(full)
    npos = sum(1 for _, y in full if y)
    print(f"deployed screen vs P4, 618 overlap: AUC={a:.4f} [{lo:.3f}, {hi:.3f}]"
          f"  ({npos} AI / {len(full)-npos} human)")

    def era(y):
        try:
            return int(str(y)[:4])
        except (TypeError, ValueError):
            return None
    post = [(dep[s], p4[s]) for s in ov
            if p4[s] == 1 or (era(yr.get(s)) or 0) >= 2023]
    a = auc(post)
    lo, hi = ci(post)
    npos = sum(1 for _, y in post if y)
    print(f"    negatives restricted to 2023+: AUC={a:.4f} [{lo:.3f}, {hi:.3f}]"
          f"  ({npos} AI / {len(post)-npos} human)")

    # 3. six-detector comparison, all P4
    sid = load_sidmap()

    def p4b(b):
        return p4.get(sid.get(b))

    def load(f, col):
        d = {}
        for r in csv.DictReader(open(p(f))):
            if r.get(col):
                d[r["blind_id"]] = int(float(r[col]))
        return d
    dets = [("Claude Opus 5 (low effort)", "opus_lean_scores.csv", "opus_ai_guess"),
            ("Claude Fable 5 (high effort)", "fable_judge_v2_scores.csv", "ai_guess"),
            ("Qwen3-32B (thinking)", "det_qwen32_high.csv", "ai_guess"),
            ("gpt-oss-120b (high reasoning)", "det_oss120_high.csv", "ai_guess"),
            ("gpt-oss-120b (low reasoning)", "det_oss120_low.csv", "ai_guess"),
            ("Qwen3-32B (no thinking)", "det_qwen32_low.csv", "ai_guess")]
    print("\nsix-detector comparison, AUC vs Pangram 4 (241-segment pool):")
    for nm, f, col in dets:
        d = load(f, col)
        pr = [(v, p4b(b)) for b, v in d.items() if p4b(b) is not None]
        print(f"  {nm:<32s} {auc(pr):.3f}  (n={len(pr)})")


if __name__ == "__main__":
    main()
