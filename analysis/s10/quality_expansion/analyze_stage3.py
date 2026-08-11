#!/usr/bin/env python3
"""Stage 3: does detector-evading rewriting improve or degrade the speech?

THE QUESTION

The most effective evasion strategy found was "self-limiting first person" --
admitting what you do not know, conceding about yourself rather than about the
world. It flipped Pangram on 39% of attempts, against 11% for stripping
tricolons and nominalisations. Epistemic humility was absent from 0 of 40
AI-drafted seeds and present in 15% of matched human speech.

So the operation that defeats the detector may be the same operation that
improves the deliberation. If so, "humanizing" is not a synonym for "hiding":
a member editing an AI draft to sound like themselves and a member laundering
one past a detector perform the same edit, and the text cannot distinguish
their motives.

DESIGN

38 texts, each contributing its unmodified ORIGINAL and its best HUMANIZED
variant. Blinded, interleaved, graded on the v2b DQI rubric. Within-text
pairing means content, speaker and occasion are held fixed by construction --
the only thing varying is the rewrite.

THE LENGTH CONFOUND IS REAL AND CONTROLLED. Humanized versions run ~30 words
longer at the median (200 vs 168). More room can lift justification and
evidence by itself, so the paired model reports the raw difference AND the
difference with word count as a covariate. Quote the adjusted one.

-1 codes INAPPLICABLE (no other demand / no counterargument on the table) and
is excluded from means, matching the published v2 convention.

Usage: python analyze_stage3.py [WORKFLOW_RUN_DIR]
"""
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENTINEL = {"respect_demands", "respect_counterargs"}
BASE = os.path.expanduser("~/.claude/projects")


def harvest(run_dir):
    out = {}

    def absorb(o):
        if isinstance(o, dict):
            i = o.get("id")
            if isinstance(i, str) and i[:1] in ("H", "G") and len(i) == 4 \
                    and "justification" in o:
                out[i] = o
            else:
                for v in o.values():
                    absorb(v)
        elif isinstance(o, list):
            for v in o:
                absorb(v)

    for p in glob.glob(os.path.join(run_dir, "*.jsonl")):
        for line in open(p):
            try:
                absorb(json.loads(line))
            except Exception:
                pass
    return out


def paired_t(diffs):
    n = len(diffs)
    if n < 3:
        return None, None
    m = statistics.mean(diffs)
    s = statistics.stdev(diffs)
    if s == 0:
        return m, float("inf")
    return m, m / (s / math.sqrt(n))


def ols(Y, X):
    n, k = len(Y), len(X[0])
    A = [[sum(X[i][a]*X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    yv = [sum(X[i][a]*Y[i] for i in range(n)) for a in range(k)]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    M = [r[:] for r in A]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]; I[c], I[p] = I[p], I[c]
        d = M[c][c]
        if abs(d) < 1e-12:
            return None
        M[c] = [v/d for v in M[c]]; I[c] = [v/d for v in I[c]]
        for r in range(k):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][j]-f*M[c][j] for j in range(k)]
                I[r] = [I[r][j]-f*I[c][j] for j in range(k)]
    beta = [sum(I[a][b]*yv[b] for b in range(k)) for a in range(k)]
    res = [Y[i]-sum(X[i][j]*beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(X[i][a]*X[i][b]*res[i]**2 for i in range(n)) for b in range(k)]
            for a in range(k)]
    sc = n/max(n-k, 1)
    V = [[sc*sum(I[a][p]*meat[p][q]*I[b][q] for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return [(beta[j], math.sqrt(max(V[j][j], 0))) for j in range(k)]


def main():
    args = [a for a in sys.argv[1:] if a != "--key4"]
    run = args[0] if args else None
    if not run:
        for c in sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                               "workflows", "wf_*")),
                        key=os.path.getmtime, reverse=True):
            if harvest(c):
                run = c
                break
    if not run:
        sys.exit("no run dir with H-ids found — pass one explicitly")
    print(f"run dir: {run}")
    kf = "key4.json" if "--key4" in sys.argv else "key3.json"
    pf = "G" if kf == "key4.json" else "H"
    key = json.load(open(os.path.join(HERE, kf)))
    g = harvest(run)
    print(f"graded {len(g)}/{len(key)}\n")
    if len(g) < 40:
        sys.exit("too few grades")

    pairs = {}
    for qid, rec in g.items():
        k = key.get(qid)
        if not k:
            continue
        pairs.setdefault(k["seg_id"], {})[k["condition"]] = (rec, k)
    full = {s: v for s, v in pairs.items() if "original" in v and "humanized" in v}
    print(f"complete pairs: {len(full)}/{len(pairs)}\n")

    print(f"{'dimension':<21s} {'original':>9s} {'humanized':>10s} "
          f"{'diff':>7s} {'t':>7s} {'+words adj':>11s}")
    for d in DIMS:
        raw, wd = [], []
        for s, v in full.items():
            o, h = v["original"][0].get(d), v["humanized"][0].get(d)
            if o is None or h is None:
                continue
            if d in SENTINEL and (o == -1 or h == -1):
                continue
            raw.append((o, h))
            wd.append(v["humanized"][1]["n_words"] - v["original"][1]["n_words"])
        if len(raw) < 5:
            print(f"{d:<21s} {'too few applicable pairs':>45s}")
            continue
        diffs = [h - o for o, h in raw]
        m, t = paired_t(diffs)
        fit = ols(diffs, [[1.0, w / 100.0] for w in wd])
        adj = f"{fit[0][0]:+.3f} (t{fit[0][0]/fit[0][1]:+.1f})" if fit else "n/a"
        print(f"{d:<21s} {statistics.mean(o for o,_ in raw):>9.2f} "
              f"{statistics.mean(h for _,h in raw):>10.2f} {m:>+7.2f} "
              f"{t:>+7.1f}{'*' if abs(t)>2.03 else ' '} {adj:>11s}  n={len(raw)}")

    print("\n  diff = humanized - original, paired within text.")
    print("  '+words adj' is the intercept with (humanized-original) word count")
    print("  as covariate: the effect at equal length. Quote that column.")
    print("  * marks |t| > 2.03 (two-sided .05 at ~35 df).")


if __name__ == "__main__":
    main()
