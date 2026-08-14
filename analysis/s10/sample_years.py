#!/usr/bin/env python3
"""Which years did each chamber's Pangram sample actually come from?

WHY THIS IS A RECORD AND NOT A CHECK

The era rule is uniform -- control is any sitting on or before 2022-06-30,
prevalence any sitting from 2025-01-01 -- but a chamber can only be sampled
from years that were DOWNLOADED, and the download windows were never uniform.
Fifteen chambers were fetched in two five-year blocks (2006-2010, 2015-2019)
plus 2025-26, so their controls stop in 2019 no matter what the era rule
permits. Federal Canada and the two US chambers run continuously and their
controls reach 2022.

That is not a defect, but it is a difference between chambers that has to be
stated rather than discovered. Two consequences follow from it:

  SPECIFICITY IS NOT MEASURED ON EQUALLY HARD TEXT. Register drifts
  continuously (4.5), so a control from 2009 is an easier test of a detector
  than one from 2022, which is much closer in register to the 2025-26 text the
  control is vouching for. A chamber whose controls average twelve years older
  than another's is making a weaker claim with the same clean numbers.

  A REDRAW MUST NOT SILENTLY WIDEN ITS OWN WINDOW. Manitoba's resample was
  first drawn from the corrected frame INCLUDING backfilled years, which pulled
  30 of 90 controls from 2011-14 and 2020-22 -- years no other chamber can draw
  from. Caught before scanning; the redraw is now restricted to the original
  windows so it changes the frame and nothing else.

The backfill completed 2026-08-13 makes 2020 to mid-2022 available for every
chamber. Using it is worth doing, but for all chambers at once, which is why it
is a separate item rather than something a per-chamber fix reaches for.

Usage: python sample_years.py [--csv]
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import banded_prevalence as BP              # noqa: E402
def load():
    """Read the dates OUT OF THE ESTIMATOR, not out of the verdict files.

    This script used to keep its own list of source files. It then went stale
    the moment federal Canada's chamber row moved from the genre arm to its
    uniform draw: the log went on reporting 218 CA-FED controls spanning
    2015-2022 while the estimator had moved to 98 spanning 2018-2022. A record
    of what is in the sample is worth nothing if it is assembled separately
    from the sample.

    banded_prevalence.load() fills META alongside its rows, so this reads the
    two together and cannot disagree with the figures they produce.
    """
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    data = BP.load()
    for (ch, era, band, nw, fl, fr), m in zip(data, BP.META):
        if era in ("prev", "ctl") and m.get("date"):
            rows[ch][era].append(m["date"])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true")
    a = ap.parse_args()
    rows = load()

    out = []
    for ch in sorted(rows):
        rec = {"chamber": ch}
        for era in ("ctl", "prev"):
            ds = sorted(rows[ch][era])
            rec[f"{era}_n"] = len(ds)
            rec[f"{era}_first"] = ds[0] if ds else ""
            rec[f"{era}_last"] = ds[-1] if ds else ""
            yrs = sorted({d[:4] for d in ds})
            rec[f"{era}_years"] = ",".join(yrs)
            if ds:
                med = sorted(int(d[:4]) for d in ds)[len(ds) // 2]
                rec[f"{era}_median_year"] = med
        out.append(rec)

    if a.csv:
        p = os.path.join(HERE, "sample_years.csv")
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        print(f"wrote {os.path.basename(p)}")
        return

    print("SAMPLED YEARS PER CHAMBER\n")
    print("Era rule: ctl <= 2022-06-30, prev >= 2025-01-01. What a chamber can")
    print("actually be drawn from is bounded by what was downloaded.\n")
    print(f"  {'chamber':<11s} {'ctl n':>6s} {'control window':>23s} "
          f"{'med':>5s} {'gap':>5s} | {'prev n':>6s} {'prevalence window':>23s}")
    for r in out:
        gap = 2025 - r.get("ctl_median_year", 2025)
        cw = f"{r['ctl_first']} .. {r['ctl_last']}" if r["ctl_n"] else "-"
        pw = f"{r['prev_first']} .. {r['prev_last']}" if r["prev_n"] else "-"
        flag = "  <-- reaches 2020+" if r["ctl_last"] >= "2020" else ""
        print(f"  {r['chamber']:<11s} {r['ctl_n']:>6d} {cw:>23s} "
              f"{r.get('ctl_median_year',0):>5d} {gap:>4d}y | "
              f"{r['prev_n']:>6d} {pw:>23s}{flag}")

    reach = [r["chamber"] for r in out if r["ctl_last"] >= "2020"]
    print(f"\n  Controls reaching 2020 or later: "
          f"{', '.join(reach) if reach else 'none'}")
    gaps = [2025 - r["ctl_median_year"] for r in out if r.get("ctl_median_year")]
    print(f"  Median control age across chambers: {sum(gaps)/len(gaps):.1f} "
          f"years before the prevalence window "
          f"(range {min(gaps)}-{max(gaps)})")


if __name__ == "__main__":
    main()
