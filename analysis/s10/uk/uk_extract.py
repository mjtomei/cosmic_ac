#!/usr/bin/env python3
"""UK Hansard (ParlParse XML) -> the same segment schema as the NB pipeline.

ParlParse gives speaker-attributed <speech> elements directly, so none of the
NB PDF machinery (column split, language ID, bold-lead speaker detection) is
needed. What we do need to match:
  - one record per <speech> turn, windowed to <=360 words, min 50
  - the same field names, so every downstream script runs unchanged
  - chair/procedural speech excluded by speaker name
  - orig_frac = 1.0 (no translation column in the UK record)

Revision handling: ParlParse ships several revisions per sitting date
(debatesYYYY-MM-DDa.xml, ...b.xml). We keep the file whose root carries
latest="yes", falling back to the highest suffix letter for that date.

Usage: python uk_extract.py XML_DIR OUT_JSONL [--workers N]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

MAX_WORDS = 360
MIN_WORDS = 50
CHAIRS = re.compile(
    r"^(mr|madam|the)?\s*(deputy\s+)?(speaker|chairman|chair)\b"
    r"|^(mr|madam)\s+deputy\s+speaker\b"
    r"|^several\s+hon", re.I)
DATE_RE = re.compile(r"debates(\d{4}-\d{2}-\d{2})([a-z]*)\.xml$")


def pick_latest(paths):
    """One file per sitting date: prefer latest='yes', else highest suffix."""
    by_date = defaultdict(list)
    for p in paths:
        m = DATE_RE.search(p.name)
        if m:
            by_date[m.group(1)].append((m.group(2), p))
    chosen = []
    for date, cands in by_date.items():
        best = None
        for suffix, p in sorted(cands):
            try:
                with open(p, "rb") as fh:
                    head = fh.read(4000).decode("utf-8", "ignore")
                if 'latest="yes"' in head:
                    best = p
            except Exception:
                pass
        chosen.append((date, best or sorted(cands)[-1][1]))
    return sorted(chosen)


def text_of(el):
    """Flatten a <p>, keeping <phrase> inner text, dropping markup."""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def extract_file(item):
    date, path = item
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"PARSE FAIL {path.name}: {e}", file=sys.stderr)
        return []
    root = tree.getroot()
    out = []
    section = ""
    turn_idx = 0
    for el in root:
        tag = el.tag
        if tag in ("major-heading", "minor-heading", "oral-heading"):
            t = text_of(el)
            if t:
                section = t[:120]
            continue
        if tag != "speech":
            continue
        speaker = (el.get("speakername") or "").strip()
        if not speaker or CHAIRS.match(speaker):
            continue
        paras = [text_of(p) for p in el.findall("p")]
        paras = [p for p in paras if p]
        if not paras:
            continue
        turn_id = f"UK{date}#t{turn_idx}"
        turn_idx += 1
        buf, words, widx = [], 0, 0

        def flush():
            nonlocal buf, words, widx
            if not buf:
                return
            out.append({
                "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
                "date": date, "file": path.name,
                "page": el.get("colnum") or "",
                "speaker": speaker, "section": section,
                "person_id": (el.get("person_id") or "").rsplit("/", 1)[-1],
                "n_words": words, "orig_frac": 1.0,
                "scoreable": words >= MIN_WORDS,
                "text": " ".join(buf),
            })
            widx += 1
            buf, words = [], 0

        for p in paras:
            w = len(p.split())
            if words + w > MAX_WORDS and words >= MIN_WORDS:
                flush()
            buf.append(p)
            words += w
        flush()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml_dir")
    ap.add_argument("out_jsonl")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    paths = list(Path(args.xml_dir).glob("debates*.xml"))
    chosen = pick_latest(paths)
    print(f"{len(paths)} files -> {len(chosen)} sitting dates", file=sys.stderr)

    n = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex, \
            open(args.out_jsonl, "w") as fh:
        for recs in ex.map(extract_file, chosen, chunksize=8):
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments to {args.out_jsonl}", file=sys.stderr)


if __name__ == "__main__":
    main()
