#!/usr/bin/env python3
"""Build Pangram batches for the 16-chamber expansion + a genre-stratified arm.

TWO ARMS

A. CHAMBER EXPANSION — 16 chambers never seen by a detector: 8 Canadian
   provinces, 6 Australian states, 3 UK devolved legislatures (17 corpora;
   PE is dropped, its early window is too thin). Per chamber, the design
   already used for Ireland/Canada/UK so the numbers stay comparable:

     60  pre-2023 controls   -> per-chamber specificity, measured not assumed
     120 post-period draws   -> prevalence, uniform random, no screen
                                stratification, so it needs no weights

   Specificity is currently 423/423 across four chambers plus 2,400 pre-LLM
   segments in the Opus band screen with zero flags. That is strong, but it
   is not transferable: a chamber's false-positive rate depends on its own
   editorial register, so each new chamber buys its own control.

B. GENRE ARM (federal Canada only) — the one corpus carrying the business
   rubric. 60 segments in each of {Statements by Members (scripted),
   Oral Questions (unscripted), Government Orders (debate)} x {pre, post}.

   This tests with the DETECTOR what is currently only inferred from the
   lexicon: does machine drafting concentrate in scripted business? The
   lexicon says the register shift is larger in SO31 than in Oral Questions;
   if prevalence tracks that, the two instruments agree for once.

SAMPLING is uniform at random within each cell, seeded per cell, restricted
to 120-360 words (Pangram needs enough text; below ~120 words its verdicts
get noisy) and to member-authored English.

Output: one RTF per segment (Pangram's web upload rejects .txt), named so the
verdict can be joined back, plus a manifest. One file per segment because
batch uploads do not preserve per-file attribution.

Usage: python build_pangram_expansion.py [--per-control 60] [--per-prev 120]
"""
import argparse
import glob
import hashlib
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CH = os.path.join(HERE, "pangram_x")
OUT_GENRE = os.path.join(HERE, "pangram_genre")
WMIN, WMAX = 120, 361

# 4-letter codes keep filenames unambiguous when 20 chambers are in flight
CODES = {"AB": "cab", "BC": "cbc", "SK": "csk", "MB": "cmb", "ON": "con",
         "NS": "cns", "NL": "cnl",
         "NSW": "ans", "VIC": "avi", "QLD": "aql", "WA": "awa",
         "SA": "asa", "TAS": "ata",
         "SCO": "usc", "WAL": "uwa", "NI": "uni"}


INVISIBLE = dict.fromkeys(map(ord, "\u00ad\u200b\u200c\u200d\ufeff"), None)


def clean(t):
    """Remove invisible characters. Manitoba's 2025-26 files carry soft
    hyphens in 81.6% of segments against 0.04% of tokens in 2006-19; left in,
    that is period-correlated noise a detector could latch onto."""
    return " ".join(t.translate(INVISIBLE).split())


def rtf(t):
    t = clean(t)
    t = t.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
    t = "".join(c if ord(c) < 128 else f"\\u{ord(c)}?" for c in t)
    return "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Times New Roman;}}\\fs24 " + t + "}"


# 2022-06-30, not 2022-12-31: ChatGPT shipped 2022-11-30, and a
# "pre-AI" control dated December 2022 is not pre-AI. Costs nothing
# — every chamber has ample earlier material.
def era_of(date, pre_max="2022-06-30", post_min="2025-01-01"):
    if date <= pre_max:
        return "ctl"
    if date >= post_min:
        return "prev"
    return None


# Transcription-regime floors, from transcript_regime_check.py.
# These chambers changed how the record is produced DURING the control
# window: contraction density steps 3.2->28.6 (NL, 2016), 7.9->25.0
# (WAL, 2015), 5.0->21.2 (MB, 2007). Traditional Hansard expands "don't"
# to "do not"; verbatim/ASR-first transcription does not. Controls drawn
# across such a step measure false positives on a text regime that no
# longer exists. Floor them to the current regime — still pre-AI, so the
# control loses nothing that matters.
#
# Tasmania is NOT here on purpose: its step (3.4 -> 15.9) falls BETWEEN
# the control and prevalence windows, so no pre-AI text exists in the
# 2025-26 regime and no choice of floor fixes it. Flagged, not patched.
REGIME_FLOOR = {"NL": "2016-01-01", "WAL": "2015-01-01", "MB": "2007-01-01"}
REGIME_FLAG = {"TAS": "contraction density +364% across the windows; "
                      "prevalence not separable from a transcription change"}


