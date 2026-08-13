#!/usr/bin/env python3
"""2025+ extension of the Victorian Hansard query-cell harvest.

Thin wrapper around aus_vic_harvest.py: same ISYS root-path query cells, same
50-document cap, same activity/member facet partitioning, same 4-workers-behind
-a-1-req/s-token-gate politeness.  Only the window, the output manifest and the
prune step differ.

  plan      2025-01-01 .. CUTOFF, writes aus_vic_manifest_2025_full.json
            (every non-SKIP_ACT activity cell) and aus_vic_manifest_2025.json
            (pruned to the same activity whitelist the 2006-2019 build used,
            derived from aus_vic_manifest.json rather than hardcoded).
            New/unknown activity labels are logged with their document counts
            to aus_vic_plan_2025.log so the prune decision is reviewable.
  download  fetch the pruned manifest into aus_vic_raw/ (same naming), skipping
            files already present.

Usage: python3 aus_vic_harvest_2025.py {plan|download}
"""
import json
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import aus_vic_harvest as H  # noqa: E402

START = date(2025, 1, 1)
CUTOFF = date(2026, 8, 9)
FULL = HERE / "aus_vic_manifest_2025_full.json"
PRUNED = HERE / "aus_vic_manifest_2025.json"
LOG = HERE / "aus_vic_plan_2025.log"


# 60th-Parliament renames of activity types the 2006-2019 build KEPT.  Recon
# quirk (3): the labels change between eras, so the prune has to match the
# CATEGORY, not the literal string.  "Grievance debate" is the Assembly's
# Thursday grievance debate, called "Grievances" in both earlier windows.
RENAMED = {"grievance debate": "grievances"}


def norm_label(s):
    """Casefold and fold the curly apostrophe: Hansard now writes
    'Council's suggested amendments' with U+2019 where 2015-2019 used ASCII."""
    return s.replace("’", "'").casefold()


def allow_set():
    """Activity labels the 2006-2019 build actually downloaded (normalised)."""
    rows = json.load(open(HERE / "aus_vic_manifest.json"))
    return {norm_label(r["activity"]) for r in rows}


def kept(activity, allow):
    a = norm_label(activity)
    return a in allow or RENAMED.get(a) in allow


def candidate_dates():
    out, d = [], START
    while d <= CUTOFF:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def plan(houses):
    log = open(LOG, "a")

    def say(*a):
        print(*a, file=log, flush=True)
        print(*a, file=sys.stderr, flush=True)

    pool = ThreadPoolExecutor(H.WORKERS)

    months = []
    y, m = START.year, START.month
    while (y, m) <= (CUTOFF.year, CUTOFF.month):
        months.append((y, m, H.MONTHS[m - 1]))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    res = list(pool.map(lambda t: H.probe("SITTINGDATE CONTAINS (%s %d)"
                                          % (t[2], t[0]))[0], months))
    live = {(y, mi) for (y, mi, _), n in zip(months, res) if n}
    say("live months: %d of %d -> %s"
        % (len(live), len(months), sorted(live)))

    cand = [d for d in candidate_dates() if (d.year, d.month) in live]
    res = list(pool.map(lambda d: H.probe("SITTINGDATE CONTAINS (%d %s %d)"
                                          % (d.day, H.MONTHS[d.month - 1],
                                             d.year))[0], cand))
    days = [d for d, n in zip(cand, res) if n]
    say("sitting dates: %d of %d candidate weekdays" % (len(days), len(cand)))
    say("dates: %s" % ", ".join(str(d) for d in days))

    pairs = [(d, h) for d in days for h in houses]
    plans = list(pool.map(lambda p: H.probe(H.q_day(p[1], p[0])), pairs))

    cells, sitting, oversize = [], Counter(), []
    labels = Counter()
    for (d, house), (n, acts, _) in zip(pairs, plans):
        if not n:
            continue
        sitting[house] += 1
        base = H.q_day(house, d)
        for act, cnt in acts:
            labels[act] += cnt
            if H.SKIP_ACT.search(act):
                continue
            q = base + " AND ACTIVITYTYPE CONTAINS (%s)" % act
            if cnt <= H.CAP:
                cells.append({"url": H.cell_url(q), "date": str(d),
                              "chamber": house, "activity": act, "n_docs": cnt,
                              "name": "%s_%s_%s.html"
                                      % (house[:2], d, H.slug(act))})
            else:
                oversize.append((d, house, act, cnt, q))
    say("cells so far %d; oversize activity cells %d"
        % (len(cells), len(oversize)))

    membs = list(pool.map(lambda o: H.probe(o[4])[2], oversize))
    for (d, house, act, cnt, q), ms in zip(oversize, membs):
        bins, cur, tot = [], [], 0
        for mem, mc in ms:
            if cur and tot + mc > H.BIN:
                bins.append(cur)
                cur, tot = [], 0
            cur.append(mem)
            tot += mc
        if cur:
            bins.append(cur)
        for i, b in enumerate(bins or [[]]):
            qq = q
            if b:
                qq += (" AND MEMBERNAME CONTAINS (%s)"
                       % " OR MEMBERNAME CONTAINS ".join(b))
            cells.append({"url": H.cell_url(qq), "date": str(d),
                          "chamber": house, "activity": act, "bin": i,
                          "n_docs": cnt,
                          "name": "%s_%s_%s_b%d.html"
                                  % (house[:2], d, H.slug(act), i)})
        say("  split %s %s %s (%d docs) -> %d bins"
            % (house, d, act, cnt, len(bins)))

    json.dump(cells, open(FULL, "w"), indent=1)
    say("activity labels dropped by SKIP_ACT regex:")
    for k, v in labels.most_common():
        if H.SKIP_ACT.search(k):
            say("   %6d  %r" % (v, k))
    prune(say)
    say("PLAN DONE sitting_days=%s" % dict(sitting))


