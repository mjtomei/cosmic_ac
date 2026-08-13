#!/usr/bin/env python3
"""Build sk_manifest_2025.json (2025-01-01 .. today) from the SK documents API.

One GET to https://www.legassembly.sk.ca/api/documents returns the whole
1947-present archive; filter documentType=='Debates' and
committee=='Legislative Assembly' and start >= 2025-01-01.
Row schema identical to sk_manifest.json: date, url, name, timeOfDay
(url = mainUrl, i.e. the PDF, so sk_extract.py works unchanged; an HTML twin
exists in htmlUrl for every 2025+ sitting but is deliberately not used).
"""
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
START, END = "2025-01-01", "2026-08-09"


def main():
    req = urllib.request.Request("https://www.legassembly.sk.ca/api/documents",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        docs = json.load(r)
    rows = []
    for d in docs:
        if d["documentType"] != "Debates" or d["committee"] != "Legislative Assembly":
            continue
        date = d["start"][:10]
        if not (START <= date <= END) or not d["mainUrl"]:
            continue
        rows.append({"date": date, "url": d["mainUrl"], "name": d["name"],
                     "timeOfDay": d["timeOfDay"]})
    rows.sort(key=lambda r: (r["date"], r["name"]))
    json.dump(rows, open(HERE / "sk_manifest_2025.json", "w"), indent=1)
    days = sorted({r["date"] for r in rows})
    print(f"total docs {len(docs)}; wrote {len(rows)} rows, "
          f"{len(days)} sitting days, {days[0]}..{days[-1]}")


if __name__ == "__main__":
    main()
