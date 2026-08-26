#!/usr/bin/env python3
"""Class-by-era cells: the committed generator (review CC10, CC2 follow-up).

Supersedes the uncommitted in-session computation behind the previous
class_by_era*.csv (whose exact recipe was not recoverable; this documented
spec reproduces it to within hundredths of a z on every cell, with identical
membership up to one member, and every qualitative claim unchanged).

SPEC
  rows        the committed member-year panel (panel_estimation:
              provincial_rows + tier1_rows, their own >=8k-words-per-year
              and ambiguity filters), 1995 onward
  bins        complete half-decades 1995-99 .. 2020-24, plus the PARTIAL
              two-year bin 2025-26 (kept in the _all file, excluded from
              the paper files -- half-sized cells, VIIab absent)
  year z      each member-year's rate is z-scored against ALL member-years
              of its chamber x bin (unweighted mean/sd, coded or not), so
              the era rise and chamber levels are removed and only the
              cross-class shape remains
  member      a member's bin value is the word-weighted mean of their year
              z's in that bin; one value per member per bin, equal weight
              thereafter
  cells       per EGP class per bin over coded members: mean z, se
              (sd/sqrt n), n

WRITES
  class_by_era_all.csv      every cell, no filters, partial bin included
                            (column `partial` marks it)
  class_by_era.csv          complete bins only, cells with n >= 25
  class_by_era_grouped.csv  same, with IVc + V/VI + VIIab pooled as
                            manual+farm (the paper figure's input)
Also prints coverage: coded members contributing vs coded members total.

Usage: python build_class_by_era.py
"""
import csv
import math
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_estimation as PE                     # noqa: E402

BINS_END = 2024          # last complete half-decade ends here
POOL = {"IVc", "V/VI", "VIIab"}


def era(y):
    if y >= 2025:
        return "2025-2026"
    if y < 1995:
        return None
    lo = 1995 + ((y - 1995) // 5) * 5
    return f"{lo}-{lo + 4}"


def main():
    code = PE.coding_maps()
    rows = PE.provincial_rows(code) + PE.tier1_rows(code)[0]
    egp = {}
    for r in rows:
        if r["egp"]:
            egp[(r["chamber"], r["member"])] = r["egp"]

    ch_bin = defaultdict(list)
    for r in rows:
        e = era(r["year"])
        if e:
            ch_bin[(r["chamber"], e)].append(r)

    memz = defaultdict(lambda: [0.0, 0.0])        # (ch, member, bin) -> [w, wz]
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

    cells = defaultdict(list)                     # (bin, class) -> member z's
    contributing = set()
    for (ch, m, e), (w, wz) in memz.items():
        c = egp.get((ch, m))
        if c:
            cells[(e, c)].append(wz / w)
            contributing.add((ch, m))

    def stat(v):
        return (statistics.mean(v),
                statistics.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0,
                len(v))

    bins = sorted({e for e, _ in cells})
    out_all, out_paper, grouped = [], [], defaultdict(list)
    for e in bins:
        partial = int(e) if False else (1 if e == "2025-2026" else 0)
        for c in ("I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"):
            v = cells.get((e, c))
            if not v:
                continue
            m, se, n = stat(v)
            out_all.append((e, c, m, se, n, partial))
            if not partial and n >= 25:
                out_paper.append((e, c, m, se, n))
            if not partial:
                if c in POOL:
                    grouped[(e, "manual+farm")] += v
                elif n >= 25:
                    grouped[(e, c)] = v

    with open(os.path.join(HERE, "class_by_era_all.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "egp", "mean_z", "se", "n_members", "partial"])
        for e, c, m, se, n, p in out_all:
            w.writerow([e, c, f"{m:.4f}", f"{se:.4f}", n, p])
    with open(os.path.join(HERE, "class_by_era.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "egp", "mean_z", "se", "n_members"])
        for e, c, m, se, n in out_paper:
            w.writerow([e, c, f"{m:.4f}", f"{se:.4f}", n])
    with open(os.path.join(HERE, "class_by_era_grouped.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "group", "mean_z", "se", "n_members"])
        for (e, g), v in sorted(grouped.items()):
            if len(v) < 25:
                continue
            m, se, n = stat(v)
            w.writerow([e, g, f"{m:.4f}", f"{se:.4f}", n])

    total_coded = len({k for k in egp})
    in_window = len({(ch, m) for (ch, m, e) in memz if (ch, m) in egp})
    print(f"coded members total (panel, any year): {total_coded:,}")
    print(f"coded members with 1995+ panel years:  {in_window:,}")
    print(f"coded members contributing a cell:     {len(contributing):,}")
    print(f"cells written: all={len(out_all)}, paper={len(out_paper)}")
    for e, c, m, se, n, p in out_all:
        if p or n < 25:
            print(f"  thin/partial: {e} {c:<6} {m:+.3f} se {se:.3f} n {n}")


if __name__ == "__main__":
    main()
