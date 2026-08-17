#!/usr/bin/env python3
"""Merge the missing-9 covariate collection into one file, from the JOURNAL.

WHY THE JOURNAL AND NOT AN AGENT'S SUMMARY

A merge agent lost 58% of the rows in the tier-1 round (2026-08-15). The
workflow journal records each agent's actual structured return, so extraction
is a script reading data, not a model summarising it. Standing practice since.

INPUTS
  covariates_missing9_part1.json   salvaged round-1 records (NSW complete, QLD
                                   partial) -- round 1 was killed by headless
                                   mode's 600s background-wait ceiling
  journal.jsonl from the round-2 workflow run directory (pass --journal, or
  copy it in first)

OUTPUT
  covariates_missing9.json         one record per (chamber, key, person), the
                                   same schema as covariates_tier1.json so the
                                   downstream join is identical

It also reports how many DISTINCT prior_occupation strings are new, because
those must go through the central occupation->EGP coding pass before the class
arm can use them: an occupation string with no class code is invisible to the
class regression, so collection alone does not buy power.

Usage: python extract_missing9.py [--journal PATH ...]
"""
import argparse
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def records_from_journal(path):
    out = []
    for line in open(path):
        try:
            o = json.loads(line)
        except Exception:
            continue
        r = o.get("result") or o.get("value") or {}
        if isinstance(r, dict) and r.get("records"):
            ch = r.get("chamber")
            for rec in r["records"]:
                rec.setdefault("chamber", ch)
                out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", nargs="*", default=[])
    ap.add_argument("--part1", default="covariates_missing9_part1.json")
    ap.add_argument("--out", default="covariates_missing9.json")
    a = ap.parse_args()

    recs = []
    p1 = os.path.join(HERE, a.part1)
    if os.path.exists(p1):
        recs += json.load(open(p1))
        print(f"round 1 (salvaged): {len(recs)} records")
    for j in a.journal:
        got = records_from_journal(j)
        print(f"{os.path.basename(os.path.dirname(j))}: {len(got)} records")
        recs += got

    # de-duplicate on (chamber, key, person_name); prefer the richer record
    def richness(r):
        return sum(1 for f in ("birth_year", "education_level",
                               "prior_occupation", "gender")
                   if r.get(f) and r.get(f) != "unknown")
    best = {}
    for r in recs:
        k = (r.get("chamber"), r.get("key"), r.get("person_name"))
        if k not in best or richness(r) > richness(best[k]):
            best[k] = r
    merged = list(best.values())

    by_ch = defaultdict(lambda: Counter())
    for r in merged:
        c = by_ch[r.get("chamber")]
        c["n"] += 1
        if r.get("birth_year"):
            c["birth"] += 1
        if r.get("education_level") and r["education_level"] != "unknown":
            c["edu"] += 1
        if r.get("prior_occupation"):
            c["occ"] += 1
        if r.get("ambiguous"):
            c["ambiguous"] += 1
    print(f"\n{'chamber':<7s} {'n':>5s} {'birth':>7s} {'edu':>7s} {'occ':>7s} "
          f"{'ambig':>6s}")
    tot = Counter()
    for ch in sorted(by_ch):
        c = by_ch[ch]
        tot.update(c)
        print(f"{ch:<7s} {c['n']:>5d} "
              f"{c['birth']:>6d}{'':1s} {c['edu']:>6d}{'':1s} "
              f"{c['occ']:>6d}{'':1s} {c['ambiguous']:>6d}")
    print(f"{'TOTAL':<7s} {tot['n']:>5d} {tot['birth']:>6d}  {tot['edu']:>6d}  "
          f"{tot['occ']:>6d}  {tot['ambiguous']:>6d}")
    if tot["n"]:
        print(f"        {'':5s} {100*tot['birth']/tot['n']:>5.0f}% "
              f"{100*tot['edu']/tot['n']:>6.0f}% {100*tot['occ']/tot['n']:>6.0f}%")

    out = os.path.join(HERE, a.out)
    json.dump(merged, open(out, "w"), indent=1)
    print(f"\nwrote {a.out} ({len(merged)} records)")

    # occupation strings needing a class code
    coded = set()
    for f in ("provinces/occupation_coding_v2.json",
              "provinces/occupation_coding.json"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            d = json.load(open(p))
            coded |= set(d.keys() if isinstance(d, dict) else
                         (r.get("string") for r in d))
    new = {(r.get("prior_occupation") or "").strip() for r in merged}
    new = {s for s in new if s and s not in coded}
    print(f"\nDISTINCT prior_occupation strings with no class code yet: "
          f"{len(new)}")
    print("  -> these must go through the occupation->EGP coding pass "
          "(workflows/occcode.js) before the class arm can use them")
    json.dump(sorted(new), open(os.path.join(HERE,
                                             "occupation_strings_missing9.json"),
                                "w"), indent=1)
    print("  wrote occupation_strings_missing9.json")


if __name__ == "__main__":
    main()
