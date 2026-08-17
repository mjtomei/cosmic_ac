#!/usr/bin/env python3
"""Speaker rosters for the tier-1 covariate expansion.

WHY ROSTERS COME FROM THE CORPUS AND NOT FROM A MEMBER LIST

The BC/SK/NL lesson (2026-08-13): a covariate file keyed on anything other
than the corpus's own speaker keys silently fails its join — BC matched 15%
of members until the file's own hansard_speaker_key was used. So the roster
each collection agent receives IS the join key set: FW.norm() of the corpus
speaker field, the same normalisation every downstream analysis uses.

WHY KEYS CARRY YEAR SPANS

US Congressional Record speakers are bare surnames ("Mr. SMITH", sometimes
"Mr. SMITH of Texas"). Over a 1994-2026 corpus one key can be several people
— different Smiths in different Congresses. Agents therefore return one
record PER PERSON per key, each with term years, and member-years are
assigned key+year -> person at analysis time. The roster's per-key first/last
years and per-year word counts are what lets an agent see that "smith" spans
1994-2026 and needs splitting.

ROLE-prefixed speakers (ministers speaking under office titles, chairs) are
excluded by the same ROLE regex the analyses use. This undercounts UK
frontbench speech under its office wrapper; consistent with every other arm.

Usage: python build_rosters.py          # writes rosters/{chamber}.json
"""
import glob
import json
import re
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

OUT = os.path.join(HERE, "rosters")
MIN_WORDS = 8000
CORPORA = {
    "US-HOUSE": ["us/segments_us_house.jsonl"],
    "US-SENATE": ["us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl", "uk/segments_uk_2023.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
    # The nine chambers with no member covariates at all (2026-08-17). They
    # were skipped in the first collection round; the class and education
    # arms are now power-bound, so they are worth buying. Each chamber's
    # files include its _fill and _2025 supplements.
    "NSW": ["provinces/segments_aus_nsw.jsonl",
            "provinces/segments_aus_nsw_fill.jsonl",
            "provinces/segments_aus_nsw_2025.jsonl"],
    "QLD": ["provinces/segments_aus_qld.jsonl",
            "provinces/segments_aus_qld_fill.jsonl",
            "provinces/segments_aus_qld_2025.jsonl"],
    "SA": ["provinces/segments_aus_sa.jsonl",
           "provinces/segments_aus_sa_fill.jsonl",
           "provinces/segments_aus_sa_2025.jsonl"],
    "TAS": ["provinces/segments_aus_tas.jsonl",
            "provinces/segments_aus_tas_fill.jsonl",
            "provinces/segments_aus_tas_2025.jsonl"],
    "VIC": ["provinces/segments_aus_vic.jsonl",
            "provinces/segments_aus_vic_fill.jsonl",
            "provinces/segments_aus_vic_2025.jsonl"],
    "WA": ["provinces/segments_aus_wa.jsonl",
           "provinces/segments_aus_wa_fill.jsonl",
           "provinces/segments_aus_wa_2025.jsonl"],
    "NI": ["provinces/segments_ni.jsonl", "provinces/segments_ni_fill.jsonl",
           "provinces/segments_ni_fill2.jsonl",
           "provinces/segments_ni_2025.jsonl"],
    "SCO": ["provinces/segments_scot.jsonl",
            "provinces/segments_scot_fill.jsonl",
            "provinces/segments_scot_2025.jsonl"],
    "WAL": ["provinces/segments_wales.jsonl",
            "provinces/segments_wales_fill.jsonl",
            "provinces/segments_wales_2025.jsonl"],
}


STOP_RE = re.compile(
    r"\b(the|and|for|with|that|this|our|was|were|has|have|will|not|from|"
    r"they|there|would|about|which|when|what|there's)\b")


def plausible_name(nm):
    """Does this speaker key look like a person?

    Some chambers' extractors leak sentence fragments into the speaker field
    (NSW: "a journey in time"; Wales: "all-wales convention reached two key
    conclusions"). Sending those to a collection agent buys nothing, so they
    are dropped from the roster rather than paid for. Initial forms are kept
    -- "a.d. buti" is Tony Buti, a real member, and several Australian
    chambers print members that way.
    """
    s = (nm or "").strip()
    if not s or len(s) > 40:
        return False
    if re.search(r"[!?;:,]", s) or STOP_RE.search(s):
        return False
    if not re.fullmatch(r"[a-zà-ÿ'’\-\. ]+", s):
        return False
    toks = s.split()
    if not 1 <= len(toks) <= 4:
        return False
    return all("." not in t or re.fullmatch(r"(?:[a-z]\.){1,3}", t)
               for t in toks)


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])          # optional chamber filter; all if empty
    for ch, files in CORPORA.items():
        if only and ch not in only:
            continue
        agg = defaultdict(lambda: defaultdict(int))
        for rel in files:
            p = os.path.join(HERE, rel)
            if not os.path.exists(p):
                print(f"  {ch}: MISSING {rel}")
                continue
            for line in open(p):
                d = json.loads(line)
                if not d.get("scoreable", True):
                    continue
                nm = FW.norm(d.get("speaker", ""))
                if not nm or FW.ROLE.match(nm):
                    continue
                agg[nm][d["date"][:4]] += d.get("n_words") or 0
        roster, junk = [], 0
        for nm, yrs in agg.items():
            tot = sum(yrs.values())
            if tot < MIN_WORDS:
                continue
            if not plausible_name(nm):
                junk += 1
                continue
            roster.append({"key": nm, "words": tot,
                           "first": min(yrs), "last": max(yrs),
                           "by_year": dict(sorted(yrs.items()))})
        roster.sort(key=lambda r: -r["words"])
        json.dump(roster, open(os.path.join(OUT, f"{ch}.json"), "w"), indent=0)
        print(f"  {ch}: {len(roster)} speakers >= {MIN_WORDS:,} words "
              f"({sum(r['words'] for r in roster)/1e6:.0f}M words covered)"
              + (f", {junk} non-name keys dropped" if junk else ""))


if __name__ == "__main__":
    main()
