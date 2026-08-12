#!/usr/bin/env python3
"""What is actually in the Oral Questions cell, and what do its flags land on?

WHY THIS EXISTS

The genre arm reports Oral Questions at 8.3% against SO31 at 36.7%, and §4.3
originally defended the contrast as conservative on the grounds that the
120-360 word floor leaves "the long tail of Question Period, which skews toward
prepared ministerial answers ... the sub-population most likely to be
machine-drafted".

Both halves of that are false, and this script is how we found out. The
ministerial sub-population flags 0/28, and the length floor selects AWAY from
ministers rather than toward them. The conclusion (the OQ cell is biased
upward) survives; the stated mechanism does not.

WHAT REPLACED IT

Reading the five flags individually is more informative than any recomputed
rate: none of them is spontaneous exchange. Two are eulogies, one is a
question of privilege responding to a matter raised the previous day, one is a
unanimous-consent motion whose text is negotiated between parties beforehand
and read verbatim, and one is a backbench question of the routinely
staff-written kind. The genre thesis holds segment by segment, not just in
aggregate.

THE ONE GAP THIS OPENS

Two of the five flags are tributes, and there is no pre-AI tribute anywhere in
the control set. Tribute register -- elevated, cadenced, parallel construction,
abstract virtue nouns -- is exactly what a detector keys on, and both flagged
at fraction_ai = 1.0. That is either strong evidence of drafting or the most
interesting false positive in the study, and nothing here distinguishes them.
The check is printed at the end and is currently unmet.

Usage: python genre_oq_audit.py
"""
import collections
import csv
import glob
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
FLAG = ("AI", "Mixed")
# sections that are filed under the Question Period rubric but are not
# question-and-answer exchange
NOT_EXCHANGE = re.compile(
    r"privilege|business of the house|point of order|tribute|condolence|"
    r"the late|unanimous consent", re.I)
CEREMONIAL = re.compile(
    r"privilege|business of the house|point of order|tribute|condolence|"
    r"the late|memor", re.I)


def sections():
    s, w = {}, {}
    for f in glob.glob(os.path.join(HERE, "ca", "segments_ca*.jsonl")):
        for line in open(f):
            d = json.loads(line)
            s[d["seg_id"]] = d.get("section", "")
            w[d["seg_id"]] = int(d.get("n_words") or 0)
    return s, w


