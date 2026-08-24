#!/usr/bin/env python3
"""Work-time report across every agent session on this machine.

One tool, one metric. Supersedes worklog_chart.py, timeofday_chart.py and
worklog_all.py, which were three files sharing a metric by import; this is the
same metric written once. (The line-count view lives elsewhere and is not
replaced: velocity-analysis/scripts/hour_histogram.py counts code lines, which
is a different measurement.)

THE METRIC
    commit windows (15 min before each commit, per repository, all refs)
  ∪ gaps under 30 min between consecutive HUMAN messages
Overlapping intervals are unioned, so a minute is never counted twice.

Both halves exclude work no person drove. On the message side that means
harness turns; on the commit side it means the commits pm makes on its own,
which are 1,709 of 3,143 in project-manager and would otherwise show as
effort. Neither filter touches human-directed, Claude-assisted work: this repo
and coherence have zero agent-generated commits by that test.

WHAT COUNTS AS HUMAN TIME (Matthew, 2026-08-23)
Everything left after those two filters. A commit without pm markers is human
work even when Claude wrote the diff and no transcript survives: the pre-April
commits were not hand-written, they were Claude-assisted sessions whose
transcripts were deleted before retention was raised (79% of February and 87%
of March project-manager commits carry a Claude co-author trailer, while no
transcript on this machine starts before April).

So the headline "hours" IS the human-time estimate. The second column is not a
human/non-human split — it reports how much of those hours the surviving
TRANSCRIPTS still account for, which is a data-coverage measure. It reads 0%
before April 2026 because the transcripts are gone, not because nobody worked.

The one real contamination left is on the message side: pm's harness prompts
still register as human turns, so session-derived hours for pm-driven projects
are an upper bound until a classifier separates them.

Only human turns count. Counting every message cannot tell a person working
from a workflow running unattended: on this machine that produced a single
unbroken 12-hour "working" run that was agents emitting messages overnight.

SOURCES
  * Claude Code  ~/.claude/projects/<slug>/*.jsonl
  * OMP          ~/.omp/agent/sessions/<slug>/*.jsonl
Both are JSONL with timestamps and a recorded cwd, but they mark a human turn
differently, so each gets its own reader (see is_human_*). Attribution uses the
recorded cwd, never the directory slug: Claude Code's slug replaces both "/"
and "_" with "-" and cannot be decoded back to a path, and the two tools slug
the same project differently (-home-matt-performance-commons vs
-performance_commons).

VIEWS
  per-project breakdown (always), then one of: daily chart, --weekly, --tod;
  then mean/SD over trailing windows.

Usage:
    python3 tools/worklog.py                      # everything, daily
    python3 tools/worklog.py --project performance_commons
    python3 tools/worklog.py --weekly --since 2026-07-01
    python3 tools/worklog.py --tod --bin 60
    python3 tools/worklog.py --include-pm         # add pm branch workdirs
    python3 tools/worklog.py --source omp
    python3 tools/worklog.py --all-time          # lifetime per-project table
    python3 tools/worklog.py --csv by-project.csv
"""
import argparse
import csv
import datetime
import glob
import json
import math
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict

# --- tunables ---------------------------------------------------------------
PRE_COMMIT_MIN = 15      # minutes of work assumed before each commit
SESSION_GAP_MIN = 30     # max gap between human messages still counted active
UNATTENDED_RUN_H = 6     # a single run longer than this is flagged as suspect

CLAUDE_GLOB = os.path.expanduser("~/.claude/projects/*/*.jsonl")
OMP_GLOB = os.path.expanduser("~/.omp/agent/sessions/*/*.jsonl")
TZ = datetime.datetime.now().astimezone().tzinfo

# pm drives autonomous work from throwaway branch checkouts under .pm/workdirs.
# Those sessions are the harness prompting itself, not a person working, and
# they outnumber the real ones — excluded unless asked for.
#
# Scoped to workdirs ONLY, deliberately. pm's own repo (~/claude-work/
# project-manager) is real development and stays in; so does anything else
# merely named "pm". An earlier version also matched /pm-test-<n> and
# .pm.old, which reached outside workdirs into scratch checkouts — dropped,
# since the rule should mean what its name says. The second alternative is
# the fallback for a session whose cwd was not recorded, where only the
# project slug is available and its separators are already dashes.
# /workspace is pm's container root, confirmed 2026-08-23: 1,245 session files
# whose cwd is literally "/workspace", carrying QA-harness prompts ("You are
# refining the test steps for QA scenario 1..."). Same class as the workdirs —
# the harness prompting itself — so it is excluded on the same switch.
PM_WORKDIR_RE = re.compile(r"/\.pm(\.old)?/workdirs/|-pm-workdirs-"
                           r"|^/workspace(/|$)")