def prune(say=lambda *a: print(*a, file=sys.stderr, flush=True)):
    """Full plan -> downloadable manifest, using the 2006-2019 whitelist."""
    cells = json.load(open(FULL))
    allow = allow_set()
    keep = [c for c in cells if kept(c["activity"], allow)]
    json.dump(keep, open(PRUNED, "w"), indent=1)

    dropped = Counter()
    for c in cells:
        if not kept(c["activity"], allow):
            dropped[c["activity"]] += c["n_docs"]
    say("PRUNE full=%d pruned=%d" % (len(cells), len(keep)))
    say("activity labels KEPT (docs): %s"
        % sorted({c["activity"] for c in keep}))
    say("activity labels DROPPED by whitelist (label, docs):")
    for k, v in dropped.most_common():
        say("   %6d  %r" % (v, k))
    say("(SKIP_ACT-dropped labels are listed by the plan stage above)")


def download():
    rows = json.load(open(PRUNED))
    rows.sort(key=lambda r: (r["chamber"] != "ASSEMBLY", r["date"], r["name"]))
    raw = HERE / "aus_vic_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "aus_vic_download_2025.log", "a")
    tally = Counter()
    lock = threading.Lock()

    def one(r):
        dest = raw / r["name"]
        if dest.exists() and dest.stat().st_size > 400:
            tally["skip"] += 1
            return
        try:
            h = H.get(r["url"])
        except Exception as e:
            tally["fail"] += 1
            with lock:
                print("FAIL %s %s" % (r["name"], e), file=log, flush=True)
            return
        b = H.body_of(h)
        if not b:
            tally["empty"] += 1
            with lock:
                print("EMPTY %s" % r["name"], file=log, flush=True)
        dest.write_text("<!--%s %s %s-->\n" % (r["date"], r["chamber"],
                                               r.get("activity", "")) + b,
                        encoding="utf-8")
        tally["dl"] += 1
        n = sum(tally.values())
        if n % 100 == 0:
            with lock:
                print("progress %d/%d %s" % (n, len(rows), dict(tally)),
                      file=log, flush=True)

    with ThreadPoolExecutor(H.WORKERS) as ex:
        list(ex.map(one, rows))
    print("DONE total=%d %s" % (len(rows), dict(tally)), file=log, flush=True)
    print("DONE total=%d %s" % (len(rows), dict(tally)), file=sys.stderr)


if __name__ == "__main__":
    mode = sys.argv[1]
    hs = sys.argv[2:] or ["ASSEMBLY", "COUNCIL"]
    if mode == "plan":
        plan(hs)
    elif mode == "prune":
        prune()
    else:
        download()
