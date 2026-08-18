#!/usr/bin/env python3
"""The two-corporates reading of the Stage-1 results, with its exact status.

LABEL, CORRECTED (Matthew, 2026-08-18). An earlier version of this header
called the whole reading post-unblinding. That was wrong, and the correction
matters:

  REGISTERED AND WON (fd3f996, 13:05, before the first fit at 13:17):
    - insulated command above exposed command -- the apex delta, in exactly
      those words ("insulated command tracks more register than exposed
      command"), beta(delta) +0.049, t 3.3.
    - insulated-corporate above front-line -- this IS the registered primary
      ordering (corporate > front-line). In the registered continuous-slope
      form it FAILED (+0.029 vs +0.047; corporate top in 24% of resamples);
      in the group form below it holds (+0.082, t 2.1).
    - the argmax grouping itself -- registered, as a display.

  THE ONE UNREGISTERED KNOB: splitting the corporate cell at its own median
  apex delta. The ingredients are registered; that particular cut is not.

  NOT PINNED EITHER WAY by the registration: exposed-corporate vs front-line
  (observed -0.046, t -1.2, exposed below).

So the finding is a registered prediction read through registered machinery
with one unregistered knob -- not a post-hoc discovery. What the write-up must
still say plainly: the PRIMARY registered form of "insulated above front-line"
(continuous slopes) failed, and the group form succeeding while the slope form
fails is itself informative -- the corporate profile's -L weight fights the
population-wide positive L gradient, and binning frees the comparison from
that fight.

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