# Commits pm makes on its own. Author identity cannot separate these — pm
# commits AS the user (3,016 of 3,143 in project-manager are authored
# "Matthew Tomei"), and a Claude co-author trailer is on 2,493 of them
# including the ones a person asked for. The subject line is what actually
# discriminates, and this is the rule velocity-analysis/scripts/
# working_hours.py already uses for the same job.
#
# Measured: 1,709 of 3,143 subjects in project-manager match; 0 of 690 in
# performance_commons and 0 of 72 in coherence — so it targets pm's loop and
# leaves human-directed, Claude-assisted work alone.
AGENTIC_COMMIT_RE = re.compile(
    r"^(merge pull request|start work on|review-loop|qa\b|pm: |pm:qa"
    r"|plan-regression|watcher)", re.I)

# /tmp/claude-<uid>/<slug>/<uuid>[/scratchpad] -> strip back toward the slug
TMP_SESSION_RE = re.compile(r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                            r"[0-9a-f]{4}-[0-9a-f]{12}$")

# Prefixes marking a turn the harness injected rather than one a person typed.
# Matched at the START only: a genuine message often has a <system-reminder>
# appended after the human's own words, and "in" would discard those.
INJECTED_PREFIXES = (
    "<system-reminder>", "[SYSTEM NOTIFICATION", "<task-notification>",
    "<local-command-stdout>", "<local-command-caveat>", "Caveat:",
    "<system-notice>",
)


# --- reading sessions -------------------------------------------------------
def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def is_human_claude(entry):
    """Claude Code: most `type: user` entries are not human.

    In one session here 3,920 of 4,636 were tool results wearing a user hat;
    the rest split into harness injections and 438 real messages. Slash
    commands count (a person typed them); their stdout does not.
    """
    if entry.get("type") != "user":
        return False
    if entry.get("toolUseResult") is not None:
        return False
    if entry.get("isMeta") or entry.get("isSidechain") or entry.get("isCompactSummary"):
        return False
    body = _text((entry.get("message") or {}).get("content")).strip()
    return bool(body) and not body.startswith(INJECTED_PREFIXES)


def is_human_omp(entry):
    """OMP: cleaner — tool results carry their own `toolResult` role."""
    if entry.get("type") != "message":
        return False
    msg = entry.get("message") or {}
    if msg.get("role") != "user":
        return False
    body = _text(msg.get("content")).strip()
    return bool(body) and not body.startswith(INJECTED_PREFIXES)


# Per source: (glob, quick line test, predicate). The line test runs before
# json.loads and skips the big lines (assistant turns, tool output), which
# takes a full 1.5GB sweep from minutes to about two seconds.
SOURCES = {
    "claude": (CLAUDE_GLOB,
               lambda ln: '"type":"user"' in ln and '"toolUseResult"' not in ln,
               is_human_claude),
    "omp": (OMP_GLOB,
            lambda ln: '"role":"user"' in ln,
            is_human_omp),
}


def normalize(proj):
    for marker in ("/scratchpad", "/.claude/projects", "/.omp/agent"):
        if marker in proj:
            proj = proj.split(marker)[0]
    return TMP_SESSION_RE.sub("", proj) or proj


def scan(sources, human_only=True):
    """{project: {session_key: [(start, end), ...]}} across the chosen sources."""
    gap = datetime.timedelta(minutes=SESSION_GAP_MIN)
    per_project = defaultdict(dict)
    for name in sources:
        pattern, quick, is_human = SOURCES[name]
        for path in glob.glob(pattern):
            if "/subagents/" in path:
                continue
            cwd, stamps = None, []
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
                    if human_only and not quick(raw):
                        continue
                    try:
                        entry = json.loads(raw)
                    except ValueError:
                        continue
                    if not isinstance(entry, dict):
                        continue
                    if human_only and not is_human(entry):
                        continue
                    ts = entry.get("timestamp")
                    if not ts:
                        continue
                    try:
                        stamps.append(datetime.datetime.fromisoformat(
                            ts.replace("Z", "+00:00")).astimezone(TZ))
                    except ValueError:
                        continue
            if not stamps:
                continue
            stamps.sort()
            ivals = [(a, b) for a, b in zip(stamps, stamps[1:]) if b - a <= gap]
            if not ivals:
                continue
            proj = normalize(cwd or os.path.basename(os.path.dirname(path)))
            key = f"{name}:{os.path.basename(path)[:8]}"
            per_project[proj][key] = ivals
    return per_project


