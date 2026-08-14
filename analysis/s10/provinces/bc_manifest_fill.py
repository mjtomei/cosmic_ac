#!/usr/bin/env python3
"""Build bc_manifest_fill.json for the years the original two-window harvest
skipped: 2011-2014 and 2020-2024.

Source: the LIMS session API, GET https://api.lims.leg.bc.ca/hdms/debates/{session}
(the same endpoint bc_manifest_2025.py uses).  BC's URLs embed a
parliament+session token that no date can determine, and the api.lims host was
never crawled by the Internet Archive, so the session list was recovered by
probing the token grid {38th..43rd} x {1st..6th}; every token that returns
nodes is listed in SESSIONS_ALL with its observed date span.  Sessions straddle
calendar years, so the calendar-year filter does the actual window selection.

THE ROW RULE (reverse-engineered from bc_manifest.json and validated below).
The API mixes three record shapes:
  - pre-2017 sessions: one node per sitting, fileName '*-Hansard-v#n#.htm',
    debateType null, no redirectLink.
  - 2017+ sessions: each sitting appears twice, as a '*-Blues.htm' draft node
    carrying the debateType and a redirectLink to the final file, and as the
    final '*-Hansard-n###.html' node itself (whose own debateType is often
    null).  Committee A / Committee C Blues normally redirect to the SAME
    combined daily file as the House Blues, so a debateType=='House' filter is
    neither necessary nor sufficient here.
So the rule is: keep every non-Blues .htm/.html fileName node, then drop only
those files that some Committee Blues points at and no House Blues does
(these are the genuinely separate committee transcripts, which exist only in
41st5th).  Date and time-of-day come from the node's own debateAttributes.

Validation (`--check`): re-deriving the 2006-2010 + 2015-2019 window with this
rule reproduces bc_manifest.json exactly - 1048/1048 rows, no missing, no
extra, no field differences.  Note the rule bc_manifest_2025.py uses
(debateType=='House' + redirectLink) does NOT reproduce it: it yields nothing
at all for the pre-2017 era and drops 20160725am-Hansard-v40n7.htm, whose
Blues redirect is malformed.

Usage:  python3 bc_manifest_fill.py [--check]
"""
import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
CACHE = HERE / "work" / "bc_sessions"

# every session token that returns nodes, with its observed date span
SESSIONS_ALL = [
    ("38th1st", "2005-09-12", "2006-02-14"),
    ("38th2nd", "2006-02-14", "2007-02-13"),
    ("38th3rd", "2007-02-13", "2008-02-12"),
    ("38th4th", "2008-02-12", "2009-02-09"),
    ("38th5th", "2009-02-09", "2009-08-25"),
    ("39th1st", "2009-08-25", "2010-02-09"),
    ("39th2nd", "2010-02-09", "2011-02-14"),
    ("39th3rd", "2011-02-14", "2011-10-03"),
    ("39th4th", "2011-10-03", "2013-02-12"),
    ("39th5th", "2013-02-12", "2013-03-14"),
    ("40th1st", "2013-06-26", "2014-02-11"),
    ("40th2nd", "2014-02-11", "2014-10-06"),
    ("40th3rd", "2014-10-06", "2015-02-10"),
    ("40th4th", "2015-02-10", "2016-02-09"),
    ("40th5th", "2016-02-09", "2017-02-14"),
    ("40th6th", "2017-02-14", "2017-03-16"),
    ("41st1st", "2017-06-22", "2017-09-08"),
    ("41st2nd", "2017-09-08", "2018-02-13"),
    ("41st3rd", "2018-02-13", "2019-02-12"),
    ("41st4th", "2019-02-12", "2020-02-11"),
    ("41st5th", "2020-02-11", "2020-08-14"),
    ("42nd1st", "2020-12-07", "2021-04-12"),
    ("42nd2nd", "2021-04-12", "2022-02-08"),
    ("42nd3rd", "2022-02-08", "2023-02-06"),
    ("42nd4th", "2023-02-06", "2024-02-20"),
    ("42nd5th", "2024-02-20", "2024-05-16"),
    ("43rd1st", "2025-02-18", "2026-02-12"),
    ("43rd2nd", "2026-02-12", "2026-05-28"),
]

