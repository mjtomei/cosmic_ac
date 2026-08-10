#!/usr/bin/env python3
"""Stage 2: cross-chamber quality pool, built from Pangram verdicts.

RUN THIS AFTER the Pangram expansion batches come back.

WHAT STAGE 2 ADDS, AND WHAT IT CANNOT

Stage 1 (pool.json) grades 840 federal-Canadian segments balanced across
genre and era. It is the only arm that can settle the genre confound, because
federal Canada is the only corpus carrying a business rubric
(OrderOfBusinessTitle). The US Congressional Record's section field turned out
to be bill-text fragments and vote tallies rather than business types (197
usable genre markers in 28,002 segments), and the sixteen provincial,
Australian and UK-devolved corpora were extracted with the core schema only.

So stage 2 does the other thing worth doing: an AI-versus-human quality
comparison at scale, with Pangram verdicts as the label rather than an LLM
screen, across every chamber that has verdicts. It adds a fourth country,
the US House/Senate institutional contrast, and enough AI-labelled segments
to make the comparison stop being underpowered — the existing unbiased
comparison rests on 8 AI segments against 82 human.

It does NOT control genre. Read stage 1 for that.

SELECTION MATCHING IS THE DESIGN POINT

AI-verdict and Human-verdict segments are drawn from the SAME uniformly
sampled prevalence stratum, so they passed identical selection filters.
Comparing a screen-selected AI tail against random human text would measure
selection, not AI status — which is why the New Brunswick tail adjudication
(576 confirmed AI, the richest source of AI-labelled text we have) is
deliberately NOT used here.

Every AI-verdict segment in the prevalence strata is taken, plus an equal
number of Human-verdict segments drawn from the same chamber and stratum.
Mixed verdicts are kept as their own class rather than folded either way.

Usage: python build_stage2.py
Then:  Workflow({ scriptPath: ".../grade_workflow.js" }) with POOL pointed at
       pool2.json and N set to the printed count (the script tells you both).
"""
import csv
import glob
import hashlib
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
S10 = os.path.dirname(HERE)
MANIFESTS = ["pangram_ch_manifest.json", "pangram_ch2_manifest.json",
             "pangram_x_manifest.json", "pangram_genre_manifest.json"]
# pangram_p4_verdicts.csv is the 2026-08-09 expansion: 4,258 verdicts on
# Pangram 4 across 19 chambers. It carries its own metadata columns, so it
# needs no manifest join; entries are synthesised below.
VERDICTS = ["pangram_ch_verdicts.csv", "pangram_p4_verdicts.csv"]
SEG_GLOBS = ["provinces/segments_*.jsonl", "ca/segments_ca2.jsonl",
             "us/segments_us_house.jsonl", "us/segments_us_senate.jsonl",
             "ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl"]


def main():
    man, selfman = {}, {}
    for mf in MANIFESTS:
        p = os.path.join(S10, mf)
        if os.path.exists(p):
            man.update(json.load(open(p)))
    verd = {}
    for vf in VERDICTS:
        p = os.path.join(S10, vf)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p)):
            v = (r.get("pangram") or r.get("prediction") or "").strip()
            if not v:
                continue
            verd[r["file"]] = v
            if r.get("chamber") and r.get("seg_id"):
                selfman[r["file"]] = {
                    "chamber": r["chamber"], "stratum": r["stratum"],
                    "seg_id": r["seg_id"], "date": r.get("date", ""),
                    "speaker": r.get("speaker", ""),
                    "n_words": int(r["n_words"] or 0),
                    "genre": r.get("genre") or None}
    if not verd:
        raise SystemExit("no verdicts yet — run the Pangram batches first")

    # keep only prevalence strata: uniform random, so AI and Human verdicts
    # inside them are selection-matched by construction
    man.update(selfman)
    rows = []
    for name, v in verd.items():
        m = man.get(name)
        if not m or m.get("stratum") not in ("prev",):
            continue
        rows.append({"file": name, "verdict": v, **m})
    if not rows:
        raise SystemExit("no prevalence-stratum verdicts found")

    by_ch = {}
    for r in rows:
        by_ch.setdefault(r["chamber"], []).append(r)

    print(f"{'chamber':<12s} {'n':>5s} {'AI':>4s} {'Mixed':>6s} {'Human':>6s} "
          f"{'-> sampled':>11s}")
    picked = []
    for ch in sorted(by_ch):
        rs = by_ch[ch]
        ai = [r for r in rs if r["verdict"] == "AI"]
        mx = [r for r in rs if r["verdict"] == "Mixed"]
        hu = [r for r in rs if r["verdict"] == "Human"]
        rng = random.Random(int(hashlib.sha1(
            (ch + "s2").encode()).hexdigest()[:8], 16))
        want = len(ai) + len(mx)
        keep = ai + mx + rng.sample(hu, min(want, len(hu)))
        picked += keep
        print(f"{ch:<12s} {len(rs):>5d} {len(ai):>4d} {len(mx):>6d} "
              f"{len(hu):>6d} {len(keep):>11d}")

    if len(picked) < 60:
        print(f"\nonly {len(picked)} segments — too few AI verdicts for a "
              f"quality comparison; wait for more chambers")

    # recover the text by seg_id
    want_ids = {r["seg_id"] for r in picked}
    text = {}
    for g in SEG_GLOBS:
        for path in glob.glob(os.path.join(S10, g)):
            for line in open(path):
                d = json.loads(line)
                if d.get("seg_id") in want_ids:
                    text[d["seg_id"]] = d["text"]
    missing = [r for r in picked if r["seg_id"] not in text]
    if missing:
        print(f"\n{len(missing)} segments could not be matched back to text "
              f"(seg_id drift between extraction runs) — dropped")
    picked = [r for r in picked if r["seg_id"] in text]

    random.Random(20260809).shuffle(picked)
    pool, key = {}, {}
    for i, r in enumerate(picked):
        sid = "R" + str(i).zfill(4)
        pool[sid] = text[r["seg_id"]]
        key[sid] = {"chamber": r["chamber"], "verdict": r["verdict"],
                    "date": r["date"], "speaker": r.get("speaker", ""),
                    "n_words": r["n_words"], "seg_id": r["seg_id"],
                    "genre": r.get("genre")}
    json.dump(pool, open(os.path.join(HERE, "pool2.json"), "w"),
              ensure_ascii=False)
    json.dump(key, open(os.path.join(HERE, "key2.json"), "w"), indent=1)
    nai = sum(1 for v in key.values() if v["verdict"] == "AI")
    print(f"\nwrote pool2.json: {len(pool)} segments "
          f"({nai} AI, {sum(1 for v in key.values() if v['verdict']=='Mixed')} "
          f"Mixed, {sum(1 for v in key.values() if v['verdict']=='Human')} Human) "
          f"across {len({v['chamber'] for v in key.values()})} chambers")
    print(f"\nTo grade: edit grade_workflow.js — set")
    print(f"  const POOL = '{os.path.join(HERE, 'pool2.json')}'")
    print(f"  const N = {len(pool)}")
    print(f"  and change the id prefix from 'Q' to 'R'")
    print(f"Then analyze with: python analyze.py --key key2.json")


if __name__ == "__main__":
    main()