def fold_slug_dirs(per_project):
    """Merge /tmp/... keys whose last component is a project SLUG.

    The slug is lossy (both / and _ became -) so it cannot be decoded, but it
    matches exactly against the slugs of real paths already seen.
    """
    real = {}
    for proj in per_project:
        if not proj.startswith("/tmp/"):
            for slug in (os.path.abspath(proj).replace(os.sep, "-"),
                         os.path.abspath(proj).replace(os.sep, "-").replace("_", "-")):
                real[slug] = proj
    for proj in list(per_project):
        if not proj.startswith("/tmp/"):
            continue
        target = real.get(os.path.basename(proj.rstrip(os.sep)))
        if not target:
            continue
        for sid, ivals in per_project.pop(proj).items():
            per_project[target].setdefault(sid, []).extend(ivals)
    return per_project


# --- git ---------------------------------------------------------------------
# Repos are discovered under $HOME, not just where a session was recorded, so
# that work whose transcripts are gone still counts. Omerta is the case that
# forced this: its top-level transcripts were pruned (0 files survive, only
# 202 subagent ones) while three checkouts still hold 514 commits from
# 2026-01-27..02-02 — none of which appeared in the report at all.
REPO_SCAN_ROOT = os.path.expanduser("~")
REPO_SCAN_DEPTH = 5
REPO_SCAN_PRUNE = ("node_modules", ".cache", ".venvs", ".nvm", ".bun",
                   ".conda", ".mamba", ".local", ".git")
# Only OUR commits count. A cloned third-party repo would otherwise contribute
# its whole upstream history as if it were work done here.
OUR_AUTHOR_RE = re.compile(r"matthewtomei@gmail\.com|mjtomei|Matthew Tomei", re.I)


def find_repos():
    """Git repos under $HOME, excluding pm workdirs and vendored trees."""
    found = []
    for dirpath, dirnames, _ in os.walk(REPO_SCAN_ROOT):
        depth = dirpath[len(REPO_SCAN_ROOT):].count(os.sep)
        if depth >= REPO_SCAN_DEPTH:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in REPO_SCAN_PRUNE]
        if PM_WORKDIR_RE.search(dirpath + "/"):
            dirnames[:] = []
            continue
        if os.path.isdir(os.path.join(dirpath, ".git")):
            found.append(dirpath)
            dirnames[:] = []          # do not descend into a repo's subtree
    return found


def commit_intervals(repo, skip_agentic=True):
    """[t - PRE_COMMIT_MIN, t] per commit. Returns (intervals, n_skipped).

    --all covers every ref: branches, remote-tracking branches and tags, not
    just the checked-out one (690 commits vs 495 for HEAD alone in this repo).
    --reflog is deliberately NOT added; it resurrects orphaned and amended
    commits, which would charge the same work twice.
    """
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", "--all",
             "--pretty=format:%ad%x00%s%x00%an <%ae>",
             "--date=format:%Y-%m-%dT%H:%M:%S"],
            capture_output=True, text=True, timeout=60)
        if out.returncode:
            return [], 0
    except (OSError, subprocess.SubprocessError):
        return [], 0
    ivals, skipped = [], 0
    for line in out.stdout.splitlines():
        parts = line.split("\0")
        if len(parts) < 3:
            continue
        stamp, subject, author = parts[0].strip(), parts[1], parts[2]
        if not stamp:
            continue
        if not OUR_AUTHOR_RE.search(author):
            continue                      # someone else's commit in a clone
        if skip_agentic and AGENTIC_COMMIT_RE.match(subject.strip()):
            skipped += 1
            continue
        try:
            t = datetime.datetime.fromisoformat(stamp).replace(tzinfo=TZ)
        except ValueError:
            continue
        ivals.append((t - datetime.timedelta(minutes=PRE_COMMIT_MIN), t))
    return ivals, skipped


