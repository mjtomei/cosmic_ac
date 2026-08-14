#!/usr/bin/env python3
"""Verification sample: is the four-chamber arm Pangram 4 or Pangram 3?

THE QUESTION AND WHY IT IS WORTH 75 CREDITS

`pangram_ch_verdicts.csv` holds the UK, Ireland and federal Canada long bands
(180 segments each) and records no model version. Canada is independently
covered by the Pangram 4 expansion, so what hangs on this is whether UK Commons
and Dail Eireann can enter the pooled prevalence figure. They are excluded
today, which costs the study its two most historically interesting chambers.

Rescoring both arms in full is 360 segments and 1,071 credits. Rescoring a
sample and checking agreement is ~25 segments and ~75. Do the cheap thing
first: if the sample agrees, the arm is Pangram 4 and 1,071 credits buys
nothing; if it disagrees, we have learned that before spending them.

WHY A SAMPLE AND NOT AN ARGUMENT

Two tier claims in this repository were settled by reasoning about verdict
distributions and both were wrong. "No Mixed, therefore Pangram 3" was wrong
because P3 does return Mixed -- the New Brunswick rescore preserves 8 of them
in `prior_p3` -- and because zero Mixed among 120 short segments is what P4
predicts anyway. The mirror-image argument, "it contains Mixed, therefore P4",
is no better. Verdict distributions do not identify the model; agreement on
known text does.

SAMPLING DELIBERATELY ENRICHED FOR DISAGREEMENT

A uniform sample would be ~92% Human, and Human-on-Human agreement is where the
two tiers agree anyway -- the New Brunswick rescore flipped 55 of 658, almost
all of them at the AI and Mixed end. So this takes every AI and Mixed verdict
in the UK/IE long band and fills the rest with Human, which concentrates the
sample where the tiers actually differ. That makes agreement a strong result
and disagreement easy to see; it is not a prevalence estimate and must not be
read as one.

Usage:
  python build_tier_check.py            # writes pangram_tier_check/tc01.csv
"""
import argparse
import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pangram_tier_check")
SRC = {"UK House of Commons": "uk/segments_uk.jsonl",
       "Dail Eireann": "ie/segments_ie_en.jsonl"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    rows = [r for r in csv.DictReader(open(os.path.join(HERE,
                                                        "pangram_ch_verdicts.csv")))
            if r["chamber"] in SRC]
    flagged = [r for r in rows if r["pangram"] in ("AI", "Mixed")]
    human = [r for r in rows if r["pangram"] == "Human"]
    rng = random.Random(20260813)
    rng.shuffle(human)
    pick = flagged + human[:max(0, a.n - len(flagged))]
    print(f"{len(rows)} UK/IE long-band rows; sampling {len(pick)} "
          f"({len(flagged)} flagged + {len(pick)-len(flagged)} Human)")

    want = {r["seg_id"]: r for r in pick}
    text = {}
    for ch, path in SRC.items():
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            print(f"  MISSING SOURCE {path}")
            continue
        for line in open(p):
            d = json.loads(line)
            if d.get("seg_id") in want:
                text[d["seg_id"]] = d["text"]

    missing = [s for s in want if s not in text]
    if missing:
        print(f"  {len(missing)} seg_ids not found in source: {missing[:4]}")

    path = os.path.join(OUT, "tc01.csv")
    credits = 0
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "text"])
        for i, (sid, r) in enumerate(sorted(want.items())):
            if sid not in text:
                continue
            t = text[sid]
            credits += -(-len(t.split()) // 100)
            w.writerow([f"tc{i:03d}", t])
    key = {f"tc{i:03d}": {"seg_id": sid, "chamber": r["chamber"],
                          "stratum": r["stratum"], "prior": r["pangram"],
                          "n_words": r["n_words"]}
           for i, (sid, r) in enumerate(sorted(want.items())) if sid in text}
    json.dump(key, open(os.path.join(OUT, "tc01_key.json"), "w"), indent=1)
    print(f"wrote {path} and tc01_key.json -- {len(key)} rows, "
          f"~{credits} credits")
    print("Upload through the WEB DASHBOARD (which is Pangram 4), then compare "
          "against the\n'prior' field in the key. Agreement means the arm was "
          "already Pangram 4 and UK\nand Ireland can join the pool.")


if __name__ == "__main__":
    main()
