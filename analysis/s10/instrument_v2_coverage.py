#!/usr/bin/env python3
"""Coverage of the v2 (post-audit) instrument: 41 elements, four components.

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

U = ["4.A.4.b.6", "4.C.3.a.4", "4.C.3.b.8", "4.A.2.b.4", "4.C.3.a.2.b"]
L = ["4.A.4.a.3", "4.A.4.a.5", "4.A.4.a.8", "1.B.1.d", "1.B.1.a"]
D = ["4.A.4.b.1", "4.A.4.c.2", "4.A.4.c.3", "4.A.4.b.3", "4.A.4.b.4",
     "4.A.4.b.5", "1.B.3.al"]
N = ["1.B.1.f", "1.B.3.ai", "1.B.3.ak", "1.D.2.d", "1.D.2.f", "2.A.1.c",
     "2.B.1.b", "2.B.1.d", "2.C.1.b", "4.A.2.a.2", "4.A.2.a.3", "4.A.3.b.2",
     "4.A.3.b.6", "4.A.4.a.1", "4.A.4.a.2", "4.A.4.a.4", "4.A.4.c.1",
     "4.C.1.a.2.f", "4.C.1.a.2.h", "4.C.1.a.2.j", "4.C.1.a.2.l", "4.C.1.a.4",
     "4.C.1.d.1", "4.C.2.a.3"]
ALL = U + L + D + N
assert len(ALL) == len(set(ALL)) == 41, len(ALL)

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
print(f"\ncomplete on all 41 elements: {len(full)}")
v1 = 862       # v1 instrument (19 elements incl. 1.B.3.al) complete set
print(f"v1 instrument (19 elements): {v1}   change {len(full)-v1:+d}")

rows = json.load(open(os.path.join(HERE, "soc_coding_new.json")))
total = sum(int(r.get("n_members") or 0) for r in rows)
slots = collections.Counter()
for r in rows:
    c = (r.get("soc_code") or "").strip()
    if c and c != "unknown":
        slots[c] += int(r.get("n_members") or 0)
cov = sum(n for c, n in slots.items() if c in full)
print(f"\nmember slots with a codeable occupation  {total:>7d}")
print(f"covered by the v2 instrument             {cov:>7d}  ({100*cov/total:.1f}%)")
print("v1 figures: 6,168 (87.7%)")
lost = sorted(((n, c) for c, n in slots.items() if c in comp_occ["U"] & comp_occ["L"] & comp_occ["D"] and c not in full), reverse=True)[:8]
if lost:
    print("\nlargest member counts lost to N's new families:")
    for n, c in lost:
        ttl = next((r["soc_title"] for r in rows if r.get("soc_code") == c), "")
        print(f"    {c}  {n:>4d}  {ttl[:50]}")
