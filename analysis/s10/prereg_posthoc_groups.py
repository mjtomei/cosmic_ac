#!/usr/bin/env python3
"""POST-HOC: the two-corporates reading of the Stage-1 results.

WHY THIS FILE EXISTS, AND ITS LABEL

After Stage 1 ran, Matthew asked where the "two corporate groups -- one above
front-line, one below" prediction stood. That structure was discussed in
design but was NOT registered as an ordering: the elements cannot separate
middle from top (the corporate-levels arm), so the split entered the
registration as the apex delta (MIDDLE - TOP, predicted +, WON at t 3.3), the
rung arm, and the altitude quadratic -- not as two profiles around front-line.

This script assembles the post-hoc reading: argmax profile groups with the
corporate cell split at its own median apex delta. EVERYTHING HERE IS
POST-UNBLINDING except where noted; the registered shadow of this ordering is
the apex delta, and only that carries pre-registered weight.

Usage: python prereg_posthoc_groups.py
"""
import collections
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = ["prof_free", "prof_front_line", "prof_corporate"]


def main():
    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    rows = [r for r in tab if r.get("z") is not None and "comp_U" in r]
    corp = [r for r in rows if max(P, key=lambda k: r[k]) == "prof_corporate"]
    med = float(np.median([r["apex_delta"] for r in corp]))
    grp = collections.defaultdict(list)
    for r in rows:
        g = max(P, key=lambda k: r[k])[5:]
        if g == "corporate":
            g = "corp-insulated" if r["apex_delta"] >= med else "corp-exposed"
        grp[g].append(r["z"])
    print("argmax profile groups, corporate split at its own median apex "
          "delta (POST-HOC):")
    order = ["corp-insulated", "front_line", "corp-exposed", "free"]
    for g in order:
        v = grp[g]
        print(f"  {g:<15s}n={len(v):>5,}  mean z {np.mean(v):+.3f}  "
              f"(se {np.std(v)/math.sqrt(len(v)):.3f})")
    b = grp["front_line"]
    for g in ("corp-insulated", "corp-exposed"):
        a = grp[g]
        d = np.mean(a) - np.mean(b)
        se = math.sqrt(np.var(a)/len(a) + np.var(b)/len(b))
        print(f"  {g} - front_line: {d:+.3f} (t {d/se:+.1f})")
    print("\nregistered pieces this echoes: apex delta +0.049 (t 3.3, WON);")
    print("rung arm employed middle +0.092 vs executives -0.002. The linear")
    print("corporate profile lost (front-line +0.047 > corporate +0.029)")
    print("because it imposes -L on the whole population, while this grouping")
    print("lets external service feed the register globally and insulation")
    print("dominate within the command-holding cell.")


if __name__ == "__main__":
    main()