def repo_identity(path):
    """Root commits — the identity that survives cloning.

    ~/.pm/workdirs holds independent CLONES, not worktrees, so they each have
    their own git dir but the same history. git-common-dir separates worktrees
    only; keying on the root commit catches clones too. Without this, one
    3,000-commit history was charged to fourteen "projects" at ~300h each.
    """
    try:
        out = subprocess.run(["git", "-C", path, "rev-list", "--max-parents=0",
                              "--all"], capture_output=True, text=True, timeout=30)
        if out.returncode or not out.stdout.strip():
            return None
        return " ".join(sorted(out.stdout.split()))
    except (OSError, subprocess.SubprocessError):
        return None


def add_commits(per_project, skip_agentic=True, scan_repos=True):
    """Fold commit windows in, once per REPOSITORY.

    Repos reached only by the filesystem scan (no surviving session) are added
    as projects in their own right, so deleted transcripts do not erase the
    work from the record.
    """
    seen, skipped_total, discovered = {}, 0, 0
    candidates = list(per_project)
    if scan_repos:
        candidates += [r for r in find_repos() if r not in per_project]
    for proj in sorted(candidates, key=len):         # prefer the shortest path
        dotgit = os.path.join(proj, ".git")
        if not (os.path.isdir(dotgit) or os.path.isfile(dotgit)):
            continue
        ident = repo_identity(proj)
        if ident is None or ident in seen:
            continue
        seen[ident] = proj
        ivals, skipped = commit_intervals(proj, skip_agentic=skip_agentic)
        skipped_total += skipped
        if ivals:
            if proj not in per_project:
                discovered += 1
            per_project[proj]["<git commits>"] = ivals
    return seen, skipped_total, discovered


# --- interval maths ----------------------------------------------------------
def merge(ivals):
    out = []
    for s, e in sorted(ivals):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def hours_per_day(merged):
    """Hours by calendar day, splitting intervals across midnight."""
    day = defaultdict(float)
    for s, e in merged:
        cur = s
        while cur.date() < e.date():
            nxt = datetime.datetime.combine(
                cur.date() + datetime.timedelta(days=1),
                datetime.time(0), tzinfo=TZ)
            day[cur.date()] += (nxt - cur).total_seconds() / 3600
            cur = nxt
        day[cur.date()] += (e - cur).total_seconds() / 3600
    return day


def clip(day, since, until):
    return {d: h for d, h in day.items()
            if (since is None or d >= since) and (until is None or d < until)}


BLOCKS = "▏▎▍▌▋▊▉█"


def bar(value, peak, width):
    if peak <= 0:
        return ""
    full = int(value / peak * width)
    frac = (value / peak * width) - full
    s = "█" * full
    if frac > 0 and full < width:
        s += BLOCKS[min(len(BLOCKS) - 1, int(frac * len(BLOCKS)))]
    return s


# --- views -------------------------------------------------------------------
def shorten(p, width=44):
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    return p if len(p) <= width else "…" + p[-(width - 1):]


def project_rows(per_project, since, until):
    rows = []
    for proj, sessions in per_project.items():
        day = clip(hours_per_day(merge(
            [iv for s in sessions.values() for iv in s])), since, until)
        hours = sum(day.values())
        if hours <= 0:
            continue
        session_ivals = [iv for sid, s in sessions.items()
                 if sid != "<git commits>" for iv in s]
        # The second figure is transcript COVERAGE, not a human/non-human
        # split: all of "hours" is human-directed work once pm's own commits
        # are filtered. Coverage matters because it is 0% before April 2026,
        # where the transcripts were deleted and only commits remain.
        rows.append({
            "project": proj,
            "hours": hours,
            "session": sum(clip(hours_per_day(merge(session_ivals)),
                                since, until).values()),
            "days": len([h for h in day.values() if h > 0]),
            "sessions": len([k for k in sessions if k != "<git commits>"]),
            "sources": sorted({k.split(":")[0] for k in sessions
                               if k != "<git commits>"}),
            "first": min(day), "last": max(day), "day": day,
        })
    rows.sort(key=lambda r: -r["hours"])
    return rows


