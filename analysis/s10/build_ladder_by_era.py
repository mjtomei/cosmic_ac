#!/usr/bin/env python3
"""The coded altitude ladder, era-resolved (Matthew, 2026-08-26).

The joint model's occupational survivor is the coded ladder (block
p = 0.0008 beside everything else), so the era question the class panels
answer gets asked of it directly: does the instrument's shape hold across
half-decades? Levels are continuous per-member scores, so the era series
is each level's BASE SLOPE ENTERED ALONE — the altitude figure's own
estimand — per bin: member-bin register z (the class-by-era machinery's
value, identical construction) regressed on the level score standardised
per sd across that bin's contributing members, HC1 errors.

WRITES ladder_by_era.csv: half_decade x level -> slope, se, n.

Usage: python build_ladder_by_era.py
"""
import csv
import json
import math
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_estimation as PE                     # noqa: E402
import build_class_by_era as CBE                  # noqa: E402

LEVELS = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]


def main():
    code = PE.coding_maps()
    rows = PE.provincial_rows(code) + PE.tier1_rows(code)[0]

    scores = {}
    for r in json.load(open(os.path.join(HERE, "prereg_member_table.json"))):
        if r.get("lvl_MIDDLE") is not None:
            scores["|".join(r["member"].split("|")[:2])] = \
                [r[k] for k in LEVELS]

    ch_bin = defaultdict(list)
    for r in rows:
        e = CBE.era(r["year"])
        if e:
            ch_bin[(r["chamber"], e)].append(r)

    memz = defaultdict(lambda: [0.0, 0.0])
    for (ch, e), rs in ch_bin.items():
        rates = [r["rate"] for r in rs]
        mu = statistics.mean(rates)
        sd = statistics.pstdev(rates)
        if not sd:
            continue
        for r in rs:
            k = (ch, r["member"], e)
            memz[k][0] += r["words"]
            memz[k][1] += r["words"] * (r["rate"] - mu) / sd

    per_bin = defaultdict(list)                   # bin -> (z, [4 scores])
    for (ch, m, e), (w, wz) in memz.items():
        sc = scores.get("|".join(m.split("|")[:2]))
        if sc:
            per_bin[e].append((wz / w, sc))

    out = []
    for e in sorted(per_bin):
        sample = per_bin[e]
        y = [z for z, _ in sample]
        n = len(sample)
        for j, lv in enumerate(LEVELS):
            x = [sc[j] for _, sc in sample]
            mx = statistics.mean(x)
            sx = statistics.pstdev(x) or 1.0
            x = [(v - mx) / sx for v in x]
            my = statistics.mean(y)
            b = sum(xi * (yi - my) for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)
            a = my - b * mx * 0  # x already centred
            e2 = [(yi - a - b * xi) ** 2 for xi, yi in zip(x, y)]
            sxx = sum(xi * xi for xi in x)
            se = math.sqrt(sum(ei * xi * xi for ei, xi in zip(e2, x)) / sxx ** 2
                           * n / (n - 2))
            out.append((e, lv.split("_")[1], b, se, n))

    with open(os.path.join(HERE, "ladder_by_era.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "level", "slope_per_sd", "se", "n_members"])
        for e, lv, b, se, n in out:
            w.writerow([e, lv, f"{b:.4f}", f"{se:.4f}", n])
    for e, lv, b, se, n in out:
        print(f"{e}  {lv:<8} {b:+.3f} (se {se:.3f})  n {n}")


if __name__ == "__main__":
    main()
