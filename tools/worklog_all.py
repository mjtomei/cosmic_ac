#!/usr/bin/env python3
"""Machine-wide work time: every Claude Code session, every project.

The sibling of worklog_chart.py / timeofday_chart.py, which look at THIS repo.
This one sweeps ~/.claude/projects entirely and adds a per-project breakdown,
so you can see where the time actually went rather than only how much this
paper got.

Same metric as the single-repo tools, imported from them rather than
reimplemented so the numbers stay comparable:

    commit windows (15 min before each commit, per repo)
  ∪ gaps under 30 min between consecutive HUMAN messages

"Human" matters more here than in the single-repo view: across 2,782 session
files only ~200k lines are candidate human turns, the rest being tool results
and harness injections. Counting all messages would mostly measure how long
agents ran unattended.

Two totals, because they answer different questions:
  * WALL-CLOCK is the union across every project — time with at least one
    session live. This is the honest "how much of the day went to Claude Code".
  * PER-PROJECT hours sum higher, because concurrent work on several projects
    double-counts the same minutes. The ratio is the concurrency factor, and
    on a machine that runs several panes at once it is the interesting number.

Project attribution comes from each session's recorded `cwd`, not from the
directory name: Claude Code's slug replaces both separators and underscores
with dashes, so the name alone cannot be decoded back to a path
(-home-matt-performance-commons could be .../performance_commons or
.../performance-commons).

Usage:
    python3 tools/worklog_all.py                    # breakdown + daily chart
    python3 tools/worklog_all.py --weekly
    python3 tools/worklog_all.py --tod              # time-of-day profile
    python3 tools/worklog_all.py --since 2026-08-01 --top 15
    python3 tools/worklog_all.py --project performance   # filter by substring
    python3 tools/worklog_all.py --csv by-project.csv
"""
import argparse
import csv
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worklog_chart as wl              # noqa: E402
import timeofday_chart as tod           # noqa: E402

# /tmp/claude-<uid>/<slug>/<session-uuid>[/scratchpad] — strip back to the slug
TMP_SESSION_RE = re.compile(r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                            r"[0-9a-f]{4}-[0-9a-f]{12}$")

PROJECTS_DIR = wl.PROJECTS_DIR
TZ = wl.TZ


def scan_projects(human_only=True):
    """{project_path: {session_id: [(start, end), ...]}} across the machine.

    Line-level prefilter before json.loads: a human turn always contains
    '"type":"user"' and never a tool result, and the lines that fail that test
    are the huge ones (assistant turns, tool output). Skipping them takes a
    full sweep of ~1.5GB from minutes to about a second and a half.
    """
    gap = datetime.timedelta(minutes=wl.SESSION_GAP_MIN)
    per_project = defaultdict(dict)
    for path in glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl")):
        if "/subagents/" in path:
            continue
        cwd = None
        ts = []
        try:
            fh = open(path, errors="replace")
        except OSError:
            continue
        with fh:
            for raw in fh:
                if cwd is None and '"cwd"' in raw:
                    try:
                        cwd = json.loads(raw).get("cwd")
                    except ValueError:
                        pass
                if human_only:
                    if '"type":"user"' not in raw or '"toolUseResult"' in raw:
                        continue
                try:
                    entry = json.loads(raw)
                except ValueError:
                    continue
                if not isinstance(entry, dict):
                    continue
                if human_only and not wl.is_human_message(entry):
                    continue
                stamp = entry.get("timestamp")
                if not stamp:
                    continue
                try:
                    ts.append(datetime.datetime.fromisoformat(
                        stamp.replace("Z", "+00:00")).astimezone(TZ))
                except ValueError:
                    continue
        if not ts:
            continue
        ts.sort()
        ivals = [(a, b) for a, b in zip(ts, ts[1:]) if b - a <= gap]
        if not ivals:
            continue
        proj = cwd or os.path.basename(os.path.dirname(path))
        # A session that cd'd into its own scratchpad still belongs to the
        # project it was launched for; otherwise one temp dir per session
        # shows up as a separate "project" with minutes on it.
        for marker in ("/scratchpad", "/.claude/projects"):
            if marker in proj:
                proj = proj.split(marker)[0]
        proj = TMP_SESSION_RE.sub("", proj) or proj
        per_project[proj][os.path.basename(path)[:-6]] = ivals
    return per_project


def fold_tmp_scratchpads(per_project):
    """Merge /tmp/claude-<uid>/<slug>/... keys into the project they belong to.

    A session that cd's into its scratchpad records a /tmp cwd whose last
    component is the project SLUG. The slug is lossy (both / and _ became -),
    so it cannot be decoded back to a path — but it can be matched against the
    slugs of the real project paths already seen, which is exact.
    """
    real = {}
    for proj in per_project:
        if not proj.startswith("/tmp/"):
            real[os.path.abspath(proj).replace(os.sep, "-").replace("_", "-")] = proj
    for proj in list(per_project):
        if not proj.startswith("/tmp/"):
            continue
        target = real.get(os.path.basename(proj.rstrip(os.sep)))
        if not target:
            continue
        for sid, ivals in per_project.pop(proj).items():
            per_project[target].setdefault(sid, []).extend(ivals)
    return per_project


