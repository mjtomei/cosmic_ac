#!/usr/bin/env python3
"""Four-cell audit against the three-cell arms: what migrates to N?

WHY THIS FILE EXISTS

The two three-cell arms could only force an element to claim a direction or
drop it. Matthew: the study cares about undirected account-giving and sociality
too, so a fourth cell N was added and the derivation rerun blind (no draft, no
earlier results). The readout is MIGRATION: an element that held a directional
cell in the three-cell arms only because no undirected home existed should move
to N; one that keeps its direction with N on offer has re-earned it against a
live alternative.

Usage: python element_audit_4col_compare.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CUR = {"4.C.1.a.2.j": "U", "4.A.3.b.6": "U", "4.A.4.a.2": "U", "4.A.4.c.1": "U",
       "4.C.3.a.4": "U", "4.C.3.b.8": "U",
       "4.A.4.a.3": "L", "4.A.4.a.4": "L", "4.A.4.a.5": "L", "4.A.4.a.8": "L",
       "1.B.1.d": "L", "1.B.1.a": "L",
       "4.A.4.b.1": "D", "4.A.4.c.2": "D", "4.A.4.c.3": "D", "4.A.4.b.3": "D",
       "4.A.4.b.4": "D", "4.A.4.b.5": "D", "1.B.3.al": "D"}

NAME = {u["id"]: (u["name"], u["file"])
        for u in json.load(open(os.path.join(HERE, "onet_element_universe.json")))}


def arm(fn):
    d = json.load(open(os.path.join(HERE, fn)))
    best = {}                       # id -> (cell, n): the cell with most votes
    for p in d["consensus_pairs"]:
        if p["id"] not in best or p["n"] > best[p["id"]][1]:
            best[p["id"]] = (p["cell"], p["n"])
    return d, {(p["id"], p["cell"]): p for p in d["consensus_pairs"]}, best


A, a, ba = arm("element_audit_anchored.json")
B, b, bb = arm("element_audit_unanchored.json")
C, c, bc = arm("element_audit_4col.json")

print(f"{'':<14s}{'noms':>7s}{'2-of-3':>8s}   cells")
for lbl, d, s in (("anchored", A, a), ("unanchored", B, b), ("4-col", C, c)):
    cells = dict(collections.Counter(p["cell"] for p in s.values()))
    print(f"  {lbl:<12s}{d['nominations']:>7d}{d['consensus']:>8d}   {cells}")

def nm(e):
    return NAME.get(e, ("?", "?"))[0][:40]

print("\n" + "=" * 74)
print("1. MIGRATION — unanchored 3-cell result vs 4-cell result, same coders' setup")
print("=" * 74)
print("  Elements directional at 2-of-3 in the UNANCHORED arm, and their 4-col fate:")
moved, kept, dropped = [], [], []
for (e, cell), p in sorted(b.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    fc = bc.get(e)
    if fc is None:
        dropped.append((e, cell))
    elif fc[0] == cell:
        kept.append((e, cell, fc[1]))
    else:
        moved.append((e, cell, fc[0], fc[1]))
print(f"\n  KEPT their direction with N available ({len(kept)}):")
for e, cell, n in kept:
    tag = "  *instrument*" if CUR.get(e) == cell else ""
    print(f"    {cell}  {e:<13s}{nm(e):<42s}{n}/3{tag}")
print(f"\n  MOVED ({len(moved)}):")
for e, old, new, n in moved:
    tag = f"  *instrument {CUR[e]}*" if e in CUR else ""
    print(f"    {old} -> {new}  {e:<13s}{nm(e):<42s}{n}/3{tag}")
print(f"\n  VANISHED in 4-col ({len(dropped)}):")
for e, cell in dropped:
    tag = f"  *instrument {CUR[e]}*" if e in CUR else ""
    print(f"    {cell} -> none  {e:<13s}{nm(e):<42s}{tag}")

print("\n" + "=" * 74)
print("2. THE 19 INSTRUMENT ELEMENTS across all three runs")
print("=" * 74)
print(f"  {'cell':<5s}{'element':<14s}{'':<42s}{'anch':>6s}{'unanch':>8s}{'4col':>10s}")
for e, cell in sorted(CUR.items(), key=lambda x: (x[1], x[0])):
    va = a.get((e, cell), {}).get("n", 0)
    vb = b.get((e, cell), {}).get("n", 0)
    f4 = bc.get(e)
    s4 = f"{f4[1]}/3 {f4[0]}" if f4 else "--"
    flag = "" if (f4 and f4[0] == cell) else "   <-"
    print(f"  {cell:<5s}{e:<14s}{nm(e):<42s}{va:>6d}{vb:>8d}{s4:>10s}{flag}")

print("\n" + "=" * 74)
print("3. N AT 2-of-3 — the undirected cell's contents, with measure votes")
print("=" * 74)
for p in sorted((p for p in c.values() if p["cell"] == "N"),
                key=lambda p: (-p["n"], p["id"])):
    ms = collections.Counter(m.upper().strip() for m in p.get("measures", []))
    mtxt = "+".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(ms.items())) or "?"
    _, fam = NAME.get(p["id"], ("?", "?"))
    tag = f"  *instrument {CUR[p['id']]}*" if p["id"] in CUR else ""
    print(f"  {p['n']}/3  {p['id']:<13s}{nm(p['id']):<42s}{mtxt:<12s}[{fam}]{tag}")

print("\n" + "=" * 74)
print("4. DIRECTIONAL PAIRS NEW IN THE 4-COL RUN (not 2-of-3 in either earlier arm)")
print("=" * 74)
for (e, cell), p in sorted(c.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    if cell == "N" or (e, cell) in a or (e, cell) in b or CUR.get(e) == cell:
        continue
    print(f"  {cell}  {e:<13s}{nm(e):<42s}{p['n']}/3  [{NAME.get(e,('?','?'))[1]}]")
