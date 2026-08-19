#!/usr/bin/env python3
"""First-person witness over the WHOLE corpus (Matthew, 2026-08-19).

The ~3x lower first-person-singular rate in AI-flagged speech was a pilot
finding (quality_methods.md, 2026-07-30) on screened samples, resting on the
superseded quality run. This measures the same lexical quantity -- the
FIRST_PERSON regex from quality_lexical.py, verbatim -- over every scoreable
segment in all 22 chambers, aggregated per member-year, and reports:

  1. the corpus-wide yearly series of first-person rate (per 100 words),
     pooled and per chamber -- did "I" fall when the machines arrived?
  2. within-member pre/post-2023 change (members appearing both sides,
     >= 2,000 words each side) -- the authorship-displacement signature at
     population scale, no detector involved (detector-independent, like the
     permeation arm)
  3. member-level career FP rate against the register z from
     prereg_member_table.json -- do register users witness less?

Build pass writes fpw_member_year.json; analyze pass prints the three
results. Usage:
  python fpw_corpus.py build      (long: full corpus scan)
  python fpw_corpus.py analyze
"""
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW                      # noqa: E402

FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'd|I'll|my|mine)\b")   # verbatim
T1 = {
    "US-HOUSE": ["us/segments_us_house.jsonl"],
    "US-SENATE": ["us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl", "uk/segments_uk_2023.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
}
OUT = os.path.join(HERE, "fpw_member_year.json")


def build():
    agg = defaultdict(lambda: [0, 0])          # ch|member|year -> [words, fp]
    files = [(None, p) for p in sorted(glob.glob(
        os.path.join(HERE, "provinces", "segments_*.jsonl")))]
    files += [(ch, os.path.join(HERE, p)) for ch, ps in T1.items() for p in ps]
    for ch, path in files:
        if not os.path.exists(path):
            print(f"  MISSING {path}", flush=True)
            continue
        n = 0
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            if d.get("translated") or (d.get("orig_frac") or 1.0) <= 0.5:
                continue
            nm = FW.norm(d.get("speaker", ""))
            if not nm or FW.ROLE.match(nm):
                continue
            cham = ch or d.get("prov")
            if not cham or not d.get("date"):
                continue
            t = d["text"]
            w = d.get("n_words") or len(t.split())
            a = agg[f"{cham}|{nm}|{d['date'][:4]}"]
            a[0] += int(w)
            a[1] += len(FIRST_PERSON.findall(t))
            n += 1
        print(f"  {os.path.basename(path):<40s}{n:>9,} segments", flush=True)
    json.dump(agg, open(OUT, "w"))
    print(f"wrote {OUT}: {len(agg):,} member-years")


def analyze():
    import numpy as np
    agg = json.load(open(OUT))
    # 1. yearly pooled series
    yr = defaultdict(lambda: [0, 0])
    for k, (w, f) in agg.items():
        y = k.split("|")[2]
        if "1990" <= y <= "2026":
            yr[y][0] += w
            yr[y][1] += f
    print("1. corpus-wide first-person rate per 100 words, by year:")
    for y in sorted(yr):
        w, f = yr[y]
        if w > 2_000_000:
            print(f"   {y}  {100*f/w:.3f}   ({w/1e6:.0f}M words)")

    # 2. within-member pre/post 2023
    mem = defaultdict(lambda: {"pw": 0, "pf": 0, "qw": 0, "qf": 0})
    for k, (w, f) in agg.items():
        ch, nm, y = k.split("|")
        m = mem[f"{ch}|{nm}"]
        if y <= "2022":
            m["pw"] += w; m["pf"] += f
        elif y >= "2023":
            m["qw"] += w; m["qf"] += f
    d = [(100*m["qf"]/m["qw"] - 100*m["pf"]/m["pw"])
         for m in mem.values() if m["pw"] >= 2000 and m["qw"] >= 2000]
    d = np.array(d)
    print(f"\n2. within-member change post-2023 (n={len(d):,} members with"
          f" >=2k words both sides):")
    print(f"   mean {d.mean():+.3f} per 100w  (se {d.std()/math.sqrt(len(d)):.3f},"
          f" t {d.mean()/(d.std()/math.sqrt(len(d))):+.1f});"
          f" share falling {100*(d<0).mean():.1f}%")

    # 3. career FP rate vs register z
    tab = json.load(open(os.path.join(HERE, "prereg_member_table.json")))
    zmap = {tuple(r["member"].split("|")[:2]): r["z"]
            for r in tab if r.get("z") is not None}
    tot = defaultdict(lambda: [0, 0])
    for k, (w, f) in agg.items():
        ch, nm, y = k.split("|")
        tot[(ch, nm)][0] += w
        tot[(ch, nm)][1] += f
    xs, ys, by_ch = [], [], defaultdict(list)
    for key, (w, f) in tot.items():
        if w >= 8000 and key in zmap:
            by_ch[key[0]].append((100*f/w, zmap[key]))
    for ch, v in by_ch.items():
        if len(v) < 10:
            continue
        r = np.array([a for a, _ in v])
        r = (r - r.mean()) / (r.std() or 1)
        for (a, z), rz in zip(v, r):
            xs.append(rz); ys.append(z)
    xs, ys = np.array(xs), np.array(ys)
    rho = float(np.corrcoef(xs, ys)[0, 1])
    print(f"\n3. member career FP rate (z within chamber) vs register z:"
          f" r = {rho:+.3f}  (n={len(xs):,})")


if __name__ == "__main__":
    (build if sys.argv[1:] == ["build"] else analyze)()