def render_breakdown(rows, wall, sess_union, sess_sum, top, width=20):
    gross = sum(r["hours"] for r in rows)
    peak = rows[0]["hours"]
    shown = rows[:top] if top else rows
    out = [
        f"Work time by project — {len(rows)} projects, "
        f"{sum(r['sessions'] for r in rows)} sessions",
        f"{'project':<44} {'hours':>7} {'transcr':>7} {'share':>6} {'days':>5} "
        f"{'sess':>5} {'src':<12} {'span':<14}",
        "-" * 118,
    ]
    for r in shown:
        out.append(
            f"{shorten(r['project']):<44} {r['hours']:7.2f} {r['session']:7.2f} "
            f"{r['hours'] / gross * 100:5.1f}% {r['days']:5d} {r['sessions']:5d} "
            f"{','.join(r['sources']):<12} {r['first']:%b %d}–{r['last']:%b %d}  "
            f"{bar(r['hours'], peak, width)}")
    if top and len(rows) > top:
        rest = rows[top:]
        out.append(
            f"{f'… {len(rest)} more projects':<44} "
            f"{sum(r['hours'] for r in rest):7.2f} "
            f"{sum(r['session'] for r in rest):7.2f} "
            f"{sum(r['hours'] for r in rest) / gross * 100:5.1f}% {'':5} "
            f"{sum(r['sessions'] for r in rest):5d}")
    out += [
        "-" * 118,
        f"{'WALL-CLOCK human time (union, counted once)':<44} {wall:7.2f}",
        f"{'summed per project':<44} {gross:7.2f} {'':22}"
        f"→ {gross / wall if wall else 0:.2f}× cross-project concurrency",
    ]
    if sess_union:
        # Compare like with like: sessions against the union of the same
        # sessions, never against a union that also holds commit windows —
        # that can drive the ratio below 1.0, which reads as nonsense.
        out.append(
            f"{'transcript-covered: union / summed':<44} {sess_union:7.2f} /{sess_sum:7.2f} "
            f"{'':13}→ {sess_sum / sess_union:.2f}× pane concurrency")
    return "\n".join(out)


def render_days(day, nsess, longest, width=40):
    start, end = min(day), max(day)
    peak = max(day.values()) or 1.0
    lines = []
    d = start
    while d <= end:
        h = day.get(d, 0.0)
        n = nsess.get(d, 0)
        lines.append(f"{d:%b %d} │{bar(h, peak, width):<{width}} "
                     f"{f'{h:.2f} h' if h else '0   h'}"
                     f"{f'  ×{n}' if n > 1 else ''}")
        d += datetime.timedelta(days=1)
    foot = [f"        └{'─' * (width + 1)}",
            f"         full block ≈ {peak / width:.3f} h"
            f"        TOTAL ≈ {sum(day.values()):.2f} h"]
    if longest and longest[0] >= UNATTENDED_RUN_H:
        h, s, e = longest
        foot.append(f"         ⚠ longest unbroken run {h:.1f} h "
                    f"({s:%b %d %H:%M}–{e:%H:%M}) — check it is not an "
                    f"unattended workflow")
    return (f"Work time per day  (commit windows ∪ human-message gaps "
            f"<{SESSION_GAP_MIN} min)\n") + "\n".join(lines) + "\n" + "\n".join(foot)


def render_weeks(day, width=40):
    weeks, active = defaultdict(float), defaultdict(int)
    for d, h in day.items():
        wk = d - datetime.timedelta(days=d.weekday())
        weeks[wk] += h
        if h:
            active[wk] += 1
    first, last = min(day), max(day)
    wk = first - datetime.timedelta(days=first.weekday())
    while wk <= last - datetime.timedelta(days=last.weekday()):
        weeks.setdefault(wk, 0.0)          # zero weeks, or a gap reads as work
        wk += datetime.timedelta(days=7)
    peak = max(weeks.values()) or 1.0
    lines = []
    for mon in sorted(weeks):
        sun = mon + datetime.timedelta(days=6)
        partial = "*" if (mon < first <= sun) or (mon <= last < sun) else ""
        n = active[mon]
        lines.append(f"{mon:%b %d}{partial:1}│{bar(weeks[mon], peak, width):<{width}} "
                     f"{weeks[mon]:6.2f} h  {n} d  "
                     f"{weeks[mon] / n if n else 0:4.1f} h/d")
    return (f"Work time per week  ({first:%Y-%m-%d} → {last:%Y-%m-%d}, "
            f"Monday-labelled, * = partial)\n" + "\n".join(lines) +
            f"\n        └{'─' * (width + 1)}\n"
            f"         TOTAL ≈ {sum(weeks.values()):.2f} h over {len(weeks)} "
            f"weeks ({sum(weeks.values()) / len(weeks):.1f} h/week)")


