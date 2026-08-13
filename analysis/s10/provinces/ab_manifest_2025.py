#!/usr/bin/env python3
"""Build ab_manifest_2025.json (2025-01-01 .. today) from the AB transcripts index.

Same row schema as ab_manifest.json (date, url, name, legl, session).
Scrapes https://www.assembly.ab.ca/assembly-business/transcripts/transcripts-by-type
for legislatures 30-32, sessions 1-4; keeps /hansards/han/ PDF hrefs whose
embedded YYYYMMDD is 2025-01-01 or later.  Backslashes in hrefs normalised.
Verified against legislature 30 session 1: reproduces the existing manifest
exactly (104/104 filenames).
"""
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
IDX = ("https://www.assembly.ab.ca/assembly-business/transcripts/"
       "transcripts-by-type?legl={l}&session={s}")
HREF = re.compile(r"LADDAR_files[^\"'>\s]*")
START, END = "20250101", "20260809"


def main():
    rows = {}
    for legl in (30, 31, 32):
        for sess in (1, 2, 3, 4):
            time.sleep(1.2)
            try:
                req = urllib.request.Request(IDX.format(l=legl, s=sess),
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    h = r.read().decode("utf-8", "replace")
            except Exception as e:
                print(f"skip {legl}/{sess}: {e}")
                continue
            kept = 0
            for raw in set(HREF.findall(h)):
                path = raw.replace("\\", "/")
                if "/hansards/han/" not in path or not path.endswith(".pdf"):
                    continue
                name = path.rsplit("/", 1)[-1]
                m = re.match(r"(\d{4})(\d{2})(\d{2})_", name)
                if not m:
                    continue
                ymd = "".join(m.groups())
                if not (START <= ymd <= END):
                    continue
                rows[name] = {
                    "date": f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
                    "url": "https://docs.assembly.ab.ca/" + path,
                    "name": name,
                    "legl": legl,
                    "session": sess,
                }
                kept += 1
            print(f"legl={legl} session={sess}: {kept} in-window files")
    out = sorted(rows.values(), key=lambda r: (r["date"], r["name"]))
    json.dump(out, open(HERE / "ab_manifest_2025.json", "w"), indent=1)
    days = sorted({r["date"] for r in out})
    print(f"wrote {len(out)} rows, {len(days)} sitting days, "
          f"{days[0]}..{days[-1]}")


if __name__ == "__main__":
    main()
