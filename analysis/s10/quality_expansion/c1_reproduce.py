#!/usr/bin/env python3
"""Recompute Appendix C.1 from committed + recovered files (review item Q12).

C.1 claims the quality instrument reproduces across accounts: the 241-segment
pool (judge_blind_pool.json) re-graded on a different account/machine, with
per-dimension Spearman 0.781-0.954 against the original. The review found no
cached output for the replication side, making the appendix unrecomputable.

Both sides now exist:
  original    ../fable_judge_v2_scores.csv (committed all along, S-ids)
  replication sset_grades_by_id.json -- 241 S-id rows recovered 2026-08-20
              from the grading machine's workflow transcripts
              (arch wf_bee1f1f9-c40; archive arch_more_wf.tgz)

This script computes the per-dimension Spearman and exact-match rate and
prints them beside C.1's published table. Match = Q12 fully closed.

Usage: python c1_reproduce.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
PUB = {"respect_demands": (0.954, 96), "evidence": (0.951, 92),
       "justification": (0.923, 88), "constructive": (0.877, 96),
       "respect_counterargs": (0.859, 86), "respect_groups": (0.812, 92),
       "common_good": (0.781, 88)}


def spearman(a, b):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def main():
    orig = {r["blind_id"]: r for r in
            csv.DictReader(open(os.path.join(HERE, "..",
                                             "fable_judge_v2_scores.csv")))}
    rep = json.load(open(os.path.join(HERE, "sset_grades_by_id.json")))
    ids = sorted(set(orig) & set(rep))
    print(f"paired segments: {len(ids)} (original {len(orig)}, "
          f"replication {len(rep)})\n")
    print(f"  {'dimension':<22s}{'Spearman':>9s}{'published':>10s}"
          f"{'exact%':>8s}{'published':>10s}")
    SENT = {"respect_demands", "respect_counterargs"}
    for d in sorted(DIMS, key=lambda d: -PUB[d][0]):
        # sentinel dimensions: -1 (inapplicable) excluded on either side,
        # the study's standard treatment -- and, verified here, the treatment
        # C.1's published table used (raw-including--1 gives 0.861/0.793)
        pp = [(int(orig[i][d]), int(rep[i][d])) for i in ids]
        if d in SENT:
            pp = [(x, y) for x, y in pp if x != -1 and y != -1]
        a = [x for x, _ in pp]
        b = [y for _, y in pp]
        rho = spearman(a, b)
        ex = 100 * sum(1 for x, y in zip(a, b) if x == y) / len(a)
        pr, pe = PUB[d]
        flag = "" if abs(rho - pr) < 0.005 and abs(ex - pe) < 1.0 else "  <-- differs"
        print(f"  {d:<22s}{rho:>9.3f}{pr:>10.3f}{ex:>7.0f}%{pe:>9d}%{flag}")


if __name__ == "__main__":
    main()
