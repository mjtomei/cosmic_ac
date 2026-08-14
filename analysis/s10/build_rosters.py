#!/usr/bin/env python3
"""Speaker rosters for the tier-1 covariate expansion.

WHY ROSTERS COME FROM THE CORPUS AND NOT FROM A MEMBER LIST

The BC/SK/NL lesson (2026-08-13): a covariate file keyed on anything other
than the corpus's own speaker keys silently fails its join — BC matched 15%
of members until the file's own hansard_speaker_key was used. So the roster
each collection agent receives IS the join key set: FW.norm() of the corpus
speaker field, the same normalisation every downstream analysis uses.

WHY KEYS CARRY YEAR SPANS

US Congressional Record speakers are bare surnames ("Mr. SMITH", sometimes
"Mr. SMITH of Texas"). Over a 1994-2026 corpus one key can be several people
— different Smiths in different Congresses. Agents therefore return one
record PER PERSON per key, each with term years, and member-years are
assigned key+year -> person at analysis time. The roster's per-key first/last
years and per-year word counts are what lets an agent see that "smith" spans
1994-2026 and needs splitting.

ROLE-prefixed speakers (ministers speaking under office titles, chairs) are
excluded by the same ROLE regex the analyses use. This undercounts UK
frontbench speech under its office wrapper; consistent with every other arm.

Usage: python build_rosters.py          # writes rosters/{chamber}.json
"""
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

OUT = os.path.join(HERE, "rosters")
MIN_WORDS = 8000
CORPORA = {
    "US-HOUSE": ["us/segments_us_house.jsonl"],
    "US-SENATE": ["us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl", "uk/segments_uk_2023.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for ch, files in CORPORA.items():
        agg = defaultdict(lambda: defaultdict(int))
        for rel in files:
            p = os.path.join(HERE, rel)
            if not os.path.exists(p):
                print(f"  {ch}: MISSING {rel}")
                continue
            for line in open(p):
                d = json.loads(line)
                if not d.get("scoreable", True):
                    continue
                nm = FW.norm(d.get("speaker", ""))
                if not nm or FW.ROLE.match(nm):
                    continue
                agg[nm][d["date"][:4]] += d.get("n_words") or 0
        roster = []
        for nm, yrs in agg.items():
            tot = sum(yrs.values())
            if tot < MIN_WORDS:
                continue
            roster.append({"key": nm, "words": tot,
                           "first": min(yrs), "last": max(yrs),
                           "by_year": dict(sorted(yrs.items()))})
        roster.sort(key=lambda r: -r["words"])
        json.dump(roster, open(os.path.join(OUT, f"{ch}.json"), "w"), indent=0)
        print(f"  {ch}: {len(roster)} speakers >= {MIN_WORDS:,} words "
              f"({sum(r['words'] for r in roster)/1e6:.0f}M words covered)")


if __name__ == "__main__":
    main()
