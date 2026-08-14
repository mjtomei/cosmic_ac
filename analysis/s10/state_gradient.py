#!/usr/bin/env python3
"""Exposure gradient: does register drift track state technology adoption?

THE HYPOTHESIS UNDER TEST (Matthew's, from the Coherence line of argument)

The 20-year UK series shows the assistant-flavoured register climbing from
~2006 -- when mass computer immersion became ambient, a decade before LLMs.
One reading: habitual interaction with highly capable systems treated as
tools reshaped how people produce language. The rival reading: the same years
are the professionalised-communications era, a NATIONAL phenomenon.

The two make different predictions about geography. Message discipline came
from party centres and hit everyone at once; exposure came through local
adoption, which varied enormously by state (Sept 2001: Mississippi ~42%
internet use, Alaska ~69%). So:

    exposure hypothesis  -> members from early-adopting states drift MORE
    national-comms rival -> drift is uniform in adoption

DESIGN

Per-speaker register drift between two pre-LLM windows -- early 2006-2010,
late 2015-2019 -- regressed on the speaker's state internet adoption (NTIA
Sept 2001 CPS, CI midpoints). Entirely pre-ChatGPT, so nothing about LLM
adoption contaminates it. Drift is the equal-weight mean log fold-change over
Kobak style words the speaker used in the early window (the statistic that
carries the corpus effect; pooled rates gave opposite answers elsewhere),
minus the same quantity on that speaker's frequency-matched placebo words.

CONFOUNDS, STATED

Adoption level correlates with urbanicity, education and income, which may
correlate with speech style DIRECTLY. Defences here: (a) the outcome is a
WITHIN-SPEAKER CHANGE, so any level difference between states cancels --
the confound must act on the drift rate, not the level; (b) region fixed
effects, so identification comes from within-region adoption differences
(e.g. Minnesota 63.5 vs Missouri 57.3); (c) party and chamber controls.
Residual confounding by state-level trends in composition (who gets elected)
is NOT excluded and is flagged in the output.

Speakers are joined to states by bioGuideId from the congMember metadata,
never by surname.

Usage: python state_gradient.py [--early 2006-2010] [--late 2015-2019]
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
MIN_WORDS = 6000
MIN_USED = 15
N_PLACEBO_SETS = 20
SEGS = ["us/segments_us_house.jsonl", "us/segments_us_senate.jsonl"]


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def years(spec):
    a, b = spec.split("-")
    return {str(y) for y in range(int(a), int(b) + 1)}


def ols(y, X, names):
    """Tiny OLS with HC1 robust SEs; X includes the intercept column."""
    n, k = len(y), len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
           for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    # gaussian elimination
    M = [row[:] + [Xty[a]] for a, row in enumerate(XtX)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            return None
        for r in range(k):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(k + 1)]
    beta = [M[c][k] / M[c][c] for c in range(k)]
    resid = [y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    # HC1
    inv = [[0.0] * k for _ in range(k)]
    A = [row[:] for row in XtX]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        I[c], I[p] = I[p], I[c]
        d = A[c][c]
        A[c] = [v / d for v in A[c]]
        I[c] = [v / d for v in I[c]]
        for r in range(k):
            if r != c:
                f = A[r][c]
                A[r] = [A[r][j] - f * A[c][j] for j in range(k)]
                I[r] = [I[r][j] - f * I[c][j] for j in range(k)]
    meat = [[sum(X[i][a] * X[i][b] * resid[i] ** 2 for i in range(n))
             for b in range(k)] for a in range(k)]
    scale = n / max(n - k, 1)
    V = [[scale * sum(I[a][p] * meat[p][q] * I[b][q]
                      for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0)))
            for j, nm in enumerate(names)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--early", default="2006-2010")
    ap.add_argument("--late", default="2015-2019")
    args = ap.parse_args()
    E, L = years(args.early), years(args.late)
    style = load_style()
    sset = set(style)

    cov = {}
    for r in csv.DictReader(open(os.path.join(_HERE, "state_covariates.csv"))):
        if r["state"].startswith("#"):
            continue
        cov[r["state"]] = (float(r["internet2001"]), r["region"])

    pre = defaultdict(Counter)
    post = defaultdict(Counter)
    meta = {}
    corpus_early = Counter()
    for path in SEGS:
        if not os.path.exists(path):
            continue
        ch = "senate" if "senate" in path else "house"
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable") or not d.get("person_id"):
                continue
            y = d["date"][:4]
            if y in E:
                tgt = pre
            elif y in L:
                tgt = post
            else:
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            pid = d["person_id"]
            tgt[pid].update(t)
            if y in E:
                corpus_early.update(t)
            if pid not in meta and d.get("state") in cov:
                meta[pid] = (d["state"], d.get("party", ""), ch)

    if not corpus_early:
        raise SystemExit(f"no data in the early window {args.early} — "
                         f"has the historical extraction run?")

    rng = random.Random(int(hashlib.sha1(b"stategrad").hexdigest()[:8], 16))
    excluded = sset | {w for w, _ in corpus_early.most_common(120)}
    bucket = defaultdict(list)
    for w, c in corpus_early.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(c + 1))].append(w)

    def pool_for(b):
        for off in (0, 1, -1, 2, -2, 3, -3):
            if bucket.get(b + off):
                return bucket[b + off]
        return max(bucket.values(), key=len)

    pools = [pool_for(int(math.log2(corpus_early[w] + 1))) for w in style]
    placs = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO_SETS)]

    def eqw(a, b, wa, wb, words):
        used = [w for w in words if a[w] > 0]
        if len(used) < MIN_USED:
            return None
        return sum(math.log(((b[w] + 0.5) / wb) / ((a[w] + 0.5) / wa))
                   for w in used) / len(used)

    rows = []
    for pid in set(pre) & set(post):
        if pid not in meta:
            continue
        a, b = pre[pid], post[pid]
        wa, wb = sum(a.values()), sum(b.values())
        if wa < MIN_WORDS or wb < MIN_WORDS:
            continue
        ei = eqw(a, b, wa, wb, style)
        if ei is None:
            continue
        ep = [x for x in (eqw(a, b, wa, wb, P) for P in placs) if x is not None]
        if not ep:
            continue
        st, party, ch = meta[pid]
        rows.append({"pid": pid, "state": st, "party": party, "chamber": ch,
                     "drift": ei - sum(ep) / len(ep),
                     "adopt": cov[st][0], "region": cov[st][1],
                     "w_early": wa, "w_late": wb})
    print(f"{len(rows)} members with >= {MIN_WORDS:,} words in both windows "
          f"({args.early} and {args.late})")
    if len(rows) < 60:
        raise SystemExit("too few members — check window coverage")

    json.dump(rows, open("state_gradient_members.json", "w"), indent=1)

    drift = [r["drift"] for r in rows]
    adopt = [r["adopt"] for r in rows]
    ma = sum(adopt) / len(adopt)
    sa = math.sqrt(sum((x - ma) ** 2 for x in adopt) / (len(adopt) - 1))
    z = [(x - ma) / sa for x in adopt]

    def spear(x, y):
        def rank(v):
            s = sorted(range(len(v)), key=lambda i: v[i])
            rk = [0.0] * len(v)
            i = 0
            while i < len(s):
                j = i
                while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                    j += 1
                a_ = (i + j) / 2 + 1
                for k2 in range(i, j + 1):
                    rk[s[k2]] = a_
                i = j + 1
            return rk
        rx, ry = rank(x), rank(y)
        n = len(rx)
        mx, my = sum(rx) / n, sum(ry) / n
        num = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
        den = math.sqrt(sum((p - mx) ** 2 for p in rx) *
                        sum((q - my) ** 2 for q in ry))
        return num / den

    print(f"\nraw Spearman(drift, state adoption 2001) = {spear(drift, adopt):+.3f}")

    regions = sorted({r["region"] for r in rows})[1:]
    names = ["const", "adoption_z", "rep", "senate"] + [f"reg_{g}" for g in regions]
    X = [[1.0, z[i], 1.0 if rows[i]["party"] == "R" else 0.0,
          1.0 if rows[i]["chamber"] == "senate" else 0.0] +
         [1.0 if rows[i]["region"] == g else 0.0 for g in regions]
         for i in range(len(rows))]
    fit = ols(drift, X, names)
    print("\nOLS of per-member drift on standardised adoption "
          "(party, chamber, region FE; HC1 robust SEs):")
    for nm in names:
        b_, se = fit[nm]
        t = b_ / se if se else float("nan")
        mark = " *" if abs(t) > 1.96 else ""
        print(f"  {nm:<12s} {b_:+.4f}  (se {se:.4f}, t {t:+.2f}){mark}")

    print("\nReading: adoption_z is the exposure test. Positive and significant")
    print("supports the exposure hypothesis over the national-communications")
    print("rival, which predicts a coefficient of zero. Composition trends in")
    print("who gets elected per state remain unexcluded.")


if __name__ == "__main__":
    main()
