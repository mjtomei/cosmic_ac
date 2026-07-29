#!/usr/bin/env python3
"""S10 pilot: assemble the chronological English record into speaker turns
and detector-sized windows.

Reading order: within a page, English paragraphs from BOTH columns sorted by
vertical position give the continuous English record (the same passage never
appears in English in both columns — the other column carries the French).

Speaker turns: a paragraph whose bold lead ends in a colon within ~45 chars
starts a new turn ("Hon. Susan Holt :", "Mr. Austin :"). Bold short lines
without a colon are section headers (tracked as `section`). Timestamps
("13:10") are dropped.

Windows: consecutive paragraphs of one turn packed to <= MAX_WORDS words,
minimum MIN_WORDS (shorter turns emitted with scoreable=False). Each window
records the fraction of its words from original-English paragraphs
(orig_frac; the rest are translations of French originals).

Usage: python segment.py PARAGRAPHS_JSONL OUT_SEGMENTS_JSONL
"""
import json
import re
import sys
from pathlib import Path

MAX_WORDS = 360   # ~480 Falcon tokens; Binoculars truncates at 512
MIN_WORDS = 50    # below this a window is kept but flagged unscoreable

TIMESTAMP_RE = re.compile(r"^\d{1,2}\s*:\s*\d{2}$")
SPEAKER_RE = re.compile(
    r"^((?:L['’]hon\.|Hon\.|Mr\.|Ms\.|Mrs\.|Dr\.|M\.|Mme|Madam|Mister|Premier|"
    r"Deputy|Acting)[^:]{0,45}?|Her Honour|His Honour|Madam Speaker|"
    r"Mr\. Speaker|The Speaker)\s*:\s*(.*)$", re.S)


def load_english_stream(jsonl_path):
    """Return EN paragraphs in chronological order across the corpus."""
    recs = [json.loads(l) for l in open(jsonl_path)]
    # keep per-file page order, then vertical order; both columns merged
    recs.sort(key=lambda r: (r["date"], r["file"], r["page"], r["y0"]))
    return [r for r in recs if r["lang"] == "en"]


def segment(paras):
    turns = []
    cur = None
    section = ""
    for p in paras:
        text = p["text"].strip()
        if TIMESTAMP_RE.match(text):
            continue
        m = SPEAKER_RE.match(text) if p["bold_lead"] else None
        if m:
            speaker, rest = m.group(1).strip(), m.group(2).strip()
            cur = {"date": p["date"], "file": p["file"], "page": p["page"],
                   "speaker": speaker, "section": section, "paras": []}
            turns.append(cur)
            if rest:
                cur["paras"].append({**p, "text": rest})
            continue
        if p["bold_lead"] and len(text.split()) <= 8 and ":" not in text:
            # stage directions ("( Madam Speaker resumed the chair.)",
            # "Mr. X moved that ...") end the turn but are not section headers
            if text.lstrip("( ").startswith(("Madam Speaker", "Mr.", "Ms.",
                                             "Mrs.", "Hon.", "L'hon", "M.",
                                             "Mme")) or "moved" in text:
                cur = None
                continue
            section = text.strip("()")
            cur = None      # a header interrupts the current turn
            continue
        if cur is None:
            cur = {"date": p["date"], "file": p["file"], "page": p["page"],
                   "speaker": "", "section": section, "paras": []}
            turns.append(cur)
        cur["paras"].append(p)
    return [t for t in turns if t["paras"]]


def windows(turns):
    out = []
    for ti, t in enumerate(turns):
        buf, buf_words, buf_orig = [], 0, 0
        widx = 0

        def flush():
            nonlocal buf, buf_words, buf_orig, widx
            if not buf:
                return
            text = " ".join(buf)
            out.append({
                "seg_id": f"{t['date']}#t{ti}w{widx}", "turn_id": f"{t['date']}#t{ti}",
                "date": t["date"], "file": t["file"], "page": t["page"],
                "speaker": t["speaker"], "section": t["section"],
                "n_words": buf_words,
                "orig_frac": round(buf_orig / buf_words, 3) if buf_words else 0.0,
                "scoreable": buf_words >= MIN_WORDS,
                "text": text,
            })
            widx += 1
            buf, buf_words, buf_orig = [], 0, 0

        for p in t["paras"]:
            w = len(p["text"].split())
            if buf_words + w > MAX_WORDS and buf_words >= MIN_WORDS:
                flush()
            buf.append(p["text"])
            buf_words += w
            buf_orig += w if p.get("orig") else 0
        flush()
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    paras = load_english_stream(src)
    turns = segment(paras)
    segs = windows(turns)
    with open(dst, "w") as f:
        for s in segs:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    n_sc = sum(1 for s in segs if s["scoreable"])
    n_words = sum(s["n_words"] for s in segs)
    n_sp = len({s["speaker"] for s in segs if s["speaker"]})
    print(f"{len(turns)} turns -> {len(segs)} windows ({n_sc} scoreable), "
          f"{n_words:,} words, {n_sp} distinct speakers", file=sys.stderr)


if __name__ == "__main__":
    main()