def repo_key(path):
    """Identity of the underlying repository, shared across worktrees.

    Keyed on the ROOT COMMIT, not on git-common-dir: the ~/.pm/workdirs
    checkouts are independent CLONES, so they each have their own git dir but
    the same history. Common-dir separates worktrees; only the root commit
    also catches clones, which is what actually inflated this report.
    """
    try:
        out = subprocess.run(["git", "-C", path, "rev-list", "--max-parents=0",
                              "--all"], capture_output=True, text=True, timeout=20)
        if out.returncode or not out.stdout.strip():
            return None
        return " ".join(sorted(out.stdout.split()))
    except (OSError, subprocess.SubprocessError):
        return None


def add_commit_windows(per_project, enabled=True):
    """Fold each project's git history in, once per REPOSITORY.

    The pm test worktrees are dozens of checkouts of one repo. Attributing
    `git log --all` to each of them charged the same history dozens of times:
    fourteen "projects" each showed ~300h starting the same day, and
    cross-project concurrency read 8.8x. Commits now land on the first
    checkout seen for a repo, and the rest get sessions only.
    """
    if not enabled:
        return {}
    added = {}
    seen_repos = {}
    for proj in sorted(per_project, key=len):     # prefer the shortest path
        if not os.path.isdir(os.path.join(proj, ".git")) and not os.path.isfile(
                os.path.join(proj, ".git")):
            continue
        key = repo_key(proj)
        if key is None or key in seen_repos:
            continue
        seen_repos[key] = proj
        ivals = wl.commit_intervals(proj)
        if ivals:
            per_project[proj]["<git commits>"] = ivals
            added[proj] = len(ivals)
    return added


def project_rows(per_project, since=None, until=None):
    rows = []
    for proj, sessions in per_project.items():
        def clipped(ivs):
            d = wl.hours_per_day(wl.merge(ivs))
            return {k: v for k, v in d.items()
                    if (since is None or k >= since)
                    and (until is None or k < until)}

        ivals = [iv for s in sessions.values() for iv in s]
        day = clipped(ivals)
        hours = sum(day.values())
        if hours <= 0:
            continue
        # Split the total, because for agent-driven repos it is almost all
        # commit windows: project-manager commits thousands of times
        # autonomously, and 15 min charged per commit dwarfs the hours anyone
        # spent typing at it. Without the split that reads as human effort.
        sess_h = sum(clipped([iv for sid, s in sessions.items()
                              if sid != "<git commits>" for iv in s]).values())
        rows.append({
            "project": proj,
            "sessions": len([k for k in sessions if k != "<git commits>"]),
            "days": len([h for h in day.values() if h > 0]),
            "hours": hours,
            "sess_hours": sess_h,
            "first": min(day), "last": max(day),
            "day": day,
        })
    rows.sort(key=lambda r: -r["hours"])
    return rows


def shorten(p, width=44):
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    return p if len(p) <= width else "…" + p[-(width - 1):]