def usable(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5
            and WMIN <= d["n_words"] < WMAX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-control", type=int, default=60)
    ap.add_argument("--per-prev", type=int, default=120)
    ap.add_argument("--per-genre-cell", type=int, default=60)
    args = ap.parse_args()

    # ---------------- ARM A: 16 chambers ----------------
    os.makedirs(OUT_CH, exist_ok=True)
    man = {}
    words = 0
    print("ARM A — chamber expansion")
    print(f"  {'chamber':<8s} {'ctl pool':>9s} {'prev pool':>10s} {'built':>7s}")
    by_prov = {}
    for path in sorted(glob.glob(os.path.join(HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not usable(d):
                continue
            pv = d.get("prov")
            if pv not in CODES:
                continue
            e = era_of(d["date"])
            if e == "ctl" and d["date"] < REGIME_FLOOR.get(pv, ""):
                continue
            if e:
                by_prov.setdefault(pv, {"ctl": [], "prev": []})[e].append(d)
    for prov in sorted(by_prov):
        pools = by_prov[prov]
        if len(pools["ctl"]) < 200 or len(pools["prev"]) < 300:
            print(f"  {prov:<8s} SKIPPED — pools too thin "
                  f"({len(pools['ctl'])}/{len(pools['prev'])})")
            continue
        code = CODES[prov]
        n = 0
        for stratum, want in (("ctl", args.per_control), ("prev", args.per_prev)):
            rng = random.Random(int(hashlib.sha1(
                f"{prov}{stratum}x".encode()).hexdigest()[:8], 16))
            for i, d in enumerate(rng.sample(pools[stratum], want)):
                name = f"{code}{stratum}{i:03d}"
                open(os.path.join(OUT_CH, name + ".rtf"), "w").write(rtf(d["text"]))
                man[name] = {"chamber": prov, "code": code, "stratum": stratum,
                             "arm": "chamber", "seg_id": d["seg_id"],
                             "src_file": d.get("file", ""),
                             "date": d["date"], "speaker": d.get("speaker", ""),
                             "n_words": d["n_words"],
                             "regime_flag": REGIME_FLAG.get(prov, "")}
                words += d["n_words"]
                n += 1
        print(f"  {prov:<8s} {len(pools['ctl']):>9,} {len(pools['prev']):>10,} "
              f"{n:>7d}")
    json.dump(man, open(os.path.join(HERE, "pangram_x_manifest.json"), "w"), indent=0)

    # ---------------- ARM A2: US Congress (already holds 2025-26) ----------------
    # The US corpora were built as a COMPLETE record rather than to the drift
    # windows, so unlike the 16 provincial/state chambers they already cover
    # the current period and need no fetching.
    for src, prov, code in ((os.path.join(HERE, "us", "segments_us_house.jsonl"),
                             "US-HOUSE", "ush"),
                            (os.path.join(HERE, "us", "segments_us_senate.jsonl"),
                             "US-SENATE", "uss")):
        if not os.path.exists(src):
            continue
        pools = {"ctl": [], "prev": []}
        for line in open(src):
            d = json.loads(line)
            if not usable(d):
                continue
            e = era_of(d["date"])
            if e:
                pools[e].append(d)
        if len(pools["ctl"]) < 200 or len(pools["prev"]) < 300:
            print(f"  {prov:<8s} SKIPPED ({len(pools['ctl'])}/{len(pools['prev'])})")
            continue
        n = 0
        for stratum, want in (("ctl", args.per_control), ("prev", args.per_prev)):
            rng = random.Random(int(hashlib.sha1(
                f"{prov}{stratum}x".encode()).hexdigest()[:8], 16))
            for i, d in enumerate(rng.sample(pools[stratum], want)):
                name = f"{code}{stratum}{i:03d}"
                open(os.path.join(OUT_CH, name + ".rtf"), "w").write(rtf(d["text"]))
                man[name] = {"chamber": prov, "code": code, "stratum": stratum,
                             "arm": "chamber", "seg_id": d["seg_id"],
                             "date": d["date"], "speaker": d.get("speaker", ""),
                             "n_words": d["n_words"]}
                words += d["n_words"]
                n += 1
        print(f"  {prov:<8s} {len(pools['ctl']):>9,} {len(pools['prev']):>10,} "
              f"{n:>7d}")
    json.dump(man, open(os.path.join(HERE, "pangram_x_manifest.json"), "w"), indent=0)

    # ---------------- ARM B: genre, federal Canada ----------------
    os.makedirs(OUT_GENRE, exist_ok=True)
    gman = {}
    gwords = 0
    src = os.path.join(HERE, "ca", "segments_ca2.jsonl")
    if os.path.exists(src):
        cells = {}
        for line in open(src):
            d = json.loads(line)
            if not usable(d):
                continue
            e = era_of(d["date"])
            if not e:
                continue
            o = (d.get("order") or "").lower()
            g = ("SO31" if "statements by members" in o else
                 "OQ" if "oral questions" in o else
                 "DEBATE" if "government orders" in o else None)
            if g:
                cells.setdefault((g, e), []).append(d)
        print("\nARM B — genre stratification (federal Canada)")
        print(f"  {'cell':<14s} {'pool':>8s} {'built':>7s}")
        for (g, e), pool in sorted(cells.items()):
            want = min(args.per_genre_cell, len(pool))
            rng = random.Random(int(hashlib.sha1(
                f"{g}{e}gx".encode()).hexdigest()[:8], 16))
            for i, d in enumerate(rng.sample(pool, want)):
                name = f"g{g[:2].lower()}{e[:1]}{i:03d}"
                open(os.path.join(OUT_GENRE, name + ".rtf"), "w").write(rtf(d["text"]))
                gman[name] = {"chamber": "CA-FED", "code": f"g{g[:2].lower()}",
                              "stratum": e, "arm": "genre", "genre": g,
                              "seg_id": d["seg_id"], "date": d["date"],
                              "speaker": d.get("speaker", ""),
                              "n_words": d["n_words"]}
                gwords += d["n_words"]
            print(f"  {g + '/' + e:<14s} {len(pool):>8,} {want:>7d}")
        json.dump(gman, open(os.path.join(HERE, "pangram_genre_manifest.json"), "w"),
                  indent=0)

    print(f"\nARM A: {len(man):>5,} files, {words:>9,} words  "
          f"~= {words // 100:>6,} credits")
    print(f"ARM B: {len(gman):>5,} files, {gwords:>9,} words  "
          f"~= {gwords // 100:>6,} credits")
    print(f"TOTAL: {len(man) + len(gman):>5,} files, {words + gwords:>9,} words "
          f" ~= {(words + gwords) // 100:>6,} credits "
          f"({(words + gwords) / 1.5e6:.0%} of a 1.5M-word month)")


if __name__ == "__main__":
    main()