FILL_YEARS = {"2011", "2012", "2013", "2014",
              "2020", "2021", "2022", "2023", "2024"}
ORIG_YEARS = {"2006", "2007", "2008", "2009", "2010",
              "2015", "2016", "2017", "2018", "2019"}


def fetch(sess):
    """Session dump, cached on disk so re-runs cost no requests."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{sess}.json"
    if p.exists():
        return json.loads(p.read_text())["allHansardFileAttributes"]["nodes"]
    time.sleep(1.2)
    req = urllib.request.Request(
        f"https://api.lims.leg.bc.ca/hdms/debates/{sess}",
        headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    p.write_text(json.dumps(d))
    return d["allHansardFileAttributes"]["nodes"]


def is_final(name):
    return bool(name) and name.lower().endswith((".htm", ".html")) \
        and "Blues" not in name


def session_rows(sess):
    """All House sitting files published under `sess` (see module docstring)."""
    nodes = fetch(sess)
    house, cmte, final = set(), set(), {}
    for n in nodes:
        fn = n["fileName"] or ""
        for da in n["debateAttributes"]["nodes"]:
            dt = da["debateType"]["name"] if da["debateType"] else None
            if not dt:
                continue
            link = da["redirectLink"] or f"/Debates/{sess}/{fn}"
            nm = link.rsplit("/", 1)[-1]
            if not is_final(nm):
                continue
            (house if dt == "House" else cmte).add(nm)
        if is_final(fn):
            da = n["debateAttributes"]["nodes"][0]
            final[fn] = {
                "date": da["date"][:10],
                "url": f"https://api.lims.leg.bc.ca/hdms/file/Debates/{sess}/{fn}",
                "name": fn,
                "session": sess,
                "tod": da["timeOfDay"]["name"] if da["timeOfDay"] else None,
            }
    committee_only = cmte - house
    return {k: v for k, v in final.items() if k not in committee_only}, \
        len(committee_only & set(final))


def harvest(years):
    lo, hi = min(years), max(years)
    rows = {}
    for sess, d0, d1 in SESSIONS_ALL:
        if d1[:4] < lo or d0[:4] > hi:          # session cannot touch window
            continue
        kept, dropped = session_rows(sess)
        inwin = {k: v for k, v in kept.items() if v["date"][:4] in years}
        rows.update(inwin)
        print(f"{sess}: {len(kept)} House files "
              f"({dropped} committee-only dropped) -> {len(inwin)} in window",
              flush=True)
    return sorted(rows.values(), key=lambda r: (r["date"], r["name"]))


def check():
    got = harvest(ORIG_YEARS)
    ref = json.load(open(HERE / "bc_manifest.json"))
    a = {r["name"]: r for r in got}
    b = {r["name"]: r for r in ref}
    diff = [n for n in set(a) & set(b) if a[n] != b[n]]
    print(f"CHECK: derived {len(a)} vs bc_manifest.json {len(b)}; "
          f"missing={len(set(b)-set(a))} extra={len(set(a)-set(b))} "
          f"fielddiff={len(diff)}")
    assert a == b, "rule does not reproduce bc_manifest.json"
    print("CHECK OK - exact reproduction")


def main():
    if "--check" in sys.argv:
        check()
        return
    out = harvest(FILL_YEARS)
    json.dump(out, open(HERE / "bc_manifest_fill.json", "w"), indent=1)
    days = sorted({r["date"] for r in out})
    print(f"\nwrote {len(out)} rows, {len(days)} sitting days, "
          f"{days[0]}..{days[-1]}")
    yc = Counter(r["date"][:4] for r in out)
    yd = {y: len({r["date"] for r in out if r["date"][:4] == y})
          for y in sorted(yc)}
    for y in sorted(FILL_YEARS):
        print(f"  {y}: {yc.get(y,0):3d} rows, {yd.get(y,0):3d} sitting days")


if __name__ == "__main__":
    main()
