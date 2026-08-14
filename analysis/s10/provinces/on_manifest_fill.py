#!/usr/bin/env python3
"""Ontario Hansard manifest for the S10 backfill years (2011-2014, 2020-2024).

WHY A HARVEST AND NOT A DATE GUESS

The ola.org day URL carries the parliament and session in its path:

    /en/legislative-business/house-documents/parliament-40/session-1/2012-03-05/hansard

A calendar date cannot tell you which (parliament, session) it belongs to, so
the URL cannot be constructed from a date alone. ola.org does publish the
mapping: /house-documents/parliament-{P}/session-{S} is a single un-paginated
page listing every sitting day of that session as a link to the day's hansard.
This script walks parliaments 38-44, sessions 1-5, keeps the pages that exist,
and reads the day links straight out of them. No probing of guessed dates, and
no reliance on the Internet Archive -- ola.org answers a plain research
User-Agent with 200 and its robots.txt disallows nothing under
/en/legislative-business (checked 2026-08-13).

The fill years span five parliaments: 39-2 and 40-1 both touch 2011, 40-2 and
41-1 both touch 2014, 42-1 and 42-2 both touch 2021, and 42-2 and 43-1 both
touch 2022. Harvesting whole sessions and then filtering on the calendar year
in the URL is what keeps those boundaries honest.

Usage: python on_manifest_fill.py   # -> on_manifest_fill.json (+ .log)
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.ola.org/en/legislative-business/house-documents"
UA = ("performance-commons-research/1.0 (academic corpus build; "
      "matthewtomei@gmail.com)")
FILL_YEARS = {2011, 2012, 2013, 2014, 2020, 2021, 2022, 2023, 2024}
PARLIAMENTS = range(38, 45)
SESSIONS = range(1, 6)


def get(url, tries=3):
    for attempt in range(tries):
        time.sleep(1.0 + attempt * 4)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"  HTTP {e.code} attempt{attempt} {url}", flush=True)
        except Exception as e:
            print(f"  ERR attempt{attempt} {url} {e}", flush=True)
    return "FAILED"


def main():
    rows, seen, failures = [], set(), []
    for p in PARLIAMENTS:
        for s in SESSIONS:
            url = f"{BASE}/parliament-{p}/session-{s}"
            h = get(url)
            if h is None:
                continue
            if h == "FAILED":
                failures.append(url)
                print(f"FAIL parliament-{p}/session-{s}", flush=True)
                continue
            pat = re.compile(
                rf"parliament-{p}/session-{s}/(\d{{4}}-\d{{2}}-\d{{2}})/hansard")
            days = sorted(set(pat.findall(h)))
            if not days:
                continue
            yrs = Counter(d[:4] for d in days)
            print(f"parliament-{p}/session-{s}: {len(days)} days "
                  f"{days[0]}..{days[-1]} " +
                  " ".join(f"{y}:{n}" for y, n in sorted(yrs.items())),
                  flush=True)
            for d in days:
                if int(d[:4]) not in FILL_YEARS or d in seen:
                    continue
                seen.add(d)
                rows.append({
                    "date": d,
                    "url": (f"{BASE}/parliament-{p}/session-{s}/{d}/hansard"),
                })
    rows.sort(key=lambda r: r["date"])
    with open(os.path.join(HERE, "on_manifest_fill.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print("\nFILL ROWS PER YEAR:")
    for y, n in sorted(Counter(r["date"][:4] for r in rows).items()):
        print(f"  {y}: {n}")
    for y in sorted(FILL_YEARS):
        if str(y) not in {r["date"][:4] for r in rows}:
            print(f"  {y}: 0  *** NO SITTING DAYS FOUND ***")
    print(f"total {len(rows)} rows; {len(failures)} unreachable listings")
    for u in failures:
        print("  unreachable:", u)


if __name__ == "__main__":
    main()
