#!/usr/bin/env python3
"""Occupation-by-era cells: the class-by-era machinery at occupation grain.

Matthew (2026-08-26): class ended up the joint model's lowest-power coding —
the occupational content absorbs the label — so the era figure gets an
occupation-code version. Same construction as build_class_by_era.py in
every respect (same bins, same chamber x bin year-z, same word-weighted
member-bin values, equal member weight in cells); the only change is the
grouping: O*NET-SOC major group (first two digits of the member's coded
SOC), from the prereg member table's double-blind occupation coding.

Panels: the seven largest major groups — management (11), legal (23),
education (25), media/arts (27), business/finance (13), health (29),
sales (41) — plus one pool of the manual, trades, service and protective
groups (31/33/35/37/39/45/47/49/51/53). Groups outside both sets
(community/social 21, science 19, military 55, office/admin 43,
engineering 17, computing 15) are written to the _all file but not
panelled; the caption says so.

WRITES occ_by_era_all.csv (every group x bin cell, no filters) and
occ_by_era.csv (the eight panel series).

Usage: python build_occ_by_era.py
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

PANEL = {"11": "management", "23": "legal", "25": "education",
         "27": "media and arts", "13": "business and finance",
         "29": "health", "41": "sales"}
POOL = {"31", "33", "35", "37", "39", "45", "47", "49", "51", "53"}
POOL_NAME = "manual trades and protective (pooled)"
OTHER = {"21": "community and social service", "19": "science",
         "55": "military", "43": "office and admin", "17": "engineering",
         "15": "computing"}


def main():
    code = PE.coding_maps()
    rows = PE.provincial_rows(code) + PE.tier1_rows(code)[0]

    soc = {}
    for r in json.load(open(os.path.join(HERE, "prereg_member_table.json"))):
        if r.get("soc"):
            soc["|".join(r["member"].split("|")[:2])] = r["soc"][:2]

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

    def keyfor(member, ch):
        return "|".join(member.split("|")[:2])

    cells = defaultdict(list)
    for (ch, m, e), (w, wz) in memz.items():
        g = soc.get(keyfor(m, ch))
        if not g:
            continue
        z = wz / w
        if g in PANEL:
            cells[(e, PANEL[g])].append(z)
        elif g in POOL:
            cells[(e, POOL_NAME)].append(z)
        if g in OTHER:
            cells[(e, OTHER[g])].append(z)

    def stat(v):
        return (statistics.mean(v),
                statistics.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0,
                len(v))

    names = list(PANEL.values()) + [POOL_NAME]
    with open(os.path.join(HERE, "occ_by_era_all.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "group", "mean_z", "se", "n_members"])
        for (e, g), v in sorted(cells.items()):
            m, se, n = stat(v)
            w.writerow([e, g, f"{m:.4f}", f"{se:.4f}", n])
    with open(os.path.join(HERE, "occ_by_era.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "group", "mean_z", "se", "n_members"])
        for (e, g), v in sorted(cells.items()):
            if g in names:
                m, se, n = stat(v)
                w.writerow([e, g, f"{m:.4f}", f"{se:.4f}", n])

    members = {(ch, m) for (ch, m, e) in memz
               if soc.get(keyfor(m, ch))}
    print(f"soc-coded members contributing: {len(members):,}")
    for (e, g), v in sorted(cells.items()):
        if g in names and len(v) < 25:
            m, se, n = stat(v)
            print(f"  thin: {e} {g:<40} {m:+.3f} se {se:.3f} n {n}")


if __name__ == "__main__":
    main()
