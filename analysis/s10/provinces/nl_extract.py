#!/usr/bin/env python3
"""Newfoundland & Labrador Hansard HTML -> shared segment schema.

Format (stable 1999-present, verified 2006/2008/2015/2016/2019 samples):
paragraphs in <p> blocks; a turn starts with an ALL-CAPS speaker label at
paragraph start ending in ":" (bold markup varies by era: plain <b><p>NAME:</b>
pre-2011, Word-HTML <span> soup after). Section headings are centered
paragraphs ("Oral Questions") -- they close the current turn. Chair and
procedural voices (MR. SPEAKER, CHAIR, CLERK, SOME HON. MEMBERS, HIS HONOUR
THE LIEUTENANT GOVERNOR, SERGEANT-AT-ARMS) are excluded via prov_common.CHAIR.

Same-date files (prorogation + regular sitting; cross-listed 15-04-21) share
one per-date turn counter so seg_ids never collide; identical cross-listed
duplicates are dropped by content hash.

Usage: python3 nl_extract.py RAW_DIR OUT_JSONL
"""
import hashlib
import html as htmllib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn

PTAG = re.compile(r"<p(\s[^>]*)?>", re.I)
TAG = re.compile(r"<[^>]+>")
CENTER = re.compile(r'align\s*=\s*"?center|text-align:\s*center', re.I)
# ALL-CAPS label at paragraph start: MR. SPEAKER, MS E. MARSHALL,
# PREMIER WILLIAMS, HIS HONOUR THE LIEUTENANT GOVERNOR ...
SPEAKER = re.compile(r"^([A-Z][A-Z .'’&()À-Þ-]{1,45}?)\s*:\s*(.*)$")
BRACKET = re.compile(r"\[[^\]\[]{0,300}\]")
DATE_FN = re.compile(r"_(\d{2})-(\d{2})-(\d{2})")


def read_text(path):
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def paragraphs(raw):
    """Yield (is_centered, text) per <p> block, tags stripped."""
    body = raw.split("</head>", 1)[-1]
    parts = PTAG.split(body)
    # parts = [pre, attrs1, body1, attrs2, body2, ...]
    for i in range(1, len(parts), 2):
        attrs = parts[i] or ""
        seg = parts[i + 1].split("</p>", 1)[0]
        txt = htmllib.unescape(TAG.sub(" ", seg))
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            yield bool(CENTER.search(attrs)), txt


def valid_label(lbl):
    letters = re.sub(r"[^A-Za-z]", "", lbl)
    return bool(letters) and letters.isupper() and len(letters) >= 2


def extract_file(path, date, turn_counter, out):
    raw = read_text(path)
    speaker, units = None, []

    def close():
        nonlocal units, speaker
        if speaker and units and not is_chair(speaker):
            pack_turn("NL", date, turn_counter[date], speaker, units, out)
            turn_counter[date] += 1
        speaker, units = None, []

    for centered, txt in paragraphs(raw):
        if centered:          # section heading / non-speech matter
            close()
            continue
        m = SPEAKER.match(txt)
        if m and valid_label(m.group(1)):
            close()
            speaker = re.sub(r"\s+", " ", m.group(1)).strip()
            rest = BRACKET.sub(" ", m.group(2)).strip()
            if rest:
                units.append(rest)
            continue
        if speaker:
            t = BRACKET.sub(" ", txt).strip()
            if t:
                units.append(t)
    close()
    return len(TAG.sub(" ", raw.split("</head>", 1)[-1]).split())


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    files = []
    for p in sorted(raw_dir.iterdir()):
        m = DATE_FN.search(p.name)
        if not m:
            print(f"SKIP no date: {p.name}", file=sys.stderr)
            continue
        yy = int(m.group(1))
        date = f"{1900 + yy if yy > 50 else 2000 + yy}-{m.group(2)}-{m.group(3)}"
        files.append((date, p))
    files.sort()
    seen_hash = set()
    turn_counter = defaultdict(int)
    out, raw_words, dup = [], 0, []
    for date, p in files:
        h = hashlib.sha1(p.read_bytes()).hexdigest()
        if (date, h) in seen_hash:
            dup.append(p.name)
            continue
        seen_hash.add((date, h))
        raw_words += extract_file(p, date, turn_counter, out)
    kept = sum(r["n_words"] for r in out)
    with open(out_path, "w") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(files)} files ({len(dup)} exact dupes dropped: {dup}); "
          f"wrote {len(out)} segments; kept {kept}/{raw_words} raw words "
          f"({kept / max(raw_words, 1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