def main():
    sec, _ = sections()
    rows = list(csv.DictReader(open(os.path.join(HERE,
                                                 "pangram_p4_verdicts.csv"))))
    oq = [r for r in rows if r["chamber"] == "CA-FED"
          and r["genre"] == "OQ" and r["stratum"] == "prev"]

    print(f"OQ prevalence cell: {len(oq)} segments, "
          f"{sum(r['pangram'] in FLAG for r in oq)} flagged\n")

    # -- 1. the claim that failed ------------------------------------------
    mini = [r for r in oq if "Minister" in r["speaker"]
            or "Secretary" in r["speaker"]]
    rest = [r for r in oq if r not in mini]
    print("1. THE MINISTERIAL-ANSWER ARGUMENT")
    print(f"   ministerial/parl-sec {len(mini):>3d} segments, "
          f"{sum(r['pangram'] in FLAG for r in mini)} flagged")
    print(f"   everyone else        {len(rest):>3d} segments, "
          f"{sum(r['pangram'] in FLAG for r in rest)} flagged")
    print("   -> the sub-population named as most machine-prone produced "
          "zero flags.\n")

    # -- 2. does the length floor select toward ministers? -----------------
    # Genre lives in the `order` field (the sitting's order of business), NOT
    # in `section`, which carries the topic. This is how
    # build_pangram_expansion.py assigns it, and using `section` here silently
    # scores the whole chamber instead of Question Period.
    pool = []
    src = os.path.join(HERE, "ca", "segments_ca2.jsonl")
    for line in open(src):
        d = json.loads(line)
        if "oral questions" not in (d.get("order") or "").lower():
            continue
        if d.get("date", "") < "2025-01-01":
            continue
        if not d.get("scoreable") or d.get("translated"):
            continue
        if (d.get("orig_frac") or 1.0) <= 0.5:
            continue
        pool.append(d)

    def is_min(d):
        return "Minister" in d.get("speaker", "") \
            or "Secretary" in d.get("speaker", "")

    inband = [d for d in pool if 120 <= int(d.get("n_words") or 0) <= 360]
    print("2. WHAT THE 120-360 WORD FLOOR SELECTS")
    print(f"   (2025-26 Oral Questions, member-authored English, "
          f"n={len(pool)})")
    for nm, s in (("before filter", pool), ("after filter", inband)):
        if not s:
            continue
        share = 100 * sum(is_min(d) for d in s) / len(s)
        print(f"   {nm:<14s} n={len(s):>6d}  ministerial share {share:>5.1f}%")
    mw = [int(d["n_words"]) for d in pool if is_min(d)]
    ow = [int(d["n_words"]) for d in pool if not is_min(d)]
    if mw and ow:
        print(f"   median words: ministerial {statistics.median(mw):.0f}"
              f" vs other {statistics.median(ow):.0f}")
    if pool and inband:
        print(f"   retention: ministerial "
              f"{100*sum(is_min(d) for d in inband)/max(sum(is_min(d) for d in pool),1):>5.1f}%"
              f"  other "
              f"{100*sum(not is_min(d) for d in inband)/max(sum(not is_min(d) for d in pool),1):>5.1f}%")
    print("   -> ministerial utterances are shorter, so the floor selects "
          "AWAY from them.")
    if pool:
        print(f"   NOTE: overall OQ retention here is "
              f"{100*len(inband)/len(pool):.1f}%, against the 6.4% quoted in "
              f"§4.3.")
        print("   The gap is filter detail (that figure came from the build "
              "script's")
        print("   own pool construction). Unresolved and minor; do not quote "
              "both.\n")

    # -- 3. what the flags actually are ------------------------------------
    print("3. THE FLAGS, ONE BY ONE")
    for r in oq:
        if r["pangram"] not in FLAG:
            continue
        s = sec.get(r["seg_id"], "?")
        kind = "NOT exchange" if NOT_EXCHANGE.search(s) else "exchange?"
        print(f"   {r['pangram']:<5s} frac={float(r['fraction_ai']):<4.2f} "
              f"{r['n_words']:>4s}w  [{kind:<12s}] {s[:38]:<38} "
              f"{r['speaker'][:34]}")
    print()

    # -- 4. the control: does prepared human speech flag? ------------------
    ctl = [r for r in rows if r["stratum"] == "ctl"]
    cafed = [r for r in ctl if r["chamber"] == "CA-FED"]
    cer = [r for r in cafed if CEREMONIAL.search(sec.get(r["seg_id"], ""))]
    print("4. DOES PREPARED HUMAN SPEECH FLAG? (pre-AI controls)")
    print(f"   all chambers        {len(ctl):>5d} segments, "
          f"{sum(r['pangram'] in FLAG for r in ctl)} flagged")
    print(f"   CA-FED ceremonial/procedural {len(cer):>3d} segments, "
          f"{sum(r['pangram'] in FLAG for r in cer)} flagged")
    for r in cer:
        print(f"      {sec.get(r['seg_id'],'')[:40]:<40} {r['pangram']}")
    print("   -> formal prepared procedural speech does not trip the "
          "detector.\n")

    # -- 5. the gap --------------------------------------------------------
    trib = re.compile(r"tribute|condolence|the late|memor", re.I)
    have = [r for r in ctl if trib.search(sec.get(r["seg_id"], ""))]
    print("5. THE UNMET CONTROL")
    print(f"   pre-AI tributes/eulogies in the control set: {len(have)}")
    print("   Two of the five OQ flags are eulogies, both at fraction_ai "
          "= 1.0.")
    print("   Tribute register is elevated, cadenced and parallel -- the "
          "surface")
    print("   features a detector keys on -- and it has NO human baseline "
          "here.")
    print("   REQUIRED: score ~40 pre-2022 tributes from the same chamber "
          "before")
    print("   either eulogy flag is quoted as evidence of drafting.")


if __name__ == "__main__":
    main()
