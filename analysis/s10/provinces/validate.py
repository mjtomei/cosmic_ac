#!/usr/bin/env python3
"""Validation report for a provincial segment file.

Usage: python3 validate.py {bc|ab|sk}
Reads segments_{prov}.jsonl + {prov}_raw/, writes {prov}_validation.txt:
  - segments and words per year (both drift windows must be covered)
  - top 10 speakers by word count (should be members, not the chair)
  - 3 random scoreable segments in full
  - fraction of raw-file words that survived extraction
"""
import html as htmllib
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
TAG = re.compile(r"<[^>]+>")


def raw_words(path):
    p = str(path)
    if p.lower().endswith(".pdf"):     # QLD serves ..._WEEKLY.PDF
        txt = subprocess.run(["pdftotext", p, "-"],
                             capture_output=True, text=True).stdout
    else:
        data = Path(p).read_bytes()
        try:
            h = data.decode("utf-8")
        except UnicodeDecodeError:
            h = data.decode("cp1252", "replace")
        h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S | re.I)
        txt = htmllib.unescape(TAG.sub(" ", h))
    return len(txt.split())


def main():
    prov = sys.argv[1]
    PROV = prov.upper()
    segs = [json.loads(l) for l in open(HERE / f"segments_{prov}.jsonl")]
    raw_dir = HERE / f"{prov}_raw"
    files = sorted(raw_dir.iterdir())

    by_year_segs = Counter()
    by_year_words = Counter()
    by_speaker_words = Counter()
    dates = set()
    for s in segs:
        y = s["date"][:4]
        by_year_segs[y] += 1
        by_year_words[y] += s["n_words"]
        by_speaker_words[s["speaker"]] += s["n_words"]
        dates.add(s["date"])

    with ProcessPoolExecutor(max_workers=12) as ex:
        rw = sum(ex.map(raw_words, files, chunksize=8))
    kept = sum(s["n_words"] for s in segs)

    scoreable = [s for s in segs if s["scoreable"]]
    random.seed(20260806)
    samples = random.sample(scoreable, 3)

    out = []
    out.append(f"=== {PROV} validation ===")
    out.append(f"raw files: {len(files)}; sitting dates with segments: {len(dates)}")
    out.append(f"segments: {len(segs)} total, {len(scoreable)} scoreable "
               f"({len(scoreable)/max(len(segs),1):.0%})")
    ids = {s["seg_id"] for s in segs}
    out.append(f"unique seg_ids: {len(ids)} / {len(segs)} "
               f"({'OK - no duplicates' if len(ids) == len(segs) else 'DUPLICATES!'})")
    provs = sorted({s["prov"] for s in segs})
    out.append(f"prov values: {provs}")
    out.append("")
    out.append("segments / words per year:")
    for y in sorted(by_year_segs):
        out.append(f"  {y}: {by_year_segs[y]:6d} segs  {by_year_words[y]:9d} words")
    w1 = sum(v for k, v in by_year_words.items() if 2006 <= int(k) <= 2010)
    w2 = sum(v for k, v in by_year_words.items() if 2015 <= int(k) <= 2019)
    out.append(f"  window 2006-2010: {w1} words; window 2015-2019: {w2} words")
    if any("chamber" in s for s in segs):
        out.append("")
        out.append("segments / words per chamber:")
        cs, cw = Counter(), Counter()
        for s in segs:
            cs[s.get("chamber", "?")] += 1
            cw[s.get("chamber", "?")] += s["n_words"]
        for ch in sorted(cs):
            out.append(f"  {ch}: {cs[ch]:6d} segs  {cw[ch]:9d} words")
    out.append("")
    out.append("top 10 speakers by word count:")
    for name, w in by_speaker_words.most_common(10):
        out.append(f"  {w:9d}  {name}")
    out.append("")
    out.append(f"raw-word survival: {kept}/{rw} = {kept/max(rw,1):.1%}")
    out.append("  (losses = chair/procedural speech, TOC/rosters, headings,"
               " stage directions, page furniture)")
    out.append("")
    for i, s in enumerate(samples, 1):
        out.append(f"--- random scoreable segment {i}: {s['seg_id']} "
                   f"({s['speaker']}, {s['n_words']} words) ---")
        out.append(s["text"])
        out.append("")
    report = "\n".join(out)
    (HERE / f"{prov}_validation.txt").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
