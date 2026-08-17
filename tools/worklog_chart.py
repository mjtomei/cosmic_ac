#!/usr/bin/env python3
"""Live work-time visualization for this repo.

Ported from ~/coherence/worklog_chart.py (2026-08-16). Same two signals and the
same union-of-intervals accounting; the changes are the ones this repo forces —
see "Differences from the coherence original" below.

Combines two signals on one merged timeline and prints an ASCII bar chart of
hours worked per day:

  1. Commit windows   -- 15 minutes before each git commit.
  2. Human messages   -- gaps < 30 min between consecutive messages a PERSON
                         sent (from ~/.claude/projects/<slug>/*.jsonl).

Overlapping intervals are unioned, so shared minutes are never double-counted.

Differences from the coherence original:

  * Only human messages count. The original used every session message, which
    on this repo cannot tell a person working from a workflow running
    unattended: it scored one continuous 12-hour "working" run (Aug 13,
    11:04-23:03) that was agents emitting messages overnight. Filtering to
    human turns breaks that day into seven runs of 3.5h, 2.3h, 1.1h and
    smaller — a long day rather than an impossible one, and ~30% lower totals
    overall. --include-agent restores the original behaviour for comparison.
  * The project slug is derived from the repo path instead of hardcoded, so a
    rename or a fresh clone does not silently produce an empty chart. (The
    same rename hazard CLAUDE.md notes for the reading/ symlinks.)
  * Sessions started from a subdirectory land in their own project directory,
    so those are swept too.
  * This repo is worked by several concurrent Claude sessions, so the chart
    tags each day with the number active and reports the concurrency factor.
  * --since, because this repo's history is months long rather than days.
  * --csv, per the analysis/README.md convention that a novel number ships
    with a reproducible artifact.

What it still cannot see: work with no commit and no message — reading,
thinking, and anything done outside Claude Code. Totals are a floor for that
reason and a ceiling for the unattended-agent reason; treat them as an index,
not a timesheet.

Usage:
    python3 tools/worklog_chart.py                  # render once
    python3 tools/worklog_chart.py --interval 60    # redraw every 60s
    python3 tools/worklog_chart.py --since 2026-08-01
    python3 tools/worklog_chart.py --per-session
    python3 tools/worklog_chart.py --include-agent  # count agent activity too
    python3 tools/worklog_chart.py --csv worklog.csv
"""
import argparse
import csv
import datetime
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

# --- tunables ---------------------------------------------------------------
PRE_COMMIT_MIN = 15          # minutes of work assumed before each commit
SESSION_GAP_MIN = 30         # max gap between messages still counted as active
UNATTENDED_RUN_H = 6         # a single run longer than this is flagged as
                             # probably-unattended agent activity, not desk time

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Claude Code names a project directory after its absolute path with BOTH the
# separators and the underscores replaced by dashes: /home/matt/performance_commons
# becomes -home-matt-performance-commons. Missing the underscore rule silently
# yields an empty glob and a chart built from commit windows alone.
PROJECT_SLUG = os.path.abspath(REPO_DIR).replace(os.sep, "-").replace("_", "-")
PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
# A session started from a subdirectory (analysis/s10, reading/, …) gets its own
# project directory named for that path. It is still work on this repo, so sweep
# the repo slug and everything beneath it.
SESSION_GLOBS = [
    os.path.join(PROJECTS_DIR, PROJECT_SLUG, "*.jsonl"),
    os.path.join(PROJECTS_DIR, PROJECT_SLUG + "-*", "*.jsonl"),
]
SESSION_GLOB = " , ".join(SESSION_GLOBS)   # for the not-found message only
TZ = datetime.datetime.now().astimezone().tzinfo


def commit_intervals():
    """[t - PRE_COMMIT_MIN, t] for every commit reachable from any ref.

    --all sweeps the backup branches too. Their commits are pre-rewrite copies
    carrying the same author dates as the rewritten ones on master, so they
    land on identical intervals and the union collapses them — no double count.
    """
    try:
        out = subprocess.check_output(
            ["git", "-C", REPO_DIR, "log", "--all",
             "--pretty=format:%ad", "--date=format:%Y-%m-%dT%H:%M:%S"],
            stderr=subprocess.DEVNULL,
        ).decode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    ivals = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            t = datetime.datetime.fromisoformat(line).replace(tzinfo=TZ)
        except ValueError:
            continue
        ivals.append((t - datetime.timedelta(minutes=PRE_COMMIT_MIN), t))
    return ivals


