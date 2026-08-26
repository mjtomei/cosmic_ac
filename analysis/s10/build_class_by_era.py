#!/usr/bin/env python3
"""Class-by-era cells: the committed generator (review CC10, CC2 follow-up).

Supersedes the uncommitted in-session computation behind the previous
class_by_era*.csv (whose exact recipe was not recoverable; run under that
recipe's own 1995-anchored binning, this documented spec reproduced it to
within hundredths of a z on every cell, with identical membership up to one
member and every qualitative claim unchanged — the binning has since moved
to end-anchored equal bins, below).

SPEC
  rows        the committed member-year panel (panel_estimation:
              provincial_rows + tier1_rows, their own >=8k-words-per-year
              and ambiguity filters), 1995 onward
  bins        six EQUAL five-year bins anchored at the data's end --
              1997-2001 .. 2022-2026 -- so every bin has the same span and
              the newest years are never the ones cut (Matthew, 2026-08-26:
              equal sizes; drop the earliest remainder, 1995-96, not the
              most recent). The last bin, 2022-2026, spans the machine era
              exactly
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
  class_by_era_all.csv      every cell, no n filter (the panel figure's
                            input)
  class_by_era.csv          cells with n >= 25
  class_by_era_grouped.csv  IVc + V/VI + VIIab pooled as manual+farm (the
                            gap-trend's input)
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

POOL = {"IVc", "V/VI", "VIIab"}


def era(y):
    """five-year bins anchored to end at 2026; years before 1997 drop."""
    if y > 2026 or y < 1997:
        return None
    hi = 2026 - ((2026 - y) // 5) * 5
    return f"{hi - 4}-{hi}"


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
        for c in ("I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"):
            v = cells.get((e, c))
            if not v:
                continue
            m, se, n = stat(v)
            out_all.append((e, c, m, se, n))
            if n >= 25:
                out_paper.append((e, c, m, se, n))
            if c in POOL:
                grouped[(e, "manual+farm")] += v
            elif n >= 25:
                grouped[(e, c)] = v

    with open(os.path.join(HERE, "class_by_era_all.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["half_decade", "egp", "mean_z", "se", "n_members"])
        for e, c, m, se, n in out_all:
            w.writerow([e, c, f"{m:.4f}", f"{se:.4f}", n])
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
    for e, c, m, se, n in out_all:
        if n < 25:
            print(f"  thin: {e} {c:<6} {m:+.3f} se {se:.3f} n {n}")


if __name__ == "__main__":
    main()
