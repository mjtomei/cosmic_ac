#!/usr/bin/env python3
"""Validation report for the Victorian segment file (adapted from validate.py).

Reads segments_aus_vic.jsonl + aus_vic_raw/, writes aus_vic_validation.txt:
  - segments and words per year, with 2006-2010 and 2015-2019 subtotals
  - top 10 speakers by word count (must be members, not the chair)
  - 3 random scoreable segments in full
  - fraction of raw-file words that survived extraction
  - seg_id uniqueness assertion (both chambers sit on the same dates)
"""
import html as htmllib
import json
import random
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
TAG = re.compile(r"<[^>]+>")


def raw_words(path):
    h = Path(path).read_text(encoding="utf-8", errors="replace")
    return len(htmllib.unescape(TAG.sub(" ", h)).split())


def main():
    segs = [json.loads(l) for l in open(HERE / "segments_aus_vic.jsonl")]
    pat = sys.argv[1] if len(sys.argv) > 1 else "*.html"
    files = sorted((HERE / "aus_vic_raw").glob(pat))

    by_year_segs, by_year_words = Counter(), Counter()
    by_speaker_words, by_chamber = Counter(), Counter()
    dates, ids = set(), set()
    for s in segs:
        y = s["date"][:4]
        by_year_segs[y] += 1
        by_year_words[y] += s["n_words"]
        by_speaker_words[s["speaker"]] += s["n_words"]
        by_chamber[s.get("chamber", "?")] += s["n_words"]
        dates.add((s["date"], s.get("chamber")))
        ids.add(s["seg_id"])

    with ProcessPoolExecutor(max_workers=12) as ex:
        rw = sum(ex.map(raw_words, files, chunksize=16))
    kept = sum(s["n_words"] for s in segs)

    scoreable = [s for s in segs if s["scoreable"]]
    random.seed(20260807)
    samples = random.sample(scoreable, 3)

    o = []
    o.append("=== VIC (Victoria, Australia) validation ===")
    o.append(f"raw query-cell files: {len(files)}; "
             f"chamber-sitting-days with segments: {len(dates)}")
    o.append(f"segments: {len(segs)} total, {len(scoreable)} scoreable "
             f"({len(scoreable)/max(len(segs),1):.0%})")
    o.append(f"unique seg_ids: {len(ids)} / {len(segs)} segments -- "
             + ("OK" if len(ids) == len(segs) else "COLLISION"))
    assert len(ids) == len(segs), "duplicate seg_ids"
    o.append("words by chamber: " + ", ".join(
        f"{k}={v}" for k, v in sorted(by_chamber.items())))
    o.append("")
    o.append("segments / words per year:")
    for y in sorted(by_year_segs):
        o.append(f"  {y}: {by_year_segs[y]:6d} segs  {by_year_words[y]:9d} words")
    for lo, hi in [(2006, 2010), (2015, 2019)]:
        s1 = sum(v for k, v in by_year_segs.items() if lo <= int(k) <= hi)
        w1 = sum(v for k, v in by_year_words.items() if lo <= int(k) <= hi)
        o.append(f"  window {lo}-{hi}: {s1} segments, {w1} words")
    stray = [k for k in by_year_segs if not (2006 <= int(k) <= 2010
                                             or 2015 <= int(k) <= 2019)]
    o.append(f"  out-of-window years present: {stray or 'none'}")
    o.append("")
    o.append("top 10 speakers by word count:")
    for name, w in by_speaker_words.most_common(10):
        o.append(f"  {w:9d}  {name}")
    o.append(f"distinct speakers: {len(by_speaker_words)}")
    o.append("")
    o.append(f"raw-word survival: {kept}/{rw} = {kept/max(rw,1):.1%}")
    o.append("  (losses = chair/procedural speech, stage directions, tabled"
             " matter, headings, page furniture, de-duplicated member-bin"
             " overlap)")
    o.append("")
    for i, s in enumerate(samples, 1):
        o.append(f"--- random scoreable segment {i}: {s['seg_id']} "
                 f"({s['speaker']}, {s['chamber']}, {s['date']}, "
                 f"{s['n_words']} words) ---")
        o.append(s["text"])
        o.append("")
    rep = "\n".join(o)
    (HERE / "aus_vic_validation.txt").write_text(rep)
    print(rep)


if __name__ == "__main__":
    main()
