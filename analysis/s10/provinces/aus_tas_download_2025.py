#!/usr/bin/env python3
"""Polite resumable downloader for the Tasmanian Hansard Word files.

Reads aus_tas_manifest_2025.json, writes into aus_tas_raw/, logs aus_tas_download_2025.log.
Max one request per second to search.parliament.tas.gov.au.

The manifest's URLs embed an ISYS "isysquery" GUID, which is server-side result-set
state and expires. When a download 404s/expires, the year+chamber query is re-run
(same call aus_tas_manifest.py makes) and every remaining URL for that year+chamber
is rewritten with the fresh GUID and doc numbers before retrying.

DUPLICATE-DAY DEDUPE (new in the 2025+ period).  The 2006-2019 windows split a
sitting day into "Part 1"/"Part 2" files, so two files per date were normal.
The 2025+ index has no Part files but DOES carry two accidental double-listings
of the same sitting day -- 2025-11-11 as both "HA Tuesday 11 November 2025.docx"
and "House of Assembly Tuesday 11 November 2025.docx" (two renderings of the
same 60.9k-word day), and 2026-05-05 as both "HA Tuesday 5 May 2026.docx"
(62.3k words, complete) and "HA Tuessday 5 May 2026.docx" (10.8k words, a
truncated proof).  Extracting both would double-count the day, so after
downloading, dedupe() keeps the longest document per date and drops the other
rows from the manifest.  The raw files stay on disk; extraction is manifest-
driven and ignores them.

Usage: python3 aus_tas_download_2025.py
"""
import json
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from aus_tas_manifest import BASE, UA, list_docs, run_query   # noqa: E402

HERE = Path(__file__).parent
RAW = HERE / "aus_tas_raw"

session = requests.Session()
session.headers["User-Agent"] = UA
_last = [0.0]


def get(url, **kw):
    wait = 1.05 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    try:
        return session.get(url, timeout=180, **kw)
    finally:
        _last[0] = time.time()


def ok(data, name):
    if len(data) < 500:
        return False
    if name.lower().endswith(".docx"):
        return data[:2] == b"PK"
    if name.lower().endswith(".doc"):
        return data[:4] in (b"\xd0\xcf\x11\xe0",) or data[:2] == b"PK"
    if name.lower().endswith(".pdf"):
        return data[:4] == b"%PDF"
    if name.lower().endswith(".rtf"):
        return data[:5] == b"{\\rtf"
    return b"<html" in data[:2000].lower()


def refresh(rows, key):
    """Re-run the year+chamber query and rewrite URLs for rows sharing `key`."""
    sample = next(r for r in rows if (r["prov_chamber"], r["year"]) == key)
    guid, n = run_query(sample["author"], sample["filter_path"])
    if not guid:
        return False
    by_file = {fn: num for num, _t, fn in list_docs(guid, n)}
    for r in rows:
        if (r["prov_chamber"], r["year"]) != key:
            continue
        num = by_file.get(r["file"])
        if num:
            r["guid"], r["docnum"] = guid, num
            r["url"] = f"{BASE}/search/isysquery/{guid}/{num}/doc/{r['file']}"
    return True


def docx_words(path):
    import zipfile
    try:
        xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8",
                                                                     "replace")
    except Exception:
        return 0
    return len(re.sub(r"<[^>]+>", " ",
                      "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml,
                                         re.S))).split())


def dedupe(rows, log):
    """Keep the longest document per sitting date; drop the double-listings."""
    from collections import defaultdict
    by_date = defaultdict(list)
    for r in rows:
        by_date[r["date"]].append(r)
    keep, dropped = [], []
    for date in sorted(by_date):
        group = by_date[date]
        if len(group) == 1 or any("Part" in r["title"] for r in group):
            keep.extend(group)
            continue
        group = sorted(group, key=lambda r: -docx_words(RAW / r["local"]))
        keep.append(group[0])
        for r in group[1:]:
            dropped.append(r)
            print(f"DEDUPE {date}: dropped {r['local']} "
                  f"({docx_words(RAW / r['local'])} words), kept "
                  f"{group[0]['local']}", file=log, flush=True)
    keep.sort(key=lambda r: (r["date"], r["local"]))
    return keep, dropped


def main():
    man = HERE / "aus_tas_manifest_2025.json"
    rows = json.load(open(man))
    RAW.mkdir(exist_ok=True)
    log = open(HERE / "aus_tas_download_2025.log", "a")
    done = skip = fail = 0
    refreshed = set()
    for i, r in enumerate(rows):
        dest = RAW / r["local"]
        if dest.exists() and ok(dest.read_bytes()[:8], r["file"]) is not False \
                and dest.stat().st_size > 500:
            skip += 1
            continue
        got = False
        for attempt in range(3):
            try:
                resp = get(r["url"])
                data = resp.content
                if resp.status_code == 200 and ok(data, r["file"]):
                    dest.write_bytes(data)
                    got = True
                    break
                print(f"BAD attempt{attempt} {resp.status_code} {len(data)}B "
                      f"{r['local']}", file=log, flush=True)
            except Exception as e:
                print(f"ERR attempt{attempt} {r['local']} {e}", file=log, flush=True)
            key = (r["prov_chamber"], r["year"])
            if key not in refreshed or attempt == 1:
                refreshed.add(key)
                print(f"REFRESH {key}", file=log, flush=True)
                refresh(rows, key)
                man.write_text(json.dumps(rows, indent=1))
            time.sleep(2 + 3 * attempt)
        if got:
            done += 1
        else:
            fail += 1
            print(f"FAIL {r['local']} {r['url']}", file=log, flush=True)
        if (i + 1) % 50 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)
    kept, dropped = dedupe(rows, log)
    if dropped:
        man.write_text(json.dumps(kept, indent=1))
        print(f"DEDUPE dropped {len(dropped)} duplicate-day rows; manifest now "
              f"{len(kept)} files", file=log, flush=True)


if __name__ == "__main__":
    main()
