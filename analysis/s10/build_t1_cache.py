#!/usr/bin/env python3
"""(chamber|key|year) -> [words, instrument hits] for the tier-1 chambers.

The tier-1 counterpart of member_year_rates.json (which covers the eight
Canadian provinces). Keys are FW.norm() of the corpus speaker field — the
same normalisation the rosters and covariates use, so the join is exact by
construction. ROLE-prefixed speakers excluded, consistent with every arm.

Usage: python build_t1_cache.py    # ~740M words, one pass
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

CORPORA = {
    "US-HOUSE": ["us/segments_us_house.jsonl"],
    "US-SENATE": ["us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl", "uk/segments_uk_2023.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
}


def main():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    cell = defaultdict(lambda: [0, 0])
    for ch, files in CORPORA.items():
        for rel in files:
            p = os.path.join(HERE, rel)
            if not os.path.exists(p):
                print(f"  {ch}: MISSING {rel}", flush=True)
                continue
            for line in open(p):
                d = json.loads(line)
                if not d.get("scoreable", True):
                    continue
                nm = FW.norm(d.get("speaker", ""))
                if not nm or FW.ROLE.match(nm):
                    continue
                toks = FW.TOKEN_RE.findall(d["text"].lower())
                c = cell[f"{ch}|{nm}|{d['date'][:4]}"]
                c[0] += len(toks)
                c[1] += sum(1 for t in toks if t in style)
        print(f"  {ch} done ({sum(1 for k in cell if k.startswith(ch))} "
              f"member-years so far)", flush=True)
    json.dump(cell, open(os.path.join(HERE, "member_year_rates_t1.json"), "w"))
    print(f"wrote member_year_rates_t1.json: {len(cell):,} member-years")


if __name__ == "__main__":
    main()
