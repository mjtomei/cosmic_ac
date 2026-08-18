#!/usr/bin/env python3
"""Three-way comparison: hand-built instrument vs anchored audit vs unanchored audit.

WHY THIS FILE EXISTS

The U/L/D cells in PREREG-occupational-accountability.md were assembled by hand
by one process, which had already got one call wrong (Management/Administration
was missing from D until Matthew put it in). Two blind re-derivations were run
over all 295 O*NET 30.3 elements carrying per-occupation ratings, three coders
per element, 2-of-3 to carry:

  ANCHORED    coders shown the current cell contents, and asked to challenge them
  UNANCHORED  coders shown no draft at all -- the anchoring control

Reading the pair: agreement in the UNANCHORED arm is independent re-derivation;
agreement only in the ANCHORED arm is plausibly the draft being read back.

Usage: python element_audit_compare.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = ("/tmp/claude-1000/-home-matt-performance-commons/"
         "90221613-745b-4ed1-89b6-bc432df3d564/tasks")

CUR = {"4.C.1.a.2.j": "U", "4.A.3.b.6": "U", "4.A.4.a.2": "U", "4.A.4.c.1": "U",
       "4.C.3.a.4": "U", "4.C.3.b.8": "U",
       "4.A.4.a.3": "L", "4.A.4.a.4": "L", "4.A.4.a.5": "L", "4.A.4.a.8": "L",
       "1.B.1.d": "L", "1.B.1.a": "L",
       "4.A.4.b.1": "D", "4.A.4.c.2": "D", "4.A.4.c.3": "D", "4.A.4.b.3": "D",
       "4.A.4.b.4": "D", "4.A.4.b.5": "D", "1.B.3.al": "D"}

NAME = {u["id"]: (u["name"], u["file"])
        for u in json.load(open(os.path.join(HERE, "onet_element_universe.json")))}


def arm(task_id):
    d = json.load(open(os.path.join(TASKS, f"{task_id}.output")))["result"]
    return d, {(p["id"], p["cell"]): p for p in d["consensus_pairs"]}


A, a = arm("wuo7nsw6g")     # anchored
B, b = arm("wz19n5z89")     # unanchored
cur = set(CUR.items())

print(f"{'':<14s}{'noms':>7s}{'2-of-3':>8s}{'unanimous':>11s}{'singletons':>12s}")
for lbl, d, s in (("anchored", A, a), ("unanchored", B, b)):
    u3 = sum(1 for p in s.values() if p["n"] == 3)
    print(f"  {lbl:<12s}{d['nominations']:>7d}{d['consensus']:>8d}{u3:>11d}{d['singletons']:>12d}")

print("\n" + "=" * 72)
print("1. DOES EACH ARM RE-DERIVE THE HAND-BUILT INSTRUMENT?")
print("=" * 72)
print(f"  {'element':<14s}{'':<44s}{'anch':>6s}{'unanch':>8s}")
for e, c in sorted(CUR.items(), key=lambda x: (x[1], x[0])):
    nm, f = NAME.get(e, ("?", "?"))
    va = a.get((e, c), {}).get("n", 0)
    vb = b.get((e, c), {}).get("n", 0)
    mark = "" if (va and vb) else ("   <- neither" if not (va or vb) else "   <- one arm")
    print(f"  {c} {e:<12s}{nm[:42]:<44s}{va:>6d}{vb:>8d}{mark}")
print(f"\n  re-derived by anchored:   {sum(1 for k in cur if k in a):>2d} of 19")
print(f"  re-derived by unanchored: {sum(1 for k in cur if k in b):>2d} of 19")
print(f"  re-derived by BOTH:       {sum(1 for k in cur if k in a and k in b):>2d} of 19")

print("\n" + "=" * 72)
print("2. FOUND BY BOTH ARMS, NOT IN THE INSTRUMENT  <- strongest candidates")
print("=" * 72)
both = sorted(set(a) & set(b) - cur, key=lambda k: (k[1], -(a[k]["n"] + b[k]["n"])))
for k in both:
    nm, f = NAME.get(k[0], ("?", "?"))
    print(f"  {k[1]} {k[0]:<12s}{nm[:38]:<40s}{a[k]['n']}+{b[k]['n']}/6  [{f}]")
print(f"  ({len(both)} pairs)")

print("\n" + "=" * 72)
print("3. UNANCHORED ONLY -- nothing pointed the coders at these")
print("=" * 72)
for k in sorted(set(b) - set(a) - cur, key=lambda k: (k[1], k[0])):
    nm, f = NAME.get(k[0], ("?", "?"))
    print(f"  {k[1]} {k[0]:<12s}{nm[:38]:<40s}{b[k]['n']}/3  [{f}]")

print("\n" + "=" * 72)
print("4. ANCHORED ONLY -- candidate anchoring artifacts")
print("=" * 72)
for k in sorted(set(a) - set(b) - cur, key=lambda k: (k[1], k[0])):
    nm, f = NAME.get(k[0], ("?", "?"))
    print(f"  {k[1]} {k[0]:<12s}{nm[:38]:<40s}{a[k]['n']}/3  [{f}]")

print("\n" + "=" * 72)
print("5. WHAT KIND OF ELEMENT IS EACH ARM REACHING FOR?")
print("=" * 72)
print(f"  {'descriptor family':<28s}{'in instrument':>14s}{'anchored':>10s}{'unanchored':>12s}")
fams = collections.Counter(NAME[e][1] for e in CUR)
fa = collections.Counter(NAME[k[0]][1] for k in a)
fb = collections.Counter(NAME[k[0]][1] for k in b)
for f in sorted(set(fams) | set(fa) | set(fb)):
    print(f"  {f:<28s}{fams.get(f,0):>14d}{fa.get(f,0):>10d}{fb.get(f,0):>12d}")
