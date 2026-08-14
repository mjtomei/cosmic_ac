#!/usr/bin/env python3
"""Harvest Manitoba Hansard day->volume map for the S10 fill years.

gov.mb.ca publishes one index page per session at
  https://www.gov.mb.ca/legislature/hansard/{sess}/{sess}.html
which is a set of month CALENDARS; a sitting day's <td> carries
"Volume N" plus <a href="vol_NN/summary.html#html">.  The transcript
itself lives at  {sess}/vol_NN/hNN.html  (same convention the existing
mb_manifest.json rows use).

Writes mb_manifest_fill.json: rows {date, session, urls:[...]} restricted
to the fill years (2011-2014, 2020-2024).
"""
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BASE = "https://www.gov.mb.ca/legislature/hansard"
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
YEARS = set(range(2011, 2015)) | set(range(2020, 2025))
SESSIONS = ["39th_5th",
            "40th_1st", "40th_2nd", "40th_3rd", "40th_4th", "40th_5th",
            "41st_1st", "41st_2nd", "41st_3rd", "41st_4th", "41st_5th",
            "42nd_1st", "42nd_2nd", "42nd_3rd", "42nd_4th", "42nd_5th",
            "43rd_1st", "43rd_2nd", "43rd_3rd"]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}
TAG = re.compile(r"<[^>]+>")


def get(url, tries=3):
    for a in range(tries):
        time.sleep(1.0 + 4 * a)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace"), r.geturl()
        except Exception as e:
            err = e
    print(f"  ERR {url}: {err}")
    return None, None


def parse_session(sess, html):
    """-> {date: [vol tokens]} for every calendar cell with an HTML link."""
    out = {}
    # split on calendar tables so a month header only governs its own table
    for tbl in re.split(r"(?i)<table", html)[1:]:
        m = re.search(r'thead_title.*?>\s*([A-Za-z]+)\s+(\d{4})', tbl, re.S)
        if not m:
            continue
        mon = MONTHS.get(TAG.sub("", m.group(1)).strip().lower())
        year = int(m.group(2))
        if mon is None:
            continue
        for cell in re.findall(r"(?is)<td\b[^>]*>(.*?)</td>", tbl):
            if "vol_" not in cell:
                continue
            dm = re.match(r"\s*(\d{1,2})\b", TAG.sub("\n", cell).strip())
            if not dm:
                continue
            day = int(dm.group(1))
            vols = re.findall(r'href="vol_([0-9a-z]+)/summary', cell, re.I)
            if not vols:
                continue
            date = f"{year:04d}-{mon:02d}-{day:02d}"
            out.setdefault(date, [])
            for v in vols:
                if v not in out[date]:
                    out[date].append(v)
    return out


def main():
    rows = []
    for sess in SESSIONS:
        html, _ = get(f"{BASE}/{sess}/{sess}.html")
        if not html or "Legislature" not in html:
            print(f"{sess}: no index page")
            continue
        days = parse_session(sess, html)
        keep = {d: v for d, v in days.items() if int(d[:4]) in YEARS}
        print(f"{sess}: {len(days)} sitting days, {len(keep)} in fill years")
        for d in sorted(keep):
            rows.append({"date": d, "session": sess,
                         "urls": [f"{BASE}/{sess}/vol_{v}/h{v}.html"
                                  for v in keep[d]]})
    rows.sort(key=lambda r: (r["date"], r["session"]))
    json.dump(rows, open(HERE / "mb_manifest_fill.json", "w"), indent=1)
    import collections
    c = collections.Counter(r["date"][:4] for r in rows)
    print("rows", len(rows), "urls",
          sum(len(r["urls"]) for r in rows), sorted(c.items()))


if __name__ == "__main__":
    main()
