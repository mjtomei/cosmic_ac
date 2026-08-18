#!/usr/bin/env python3
"""Coverage of the FINAL (audit-criterion) instrument: 64 elements, four components.

WHY THIS FILE EXISTS

The element audit (three blind fable runs; element_audit*.json) restructured
the instrument: U became consultation + discretion reverse-scored, four old U
elements and one L element moved to a new undirected component N, and N pulled
in elements from families the v1 instrument never touched -- Work Styles,
Essential Skills, Transferable Skills, Knowledge, interest areas. Every family
added is a family that can shrink the complete-on-all-elements occupation set,
so the prereg's coverage figures must be re-measured, not assumed from v1.

Scales used, per family (checked against Scales Reference.txt):
  4.A  Work Activities        IM  importance 1-5
  4.C  Work Context           CX  context 1-5
  1.B  interests (both files) OI  occupational interest 1-7
  1.D  Work Styles            WI  work-styles impact -3..3  (DR is a rank)
  2.A/2.B  skills files       IM  importance 1-5
  2.C  Knowledge              IM  importance 1-5

Usage: python instrument_v2_coverage.py
"""
import collections
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V30 = "/tmp/onet303/db_30_3_text"

# The four rosters are the audit's: every element-cell pair unanimous in the
# four-cell blind run, plus Frequency of Decision Making (2/3, Matthew's call),
# minus Realistic (never blind-supported). Canonical copy, written by
# instrument derivation: instrument_final_cells.json.
import json as _json
_cells = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "instrument_final_cells.json")))
U, L, D, N = _cells["U"], _cells["L"], _cells["D"], _cells["N"]
ALL = U + L + D + N
assert len(ALL) == len(set(ALL)) == 64, len(ALL)

FILES = [("Work Activities.txt", "IM"), ("Work Context.txt", "CX"),
         ("Career Interest Types.txt", "OI"), ("Specific Interest Areas.txt", "OI"),
         ("Work Styles.txt", "WI"), ("Essential Skills.txt", "IM"),
         ("Transferable Skills.txt", "IM"), ("Knowledge.txt", "IM")]

have = collections.defaultdict(dict)
for fn, scale in FILES:
    with open(os.path.join(V30, fn), encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["Element ID"] in ALL and r["Scale ID"] == scale:
                have[r["Element ID"]][r["O*NET-SOC Code"]] = float(r["Data Value"])

univ = set().union(*(set(have[e]) for e in ALL))
print(f"element universe: {len(univ)} occupations appear somewhere\n")
print(f"  {'component':<11s}{'elements':>9s}{'complete-on-component':>23s}")
comp_occ = {}
for lbl, grp in (("U", U), ("L", L), ("D", D), ("N", N)):
    missing = [e for e in grp if not have[e]]
    if missing:
        print(f"  !! {lbl}: elements with NO ratings at the chosen scale: {missing}")
    s = set(univ)
    for e in grp:
        s &= set(have[e])
    comp_occ[lbl] = s
    print(f"  {lbl:<11s}{len(grp):>9d}{len(s):>23d}")

full = comp_occ["U"] & comp_occ["L"] & comp_occ["D"] & comp_occ["N"]
print(f"\ncomplete on all {len(ALL)} elements: {len(full)}")
v1 = 862       # 19- and 41-element drafts: both complete on 862
print(f"19- and 41-element drafts:   {v1}   change {len(full)-v1:+d}")

rows = json.load(open(os.path.join(HERE, "soc_coding_new.json")))
total = sum(int(r.get("n_members") or 0) for r in rows)
slots = collections.Counter()
for r in rows:
    c = (r.get("soc_code") or "").strip()
    if c and c != "unknown":
        slots[c] += int(r.get("n_members") or 0)
cov = sum(n for c, n in slots.items() if c in full)
print(f"\nmember slots with a codeable occupation  {total:>7d}")
print(f"covered by the final instrument          {cov:>7d}  ({100*cov/total:.1f}%)")
print("41-element draft: 6,168 (87.7%)")
lost = sorted(((n, c) for c, n in slots.items() if c in comp_occ["U"] & comp_occ["L"] & comp_occ["D"] and c not in full), reverse=True)[:8]
if lost:
    print("\nlargest member counts lost to N's new families:")
    for n, c in lost:
        ttl = next((r["soc_title"] for r in rows if r.get("soc_code") == c), "")
        print(f"    {c}  {n:>4d}  {ttl[:50]}")
