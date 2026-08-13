#!/usr/bin/env python3
"""Build bc_manifest_2025.json (2025-01-01 .. today) from the LIMS session API.

Same row schema and same filtering rule as bc_manifest.json:
  - iterate allHansardFileAttributes.nodes[].debateAttributes.nodes[]
  - keep debateType == 'House'  (drops Committee A / Committee C)
  - final file = redirectLink if set, else the node's own fileName
  - drop Blues drafts and anything that is not .htm/.html
Verified against session 41st4th: reproduces the existing manifest exactly
(106/106 rows, identical date + tod fields).
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
SESSIONS = ["42nd4th", "42nd5th", "43rd1st", "43rd2nd", "43rd3rd",
            "44th1st", "44th2nd"]
START, END = "2025-01-01", "2026-08-09"


def fetch(sess):
    req = urllib.request.Request(
        f"https://api.lims.leg.bc.ca/hdms/debates/{sess}",
        headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["allHansardFileAttributes"]["nodes"]


def main():
    rows = {}
    for sess in SESSIONS:
        time.sleep(1.2)
        try:
            nodes = fetch(sess)
        except Exception as e:
            print(f"skip {sess}: {e}")
            continue
        n_kept = 0
        for node in nodes:
            for da in node["debateAttributes"]["nodes"]:
                dt = da["debateType"]["name"] if da["debateType"] else None
                if dt != "House":
                    continue
                link = da["redirectLink"] or f"/Debates/{sess}/{node['fileName']}"
                name = link.rsplit("/", 1)[-1]
                if "Blues" in name or not name.lower().endswith((".htm", ".html")):
                    continue
                date = da["date"][:10]
                if not (START <= date <= END):
                    continue
                rows[name] = {
                    "date": date,
                    "url": "https://api.lims.leg.bc.ca/hdms/file" + link,
                    "name": name,
                    "session": sess,
                    "tod": da["timeOfDay"]["name"] if da["timeOfDay"] else None,
                }
                n_kept += 1
        print(f"{sess}: {len(nodes)} nodes -> {n_kept} in-window House files")
    out = sorted(rows.values(), key=lambda r: (r["date"], r["name"]))
    json.dump(out, open(HERE / "bc_manifest_2025.json", "w"), indent=1)
    days = sorted({r["date"] for r in out})
    print(f"wrote {len(out)} rows, {len(days)} sitting days, "
          f"{days[0]}..{days[-1]}")


if __name__ == "__main__":
    main()
