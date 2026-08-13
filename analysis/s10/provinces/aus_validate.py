#!/usr/bin/env python3
"""Validation report for an Australian state segment file.

Usage: python3 aus_validate.py {nsw|vic|qld|wa|sa|tas}
Reads segments_aus_{state}.jsonl + aus_{state}_raw/, writes aus_{state}_validation.txt:
  - segments and words per year, with explicit subtotals for BOTH drift windows
  - top 10 speakers by word count (must be members, not the chair)
  - 3 random scoreable segments printed in full
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
W1 = range(2006, 2011)
W2 = range(2015, 2020)


def raw_words(path):
    p = str(path)
    if p.lower().endswith(".pdf"):
        txt = subprocess.run(["pdftotext", "-layout", p, "-"],
                             capture_output=True, text=True,
                             errors="replace").stdout
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
    st = sys.argv[1]
    ST = st.upper()
    segs = [json.loads(l) for l in open(HERE / f"segments_aus_{st}.jsonl")]
    raw_dir = HERE / f"aus_{st}_raw"
    files = sorted(p for p in raw_dir.iterdir() if p.is_file())

    by_year_segs, by_year_words = Counter(), Counter()
    by_speaker_words, by_speaker_segs = Counter(), Counter()
    by_chamber = Counter()
    dates, seg_ids = set(), set()
    dup = 0
    for s in segs:
        y = s["date"][:4]
        by_year_segs[y] += 1
        by_year_words[y] += s["n_words"]
        key = s.get("speaker_key") or s["speaker"]
        by_speaker_words[key] += s["n_words"]
        by_speaker_segs[key] += 1
        by_chamber[s.get("chamber", "-")] += s["n_words"]
        dates.add(s["date"])
        if s["seg_id"] in seg_ids:
            dup += 1
        seg_ids.add(s["seg_id"])

    with ProcessPoolExecutor(max_workers=12) as ex:
        rw = sum(ex.map(raw_words, files, chunksize=4))
    kept = sum(s["n_words"] for s in segs)

    scoreable = [s for s in segs if s["scoreable"]]
    random.seed(20260807)
    samples = random.sample(scoreable, 3)

    printed = defaultdict(set)
    for s in segs:
        printed[s.get("speaker_key") or s["speaker"]].add(s["speaker"])

    o = []
    o.append(f"=== {ST} validation ===")
    o.append(f"raw files: {len(files)}; sitting dates with segments: {len(dates)}")
    o.append(f"segments: {len(segs)} total, {len(scoreable)} scoreable "
             f"({len(scoreable)/max(len(segs),1):.0%}); duplicate seg_ids: {dup}")
    o.append(f"distinct speakers (normalised): {len(by_speaker_words)}")
    if len(by_chamber) > 1:
        o.append("words by chamber: " + ", ".join(
            f"{k}={v}" for k, v in sorted(by_chamber.items())))
    o.append("")
    o.append("segments / words per year:")
    for y in sorted(by_year_segs):
        o.append(f"  {y}: {by_year_segs[y]:7d} segs  {by_year_words[y]:10d} words")
    s1 = sum(v for k, v in by_year_segs.items() if int(k) in W1)
    w1 = sum(v for k, v in by_year_words.items() if int(k) in W1)
    s2 = sum(v for k, v in by_year_segs.items() if int(k) in W2)
    w2 = sum(v for k, v in by_year_words.items() if int(k) in W2)
    out_of = sum(v for k, v in by_year_words.items()
                 if int(k) not in W1 and int(k) not in W2)
    o.append(f"  WINDOW 2006-2010: {s1} segs, {w1} words")
    o.append(f"  WINDOW 2015-2019: {s2} segs, {w2} words")
    o.append(f"  outside both windows: {out_of} words (should be 0)")
    o.append("")
    o.append("top 10 speakers by word count:")
    for name, w in by_speaker_words.most_common(10):
        forms = sorted(printed[name])[:3]
        o.append(f"  {w:9d}  {by_speaker_segs[name]:5d} segs  {name}"
                 f"   [printed as: {'; '.join(forms)}]")
    o.append("")
    o.append(f"raw-word survival: {kept}/{rw} = {kept/max(rw,1):.1%}")
    o.append("  (losses = chair/procedural speech, division name lists, headings,"
             " page furniture, tabled documents)")
    o.append("")
    for i, s in enumerate(samples, 1):
        o.append(f"--- random scoreable segment {i}: {s['seg_id']} "
                 f"({s['speaker']}, {s['date']}, {s['n_words']} words) ---")
        o.append(s["text"])
        o.append("")
    rep = "\n".join(o)
    (HERE / f"aus_{st}_validation.txt").write_text(rep)
    print(rep)


if __name__ == "__main__":
    main()