def _entry_text(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


# Prefixes that mark an entry the harness injected into the user turn rather
# than something a person typed. Matched at the START only: a genuine message
# often has a <system-reminder> appended after the human's own words, and
# testing with "in" would throw those away.
_INJECTED_PREFIXES = (
    "<system-reminder>",
    "[SYSTEM NOTIFICATION",
    "<task-notification>",
    "<local-command-stdout>",
    "<local-command-caveat>",
    "Caveat:",
)


def is_human_message(entry):
    """True only for a message a person actually sent.

    Most `type: user` entries are not human: in one session here 3,920 of 4,636
    were tool results. The rest split into harness injections (system reminders,
    task notifications, compact summaries, command output) and 438 real ones.
    Slash commands count — the person typed them; their stdout does not.
    """
    if entry.get("type") != "user":
        return False
    if entry.get("toolUseResult") is not None:   # tool result wearing a user hat
        return False
    if entry.get("isMeta") or entry.get("isSidechain") or entry.get("isCompactSummary"):
        return False
    text = _entry_text(entry).strip()
    if not text:
        return False
    return not text.startswith(_INJECTED_PREFIXES)


def session_intervals_by_file(human_only=True):
    """{session_id: [(start, end), ...]} for gaps <= SESSION_GAP_MIN.

    Kept per file rather than pooled: with concurrent sessions, pooling first
    would stitch a gap in one session shut using another session's messages
    and report activity that session never had.

    human_only restricts the timeline to messages a person sent. Counting every
    message conflates a person working with a workflow running unattended — on
    this repo that produced a single unbroken 12-hour "working" run.
    """
    gap = datetime.timedelta(minutes=SESSION_GAP_MIN)
    per_session = {}
    files = sorted({f for g in SESSION_GLOBS for f in glob.glob(g)})
    for f in files:
        ts = []
        with open(f, errors="replace") as fh:
            for raw in fh:
                try:
                    entry = json.loads(raw)
                except ValueError:
                    continue
                if not isinstance(entry, dict):
                    continue
                if human_only and not is_human_message(entry):
                    continue
                stamp = entry.get("timestamp")
                if not stamp:
                    continue
                try:
                    ts.append(
                        datetime.datetime.fromisoformat(
                            stamp.replace("Z", "+00:00")
                        ).astimezone(TZ)
                    )
                except ValueError:
                    continue
        ts.sort()
        ivals = [(a, b) for a, b in zip(ts, ts[1:]) if b - a <= gap]
        if ivals:
            per_session[os.path.basename(f)[:-6]] = ivals
    return per_session


def merge(ivals):
    """Union overlapping intervals."""
    ivals = sorted(ivals)
    merged = []
    for s, e in ivals:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def hours_per_day(merged):
    """Sum interval hours by calendar day, splitting across midnight."""
    day = defaultdict(float)
    for s, e in merged:
        cur = s
        while cur.date() < e.date():
            nxt = datetime.datetime.combine(
                cur.date() + datetime.timedelta(days=1),
                datetime.time(0), tzinfo=TZ,
            )
            day[cur.date()] += (nxt - cur).total_seconds() / 3600
            cur = nxt
        day[cur.date()] += (e - cur).total_seconds() / 3600
    return day


def sessions_per_day(per_session):
    """{date: number of distinct sessions with activity that day}."""
    day = defaultdict(set)
    for sid, ivals in per_session.items():
        for s, e in ivals:
            d = s.date()
            while d <= e.date():
                day[d].add(sid)
                d += datetime.timedelta(days=1)
    return {d: len(v) for d, v in day.items()}


def clip(day, since):
    return {d: h for d, h in day.items() if d >= since} if since else day


def render(day, nsess, gross, solo=0.0, longest=None, width=40):
    if not day:
        return ("No commits or session logs found.\n"
                f"Looked for sessions in: {SESSION_GLOB}")
    start, end = min(day), max(day)
    peak = max(day.values()) or 1.0
    per_block = peak / width
    lines = []
    d = start
    blocks = "▏▎▍▌▋▊▉█"
    while d <= end:
        h = day.get(d, 0.0)
        full = int(h / per_block)
        frac = (h / per_block) - full
        bar = "█" * full
        if frac > 0 and full < width:
            bar += blocks[min(len(blocks) - 1, int(frac * len(blocks)))]
        label = f"{h:.2f} h" if h else "0   h"
        n = nsess.get(d, 0)
        tag = f"  ×{n}" if n > 1 else ""
        lines.append(f"{d:%b %d} │{bar:<{width}} {label}{tag}")
        d += datetime.timedelta(days=1)
    total = sum(day.values())
    now = datetime.datetime.now(TZ)
    header = (
        f"Work time per day  (commit windows ∪ session gaps <{SESSION_GAP_MIN} min)\n"
        f"updated {now:%Y-%m-%d %H:%M:%S}\n"
    )
    footer = [
        f"        └{'─' * (width + 1)}",
        f"         full block ≈ {per_block:.3f} h        TOTAL ≈ {total:.2f} h",
    ]
    if gross and solo:
        footer.append(
            f"         session time {solo:.2f} h wall-clock, {gross:.2f} h summed "
            f"across sessions ({gross / solo:.1f}× concurrency; ×N = sessions that day)"
        )
    if longest and longest[0] >= UNATTENDED_RUN_H:
        h, s, e = longest
        footer.append(
            f"         ⚠ longest unbroken run {h:.1f} h "
            f"({s:%b %d %H:%M}–{e:%H:%M}). A run this long is a workflow "
            f"emitting messages,\n           not time at the keyboard — "
            f"'active' counts agent activity too. Read totals as an upper bound."
        )
    return header + "\n".join(lines) + "\n" + "\n".join(footer)


def build(since=None, want_gross=True, human_only=True):
    per_session = session_intervals_by_file(human_only=human_only)
    merged = merge(commit_intervals()
                   + [iv for ivals in per_session.values() for iv in ivals])
    day = clip(hours_per_day(merged), since)
    nsess = sessions_per_day(per_session)
    # Concurrency compares like with like: the per-session sum against the union
    # of the SAME session intervals. Comparing it to `day` would fold in the
    # commit windows, which belong to no session, and can push the ratio below
    # 1.0 — reading as "less than no concurrency", which is nonsense.
    gross = solo = 0.0
    if want_gross:
        for ivals in per_session.values():
            gross += sum(clip(hours_per_day(merge(ivals)), since).values())
        solo = sum(clip(hours_per_day(merge(
            [iv for ivals in per_session.values() for iv in ivals])), since).values())
    scope = [(s, e) for s, e in merged if since is None or e.date() >= since]
    longest = max((((e - s).total_seconds() / 3600, s, e) for s, e in scope),
                  default=None)
    return render(day, nsess, gross, solo, longest), day, nsess, per_session


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--interval", "-i", type=float, default=0,
                    help="seconds between redraws; 0 = render once and exit")
    ap.add_argument("--since", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD", help="ignore days before this date")
    ap.add_argument("--per-session", action="store_true",
                    help="also list each session's own active hours")
    ap.add_argument("--include-agent", action="store_true",
                    help="count every session message, not just the human's "
                         "(the original coherence behaviour; inflates totals "
                         "with unattended workflow activity)")
    ap.add_argument("--csv", metavar="PATH", default=None,
                    help="write date,hours,sessions_active to PATH")
    args = ap.parse_args()

    if args.interval <= 0:
        chart, day, nsess, per_session = build(
            args.since, human_only=not args.include_agent)
        print(chart)
        if args.per_session:
            print("\nPer-session active hours (sums above the union — they overlap):")
            rows = []
            for sid, ivals in per_session.items():
                h = sum(clip(hours_per_day(merge(ivals)), args.since).values())
                if h:
                    rows.append((h, sid))
            for h, sid in sorted(rows, reverse=True):
                print(f"  {h:8.2f} h  {sid}")
        if args.csv:
            with open(args.csv, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["date", "hours", "sessions_active"])
                for d in sorted(day):
                    w.writerow([d.isoformat(), f"{day[d]:.4f}", nsess.get(d, 0)])
            print(f"\nwrote {args.csv}")
        return

    import time
    try:
        while True:
            sys.stdout.write("\033[2J\033[H")
            print(build(args.since,
                        human_only=not args.include_agent)[0])
            print(f"\n(refresh every {args.interval:g}s — Ctrl-C to stop)")
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
