#!/usr/bin/env python3
"""Does O*NET 30.3 change the instrument for the pre-registered study?

WHY THIS FILE EXISTS

PREREG-occupational-accountability.md names an O*NET version, and the study's
three directional components (U, L, D) are built from eighteen named elements.
The copy on disk when the coverage check first ran was 29.1 (Nov 2024); the
current release is 30.3 (May 2026), and its notes say vocational interest data
was re-estimated for 871 occupations by a new method -- which touches two of our
eighteen. Freezing the wrong version, or freezing one without knowing how far it
moved, is not something a pre-registration can leave open.

This compares the two on the three things that matter:
  1. how many occupations carry the full element set   (instrument coverage)
  2. how many MEMBER SLOTS that covers, via our 470 SOC codes  (study coverage)
  3. how far each element's values moved between versions      (does it matter)

Usage: python onet_version_compare.py
"""
import collections
import csv
import json
import os

V29 = "/tmp/onet/db_29_1_text"
V30 = "/tmp/onet303/db_30_3_text"
HERE = os.path.dirname(os.path.abspath(__file__))

U = ["4.C.1.a.2.j", "4.A.3.b.6", "4.A.4.a.2", "4.A.4.c.1", "4.C.3.a.4", "4.C.3.b.8"]
L = ["4.A.4.a.3", "4.A.4.a.4", "4.A.4.a.5", "4.A.4.a.8", "1.B.1.d", "1.B.1.a"]
D = ["4.A.4.b.1", "4.A.4.c.2", "4.A.4.c.3", "4.A.4.b.3", "4.A.4.b.4", "4.A.4.b.5"]
ALL = U + L + D
COMP = {e: c for c, g in (("U", U), ("L", L), ("D", D)) for e in g}

# Interests.txt was renamed Career Interest Types.txt in 30.3; same IDs, same OI scale.
FILES = {29: [("Work Activities.txt", "IM"), ("Work Context.txt", "CX"),
              ("Interests.txt", "OI")],
         30: [("Work Activities.txt", "IM"), ("Work Context.txt", "CX"),
              ("Career Interest Types.txt", "OI")]}


def load(root, spec):
    """element id -> {soc code: value} for the scales we use."""
    out = collections.defaultdict(dict)
    for fn, scale in spec:
        with open(os.path.join(root, fn), encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["Element ID"] in ALL and r["Scale ID"] == scale:
                    out[r["Element ID"]][r["O*NET-SOC Code"]] = float(r["Data Value"])
    return out


def complete(d):
    occ = set().union(*(set(d[e]) for e in ALL))
    return {o for o in occ if all(o in d[e] for e in ALL)}


a, b = load(V29, FILES[29]), load(V30, FILES[30])
ca, cb = complete(a), complete(b)

print("=" * 68)
print("1. INSTRUMENT COVERAGE — occupations carrying all 18 elements")
print("=" * 68)
print(f"  29.1  {len(ca):>5d}")
print(f"  30.3  {len(cb):>5d}    ({len(cb)-len(ca):+d})")
gained, lost = sorted(cb - ca), sorted(ca - cb)
print(f"  gained {len(gained)}, lost {len(lost)}")

# --- 2. what that does to the study's own coverage ---------------------
rows = json.load(open(os.path.join(HERE, "soc_coding_new.json")))
slots = collections.Counter()
for r in rows:
    c = (r.get("soc_code") or "").strip()
    if c and c != "unknown":
        slots[c] += int(r.get("n_members") or 0)
total = sum(int(r.get("n_members") or 0) for r in rows)
cov29 = sum(n for c, n in slots.items() if c in ca)
cov30 = sum(n for c, n in slots.items() if c in cb)

print()
print("=" * 68)
print("2. STUDY COVERAGE — member slots whose SOC code carries the full set")
print("=" * 68)
print(f"  member slots with a codeable occupation   {total:>7d}")
print(f"  rated under 29.1                          {cov29:>7d}  ({100*cov29/total:.1f}%)")
print(f"  rated under 30.3                          {cov30:>7d}  ({100*cov30/total:.1f}%)")
print(f"  net                                       {cov30-cov29:>+7d}")
newly = [(c, n) for c, n in slots.items() if c in cb and c not in ca]
for c, n in sorted(newly, key=lambda x: -x[1])[:10]:
    ttl = next((r["soc_title"] for r in rows if r.get("soc_code") == c), "")
    print(f"    + {c}  {n:>4d} members  {ttl[:44]}")

# --- 3. did the values move? -------------------------------------------
print()
print("=" * 68)
print("3. VALUE SHIFT on the shared occupations")
print("=" * 68)
print(f"  {'element':<14s}{'comp':>5s}{'n':>7s}{'r':>8s}{'mean|d|':>9s}{'max|d|':>8s}{'range':>8s}")
import math
for e in ALL:
    sh = sorted(set(a[e]) & set(b[e]))
    if not sh:
        print(f"  {e:<14s}{COMP[e]:>5s}{0:>7d}       --")
        continue
    x = [a[e][o] for o in sh]
    y = [b[e][o] for o in sh]
    n = len(sh)
    mx, my = sum(x)/n, sum(y)/n
    sx = math.sqrt(sum((v-mx)**2 for v in x)) or 1e-12
    sy = math.sqrt(sum((v-my)**2 for v in y)) or 1e-12
    r = sum((x[i]-mx)*(y[i]-my) for i in range(n))/(sx*sy)
    dif = [abs(x[i]-y[i]) for i in range(n)]
    rng = max(max(x), max(y)) - min(min(x), min(y))
    print(f"  {e:<14s}{COMP[e]:>5s}{n:>7d}{r:>8.3f}{sum(dif)/n:>9.3f}{max(dif):>8.3f}{rng:>8.1f}")
