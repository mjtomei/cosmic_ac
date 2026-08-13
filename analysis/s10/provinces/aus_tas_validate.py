#!/usr/bin/env python3
"""Validation report for the Tasmanian segment file (adapted from validate.py).

Reads segments_aus_tas.jsonl + aus_tas_raw/, writes aus_tas_validation.txt:
  - segments and words per year, with explicit 2006-2010 / 2015-2019 subtotals
  - top 10 speakers by word count (must be members, not the chair)
  - 3 random scoreable segments in full
  - fraction of raw .docx words that survived extraction
  - seg_id uniqueness and out-of-window date checks

Usage: python3 aus_tas_validate.py
"""
import json
import random
import re
import sys
import zipfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
W_T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)


def raw_words(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return 0
    return len(" ".join(W_T.findall(xml)).split())


def main():
    segs = [json.loads(l) for l in open(HERE / "segments_aus_tas.jsonl")]
    files = sorted((HERE / "aus_tas_raw").iterdir())

    by_year_segs, by_year_words, by_speaker = Counter(), Counter(), Counter()
    dates = set()
    for s in segs:
        y = s["date"][:4]
        by_year_segs[y] += 1
        by_year_words[y] += s["n_words"]
        by_speaker[s["speaker"]] += s["n_words"]
        dates.add(s["date"])

    with ProcessPoolExecutor(max_workers=12) as ex:
        rw = sum(ex.map(raw_words, files, chunksize=8))
    kept = sum(s["n_words"] for s in segs)

    scoreable = [s for s in segs if s["scoreable"]]
    random.seed(20260807)
    samples = random.sample(scoreable, 3)

    ids = [s["seg_id"] for s in segs]
    in_window = [s for s in segs
                 if 2006 <= int(s["date"][:4]) <= 2010
                 or 2015 <= int(s["date"][:4]) <= 2019]

    out = ["=== TAS (House of Assembly) validation ===",
           f"raw files: {len(files)}; sitting dates with segments: {len(dates)}",
           f"segments: {len(segs)} total, {len(scoreable)} scoreable "
           f"({len(scoreable)/max(len(segs),1):.0%})",
           f"unique seg_ids: {len(set(ids))} of {len(ids)} "
           f"({'OK' if len(set(ids)) == len(ids) else 'DUPLICATES'})",
           f"segments inside the two drift windows: {len(in_window)}/{len(segs)}",
           "", "segments / words per year:"]
    for y in sorted(by_year_segs):
        out.append(f"  {y}: {by_year_segs[y]:6d} segs  {by_year_words[y]:9d} words"
                   f"  ({len({d for d in dates if d[:4] == y})} sitting days)")
    for lo, hi in ((2006, 2010), (2015, 2019)):
        s1 = sum(v for k, v in by_year_segs.items() if lo <= int(k) <= hi)
        w1 = sum(v for k, v in by_year_words.items() if lo <= int(k) <= hi)
        d1 = len({d for d in dates if lo <= int(d[:4]) <= hi})
        out.append(f"  WINDOW {lo}-{hi}: {s1} segs, {w1} words, {d1} sitting days")
    out += ["", "top 10 speakers by word count:"]
    for name, w in by_speaker.most_common(10):
        out.append(f"  {w:9d}  {name}")
    out += ["",
            f"raw-word survival: {kept}/{rw} = {kept/max(rw,1):.1%}",
            "  (losses = chair/procedural speech, committee-style narration,"
            " quoted motions/bills/letters, headings, page furniture)", ""]
    for i, s in enumerate(samples, 1):
        out.append(f"--- random scoreable segment {i}: {s['seg_id']} "
                   f"({s['speaker']}, {s['n_words']} words, {s['date']}) ---")
        out.append(s["text"])
        out.append("")
    report = "\n".join(out)
    (HERE / "aus_tas_validation.txt").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
