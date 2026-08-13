#!/usr/bin/env python3
"""Validation report for a provincial segment corpus.

Usage: python provinces_validate.py {on,mb,ns} RAW_DIR SEGMENTS_JSONL OUT_TXT
"""
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)


def raw_words(path, enc):
    h = path.read_text(encoding=enc, errors="replace")
    h = SCRIPT.sub(" ", h)
    return len(TAG.sub(" ", h).split())


def main():
    prov = sys.argv[1].upper()
    raw_dir = Path(sys.argv[2])
    segs = [json.loads(l) for l in open(sys.argv[3])]
    out = open(sys.argv[4], "w")
    enc = "latin-1" if prov == "MB" else "utf-8"

    def w(s=""):
        print(s, file=out)

    w(f"=== {prov} corpus validation ===")
    files = [p for p in sorted(raw_dir.iterdir()) if p.suffix in (".html", ".htm")]
    w(f"raw files: {len(files)}")
    w(f"segments: {len(segs)}  scoreable: {sum(s['scoreable'] for s in segs)}")
    w(f"unique sitting dates: {len(set(s['date'] for s in segs))}")
    w()
    w("--- segments / words per year ---")
    per = defaultdict(lambda: [0, 0, 0])
    for s in segs:
        y = s["date"][:4]
        per[y][0] += 1
        per[y][1] += s["n_words"]
        per[y][2] += s["scoreable"]
    w(f"{'year':>5} {'segs':>7} {'scoreable':>9} {'words':>10}")
    for y in sorted(per):
        a, b, c = per[y]
        w(f"{y:>5} {a:>7} {c:>9} {b:>10}")
    w()
    w("--- top 10 speakers by words ---")
    sp = Counter()
    for s in segs:
        sp[s["speaker"]] += s["n_words"]
    for k, v in sp.most_common(10):
        w(f"{v:>9}  {k}")
    w()
    w("--- language mix ---")
    w(str(Counter(s["lang"] for s in segs).most_common()))
    w()
    w("--- fraction of raw words surviving extraction ---")
    rw = sum(raw_words(p, enc) for p in files)
    ew = sum(s["n_words"] for s in segs)
    w(f"raw words (all HTML text incl. site chrome/TOC/procedure): {rw}")
    w(f"extracted words: {ew}  ({ew/rw:.1%})")
    w()
    w("--- 3 random scoreable segments (full) ---")
    random.seed(10)
    for s in random.sample([s for s in segs if s["scoreable"]], 3):
        w(f"[{s['seg_id']}] {s['date']} {s['speaker']} | section: {s['section']}"
          f" | {s['n_words']} words")
        w(s["text"])
        w()
    out.close()
    print(open(sys.argv[4]).read()[:1500])


if __name__ == "__main__":
    main()