def render_breakdown(rows, wall, per_session_sum=0.0, session_union=0.0,
                     top=None, width=22):
    if not rows:
        return "No activity found."
    gross = sum(r["hours"] for r in rows)
    peak = rows[0]["hours"]
    shown = rows if not top else rows[:top]
    lines = [
        f"Work time by project — {len(rows)} projects, "
        f"{sum(r['sessions'] for r in rows)} sessions",
        f"{'project':<46} {'hours':>7} {'human':>7} {'share':>6} {'days':>5} "
        f"{'sess':>5}  {'span':<21}",
        "-" * 108,
    ]
    for r in shown:
        bar = "█" * max(1, int(r["hours"] / peak * width))
        lines.append(
            f"{shorten(r['project']):<46} {r['hours']:7.2f} "
            f"{r['sess_hours']:7.2f} {r['hours'] / gross * 100:5.1f}% "
            f"{r['days']:5d} {r['sessions']:5d}  "
            f"{r['first']:%b %d}–{r['last']:%b %d}  {bar}")
    if top and len(rows) > top:
        rest = rows[top:]
        lines.append(f"{f'… {len(rest)} more projects':<46} "
                     f"{sum(r['hours'] for r in rest):7.2f} "
                     f"{sum(r['sess_hours'] for r in rest):7.2f} "
                     f"{sum(r['hours'] for r in rest) / gross * 100:5.1f}% "
                     f"{'':5} {sum(r['sessions'] for r in rest):5d}")
    lines += [
        "-" * 108,
        f"{'WALL-CLOCK (union, concurrent work counted once)':<46} {wall:7.2f}",
        f"{'summed per project':<46} {gross:7.2f} "
        f"{'':6} → {gross / wall if wall else 0:.2f}× cross-project concurrency",
    ]
    if per_session_sum and session_union:
        lines.append(
            f"{'sessions: union / summed':<46} {session_union:7.2f} /"
            f"{per_session_sum:7.2f} → {per_session_sum / session_union:.2f}× "
            f"pane concurrency")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD")
    ap.add_argument("--until", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD")
    ap.add_argument("--top", type=int, default=20,
                    help="show this many projects, roll up the rest (0 = all)")
    ap.add_argument("--project", metavar="SUBSTR", default=None,
                    help="only projects whose path contains SUBSTR")
    ap.add_argument("--weekly", action="store_true", help="weekly chart")
    ap.add_argument("--tod", action="store_true", help="time-of-day profile")
    ap.add_argument("--bin", type=int, default=15, metavar="MIN",
                    help="slot width for --tod (default 15)")
    ap.add_argument("--no-commits", action="store_true",
                    help="human messages only; skip the git commit windows")
    ap.add_argument("--include-agent", action="store_true",
                    help="count every session message, not just human turns")
    ap.add_argument("--include-today", action="store_true",
                    help="include today in the mean/SD windows")
    ap.add_argument("--csv", metavar="PATH", default=None,
                    help="write the per-project breakdown to PATH")
    args = ap.parse_args()

    per_project = fold_tmp_scratchpads(scan_projects(
        human_only=not args.include_agent))
    add_commit_windows(per_project, enabled=not args.no_commits)
    if args.project:
        per_project = {k: v for k, v in per_project.items()
                       if args.project in k}
        if not per_project:
            print(f"no project path contains {args.project!r}")
            return

    rows = project_rows(per_project, args.since, args.until)
    if not rows:
        print("No activity in range.")
        return

    # Wall-clock union across every project: concurrent panes counted once.
    all_ivals = [iv for sessions in per_project.values()
                 for s in sessions.values() for iv in s]
    merged = wl.merge(all_ivals)
    day = wl.hours_per_day(merged)
    day = {d: h for d, h in day.items()
           if (args.since is None or d >= args.since)
           and (args.until is None or d < args.until)}
    wall = sum(day.values())

    sess_ivals = []
    sess_sum = 0.0
    for sessions in per_project.values():
        for sid, ivals in sessions.items():
            if sid == "<git commits>":
                continue
            sess_ivals.extend(ivals)
            d = wl.hours_per_day(wl.merge(ivals))
            sess_sum += sum(h for dt, h in d.items()
                            if (args.since is None or dt >= args.since)
                            and (args.until is None or dt < args.until))
    # Union of sessions ONLY. Comparing the per-session sum against `wall`
    # would fold in the commit windows, which belong to no session, and can
    # drive the ratio under 1.0 — "less than no concurrency", which is absurd.
    sd = wl.hours_per_day(wl.merge(sess_ivals))
    sess_union = sum(h for dt, h in sd.items()
                     if (args.since is None or dt >= args.since)
                     and (args.until is None or dt < args.until))
    print(render_breakdown(rows, wall, sess_sum, sess_union,
                           top=args.top or None))
    print()

    if args.tod:
        per_slot = tod.active_slots(merged, args.bin, args.since, args.until)
        days = set()
        for ds in per_slot.values():
            days |= ds
        print(tod.render(per_slot, args.bin, len(days)))
    else:
        # ×N must mean what wl.render's legend says it means — sessions
        # active that day, not projects — or the marker silently changes
        # meaning between the single-repo and machine-wide reports.
        nsess = defaultdict(set)
        for sessions in per_project.values():
            for sid, ivals in sessions.items():
                if sid == "<git commits>":
                    continue
                for st, en in ivals:
                    d = st.date()
                    while d <= en.date():
                        nsess[d].add(sid)
                        d += datetime.timedelta(days=1)
        nsess = {d: len(v) for d, v in nsess.items()}
        if args.weekly:
            print(wl.render_weekly(day, nsess))
        else:
            print(wl.render(day, nsess, 0.0, 0.0, None))
    print(wl.summary_stats(day, include_today=args.include_today))

    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["project", "hours", "share_pct", "active_days",
                        "sessions", "first_day", "last_day",
                        "human_session_hours"])
            gross = sum(r["hours"] for r in rows)
            for r in rows:
                w.writerow([r["project"], f"{r['hours']:.4f}",
                            f"{r['hours'] / gross * 100:.2f}", r["days"],
                            r["sessions"], r["first"], r["last"],
                            f"{r['sess_hours']:.4f}"])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
