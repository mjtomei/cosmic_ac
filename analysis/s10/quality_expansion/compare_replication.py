#!/usr/bin/env python3
"""Stage 0: does the v2 judge reproduce on a different account?

WHY THIS EXISTS

The v2 rubric was verified byte-identical between commit 19deb97 and the
current dqi_judge_v2b.js, so re-running it on the SAME pool is a REPLICATION,
not a new measurement.

The pool is judge_blind_pool.json -- 241 segments, S-prefixed. NOT
judge_blind_pool_t.json, which is the 220-segment T-prefixed pool belonging to
the later per-year variant; its ids share zero overlap with the published
scores, so using it produces an empty comparison that reads like a clean run. If the group means
move materially, the "form up, deliberation down" result was a property of one
run rather than of the instrument, and every downstream quality claim is on
sand.

WHAT IT REPORTS, IN ORDER OF WHAT WOULD KILL THE FINDING

  1. GROUP MEANS, old vs new, per dimension. The published claim lives here:
     AI-flagged speech higher on justification/evidence, lower on
     respect_demands and constructive.
  2. THE SIGN TEST. For each dimension, does the AI-vs-human gap keep its
     sign? A replication that preserves magnitudes but flips a sign is worse
     than one that shifts everything uniformly.
  3. PER-SEGMENT AGREEMENT. Spearman and exact-match rate against the
     original codings. The original run's own repeat-pass Spearman was
     0.68-0.91, so cross-run agreement inside that band is reproducibility;
     below it is instability.

-1 IS EXCLUDED FROM MEANS, matching the original run's own convention
(recorded in fable_judge_v2_summary.csv: "-1=n/a excluded from means").
It codes INAPPLICABLE -- no other demand or counterargument on the table --
not a low score.

Usage: python compare_replication.py [WORKFLOW_RUN_DIR]
"""
import csv
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S10 = os.path.dirname(HERE)
# prefer the copy inside this folder so the package is portable
ORIG = (os.path.join(HERE, "fable_judge_v2_scores.csv")
        if os.path.exists(os.path.join(HERE, "fable_judge_v2_scores.csv"))
        else os.path.join(S10, "fable_judge_v2_scores.csv"))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENTINEL = {"respect_demands", "respect_counterargs"}
BASE = os.path.expanduser("~/.claude/projects")


def harvest(run_dir):
    out = {}

    def absorb(o):
        if isinstance(o, dict):
            i = o.get("id")
            if isinstance(i, str) and i.startswith("S") and len(i) == 4 \
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


def mean_ex(rows, d):
    v = [r[d] for r in rows if not (d in SENTINEL and int(r[d]) == -1)]
    return statistics.mean(v) if v else float("nan")


def spearman(a, b):
    n = len(a)
    if n < 3:
        return float("nan")
    def rank(x):
        order = sorted(range(n), key=lambda i: x[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and x[order[j + 1]] == x[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra)
                    * sum((y - mb) ** 2 for y in rb))
    return num / den if den else float("nan")


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    if not run:
        cands = sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                              "workflows", "wf_*")),
                       key=os.path.getmtime, reverse=True)
        for c in cands:
            if harvest(c):
                run = c
                break
    if not run:
        sys.exit("no workflow run with S-ids found — pass one explicitly")
    print(f"run dir: {run}")

    orig = {r["blind_id"]: r for r in csv.DictReader(open(ORIG))}
    new = harvest(run)
    both = sorted(set(orig) & set(new))
    print(f"original {len(orig)}, replication {len(new)}, overlap {len(both)}\n")
    if not both:
        sys.exit("ZERO overlap between run ids and fable_judge_v2_scores.csv — "
                 "wrong pool. Stage 0 must use judge_blind_pool.json (S-ids), "
                 "not judge_blind_pool_t.json (T-ids).")
    if len(both) < 100:
        sys.exit(f"only {len(both)} overlapping segments — too few to judge "
                 f"reproducibility")

    groups = sorted({orig[b]["group"] for b in both})
    print("=== 1. group means, original -> replication ===")
    for g in groups:
        ids = [b for b in both if orig[b]["group"] == g]
        o = [{d: int(orig[b][d]) for d in DIMS} for b in ids]
        n = [{d: int(new[b][d]) for d in DIMS} for b in ids]
        print(f"  {g} (n={len(ids)})")
        for d in DIMS:
            a, c = mean_ex(o, d), mean_ex(n, d)
            flag = "   <-- shifted" if abs(a - c) > 0.30 else ""
            print(f"    {d:<20s} {a:>6.3f} -> {c:>6.3f}  ({c-a:+.3f}){flag}")

    print("\n=== 2. sign test: does the AI-vs-human gap survive? ===")
    pairs = [("cand_ai", "cand_human"), ("B_ai", "B_human")]
    for ai_g, hu_g in pairs:
        ai_ids = [b for b in both if orig[b]["group"] == ai_g]
        hu_ids = [b for b in both if orig[b]["group"] == hu_g]
        if not ai_ids or not hu_ids:
            continue
        print(f"  {ai_g} vs {hu_g}  (n={len(ai_ids)} vs {len(hu_ids)})")
        for d in DIMS:
            def gap(src):
                return (mean_ex([{d: int(src[b][d])} for b in ai_ids], d)
                        - mean_ex([{d: int(src[b][d])} for b in hu_ids], d))
            go, gn = gap(orig), gap(new)
            same = "same sign" if (go > 0) == (gn > 0) else "** SIGN FLIP **"
            print(f"    {d:<20s} {go:>+6.3f} -> {gn:>+6.3f}   {same}")

    print("\n=== 3. per-segment agreement ===")
    print(f"  {'dimension':<20s} {'spearman':>9s} {'exact':>7s} {'n':>5s}")
    for d in DIMS:
        ids = [b for b in both
               if not (d in SENTINEL and (int(orig[b][d]) == -1
                                          or int(new[b][d]) == -1))]
        a = [int(orig[b][d]) for b in ids]
        c = [int(new[b][d]) for b in ids]
        ex = sum(1 for x, y in zip(a, c) if x == y) / len(ids) if ids else 0
        print(f"  {d:<20s} {spearman(a, c):>9.3f} {ex:>6.0%} {len(ids):>5d}")
    ai_a = [int(orig[b]["ai_guess"]) for b in both]
    ai_c = [int(new[b]["ai_guess"]) for b in both]
    print(f"  {'ai_guess':<20s} {spearman(ai_a, ai_c):>9.3f} "
          f"{'':>6s} {len(both):>5d}")
    print("\n  Original run's own repeat-pass Spearman was 0.68-0.91.")
    print("  Cross-run agreement inside that band = reproducible;")
    print("  materially below it = the instrument is unstable, and every")
    print("  downstream quality claim inherits that instability.")


if __name__ == "__main__":
    main()
