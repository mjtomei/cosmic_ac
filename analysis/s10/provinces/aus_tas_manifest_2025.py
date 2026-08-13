#!/usr/bin/env python3
"""Build aus_tas_manifest_2025.json -- the 2025-01-01..today extension.

Same route and row schema as aus_tas_manifest.py (ISYS advanced-search form ->
per-year IW_FILTER_PATH -> isysquery result list -> .docx), House of Assembly
only, Estimates / GBE / committee transcripts dropped.  Only the year list and
the output filename differ.

One index defect specific to the new period: a handful of 2025 result rows carry
the WRONG TITLE for their filename (e.g. title "House of Assembly Tuesday
2 December 2025" against file "HA Wednesday 5 November 2025.docx").  The 2025+
filenames all carry an explicit date, so the date is taken from the FILENAME
when it parses and from the title otherwise; disagreements are reported.

Usage: python3 aus_tas_manifest_2025.py
"""
import json
import re
import urllib.parse
from pathlib import Path

import aus_tas_manifest as M

HERE = Path(__file__).parent
YEARS = [2025, 2026]
BUILD = ["HA"]


def date_from(text, year=None):
    m = M.DATE_RE.search(text)
    if not m:
        return None
    y = int(m.group(3))
    if year is not None and y != year:
        return None
    return f"{y}-{M.MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def main():
    manifest, report, dropped = [], [], []
    for code in BUILD:
        slug, author = M.CHAMBERS[code]
        paths = M.year_paths(slug)
        for y in YEARS:
            path = paths.get(y)
            if not path:
                report.append(f"{code} {y}: NO FILTER PATH")
                continue
            guid, n = M.run_query(author, path)
            if not guid or not n:
                report.append(f"{code} {y}: query returned nothing")
                continue
            rows = M.list_docs(guid, n)
            kept = drop = undated = fixed = 0
            for num, title, fn in rows:
                if M.DROP.search(title) or M.DROP.search(urllib.parse.unquote(fn)):
                    drop += 1
                    dropped.append(f"{code} {y} {title} [{fn}]")
                    continue
                fname = urllib.parse.unquote(fn)
                d_file = date_from(fname, y)
                d_title = date_from(title, y)
                date = d_file or d_title
                if not date:
                    undated += 1
                    continue
                if d_file and d_title and d_file != d_title:
                    fixed += 1
                    report.append(f"    title/file date mismatch: title={d_title} "
                                  f"file={d_file} ({fname}) -> using file date")
                manifest.append({
                    "url": f"{M.BASE}/search/isysquery/{guid}/{num}/doc/{fn}",
                    "date": date,
                    "chamber": author,
                    "prov_chamber": code,
                    "year": y,
                    "file": fn,
                    "title": title,
                    "guid": guid,
                    "docnum": num,
                    "filter_path": path,
                    "author": author,
                    "local": f"{code}_{y}_{fn}",
                })
                kept += 1
            report.append(f"{code} {y}: {len(rows)} docs -> keep {kept}, "
                          f"committee/other {drop}, undated {undated}, "
                          f"date-mismatch {fixed}")
    manifest.sort(key=lambda r: (r["date"], r["local"]))
    out = HERE / "aus_tas_manifest_2025.json"
    out.write_text(json.dumps(manifest, indent=1))
    (HERE / "aus_tas_dropped_titles_2025.txt").write_text("\n".join(dropped))
    print("\n".join(report))
    print(f"\n{len(manifest)} files, "
          f"{len({(r['prov_chamber'], r['date']) for r in manifest})} chamber-days "
          f"-> {out}")


if __name__ == "__main__":
    main()
