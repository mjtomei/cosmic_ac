#!/usr/bin/env python3
"""Blinded pool for the Opus band screen: 3 chambers x 2 bands x 2 eras.

WHAT THIS IS FOR

The permeation argument rests on a dose-response claim: the AI-vocabulary
shift is LARGER in the short spontaneous band than in the long prepared band,
while the short band contains far less machine-drafted text. The "far less"
half currently rests on 120 Pangram verdicts, and on one detector.

This measures the same thing with an independent instrument at ~40x the
sample size, and -- crucially -- measures BOTH bands with the SAME instrument,
so the short/long comparison is not Pangram-on-one-band versus Opus-on-the-
other.

Design rules that make the comparison legitimate:
  - identical selection rule in every cell: uniform random from that
    (chamber, band, era) stratum, no screen stratification
  - the pool file carries TEXT ONLY. No date, no chamber, no band, no
    speaker. The screen cannot condition on era, which is the whole point:
    the pre-2023 cells are the false-positive floor and must be
    indistinguishable to the judge
  - IDs are shuffled globally, so batch composition leaks nothing either
  - the key mapping ID -> stratum is written to a separate file the judge
    never sees

Usage: python build_band_screen_pool.py [--per-cell 400]
"""
import argparse
import hashlib
import json
import random

CORPORA = {
    "ie": ("ie/segments_ie_en.jsonl", "Dail Eireann"),
    "ca": ("ca/segments_ca_en.jsonl", "Canada House of Commons"),
    "uk": ("uk/segments_uk.jsonl", "UK House of Commons"),
}
POOL = "band_screen_pool.json"
KEY = "band_screen_key.json"


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5)


def era(date):
    if date <= "2022-12-31":
        return "pre"
    if date >= "2024-01-01":
        return "post"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cell", type=int, default=400)
    args = ap.parse_args()

    cells = {}
    for code, (path, name) in CORPORA.items():
        buckets = {}
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            e = era(d["date"])
            if not e:
                continue
            band = "short" if d["n_words"] < 120 else "long"
            buckets.setdefault((code, band, e), []).append(d)
        for k, v in buckets.items():
            rng = random.Random(int(hashlib.sha1(
                ("|".join(k) + "bandscreen").encode()).hexdigest()[:8], 16))
            n = min(args.per_cell, len(v))
            cells[k] = rng.sample(v, n)
            print(f"  {k[0]}-{k[1]}-{k[2]}: pool {len(v):>7,} -> {n}")

    items = [(k, d) for k, v in cells.items() for d in v]
    random.Random(20260802).shuffle(items)

    pool, key = {}, {}
    for i, (k, d) in enumerate(items):
        sid = "B" + str(i).zfill(4)
        pool[sid] = d["text"]
        key[sid] = {"chamber": k[0], "band": k[1], "era": k[2],
                    "seg_id": d["seg_id"], "date": d["date"],
                    "speaker": d.get("speaker", ""), "n_words": d["n_words"]}

    json.dump(pool, open(POOL, "w"), ensure_ascii=False)
    json.dump(key, open(KEY, "w"), indent=1)
    words = sum(v["n_words"] for v in key.values())
    print(f"\n{len(pool)} segments, {words:,} words -> {POOL} (blinded), {KEY} (key)")


if __name__ == "__main__":
    main()
