#!/usr/bin/env python3
"""Cross-chamber summary of the 2025+ extension.

Reads every segments_{prov}_2025.jsonl present and prints one row per chamber:
sitting days, segments, scoreable, words, period covered, zero-month count.
Chambers with no file at all are listed as MISSING so a silent gap cannot hide.

Usage: python3 extend2025_summary.py [--csv OUT.csv]
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent

CHAMBERS = [
    ("bc", "BC - British Columbia"),
    ("ab", "AB - Alberta"),
    ("sk", "SK - Saskatchewan"),
    ("mb", "MB - Manitoba"),
    ("on", "ON - Ontario"),
    ("ns", "NS - Nova Scotia"),
    ("nl", "NL - Newfoundland & Labrador"),
    ("pe", "PE - Prince Edward Island"),
    ("aus_nsw", "NSW - New South Wales"),
    ("aus_vic", "VIC - Victoria"),
    ("aus_qld", "QLD - Queensland"),
    ("aus_wa", "WA - Western Australia"),
    ("aus_sa", "SA - South Australia"),
    ("aus_tas", "TAS - Tasmania"),
    ("scot", "SCO - Scotland"),
    ("wales", "WAL - Wales"),
    ("ni", "NI - Northern Ireland"),
]


def months_between(first, last):
    y, m = int(first[:4]), int(first[5:7])
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    a = ap.parse_args()

    rows = []
    for prov, label in CHAMBERS:
        f = HERE / f"segments_{prov}_2025.jsonl"
        if not f.exists():
            rows.append([label, "MISSING", "", "", "", "", ""])
            continue
        segs = [json.loads(l) for l in open(f)]
        if not segs:
            rows.append([label, "EMPTY", 0, 0, 0, "-", "-"])
            continue
        dates = sorted({s["date"] for s in segs})
        mseg = Counter(s["date"][:7] for s in segs)
        zero = [m for m in months_between(dates[0][:7], dates[-1][:7])
                if mseg[m] == 0]
        rows.append([
            label, "ok", len(dates), len(segs),
            sum(1 for s in segs if s["scoreable"]),
            sum(s["n_words"] for s in segs),
            f"{dates[0]}..{dates[-1]}",
            len(zero),
        ])

    hdr = ["chamber", "status", "sitting days", "segments", "scoreable",
           "words", "period", "zero months"]
    widths = [max(len(str(r[i])) if i < len(r) else 0 for r in rows + [hdr])
              for i in range(len(hdr))]
    def line(r):
        r = list(r) + [""] * (len(hdr) - len(r))
        return "  ".join(str(v).ljust(widths[i]) if i < 2 else
                         str(v).rjust(widths[i]) for i, v in enumerate(r))
    print(line(hdr))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(line(r))

    tot = [r for r in rows if r[1] == "ok"]
    if tot:
        print()
        print(f"TOTAL: {len(tot)} chambers, "
              f"{sum(r[2] for r in tot)} sitting days, "
              f"{sum(r[3] for r in tot)} segments, "
              f"{sum(r[5] for r in tot)} words")

    if a.csv:
        import csv
        with open(a.csv, "w", newline="") as fh:
            wtr = csv.writer(fh)
            wtr.writerow(hdr)
            wtr.writerows(rows)
        print(f"wrote {a.csv}")


if __name__ == "__main__":
    main()
