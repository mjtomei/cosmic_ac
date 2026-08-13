#!/usr/bin/env python3
"""2025+ extension of the Queensland manifest harvest.

Thin wrapper around aus_qld_harvest.py: same POST endpoint, same GUID, same
two-phrase union, but for years 2025 and 2026, and writing
aus_qld_manifest_2025.json.  Adds the "fname" key aus_download.py needs
(the existing 2006-2019 manifest had no fname because aus_qld_raw/ files are
named after the URL basename; the same basename convention is kept).

Usage: python3 aus_qld_harvest_2025.py
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import aus_qld_harvest as H  # noqa: E402

YEARS = [2025, 2026]
CUTOFF = "2026-08-09"


def main():
    found = {}
    for year in YEARS:
        for phrase in H.PHRASES:
            time.sleep(1.2)
            try:
                frag = H.query(phrase, year)
            except Exception as e:
                print(f"ERR {year} {phrase}: {e}", file=sys.stderr, flush=True)
                continue
            n = 0
            for url in H.HREF.findall(frag):
                m = H.DATE.search(url)
                if not m or m.group(1) != m.group(2):
                    continue
                if int(m.group(2)) != year:
                    continue
                date = f"{m.group(2)}-{m.group(3)}-{m.group(4)}"
                if date < "2025-01-01" or date > CUTOFF:
                    continue
                found.setdefault(date, url)
                n += 1
            print(f"{year} '{phrase}': {n} hits, running total {len(found)}",
                  file=sys.stderr, flush=True)

    rows = [{"url": u, "date": d, "prov": "QLD",
             "fname": u.rsplit("/", 1)[-1]}
            for d, u in sorted(found.items())]
    (HERE / "aus_qld_manifest_2025.json").write_text(json.dumps(rows, indent=1))
    per = {}
    for r in rows:
        per[r["date"][:4]] = per.get(r["date"][:4], 0) + 1
    print(f"manifest: {len(rows)} sitting days", file=sys.stderr)
    for y in sorted(per):
        print(f"  {y}: {per[y]}", file=sys.stderr)


if __name__ == "__main__":
    main()
