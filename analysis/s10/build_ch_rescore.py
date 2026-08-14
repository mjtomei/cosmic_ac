#!/usr/bin/env python3
"""Rescore the UK and Ireland long bands on Pangram 4.

WHY THE WHOLE ARM AND NOT A SAMPLE

`pangram_ch_verdicts.csv` records no model version, so whether its verdicts are
Pangram 3 or Pangram 4 is unknown. A 25-segment verification sample would have
answered that for ~83 credits, but it answers only the tier question: if the
arm turns out to be P3 the full rescore still has to happen, and the sample is
wasted. Rescoring outright costs 1,071 credits, produces verdicts that are
correct whatever the old tier was, and settles the tier as a by-product by
diffing old against new on 360 segments -- a far larger P3-vs-P4 comparison
than the 20-segment route check §3.2 currently rests on.

WHAT IS AND IS NOT IN SCOPE

  IN   UK Commons and Dail Eireann long bands, 180 segments each. These are
       the two chambers excluded from the §4.2 pool for want of a Pangram 4
       long band, and they are the study's most historically interesting: UK
       carries the 1985-2026 deep series, Ireland is the one chamber besides
       the UK whose instrument rate is still rising.

  OUT  The arm's 120 short-band rows. Superseded by the matched-rate short
       band (1,648 segments), which is Pangram 4 and self-weighting.

  OUT  Its 180 Canada rows. Federal Canada already has 360 Pangram 4 verdicts
       in the expansion; rescoring would buy nothing.

BILLING is ceil(words/100) per segment, so the cost is set by total words and
not by segment count: 44,983 words for the UK and 43,201 for Ireland, 1,071
credits together. The dashboard processes at most 100 rows per upload, hence
four batches.

Usage:
  python build_ch_rescore.py           # writes pangram_ch_rescore/ch01..04.csv
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pangram_ch_rescore")
BATCH = 100                      # dashboard cap: only the first 100 are processed
SRC = {"UK House of Commons": ("uk/segments_uk.jsonl", "uk"),
       "Dail Eireann": ("ie/segments_ie_en.jsonl", "ie")}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [r for r in csv.DictReader(
        open(os.path.join(HERE, "pangram_ch_verdicts.csv")))
        if r["chamber"] in SRC]
    print(f"{len(rows)} UK/IE long-band segments to rescore")

    want = {r["seg_id"]: r for r in rows}
    text = {}
    for ch, (path, _) in SRC.items():
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            raise SystemExit(f"missing source corpus {path}")
        for line in open(p):
            d = json.loads(line)
            if d.get("seg_id") in want:
                text[d["seg_id"]] = d["text"]

    missing = sorted(set(want) - set(text))
    if missing:
        # Report rather than silently shrink the batch: a segment that cannot
        # be recovered from the corpus is a reproducibility failure, not a
        # rounding error, and the pooled figure would quietly rest on fewer
        # segments than the method section claims.
        print(f"  WARNING: {len(missing)} seg_ids not found in the corpora")
        for s in missing[:5]:
            print(f"    {s}  ({want[s]['chamber']})")

    ordered = sorted(s for s in want if s in text)
    key, credits = {}, 0
    for i, sid in enumerate(ordered):
        r = want[sid]
        cid = f"ch{i:03d}"
        credits += math.ceil(len(text[sid].split()) / 100)
        key[cid] = {"seg_id": sid, "chamber": r["chamber"],
                    "stratum": r["stratum"], "prior": r["pangram"],
                    "n_words": int(r["n_words"]), "date": r["date"]}

    nb = 0
    for b in range(0, len(ordered), BATCH):
        nb += 1
        path = os.path.join(OUT, f"ch{nb:02d}.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "text"])
            for i in range(b, min(b + BATCH, len(ordered))):
                sid = ordered[i]
                w.writerow([f"ch{i:03d}", text[sid]])
        print(f"  wrote {os.path.basename(path)}: "
              f"{min(BATCH, len(ordered)-b)} rows")

    json.dump(key, open(os.path.join(OUT, "rescore_key.json"), "w"), indent=1)
    print(f"\n{len(ordered)} segments in {nb} batches, ~{credits} credits")
    print("Upload each through the WEB DASHBOARD (Pangram 4), harvest by id, "
          "then\n`python record_ch_rescore.py` to join back and diff against "
          "the prior verdicts.")


if __name__ == "__main__":
    main()
