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
import statistics
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


FOREIGN_REF_MIN = 5          # references to the repo before a session started
                             # elsewhere counts as work on this repo

# Rulings on sessions filed under another project directory. The automatic test
# cannot separate working on this repo from mentioning it — the genuine 07-03
# session never opened a file here (it drove tmux) while the coherence session
# that only discussed the paper did — so the calls are recorded by hand and the
# undecided ones are reported rather than guessed at.
FOREIGN_RULINGS = {
    # session-id prefix: (counts?, why)
    "dc16072e": (True,  "2026-07-03 from ~: set up this project's tmux panes"),
    "45e78f09": (False, "coherence's own work; only mentions this paper "
                        "(Matthew, 2026-08-17)"),
}


def foreign_session_files():
    """Session files in OTHER project directories that worked on this repo.

    Claude Code files a session under the directory it was launched from, so
    work on this repo done from ~ or from a sibling checkout lands elsewhere
    and a glob of this project's directory alone silently misses it. That is
    not hypothetical: a 2026-07-03 session run from /home/matt referenced this
    repo 22 times while setting up the tmux panes, and its whole week charted
    as zero.

    Attribution is therefore by what a session TOUCHED, not where it ran.
    grep does the prefilter because it scans 1.5GB in ~0.05s where parsing
    every file in Python would not be worth the wait; a session must mention
    the repo path at least FOREIGN_REF_MIN times, so that merely discussing
    the project does not count as working on it.
    """
    try:
        out = subprocess.run(
            ["grep", "-rlF", "--include=*.jsonl", REPO_DIR, PROJECTS_DIR],
            capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    own = os.path.join(PROJECTS_DIR, PROJECT_SLUG) + os.sep
    found = {}
    for path in out.splitlines():
        if not path or path.startswith(own) or "/subagents/" in path:
            continue
        try:
            n = subprocess.run(["grep", "-cF", REPO_DIR, path],
                               capture_output=True, text=True).stdout.strip()
            if int(n or 0) >= FOREIGN_REF_MIN:
                found[path] = int(n)
        except (OSError, subprocess.SubprocessError, ValueError):
            continue
    return found


def session_intervals_by_file(human_only=True, include_foreign=False):
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
    files = {f for g in SESSION_GLOBS for f in glob.glob(g)}
    for path in foreign_session_files():
        counts, _ = FOREIGN_RULINGS.get(os.path.basename(path)[:8],
                                        (include_foreign, ""))
        if counts:
            files.add(path)
    files = sorted(files)
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


def render_weekly(day, nsess, width=40):
    """Same hours, bucketed by ISO week — the shape over a project, not a day.

    Weeks are labelled by their Monday. A partial first or last week is shown
    as-is and marked, rather than dropped or scaled up: this repo's history
    starts and ends mid-week, and a silently rescaled bar would read as a real
    difference in effort.
    """
    if not day:
        return "No commits or session logs found."
    weeks = defaultdict(float)
    active = defaultdict(int)
    for d, h in day.items():
        monday = d - datetime.timedelta(days=d.weekday())
        weeks[monday] += h
        if h:
            active[monday] += 1
    first, last = min(day), max(day)
    # Walk every week in range, not just the ones with data: skipping empty
    # weeks would print Jun 22 next to Jul 13 and read as continuous work.
    wk = first - datetime.timedelta(days=first.weekday())
    end = last - datetime.timedelta(days=last.weekday())
    while wk <= end:
        weeks.setdefault(wk, 0.0)
        wk += datetime.timedelta(days=7)
    peak = max(weeks.values()) or 1.0
    per_block = peak / width
    blocks = "▏▎▍▌▋▊▉█"
    lines = []
    for monday in sorted(weeks):
        h = weeks[monday]
        full = int(h / per_block)
        frac = (h / per_block) - full
        bar = "█" * full
        if frac > 0 and full < width:
            bar += blocks[min(len(blocks) - 1, int(frac * len(blocks)))]
        sunday = monday + datetime.timedelta(days=6)
        # A week is partial when the data starts or ends inside it.
        partial = "*" if (monday < first <= sunday) or (monday <= last < sunday) else ""
        n = active[monday]
        lines.append(f"{monday:%b %d}{partial:1}│{bar:<{width}} "
                     f"{h:6.2f} h  {n} d  {h / n if n else 0:4.1f} h/d")
    total = sum(weeks.values())
    header = (
        f"Work time per week  (commit windows ∪ human-message gaps "
        f"<{SESSION_GAP_MIN} min)\n"
        f"{first:%Y-%m-%d} → {last:%Y-%m-%d} · weeks labelled by Monday · "
        f"* = partial week\n"
    )
    footer = (
        f"        └{'─' * (width + 1)}\n"
        f"         full block ≈ {per_block:.3f} h        TOTAL ≈ {total:.2f} h "
        f"over {len(weeks)} weeks ({total / len(weeks):.1f} h/week)"
    )
    return header + "\n".join(lines) + "\n" + footer


def summary_stats(day, windows=(7, 30, None)):
    """Mean and SD of hours/day over trailing windows.

    Two means, because they answer different questions and diverge a lot here:
    per CALENDAR day in the window (zero days included — the honest "how much
    per day did this project get") and per ACTIVE day (how heavy a working day
    is when there is one). Quoting only the first makes a focused worker look
    idle; only the second hides how many days were skipped.

    SD is the sample SD over calendar days, so it reflects the on/off pattern
    rather than only the variation among working days.
    """
    if not day:
        return ""
    today = datetime.datetime.now(TZ).date()
    first = min(day)
    rows = []
    for w in windows:
        start = first if w is None else today - datetime.timedelta(days=w - 1)
        start = max(start, first)
        n_days = (today - start).days + 1
        vals = [day.get(start + datetime.timedelta(days=i), 0.0)
                for i in range(n_days)]
        if not vals:
            continue
        act = [v for v in vals if v > 0]
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        rows.append((
            "all" if w is None else f"last {w}",
            n_days, len(act), mean, sd,
            statistics.fmean(act) if act else 0.0,
        ))
    if not rows:
        return ""
    out = ["", "         window     days  active   mean h/d      SD   mean h/active-d",
           "         " + "-" * 62]
    for name, n, a, mean, sd, amean in rows:
        out.append(f"         {name:<10} {n:5d}  {a:6d}   {mean:8.2f}  {sd:6.2f}"
                   f"   {amean:13.2f}")
    out.append("         mean and SD are per calendar day, zero days included")
    return "\n".join(out)


def build(since=None, want_gross=True, human_only=True, include_foreign=False):
    per_session = session_intervals_by_file(human_only=human_only,
                                           include_foreign=include_foreign)
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
    ap.add_argument("--include-foreign", action="store_true",
                    help="count sessions launched from another directory that "
                         "reference this repo. Off by default: the test cannot "
                         "reliably tell working on this repo from mentioning "
                         "it, so candidates are listed and you decide")
    ap.add_argument("--weekly", action="store_true",
                    help="bucket by ISO week instead of by day")
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
            args.since, human_only=not args.include_agent,
            include_foreign=args.include_foreign)
        cand = foreign_session_files()
        if cand:
            print(f"note: {len(cand)} session(s) outside this repo's project "
                  f"directory reference it:")
            for path, n in sorted(cand.items()):
                sid = os.path.basename(path)[:8]
                ruled = FOREIGN_RULINGS.get(sid)
                if ruled is None:
                    mark = "counted" if args.include_foreign else "not counted"
                    why = "undecided; --include-foreign to add"
                else:
                    mark = "counted" if ruled[0] else "not counted"
                    why = ruled[1]
                print(f"  {sid}  {os.path.basename(os.path.dirname(path)):30} "
                      f"{n:3d} refs  [{mark}] {why}")
            print()
        print(render_weekly(day, nsess) if args.weekly else chart)
        print(summary_stats(day))
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
