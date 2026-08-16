#!/usr/bin/env python3
"""Detect transcription-regime changes in the chamber corpora.

WHY

S10 compares a pre-AI control window against a 2025-26 prevalence window and
reads the difference as machine drafting. That inference fails if the way the
*record itself* is produced changed between the two windows. A chamber that
moved from heavily-edited Hansard to verbatim or ASR-assisted transcription
will shift on exactly the surface features a detector reads, with nobody
having drafted anything with a machine.

This is the same hazard as Manitoba's soft hyphens (period-correlated
characters, caught in build_pangram_expansion.clean) one level up: at the
level of wording rather than encoding.

The Aug 2026 AI-policy scan named NSW and WA as ASR users. That is a claim
about procurement, not about the text. This measures the text.

WHAT IT MEASURES

Two markers chosen because they track editorial convention rather than what
was said:

  words per sentence   - how the transcriber segments speech into sentences
  contractions /1k     - traditional Hansard expands "don't" to "do not";
                         verbatim and ASR-first transcription does not

Neither is a detector score. The claim is only that a step change means the
text-production process changed, which is enough to disqualify a naive
pre/post comparison in that chamber.

SAMPLING. Random within chamber-year, seeded per cell. An earlier version of
this diagnostic took the FIRST 400 segments per chamber-year, which weights
each year toward whatever was debated in January and manufactured a spurious
Tasmania result. Do not reintroduce that.

Usage: python transcript_regime_check.py [--per-cell 400] [--min-words 80]
Writes transcript_regime.csv
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import random
import re
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SENT = re.compile(r"[.!?]+")
# both apostrophes: most Hansards use U+2019, a straight-quote-only pattern
# silently reports zero contractions for them
CONTR = re.compile(r"\b\w+['’]\w+")
PRE_MAX, POST_MIN = "2019", "2025"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cell", type=int, default=400)
    ap.add_argument("--min-words", type=int, default=80)
    args = ap.parse_args()

    # provinces/ carries `prov`; the US and CA-FED corpora do not, so key
    # them by file (P6: these three were previously never screened because the
    # glob stopped at provinces/).
    FILE_CH = {"us/segments_us_house.jsonl": "US-HOUSE",
               "us/segments_us_senate.jsonl": "US-SENATE",
               "ca/segments_ca2.jsonl": "CA-FED"}
    sources = [(p, None) for p in sorted(glob.glob(
        os.path.join(HERE, "provinces", "segments_*.jsonl")))]
    sources += [(os.path.join(HERE, rel), ch) for rel, ch in FILE_CH.items()]
    pool = defaultdict(lambda: defaultdict(list))
    for path, forced in sources:
        if not os.path.exists(path):
            continue
        for line in open(path):
            d = json.loads(line)
            t = d.get("text", "")
            if len(t.split()) >= args.min_words:
                pool[forced or d.get("prov")][d["date"][:4]].append(t)

    rows = []
    for pv in sorted(pool):
        for y in sorted(pool[pv]):
            ts = pool[pv][y]
            if len(ts) < 100:
                continue
            rng = random.Random(int(hashlib.sha1(
                f"{pv}{y}".encode()).hexdigest()[:8], 16))
            s = rng.sample(ts, min(args.per_cell, len(ts)))
            wps, ctr = [], []
            for t in s:
                w = t.split()
                ns = max(len([x for x in SENT.split(t) if x.strip()]), 1)
                wps.append(len(w) / ns)
                ctr.append(1000 * len(CONTR.findall(t)) / len(w))
            rows.append({"chamber": pv, "year": y, "n_pool": len(ts),
                         "n_sampled": len(s),
                         "words_per_sentence": round(statistics.mean(wps), 2),
                         "contractions_per_1k": round(statistics.mean(ctr), 2)})

    with open(os.path.join(HERE, "transcript_regime.csv"), "w",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    by = defaultdict(dict)
    for r in rows:
        by[r["chamber"]][r["year"]] = r

    print("FLAGGED CHAMBERS\n")
    for pv in sorted(by):
        ys = sorted(by[pv])
        pre = [by[pv][y] for y in ys if y <= PRE_MAX]
        post = [by[pv][y] for y in ys if y >= POST_MIN]
        if not pre or not post:
            continue
        for k, nm in (("contractions_per_1k", "contractions"),
                      ("words_per_sentence", "words/sentence")):
            a = statistics.mean(r[k] for r in pre)
            b = statistics.mean(r[k] for r in post)
            if a > 0 and abs(b - a) / a > 0.40:
                print(f"  {pv:<5s} {nm:<14s} pre {a:6.1f} -> post {b:6.1f} "
                      f"({(b - a) / a:+.0%})   REGIME CHANGE ACROSS THE WINDOWS")
        # step changes strictly inside the control window matter too: they
        # make measured specificity an average over two different text regimes
        prev = None
        for y in ys:
            if y > PRE_MAX:
                break
            cur = by[pv][y]["contractions_per_1k"]
            if prev is not None and prev > 0 and abs(cur - prev) / prev > 0.8:
                print(f"  {pv:<5s} contractions   {prev:6.1f} -> {cur:6.1f} "
                      f"at {y}   STEP INSIDE THE CONTROL WINDOW")
            prev = cur
    print("\nwrote transcript_regime.csv")


if __name__ == "__main__":
    main()
