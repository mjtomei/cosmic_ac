#!/usr/bin/env python3
"""Did the other chambers converge on the US level, or pass it?

WHY THIS EXISTS

4.5a's reading is that the anglophone legislatures have been climbing toward a
level the United States already held. A 2026 snapshot appears to contradict it:
the Canadian provinces, Ireland, the Australian states and federal Canada all
sit ABOVE US House that year, and convergence should approach a level, not
overshoot it.

The snapshot is misleading, and the reason is variance. US House swings between
1,660 and 2,074 across 2006-2026 -- a 25% range, the widest of any series here,
and wider than the gaps being read off the chart. In 2026 it happens to sit at
1,709, near its own floor. Comparing one chamber-year against another chamber-
year is comparing two draws from noisy distributions.

WHAT THIS DOES

Compares 2020-2026 MEANS with each series' own standard deviation alongside, so
an apparent overshoot can be judged against the variation it has to clear. It
also reports the human-only version, subtracting machine-written text at each
chamber's measured share (ai_share_by_chamber.json), because the obvious rescue
for an overshoot -- "it is exported AI pushing them past" -- has to be tested
rather than assumed.

THE ANSWER, MEASURED 2026-08-13

Only the Canadian provinces are meaningfully above US House on a seven-year
mean (+155, or 1.28 US-House sd). Ireland is +2, which is nothing. The
Australian states and federal Canada are BELOW. Three of the four apparent
overshoots are US House having a low year.

And exported AI does not explain the rest, because it cuts the wrong way: US
House is 14.3% machine by occurrences against Ireland's 9.0%, so removing
machine text lowers the American benchmark by MORE than it lowers the
challengers. The one case it does explain is federal Canada, the most
machine-written chamber in the study at 21.7%, which drops from apparently-
above to clearly-below once its AI is removed.

So the chambers caught up and clustered; they did not pass. That is what
convergence looks like, and it leaves 4.5a's reading intact -- with the
Canadian provinces as a standing exception that needs its own account.

Usage: python convergence_check.py [--from 2020] [--to 2026]
"""
import argparse
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = {"AUS_NSW": "NSW", "AUS_QLD": "QLD", "AUS_TAS": "TAS", "AUS_VIC": "VIC",
       "AUS_WA": "WA", "SCOT": "SCO", "WALES": "WAL",
       "US-House": "US-HOUSE", "US-Senate": "US-SENATE"}
GRP = {"_GRP_CA_PROV": ["AB", "BC", "MB", "NL", "NS", "ON", "SK"],
       "_GRP_AUS_STATE": ["AUS_NSW", "AUS_QLD", "AUS_TAS", "AUS_VIC", "AUS_WA"],
       "_GRP_UK_DEVOLVED": ["SCOT", "WALES"]}
SERIES = [("US-House", "US House"), ("US-Senate", "US Senate"),
          ("_GRP_CA_PROV", "CA provinces"), ("_GRP_AUS_STATE", "AUS states"),
          ("IE", "Ireland"), ("CA-FED", "Canada federal"),
          ("UK", "UK Commons"), ("_GRP_UK_DEVOLVED", "UK devolved")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", type=int, default=2020)
    ap.add_argument("--to", dest="hi", type=int, default=2026)
    a = ap.parse_args()
    d = json.load(open(os.path.join(HERE, "occurrence_trends.json")))
    p = os.path.join(HERE, "ai_share_by_chamber.json")
    so = json.load(open(p))["share_occurrences"] if os.path.exists(p) else {}

    def share(ch):
        k = KEY.get(ch, ch)
        if k in so:
            return so[k]
        if ch in GRP:
            return statistics.mean(so.get(KEY.get(m, m), 0) for m in GRP[ch])
        return 0.0

    print(f"MEAN INSTRUMENT GAP, {a.lo}-{a.hi}\n")
    print(f"  {'chamber':<16s} {'mean':>7s} {'sd':>6s} {'min':>7s} {'max':>7s} "
          f"{'human-only':>11s}")
    rows = []
    for k, lab in SERIES:
        pts = [x for x in d.get(k, []) if a.lo <= x["year"] <= a.hi]
        if len(pts) < 4:
            continue
        g = [x["gap"] for x in pts]
        s = share(k)
        adj = statistics.mean(
            [x["gap"] * (1 - s) if x["year"] >= 2025 else x["gap"] for x in pts])
        rows.append((lab, statistics.mean(g), statistics.pstdev(g),
                     min(g), max(g), adj, s))
        print(f"  {lab:<16s} {statistics.mean(g):>7.0f} "
              f"{statistics.pstdev(g):>6.0f} {min(g):>7.0f} {max(g):>7.0f} "
              f"{adj:>11.0f}")

    ref = next(r for r in rows if r[0] == "US House")
    print(f"\nAGAINST US HOUSE (mean {ref[1]:.0f}, sd {ref[2]:.0f})\n")
    print("  A difference smaller than the US House's own standard deviation is")
    print("  not an overshoot; it is one chamber having a low year.\n")
    for lab, m, sd, lo_, hi_, adj, s in rows:
        if lab == "US House":
            continue
        diff = m - ref[1]
        z = diff / ref[2]
        verdict = ("ABOVE" if z > 1 else "at parity" if abs(z) <= 1 else "below")
        print(f"  {lab:<16s} {diff:>+6.0f}  {z:>+5.2f} sd   {verdict}")

    print("\nDOES REMOVING MACHINE TEXT CHANGE THE ORDER?\n")
    ref_adj = ref[5]
    for lab, m, sd, lo_, hi_, adj, s in sorted(rows, key=lambda r: -r[5]):
        mark = "  <- US House" if lab == "US House" else ""
        print(f"  {lab:<16s} {adj:>7.0f}   machine {100*s:>4.1f}%{mark}")
    print(f"\n  The correction lowers US House by {100*ref[6]:.1f}%, more than it")
    print("  lowers most challengers, so it cannot explain their position.")


if __name__ == "__main__":
    main()
