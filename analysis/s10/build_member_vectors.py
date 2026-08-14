#!/usr/bin/env python3
"""Per-member style-word vectors, and the text of every scored segment.

ONE PASS, TWO OUTPUTS, because both need the same full read of the eight
provincial corpora and that read costs ~10 minutes:

  member_word_vectors.json
      For every named non-chair speaker: a style-word count vector and a
      total word count, split into pre (<= 2022) and post (>= 2023) eras.
      This is the raw material for every clustering question -- vectors are
      per MEMBER, not per class, so clusters can be found with no priors and
      then tested against class, education and cohort afterwards.

  scored_seg_texts.jsonl
      For every 2025-26 prevalence segment that Pangram scored in these
      provinces: prov, the corpus speaker key, and the text. This is what
      joins verdicts to members PROPERLY -- by seg_id, through the corpus --
      instead of by parsing "Mr. Nally" out of a verdict row, which matched
      only 243 of 840. It also provides the machine-flagged text itself for
      similarity analysis.

Usage: python build_member_vectors.py
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

VEC_OUT = os.path.join(HERE, "member_word_vectors.json")
SEG_OUT = os.path.join(HERE, "scored_seg_texts.jsonl")
CA = {"AB", "BC", "MB", "NL", "NS", "ON", "PE", "SK"}


def scored_ids():
    """seg_id -> verdict row, for CA-province prevalence segments."""
    want = {}
    for r in csv.DictReader(open(os.path.join(HERE,
                                              "pangram_p4_verdicts.csv"))):
        if r.get("stratum") != "prev":
            continue
        if (r.get("chamber") or "").upper() not in CA:
            continue
        want[r["seg_id"]] = {"verdict": r["pangram"],
                             "fraction_ai": r.get("fraction_ai") or "",
                             "file": r["file"]}
    p = os.path.join(HERE, "pangram_shortband_verdicts.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            if r.get("era") != "prev":
                continue
            if (r.get("chamber") or "").upper() not in CA:
                continue
            want[r["seg_id"]] = {"verdict": r["pangram"], "fraction_ai": "",
                                 "file": r["id"]}
    mb = os.path.join(HERE, "pangram_mb_redraw_verdicts.csv")
    if os.path.exists(mb):
        for r in csv.DictReader(open(mb)):
            if r.get("era") == "prev":
                want[r["seg_id"]] = {"verdict": r["pangram"], "fraction_ai": "",
                                     "file": r["id"]}
    return want


def main():
    style = sorted({r["word"].lower() for r in
                    csv.DictReader(open(os.path.join(
                        HERE, "kobak_excess_words.csv")))
                    if r["type"] == "style" and r["word"].isalpha()})
    sset = set(style)
    want = scored_ids()
    print(f"{len(want):,} scored prevalence seg_ids to capture; "
          f"{len(style)} style words")

    vec = defaultdict(lambda: {"pre": defaultdict(int), "post": defaultdict(int),
                               "pre_w": 0, "post_w": 0})
    caught = 0
    seg_f = open(SEG_OUT, "w")
    for path in sorted(glob.glob(os.path.join(HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            nm = FW.norm(d.get("speaker", ""))
            if not nm or FW.ROLE.match(nm):
                continue
            toks = FW.TOKEN_RE.findall(d["text"].lower())
            era = "pre" if d["date"][:4] <= "2022" else "post"
            v = vec[f"{d['prov']}|{nm}"]
            v[f"{era}_w"] += len(toks)
            ve = v[era]
            for t in toks:
                if t in sset:
                    ve[t] += 1
            sid = d.get("seg_id")
            if sid in want:
                caught += 1
                w = want[sid]
                seg_f.write(json.dumps({
                    "seg_id": sid, "prov": d["prov"], "speaker": nm,
                    "date": d["date"], "n_words": d.get("n_words"),
                    "verdict": w["verdict"], "fraction_ai": w["fraction_ai"],
                    "file": w["file"], "text": d["text"]}) + "\n")
    seg_f.close()
    json.dump({k: {"pre": dict(v["pre"]), "post": dict(v["post"]),
                   "pre_w": v["pre_w"], "post_w": v["post_w"]}
               for k, v in vec.items()},
              open(VEC_OUT, "w"))
    print(f"wrote {os.path.basename(VEC_OUT)}: {len(vec):,} speakers")
    print(f"wrote {os.path.basename(SEG_OUT)}: {caught:,} of {len(want):,} "
          f"scored segments found in the corpus")


if __name__ == "__main__":
    main()
