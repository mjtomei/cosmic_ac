#!/usr/bin/env python3
"""Harvest Nova Scotia Hansard day pages for the S10 fill years.

nslegislature.ca lists every sitting day of a session in a paginated
Drupal view at
  /legislative-business/hansard-debates/assembly-{N}-session-{S}[?page=k]
one <tr> per sitting: sitting no., date ("2024-Sep-20") linking to the
day's HTML transcript, pages, video, and a PDF link.

Writes ns_manifest_fill.json with the same row schema as ns_manifest.json:
{date, session, html_url, pdf_url}, restricted to 2011-2014 / 2020-2024.

robots.txt on nslegislature.ca declares Crawl-delay: 10 -> 10 s between
requests.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ROOT = "https://nslegislature.ca"
BASE = "/legislative-business/hansard-debates"
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")
DELAY = 10.0
YEARS = set(range(2011, 2015)) | set(range(2020, 2025))
# every session that could contain a fill-year sitting
SESSIONS = [(61, 2), (61, 3), (61, 4), (61, 5), (62, 1), (62, 2),
            (63, 2), (63, 3), (64, 1), (64, 2), (65, 1)]
MON = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}
ROW = re.compile(r"(?is)<tr\b[^>]*>(.*?)</tr>")
DAY = re.compile(r'(?is)<a href="(' + BASE + r'/[^"]*?/house_[^"]*?)">\s*'
                 r"(\d{4})-([A-Za-z]{3})-(\d{1,2})\s*</a>")   # "2020-Mar-9"
PDF = re.compile(r'(?i)href="(https?://[^"]*?/hansard/[^"]*?\.pdf[^"]*)"')


def get(url, tries=3):
    err = None
    for a in range(tries):
        time.sleep(DELAY + 10 * a)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            err = e
    print(f"  ERR {url}: {err}")
    return None


def parse(html):
    out = []
    for row in ROW.findall(html):
        m = DAY.search(row)
        if not m:
            continue
        href, yy, mon, dd = m.groups()
        mo = MON.get(mon[:3].lower())
        if not mo:
            continue
        p = PDF.search(row)
        out.append({"date": f"{yy}-{mo:02d}-{int(dd):02d}",
                    "html_url": ROOT + href,
                    "pdf_url": p.group(1).split("?")[0] if p else None})
    return out


def main():
    rows, seen = [], set()
    for asm, ses in SESSIONS:
        slug = f"assembly-{asm}-session-{ses}"
        tag = f"a{asm}s{ses}"
        got = tot = 0
        for page in range(0, 12):
            url = f"{ROOT}{BASE}/{slug}" + (f"?page={page}" if page else "")
            html = get(url)
            if html is None or "views-field-field-hansard-date" not in html:
                if page == 0:
                    print(f"{slug}: no session page")
                break
            days = parse(html)
            if not days:
                break
            tot += len(days)
            for d in days:
                if int(d["date"][:4]) not in YEARS:
                    continue
                key = d["html_url"]
                if key in seen:
                    continue
                seen.add(key)
                d["session"] = tag
                rows.append({"date": d["date"], "session": tag,
                             "html_url": d["html_url"],
                             "pdf_url": d["pdf_url"]})
                got += 1
            if f"?page={page + 1}" not in html:
                break
        print(f"{slug}: {tot} sitting days listed, {got} in fill years")
    rows.sort(key=lambda r: (r["date"], r["html_url"]))
    json.dump(rows, open(HERE / "ns_manifest_fill.json", "w"), indent=1)
    import collections
    c = collections.Counter(r["date"][:4] for r in rows)
    print("rows", len(rows), sorted(c.items()))


if __name__ == "__main__":
    main()
