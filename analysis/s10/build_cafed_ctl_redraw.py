#!/usr/bin/env python3
"""Replace federal Canada's seven out-of-window control segments.

WHAT IS WRONG

CA-FED's uniform control draw holds 60 segments, and seven of them are dated
after the study's own control cutoff of 2022-06-30:

    cactl013 2022-09-29    cactl031 2022-10-18    cactl016 2022-11-01
    cactl027 2022-10-17    cactl025 2022-10-24    cactl049 2022-11-29
    cactl001 2022-12-05

The cutoff is 2022-06-30 rather than year-end for a stated reason: ChatGPT
shipped 2022-11-30, and a "pre-AI" control dated December 2022 is not pre-AI.
cactl001 sits five days the wrong side of that line.

THIS IS A DESIGN DEFECT, NOT A WRONG NUMBER

All seven scored Human, as did the other 53 -- specificity is 60/60 either way,
so no reported figure moves. What cannot survive is the sentence "our pre-AI
control contains a post-ChatGPT sitting", and a reader is entitled to ask why
the cutoff was stated if it was not enforced. The seven are replaced so the
control means what it says.

If the replacements also come back Human, specificity stays 60/60 and the only
thing that changed is that the claim is now true. That is the expected outcome
and it is worth the ~21 credits.

THE WINDOW IS DELIBERATELY NOT WIDENED

Replacements are drawn from 2018-02-15 to 2022-06-30 -- the span the surviving
53 already occupy -- and not from CA-FED's full pre-2022 record, which reaches
back to 2006. Manitoba's redraw taught this: a first draw from the corrected
frame pulled 30 of 90 controls from years no other chamber could draw from,
confounding a frame repair with a change of window. One fix at a time.

Already-sampled seg_ids are excluded, so a replacement cannot duplicate a
surviving control.

Usage:
  python build_cafed_ctl_redraw.py --plan     # what it would draw
  python build_cafed_ctl_redraw.py --build    # write the upload batch + key
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ca", "segments_ca2.jsonl")
MANIFEST = os.path.join(HERE, "pangram_ch_manifest.json")
OUT = os.path.join(HERE, "pangram_cafed_ctl2")
KEY = os.path.join(HERE, "pangram_cafed_ctl2_key.json")

CUTOFF = "2022-06-30"
WMIN, WMAX = 120, 360
SEED = 20260813

sys.path.insert(0, HERE)
import build_pangram_expansion as BX          # noqa: E402


def rtf(text):
    return BX.rtf(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()

    man = json.load(open(MANIFEST))
    ca = {k: v for k, v in man.items()
          if v.get("chamber") == "Canada House of Commons"
          and v["stratum"] == "ctl"}
    drop = {k: v for k, v in ca.items() if v["date"] > CUTOFF}
    keep = {k: v for k, v in ca.items() if v["date"] <= CUTOFF}
    used = {v["seg_id"] for v in man.values()}

    ds = sorted(v["date"][:10] for v in keep.values())
    lo, hi = ds[0], CUTOFF
    print(f"CA-FED controls: {len(ca)} total, {len(keep)} in window, "
          f"{len(drop)} to replace")
    print(f"surviving window {ds[0]} .. {ds[-1]}; drawing from {lo} .. {hi}\n")
    for k, v in sorted(drop.items(), key=lambda kv: kv[1]["date"]):
        print(f"  DROP {k}  {v['date'][:10]}  {v['n_words']:>4d}w")

    pool = []
    for line in open(SRC):
        d = json.loads(line)
        if not d.get("scoreable") or d.get("translated"):
            continue
        if d.get("orig_frac", 1.0) <= 0.5:
            continue
        if not (WMIN <= d["n_words"] <= WMAX):
            continue
        if not (lo <= d["date"][:10] <= hi):
            continue
        if d["seg_id"] in used:            # never redraw a surviving control
            continue
        pool.append(d)

    print(f"\npool: {len(pool):,} in-window segments not already sampled")
    rng = random.Random(SEED)
    pick = rng.sample(pool, len(drop))
    pick.sort(key=lambda d: d["seg_id"])
    credits = sum(math.ceil(d["n_words"] / 100) for d in pick)

    print(f"\ndraw {len(pick)}, ~{credits} credits\n")
    print(f"  {'id':<12s}{'date':<12s}{'words':>6s}  speaker")
    key = {}
    for i, d in enumerate(pick):
        cid = f"cafedctl2{i:02d}"
        key[cid] = {"seg_id": d["seg_id"], "chamber": "CA-FED", "stratum": "ctl",
                    "band": "long", "date": d["date"], "n_words": d["n_words"],
                    "speaker": d.get("speaker", ""),
                    "replaces": sorted(drop)[i] if i < len(drop) else ""}
        print(f"  {cid:<12s}{d['date'][:10]:<12s}{d['n_words']:>6d}  "
              f"{(d.get('speaker') or '')[:40]}")

    yrs = collections.Counter(d["date"][:4] for d in pick)
    print(f"\n  by year: {dict(sorted(yrs.items()))}")

    if not a.build:
        print("\n(--plan only; rerun with --build to write the batch)")
        return

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "cafedctl2.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "text"])
        for i, d in enumerate(pick):
            w.writerow([f"cafedctl2{i:02d}", d["text"]])
    for i, d in enumerate(pick):
        p = os.path.join(OUT, f"cafedctl2{i:02d}.rtf")
        open(p, "w").write(rtf(d["text"]))
    json.dump(key, open(KEY, "w"), indent=1)
    print(f"\nwrote {os.path.relpath(OUT, HERE)}/ "
          f"({len(pick)} rtf + cafedctl2.csv) and "
          f"{os.path.basename(KEY)}")
    print("\nScore through the DASHBOARD, not the API: the rest of this arm is")
    print("4.0-web, and a defaulted API call would score them on Pangram 3.")


if __name__ == "__main__":
    main()
