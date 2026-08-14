#!/usr/bin/env python3
"""Which sitting days did we download and then fail to extract?

WHY

Three separate extractor faults were found by accident in one day, and every
one of them failed the same way: it produced no error, no warning and no
segments, so a day that was downloaded and parsed to nothing was
indistinguishable from a day the chamber did not sit.

  Northern Ireland  a speaker-type string changed in the pre-2015 API; 2012,
                    2013 and most of 2014 extracted to ZERO segments
  Nova Scotia       37 days of 2011 are published with unclosed <p> tags; the
                    closed-tag regex found only page furniture, zero speech
  Manitoba          a speaker prefix split across <b> runs from mid-2018; the
                    speech accreted to the Speaker and was dropped as chair
                    voice, costing 41% of 2019 and 65-78% of 2025-26

None of these was caught by a test. All three were caught because somebody
looked at a per-year table and thought a number seemed low. That is not a
control, so this is: for every chamber, compare the sitting days we DOWNLOADED
against the days that appear in the extracted segments, and report the
difference.

WHAT IT FLAGS, AND WHY EACH MATTERS

  MISSING   a raw file exists for that date and the segments file has no
            segment for it at all. This is the NI/NS failure and it is the
            dangerous one -- it looks exactly like a recess.

  THIN      the date yields segments but far fewer words than that chamber's
            own median day. This is the MB failure, which does not zero a day
            but quietly halves it.

A flag is not a bug. Chambers really do hold short sittings -- swearing-in,
condolence, prorogation, a single-item recall -- and some raw files really are
order papers rather than transcripts. The output is a list to look at, not a
verdict. What it buys is that the next fault of this kind is found by running
this rather than by noticing an odd number months later.

Usage:
  python extraction_audit.py                 # all chambers
  python extraction_audit.py --chamber mb    # one
  python extraction_audit.py --thin 0.15     # thin = under 15% of median day
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATE_RE = re.compile(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})")


def raw_dates(raw_dir):
    """Dates recoverable from the raw filenames in a directory."""
    out = collections.Counter()
    if not os.path.isdir(raw_dir):
        return out
    for name in os.listdir(raw_dir):
        m = DATE_RE.search(name)
        if not m:
            continue
        y, mo, d = m.groups()
        if not (1980 < int(y) < 2030 and 1 <= int(mo) <= 12 and 1 <= int(d) <= 31):
            continue
        out[f"{y}-{mo}-{d}"] += 1
    return out


def seg_days(paths):
    """date -> words, from the extracted segments."""
    out = collections.Counter()
    for p in paths:
        if not os.path.exists(p):
            continue
        for line in open(p):
            d = json.loads(line)
            dt = (d.get("date") or "")[:10]
            if dt:
                out[dt] += int(d.get("n_words") or 0)
    return out


def chambers():
    """prov -> (raw dirs, segment files), by filename convention."""
    out = collections.defaultdict(lambda: ([], []))
    prov = os.path.join(HERE, "provinces")
    for p in sorted(glob.glob(os.path.join(prov, "segments_*.jsonl"))):
        stem = os.path.basename(p)[len("segments_"):-len(".jsonl")]
        key = re.sub(r"_(?:2025|fill\d*|FIXED)$", "", stem)
        out[key][1].append(p)
    for d in sorted(glob.glob(os.path.join(prov, "*_raw*"))):
        if not os.path.isdir(d):
            continue
        key = re.sub(r"_raw(?:_.*)?$", "", os.path.basename(d))
        if key in out:
            out[key][0].append(d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chamber", default="")
    ap.add_argument("--thin", type=float, default=0.15)
    ap.add_argument("--show", type=int, default=6)
    a = ap.parse_args()

    print("EXTRACTION AUDIT -- downloaded days that produced no or little text\n")
    print(f"  {'chamber':<10s} {'raw days':>9s} {'extracted':>10s} "
          f"{'MISSING':>8s} {'THIN':>6s}  worst years")
    total_missing = 0
    for key, (raws, segs) in sorted(chambers().items()):
        if a.chamber and key != a.chamber:
            continue
        if not raws or not segs:
            continue
        rd = collections.Counter()
        for r in raws:
            rd.update(raw_dates(r))
        sd = seg_days(segs)
        if not rd:
            continue
        missing = sorted(d for d in rd if d not in sd)
        got = [w for w in sd.values() if w > 0]
        med = sorted(got)[len(got) // 2] if got else 0
        thin = sorted(d for d in rd
                      if d in sd and med and sd[d] < a.thin * med)
        total_missing += len(missing)
        byyear = collections.Counter(d[:4] for d in missing)
        worst = ", ".join(f"{y}:{n}" for y, n in byyear.most_common(3)) or "-"
        print(f"  {key:<10s} {len(rd):>9,} {len(sd):>10,} "
              f"{len(missing):>8d} {len(thin):>6d}  {worst}")
        if missing and a.show:
            print(f"      missing e.g. {', '.join(missing[:a.show])}")
    print(f"\n  {total_missing:,} downloaded days across all chambers produced "
          f"no segments.")
    print("  A flag is a thing to look at, not a bug: short sittings, "
          "condolence days and\n  order papers all land here legitimately. "
          "What matters is a RUN of them in one\n  year -- that is the "
          "signature of a markup change the extractor missed.")


if __name__ == "__main__":
    main()
