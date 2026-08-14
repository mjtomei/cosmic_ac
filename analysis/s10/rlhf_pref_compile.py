#!/usr/bin/env python3
"""Final compilation of the base-vs-instruct arm, at the point generation stopped.

WHAT WAS ACTUALLY GENERATED

The scaled run targeted four families at 6,400 prompts. It was stopped at 1,600
because the marginal information was small and the GPU was needed elsewhere.
What exists on disk:

    qwen3      (8B dense)   base 3200   instruct 3200
    llama31    (8B dense)   base 1600   instruct 1600
    mistral    (7B dense)   base 1600   instruct 1600
    qwen3_a3b  (30B MoE)    base 1600   instruct  800

Every family is reported at the largest checkpoint it COMPLETES ON BOTH SIDES,
and the headline is the checkpoint where the most families agree. qwen3 is
truncated to 1,600 rather than reported at 3,200 in the pooled figure, because
a pooled estimate that lets one family contribute twice the words of the others
is that family's estimate wearing a pool's name.

qwen3_a3b reaches 1,600 on base but only 800 on instruct, so it enters the
800-prompt row and not the 1,600 row. Its base surplus is not usable on its
own: the whole design is the PAIRED difference between a base model and its own
post-trained sibling, and half a pair measures nothing.

WHY IT STOPPED AT 1,600 RATHER THAN RUNNING TO 6,400

The A3B pair cost roughly six times its estimate. The plan priced a 30B MoE at
half the dense-8B rate on the assumption that ~3B active parameters buy most of
a 10x saving; at batch 48 they do not, because 48 sequences route to different
experts and the union of experts touched per step approaches the whole model.
Active-parameter arithmetic describes batch 1. The estimate should have been
built on measured throughput and was not.

WHAT THIS SCRIPT PRINTS

  * the excess at each checkpoint, on the families common to that checkpoint
  * per-family excess, which is the replication that matters more than the pool
  * the convergence table: does the estimate move as prompts double?

Usage: python rlhf_pref_compile.py
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rlhf_pref_scale as S          # noqa: E402
import rlhf_pref_analyze as A        # noqa: E402

GEN = os.path.join(HERE, "rlhf_gen")


def have(fam, role):
    p = os.path.join(GEN, f"{fam}_{role}.json")
    return len(json.load(open(p))) if os.path.exists(p) else 0


def main():
    style = A.load_style()
    rng = random.Random(20260812)

    print("WHAT IS ON DISK\n")
    print(f"  {'family':<12s} {'base':>7s} {'instruct':>9s} {'paired at':>10s}")
    paired = {}
    for fam, _, _ in S.PAIRS:
        b, i = have(fam, "base"), have(fam, "instruct")
        paired[fam] = min(b, i)
        print(f"  {fam:<12s} {b:>7d} {i:>9d} {min(b, i):>10d}")

    print("\n\nEXCESS BY CHECKPOINT (pooled over families complete at that n)\n")
    print(f"  {'n':>6s} {'fams':>5s} {'base words':>12s} {'pooled':>9s} "
          f"{'well-measured':>14s} {'#>=20 occ':>10s}")
    rows = []
    for c in (800, 1600, 3200):
        fams = [f for f, _, _ in S.PAIRS if paired[f] >= c]
        if not fams:
            continue
        r = S.excess_at(c, A, style, rng, only=set(fams))
        if not r:
            continue
        rows.append((c, fams, r))
        wm = r["excess_well_measured"]
        print(f"  {c:>6d} {r['families']:>5d} {r['base_words']:>12,} "
              f"{r['excess_pooled']:>+9.4f} "
              f"{(f'{wm:+.4f}' if wm is not None else 'n/a'):>14s} "
              f"{r['well_measured']:>10d}")
        print(f"         [{', '.join(fams)}]")

    print("\n\nPER FAMILY, each at its own largest complete checkpoint\n")
    print(f"  {'family':<12s} {'n':>6s} {'base words':>12s} {'pooled':>9s} "
          f"{'well-measured':>14s}")
    per = {}
    for fam, _, _ in S.PAIRS:
        n = paired[fam]
        if n < 800:
            print(f"  {fam:<12s} {n:>6d}  only {n} paired -- excluded")
            continue
        n = max(c for c in (800, 1600, 3200) if c <= n)
        r = S.excess_at(n, A, style, rng, only={fam})
        if not r:
            continue
        per[fam] = (n, r)
        wm = r["excess_well_measured"]
        print(f"  {fam:<12s} {n:>6d} {r['base_words']:>12,} "
              f"{r['excess_pooled']:>+9.4f} "
              f"{(f'{wm:+.4f}' if wm is not None else 'n/a'):>14s}")

    if per:
        vals = [r["excess_pooled"] for _, r in per.values()]
        print(f"\n  all {len(vals)} families positive: "
              f"{all(v > 0 for v in vals)}   "
              f"range {min(vals):+.4f} to {max(vals):+.4f}")

    print("\n\nCONVERGENCE: does the estimate move as prompts double?\n")
    print("  Compared on the SAME families, so the movement is sample size and")
    print("  not a change in which models are in the pool.\n")
    for a, b in ((800, 1600), (1600, 3200)):
        fa = [f for f, _, _ in S.PAIRS if paired[f] >= b]
        if not fa:
            continue
        ra = S.excess_at(a, A, style, rng, only=set(fa))
        rb = S.excess_at(b, A, style, rng, only=set(fa))
        if not (ra and rb):
            continue
        print(f"  {a} -> {b} on [{', '.join(fa)}]")
        print(f"     pooled        {ra['excess_pooled']:+.4f} -> "
              f"{rb['excess_pooled']:+.4f}  "
              f"({rb['excess_pooled']-ra['excess_pooled']:+.4f})")
        wa, wb = ra["excess_well_measured"], rb["excess_well_measured"]
        if wa is not None and wb is not None:
            print(f"     well-measured {wa:+.4f} -> {wb:+.4f}  ({wb-wa:+.4f})")
        print(f"     words at >=20 occurrences: {ra['well_measured']} -> "
              f"{rb['well_measured']}")

    out = {"paired": paired,
           "by_checkpoint": [{"n": c, "families": f, **r} for c, f, r in rows],
           "per_family": {k: {"n": n, **r} for k, (n, r) in per.items()}}
    json.dump(out, open(os.path.join(HERE, "rlhf_pref_final.json"), "w"),
              indent=1)
    print("\nwrote rlhf_pref_final.json")


if __name__ == "__main__":
    main()
