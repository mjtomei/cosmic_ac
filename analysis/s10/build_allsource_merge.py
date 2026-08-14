#!/usr/bin/env python3
"""Merge the per-member all-source search into one provenance-keeping file.

WHY THIS IS A SCRIPT AND NOT AN AGENT

The 24 search agents returned 1,396 member records. The merge agent that first
consolidated them wrote 584 -- it transcribed the payload by hand and lost 58%
of the rows, including two thirds of the parental occupations, which are the
scarcest and most expensive field in the whole collection. Its own note said
so ("transcription was manual ... treat the count as the merged set rather than
a guaranteed-exhaustive census"), which is the only reason the loss was caught
rather than absorbed.

The lesson is narrow and worth stating plainly: agents are the right tool for
judgement over text and the wrong tool for transcribing a large payload
verbatim. Anything that is a pure function of structured data belongs in code,
where it is exact, re-runnable and diffable. The coding of occupation strings
stays with agents; the copying of their output does not.

Source of truth is the workflow journal, which records each agent's full
structured return, not the summary that reached the orchestrator.

WHAT THE MERGE ENFORCES

  EVIDENCE OR IT DID NOT HAPPEN. A field survives only if some entry in that
  record's `evidence` array names it. This is what makes the file
  re-analysable by source tier: every surviving value can be attributed, so an
  analysis can be re-run on official-only, or with wikipedia-tier evidence
  dropped, without recollecting anything.

  QUOTES ARE KEPT. The first merge discarded them "to keep the merge
  tractable". They are the only way to spot-check a claim without re-fetching
  the page, and tractability is not a concern for a script.

  DEDUPLICATION ON (prov, name), keeping the record with more evidence.
  Near-collisions that look like duplicates are NOT merged -- "john o'toole"
  and "john o’toole" differ only by apostrophe, and MB's "helwer" and
  "reg helwer" are separate Hansard speaker keys. Both are real register keys
  and both must survive, or the join drops speech.

  NOTHING IS WRITTEN TO member_bios.json. This file is deliberately parallel
  so official-only and all-source analyses can be compared. Overwriting the
  official collection would destroy the comparison the pass exists to enable.

Usage:
  python build_allsource_merge.py --journal <path> [--out provinces/member_allsource.json]
"""
import argparse
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "provinces", "member_allsource.json")

# Fields that must be named by an evidence entry to survive. `name` and `prov`
# are identity, not claims, and are exempt.
EVIDENCED = ["birth_year", "education_level", "education_field", "alma_maters",
             "prior_occupation", "occupation_category", "father_occupation",
             "mother_occupation", "wikipedia_article_chars",
             "wikipedia_article_exists", "matched_name"]


def load_journal(path):
    recs = []
    for line in open(path):
        d = json.loads(line)
        if d.get("type") != "result":
            continue
        r = d.get("result")
        if isinstance(r, dict) and isinstance(r.get("records"), list):
            recs.extend(r["records"])
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", required=True)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()

    raw = load_journal(a.journal)
    print(f"{len(raw)} records read from the journal\n")

    dropped = Counter()
    by_key = {}
    for r in raw:
        nm, pv = r.get("name"), r.get("prov")
        if not nm or not pv:
            dropped["no identity"] += 1
            continue
        ev = r.get("evidence") or []
        named = {e.get("field") for e in ev if isinstance(e, dict)}
        out = {"name": nm, "prov": pv, "evidence": ev}
        for f in EVIDENCED:
            v = r.get(f)
            if v in (None, "", [], "unknown"):
                continue
            if f in named:
                out[f] = v
            else:
                dropped[f] += 1
        # A wikipedia-tier evidence URL is the reliable signal that an article
        # exists; the agents rarely carried the boolean as its own evidence
        # entry, and WP:NPOL makes near-universal existence uninformative
        # anyway. Article DEPTH is the notability instrument, not existence.
        out["has_wikipedia_evidence"] = any(
            e.get("tier") == "wikipedia" for e in ev if isinstance(e, dict))
        out["evidence_tiers"] = sorted(
            {e.get("tier") for e in ev if isinstance(e, dict) and e.get("tier")})

        k = (pv, nm)
        if k in by_key and len(by_key[k].get("evidence") or []) >= len(ev):
            dropped["duplicate"] += 1
            continue
        if k in by_key:
            dropped["duplicate"] += 1
        by_key[k] = out

    recs = sorted(by_key.values(), key=lambda x: (x["prov"], x["name"]))
    json.dump(recs, open(a.out, "w"), indent=1)

    def has(f):
        return sum(1 for r in recs if r.get(f))
    print(f"  merged            {len(recs):>5}")
    print(f"  education_level   {has('education_level'):>5}")
    print(f"  birth_year        {has('birth_year'):>5}")
    print(f"  occupation        {has('prior_occupation'):>5}")
    print(f"  father_occupation {has('father_occupation'):>5}")
    print(f"  mother_occupation {has('mother_occupation'):>5}")
    print(f"  any parental      "
          f"{sum(1 for r in recs if r.get('father_occupation') or r.get('mother_occupation')):>5}")

    print(f"\n  dropped for lacking an evidence entry:")
    for k, v in dropped.most_common():
        print(f"    {k:<26}{v:>5}")

    tiers = Counter()
    for r in recs:
        for e in r["evidence"]:
            if isinstance(e, dict) and e.get("tier"):
                tiers[e["tier"]] += 1
    print(f"\n  evidence entries by tier ({sum(tiers.values())} total):")
    for k, v in tiers.most_common():
        print(f"    {k:<12}{v:>6}  {100*v/sum(tiers.values()):>5.1f}%")

    # The notability-sensitivity subset: how much survives if wikipedia-tier
    # evidence is discarded. If that number is small, an education analysis on
    # this file IS a notability analysis, and saying so is the point of
    # carrying tiers at all.
    edu = [r for r in recs if r.get("education_level")]
    nonwiki = [r for r in edu if any(
        e.get("field") == "education_level" and e.get("tier") != "wikipedia"
        for e in r["evidence"] if isinstance(e, dict))]
    print(f"\n  education_level from a NON-wikipedia source: "
          f"{len(nonwiki)} of {len(edu)} "
          f"({100*len(nonwiki)/max(len(edu),1):.0f}%)")

    prov = Counter(r["prov"] for r in recs)
    print(f"\n  by province: " + "  ".join(f"{k} {v}" for k, v in sorted(prov.items())))
    print(f"\nwrote {os.path.relpath(a.out, HERE)}")


if __name__ == "__main__":
    main()