def render_tod(merged, bin_min, since, until, width=44):
    """Clock profile: each slot scores 1 per DAY it sees activity.

    Counting days rather than minutes stops one marathon session from
    swamping the shape of a typical day, which is the question being asked.
    """
    slots = 24 * 60 // bin_min
    per_slot = defaultdict(set)
    step = datetime.timedelta(minutes=bin_min)
    for s, e in merged:
        cur = s.replace(second=0, microsecond=0)
        cur -= datetime.timedelta(minutes=cur.minute % bin_min)
        while cur < e:
            d = cur.date()
            if (since is None or d >= since) and (until is None or d < until):
                per_slot[((cur.hour * 60 + cur.minute) // bin_min) % slots].add(d)
            cur += step
    counts = [len(per_slot.get(i, ())) for i in range(slots)]
    if not any(counts):
        return "No activity found."
    days = len(set().union(*per_slot.values()))
    peak = max(counts)
    total = sum(counts)
    ent = -sum((c / total) * math.log(c / total) for c in counts if c)
    flat = ent / math.log(slots)
    win = int(4 * 60 // bin_min)
    best, at = max(((sum(counts[(i + k) % slots] for k in range(win)), i)
                    for i in range(slots)))
    label = lambda i: f"{i * bin_min // 60:02d}:{i * bin_min % 60:02d}"
    lines = []
    for i, c in enumerate(counts):
        mark = "│" if (i * bin_min) % 60 == 0 else "┊"
        cell = f"{c:3d} d {c / days * 100:3.0f}%" if c else "      -  "
        lines.append(f"{label(i)}{mark}{bar(c, peak, width):<{width}} {cell}")
    return (f"Activity by time of day  ({bin_min}-min slots; a slot scores 1 per "
            f"day it sees any activity)\n{days} active days\n"
            + "\n".join(lines) +
            f"\n      └{'─' * (width + 1)}\n"
            f"       peak {peak} of {days} days        flatness {flat * 100:.0f}%"
            f"  (100% = even across the clock)\n"
            f"       busiest 4h {label(at)}–{label((at + win) % slots)} holds "
            f"{best / total * 100:.0f}% of all activity")


def window_means(day, include_today=False, windows=(7, 30, None)):
    """[(label, mean h/calendar-day), ...] over trailing windows."""
    if not day:
        return []
    today = datetime.datetime.now(TZ).date()
    end = today if include_today else today - datetime.timedelta(days=1)
    first = min(day)
    if end < first:
        return []
    out = []
    for w in windows:
        start = max(first if w is None else end - datetime.timedelta(days=w - 1),
                    first)
        n = (end - start).days + 1
        vals = [day.get(start + datetime.timedelta(days=i), 0.0) for i in range(n)]
        out.append(("all" if w is None else f"last {w}",
                    statistics.fmean(vals) if vals else 0.0))
    return out


def render_project_time(per_project, top=None, include_today=False, width=44):
    """Per-project time summary, ALWAYS over full history.

    Deliberately unfiltered by --since/--until: the tables above answer "what
    happened in this window", and this one keeps the lifetime context that a
    windowed run otherwise hides — total hours, how much of it was human, the
    span, and the same trailing means the machine-wide block reports.
    """
    rows = []
    for proj, sessions in per_project.items():
        day = hours_per_day(merge([iv for s in sessions.values() for iv in s]))
        if not day:
            continue
        transcript_day = hours_per_day(merge(
            [iv for sid, s in sessions.items()
             if sid != "<git commits>" for iv in s]))
        means = dict(window_means(day, include_today))
        # "all" over the project's OWN span, not since-its-start-until-today:
        # a project that finished in May would otherwise be averaged across
        # months of zeros and read as idle rather than finished. last7/last30
        # stay trailing from today, so a dormant project shows 0.00 there —
        # which is the honest signal that it is dormant.
        span_days = (max(day) - min(day)).days + 1
        means["span"] = sum(day.values()) / span_days
        rows.append((sum(day.values()), sum(transcript_day.values()), len(day),
                     min(day), max(day), means, proj))
    if not rows:
        return ""
    rows.sort(reverse=True)
    shown = rows[:top] if top else rows
    out = ["", "All-time by project (full history, ignoring --since/--until)",
           f"{'project':<{width}} {'hours':>8} {'transcr':>8} {'days':>5} "
           f"{'last7':>7} {'last30':>7} {'h/d':>6}  {'span':<23}",
           "-" * 108]
    for h, tr, days, first, last, means, proj in shown:
        out.append(
            f"{shorten(proj, width):<{width}} {h:8.2f} {tr:8.2f} {days:5d} "
            f"{means.get('last 7', 0):7.2f} {means.get('last 30', 0):7.2f} "
            f"{means.get('span', 0):6.2f}  {first:%Y-%m-%d}–{last:%Y-%m-%d}")
    if top and len(rows) > top:
        rest = rows[top:]
        out.append(f"{f'… {len(rest)} more':<{width}} "
                   f"{sum(r[0] for r in rest):8.2f} {sum(r[1] for r in rest):8.2f}")
    out.append("-" * 108)
    out.append("(hours = human time: human turns ∪ commits without pm markers. "
               "transcr = how much of it surviving transcripts cover — 0 before "
               "Apr 2026, where transcripts were deleted, not where nobody "
               "worked. last7/last30 trail from today; h/d spans first..last.)")
    return "\n".join(out)


def render_summary(day, include_today=False):
    """Mean and SD over trailing windows, ending on the last COMPLETE day.

    Today is excluded by default: it is always partial, so it contributes an
    hour or two against a full day's denominator and drags every mean down by
    an amount that depends only on when the script is run. The cutoff applies
    to the "all" row too, so the rows stay comparable — which makes this table
    one day shorter than the chart above.

    Two means: per calendar day (zero days in — "what did this get per day")
    and per active day ("how heavy is a working day"). Quoting only the first
    makes focused work look idle; only the second hides the days off.
    """
    if not day:
        return ""
    today = datetime.datetime.now(TZ).date()
    end = today if include_today else today - datetime.timedelta(days=1)
    first = min(day)
    if end < first:
        return "\n         (no complete days yet — only today has activity)"
    rows = []
    for w in (7, 30, None):
        start = max(first if w is None else end - datetime.timedelta(days=w - 1),
                    first)
        n = (end - start).days + 1
        vals = [day.get(start + datetime.timedelta(days=i), 0.0) for i in range(n)]
        act = [v for v in vals if v > 0]
        rows.append(("all" if w is None else f"last {w}", n, len(act),
                     statistics.fmean(vals),
                     statistics.stdev(vals) if len(vals) > 1 else 0.0,
                     statistics.fmean(act) if act else 0.0))
    out = ["", "         window     days  active   mean h/d      SD   mean h/active-d",
           "         " + "-" * 62]
    for name, n, a, mean, sd, amean in rows:
        out.append(f"         {name:<10} {n:5d}  {a:6d}   {mean:8.2f}  {sd:6.2f}"
                   f"   {amean:13.2f}")
    out.append(f"         per calendar day, zero days included; windows end "
               f"{'today' if include_today else 'yesterday (today is partial)'}")
    return "\n".join(out)


# --- main --------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=("all",) + tuple(SOURCES), default="all",
                    help="which agent's history to read (default all)")
    ap.add_argument("--since", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD")
    ap.add_argument("--until", type=datetime.date.fromisoformat, default=None,
                    metavar="YYYY-MM-DD")
    ap.add_argument("--project", metavar="SUBSTR", default=None,
                    help="only projects whose path contains SUBSTR")
    ap.add_argument("--include-pm", action="store_true",
                    help="include sessions from pm branch workdirs "
                         "(~/.pm/workdirs, pm-test checkouts). Excluded by "
                         "default: those are pm's harness prompting itself, "
                         "not a person working, and they outnumber real ones")
    ap.add_argument("--top", type=int, default=20,
                    help="projects to list, rest rolled up (0 = all)")
    ap.add_argument("--weekly", action="store_true")
    ap.add_argument("--tod", action="store_true", help="time-of-day profile")
    ap.add_argument("--bin", type=int, default=15, metavar="MIN",
                    help="slot width for --tod; must divide 1440 (default 15)")
    ap.add_argument("--all-time", action="store_true",
                    help="also print the lifetime per-project table "
                         "(hours, human hours, trailing means, span)")
    ap.add_argument("--include-agentic-commits", action="store_true",
                    help="count commits pm made on its own (review-loop/qa/"
                         "start-work-on/merge subjects). Excluded by default: "
                         "they are the harness committing, not a person")
    ap.add_argument("--no-repo-scan", action="store_true",
                    help="only count repos where a session was recorded; by "
                         "default $HOME is scanned so repos whose transcripts "
                         "were deleted (omerta) still count")
    ap.add_argument("--no-commits", action="store_true",
                    help="human messages only; skip git commit windows")
    ap.add_argument("--include-agent", action="store_true",
                    help="count every message, not just human turns")
    ap.add_argument("--include-today", action="store_true",
                    help="include today in the mean/SD windows")
    ap.add_argument("--csv", metavar="PATH", default=None)
    args = ap.parse_args()

    if 1440 % args.bin or args.bin <= 0:
        ap.error(f"--bin {args.bin} does not divide 1440 evenly")

    sources = list(SOURCES) if args.source == "all" else [args.source]
    per_project = fold_slug_dirs(scan(sources, human_only=not args.include_agent))

    dropped = 0
    if not args.include_pm:
        for proj in list(per_project):
            if PM_WORKDIR_RE.search(proj + "/"):
                del per_project[proj]
                dropped += 1
    if args.project:
        per_project = {k: v for k, v in per_project.items() if args.project in k}
    if not per_project:
        print("No matching sessions found.")
        return

    skipped_commits = discovered = 0
    if not args.no_commits:
        _, skipped_commits, discovered = add_commits(
            per_project, skip_agentic=not args.include_agentic_commits,
            scan_repos=not args.no_repo_scan)
        if args.project:                 # re-apply after discovery adds repos
            per_project = {k: v for k, v in per_project.items()
                           if args.project in k}
        for proj in list(per_project):   # pm workdirs can arrive via the scan
            if not args.include_pm and PM_WORKDIR_RE.search(proj + "/"):
                del per_project[proj]

    rows = project_rows(per_project, args.since, args.until)
    if not rows:
        print("No activity in range.")
        return

    all_ivals = [iv for s in per_project.values() for v in s.values() for iv in v]
    merged = merge(all_ivals)
    day = clip(hours_per_day(merged), args.since, args.until)
    wall = sum(day.values())

    sess_ivals, sess_sum = [], 0.0
    nsess = defaultdict(set)
    for sessions in per_project.values():
        for sid, ivals in sessions.items():
            if sid == "<git commits>":
                continue
            sess_ivals.extend(ivals)
            sess_sum += sum(clip(hours_per_day(merge(ivals)),
                                 args.since, args.until).values())
            for s, e in ivals:
                d = s.date()
                while d <= e.date():
                    nsess[d].add(sid)
                    d += datetime.timedelta(days=1)
    sess_union = sum(clip(hours_per_day(merge(sess_ivals)),
                          args.since, args.until).values())

    notes = []
    if dropped:
        notes.append(f"{dropped} pm branch-workdir project(s) excluded "
                     f"(--include-pm to add)")
    if skipped_commits:
        notes.append(f"{skipped_commits} agent-generated commit(s) skipped "
                     f"(--include-agentic-commits to add)")
    if discovered:
        notes.append(f"{discovered} repo(s) found on disk with no surviving "
                     f"transcript — counted from commits alone")
    if notes:
        print("note: " + "\n      ".join(notes) + "\n")
    print(render_breakdown(rows, wall, sess_union, sess_sum,
                           top=args.top or None))
    print()

    if args.tod:
        print(render_tod(merged, args.bin, args.since, args.until))
    elif args.weekly:
        print(render_weeks(day))
    else:
        longest = max((((e - s).total_seconds() / 3600, s, e)
                       for s, e in merged
                       if args.since is None or e.date() >= args.since),
                      default=None)
        print(render_days(day, {d: len(v) for d, v in nsess.items()}, longest))
    print(render_summary(day, include_today=args.include_today))
    if args.all_time:
        print(render_project_time(per_project, top=args.top or None,
                                  include_today=args.include_today))

    if args.csv:
        gross = sum(r["hours"] for r in rows)
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["project", "human_hours", "transcript_hours",
                        "share_pct",
                        "active_days", "sessions", "sources", "first", "last"])
            for r in rows:
                w.writerow([r["project"], f"{r['hours']:.4f}",
                            f"{r['session']:.4f}",
                            f"{r['hours'] / gross * 100:.2f}",
                            r["days"], r["sessions"], "+".join(r["sources"]),
                            r["first"], r["last"]])
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
