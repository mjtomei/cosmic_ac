#!/usr/bin/env python3
"""When in the day does work happen? Quarter-hour profile of activity.

The time-of-day companion to worklog_chart.py. Where that answers "how many
hours on each date", this answers "at which times of day", by folding every
date onto a single 24-hour clock.

Adapted from ~/claude-work/project-manager/docs/velocity-analysis/scripts/
hour_histogram.py, which buckets commits by author-hour and sums net non-test
CODE LINES. Lines are the wrong unit here — this repo commits prose, analysis
scripts and data artifacts, so a code-extension filter would discard most of
what gets written. This version uses the activity metric worklog_chart.py
already defines, imported from it rather than reimplemented:

    commit windows (15 min before each commit)
  ∪ gaps under 30 min between consecutive HUMAN messages

The metric: the clock is cut into 15-minute slots (96 of them). For each
calendar day, every slot that contains any activity scores 1 — so a slot's
count is the NUMBER OF DAYS it was active, not how long. Counting days rather
than minutes keeps one marathon session from swamping the profile, which is
the whole point of asking about the shape of a day.

Kept from hour_histogram.py, because they are what make two windows
comparable:

  * flatness — normalized Shannon entropy over the slots, 100% = perfectly
    even across the clock. Its thesis: as autonomous work takes over, the day
    should FLATTEN, because agents write outside the human's focused hours.
    Run it over two --since/--until windows and compare.
  * busiest-4h share — the fraction of all activity inside the densest
    four-hour window, wrapping across midnight.

Usage:
    python3 tools/timeofday_chart.py
    python3 tools/timeofday_chart.py --since 2026-08-01
    python3 tools/timeofday_chart.py --since 2026-07-01 --until 2026-08-01
    python3 tools/timeofday_chart.py --bin 30 --include-agent
    python3 tools/timeofday_chart.py --csv tod.csv
"""
import argparse
import csv
import datetime
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worklog_chart as wl          # noqa: E402  (path set above)


def active_slots(merged, bin_min, since=None, until=None):
    """{slot_index: set of dates active in that slot}.

    A slot is scored once per day no matter how much of it was worked, so the
    profile answers "how often is this time of day in use".
    """
    per_slot = defaultdict(set)
    slots_per_day = 24 * 60 // bin_min
    step = datetime.timedelta(minutes=bin_min)
    for s, e in merged:
        # Walk slot by slot so intervals crossing midnight land on both dates.
        cur = s.replace(second=0, microsecond=0)
        cur -= datetime.timedelta(minutes=cur.minute % bin_min)
        while cur < e:
            d = cur.date()
            if (since is None or d >= since) and (until is None or d < until):
                idx = (cur.hour * 60 + cur.minute) // bin_min
                per_slot[idx % slots_per_day].add(d)
            cur += step
    return per_slot


def flatness(counts):
    """Normalized Shannon entropy: 1.0 = perfectly even across the clock."""
    total = sum(counts)
    if total <= 0:
        return 0.0
    ps = [c / total for c in counts if c > 0]
    if len(ps) <= 1:
        return 0.0
    h = -sum(p * math.log(p) for p in ps)
    return h / math.log(len(counts))


def busiest_window(counts, hours, bin_min):
    """(share, start_slot) for the densest contiguous window, wrapping midnight."""
    total = sum(counts)
    if not total:
        return 0.0, 0
    width = int(hours * 60 // bin_min)
    best, best_i = -1, 0
    n = len(counts)
    for i in range(n):
        s = sum(counts[(i + k) % n] for k in range(width))
        if s > best:
            best, best_i = s, i
    return best / total, best_i


def slot_label(idx, bin_min):
    mins = idx * bin_min
    return f"{mins // 60:02d}:{mins % 60:02d}"


def render(per_slot, bin_min, n_days, width=44):
    slots_per_day = 24 * 60 // bin_min
    counts = [len(per_slot.get(i, ())) for i in range(slots_per_day)]
    if not any(counts):
        return "No activity found."
    peak = max(counts)
    blocks = "▏▎▍▌▋▊▉█"
    lines = []
    for i, c in enumerate(counts):
        full = int(c / peak * width)
        frac = (c / peak * width) - full
        bar = "█" * full
        if frac > 0 and full < width:
            bar += blocks[min(len(blocks) - 1, int(frac * len(blocks)))]
        on_hour = (i * bin_min) % 60 == 0
        label = slot_label(i, bin_min)
        pct = (c / n_days * 100) if n_days else 0
        cell = f"{c:3d} d {pct:3.0f}%" if c else "      -  "
        lines.append(f"{label}{'│' if on_hour else '┊'}{bar:<{width}} {cell}")
    flat = flatness(counts)
    share, start = busiest_window(counts, 4, bin_min)
    end = (start + int(4 * 60 // bin_min)) % slots_per_day
    header = (
        f"Activity by time of day  ({bin_min}-min slots; a slot scores 1 per day it "
        f"sees any activity)\n"
        f"{n_days} active days · commit windows ∪ human-message gaps "
        f"<{wl.SESSION_GAP_MIN} min\n"
    )
    footer = (
        f"      └{'─' * (width + 1)}\n"
        f"       peak slot {peak} of {n_days} days"
        f"        flatness {flat * 100:.0f}%  (100% = even across the clock)\n"
        f"       busiest 4h {slot_label(start, bin_min)}–{slot_label(end, bin_min)}"
        f" holds {share * 100:.0f}% of all activity"
    )
    return header + "\n".join(lines) + "\n" + footer


def build(bin_min=15, since=None, until=None, human_only=True):
    per_session = wl.session_intervals_by_file(human_only=human_only)
    merged = wl.merge(wl.commit_intervals()
                      + [iv for ivals in per_session.values() for iv in ivals])
    per_slot = active_slots(merged, bin_min, since, until)
    days = set()
    for ds in per_slot.values():
        days |= ds
    return per_slot, len(days)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", type=int, default=15, metavar="MIN",
                    help="slot width in minutes; must divide 1440 (default 15)")
    ap.add_argument("--since", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD", help="ignore days before this date")
    ap.add_argument("--until", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD", help="ignore days on/after this date")
    ap.add_argument("--include-agent", action="store_true",
                    help="count all session messages, not just the human's")
    ap.add_argument("--csv", metavar="PATH", default=None,
                    help="write slot,start,days_active,share to PATH")
    ap.add_argument("--width", type=int, default=44, help="max bar width")
    args = ap.parse_args()

    if 1440 % args.bin or args.bin <= 0:
        ap.error(f"--bin {args.bin} does not divide 1440 evenly")

    per_slot, n_days = build(args.bin, args.since, args.until,
                             human_only=not args.include_agent)
    print(render(per_slot, args.bin, n_days, args.width))

    if args.csv:
        slots = 24 * 60 // args.bin
        counts = [len(per_slot.get(i, ())) for i in range(slots)]
        total = sum(counts) or 1
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["slot", "start", "days_active", "share_of_activity"])
            for i, c in enumerate(counts):
                w.writerow([i, slot_label(i, args.bin), c, f"{c / total:.5f}"])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
