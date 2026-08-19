#!/usr/bin/env python3
"""Q1's quantity: P(sentinel dimension applicable) by screen-score band.

Review item Q1 (2026-08-11): excluding the -1 (inapplicable) rows from the
sentinel dimensions conditions on something the treatment affects. This
script reports that quantity directly -- the share of stage-1 segments where
each sentinel dimension is applicable at all, by Opus-screen score band --
so the write-up can state the two claims separately: "engages no worse when
there is something to engage with" (the null) and "less likely to contain
anything to engage with" (this, not a null).

Usage: python applicability_by_band.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [("ai<10", lambda a: a < 10), ("10-49", lambda a: 10 <= a < 50),
         (">=50", lambda a: a >= 50)]


def main():
    rows = json.load(open(os.path.join(HERE, "results_stage1.json")))
    print(f"stage 1, {len(rows)} segments; applicability by screen band:")
    print(f"  {'dimension':<22s}" + "".join(f"{b:>9s}" for b, _ in BANDS)
          + f"{'n/band':>20s}")
    for d in ("respect_demands", "respect_counterargs"):
        cells, ns = [], []
        for _, f in BANDS:
            sub = [r for r in rows if f(r["ai"])]
            ns.append(len(sub))
            cells.append(100 * sum(1 for r in sub if r[d] != -1) / len(sub))
        print(f"  {d:<22s}" + "".join(f"{c:>8.1f}%" for c in cells)
              + f"   {'/'.join(map(str, ns))}")


if __name__ == "__main__":
    main()
