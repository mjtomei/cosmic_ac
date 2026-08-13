#!/usr/bin/env python3
"""Prince Edward Island Hansard PDF -> shared segment schema.

pdftotext -layout preserves the two-column page layout (default reading
order zippers the columns); each page's gutter is detected as the most
consistently blank character band near the middle, then the left column is
read before the right. Front matter (cover, TABLE OF CONTENTS dot-leader
lines) carries no speaker labels and is dropped naturally or via the
heading rules.

Turns start at "Name: " labels at line start within a column ("Speaker:",
"Premier Binns:", "Ms. MacKenzie:", "Mr. R. Brown:", "Some Hon. Members:").
Chair/procedural voices are excluded via prov_common.is_chair ("Speaker"
matches). Section headings (all-caps lines, short centered lines) close
the current turn. Units for packing are paragraphs (blank-line separated
within a column); sentences are not needed since -layout keeps paragraphs.

Usage: python3 pe_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences

SPEAKER = re.compile(
    r"^((?:Hon\.\s)?(?:Mr\.|Mrs\.|Ms\.?|Miss|Dr\.|Rev\.)\s?[A-Z][A-Za-z'’\-. ]{1,40}"
    r"|Speaker(?:\s?\([A-Za-z'’\-. ]{2,30}\))?"
    r"|Deputy Speaker|Chair(?:man|person)?(?:\s?\([A-Za-z'’\-. ]{2,30}\))?"
    r"|Premier\s[A-Z][A-Za-z'’\-. ]{1,30}|Leader of the (?:Official )?Opposition"
    r"|Hon\.\s[A-Z][A-Za-z'’\-. ]{2,40}"
    r"|(?:An|Some)\s(?:Hon\.\s)?Members?|Clerk(?:\sAssistant)?"
    r"|Sergeant-at-Arms|Lieutenant Governor|His Honour|Her Honour"
    r"):\s+(.*)$")
# 2025+ era only: PEI Hansard dropped the honorific for members who are not
# "Hon.", printing "P. Bevan-Baker:" / "G. McNeilly:" where the 1996-2019 era
# printed "Mr. Bevan-Baker:". Initial + surname (surname may be hyphenated or
# two-part). Dispatched on a per-file markup signature below; this alternative
# matches ZERO labels anywhere in the 1996-2019 files, so the old corpus is
# byte-identical either way (verified against segments_pe.jsonl).
INITIAL_LABEL = (r"[A-Z]\.\s?[A-Z][A-Za-z'’\-]{1,25}"
                 r"(?:[ -][A-Z][A-Za-z'’\-]{1,25}){0,2}")
SPEAKER_MODERN = re.compile(
    SPEAKER.pattern[:-len(r"):\s+(.*)$")] + r"|" + INITIAL_LABEL + r"):\s+(.*)$")
ERA_PROBE = re.compile(r"^" + INITIAL_LABEL + r":\s+\S")
ERA_MIN_HITS = 5        # a sitting day carries dozens; noise carries none
HEADERLINE = re.compile(
    r"P\.?E\.?I\.? LEGISLATIVE ASSEMBLY|^HANSARD\b|^\s*\d{1,4}\s*$"
    r"|^(?:\d{1,2} )?(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST"
    r"|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \d{4}\s*$")
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.'’\-()&/]{3,}$")
DOTLEADER = re.compile(r"(\. ){4,}|\.{6,}")
TIMESTAMP = re.compile(r"^\[?~?\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.)?\]?$", re.I)
BRACKET = re.compile(r"\[[^\]\[]{0,300}\]")


def gutter(lines):
    """Find the column-gap x position for one page, or None if single-col."""
    cand = None
    best = -1.0
    long_lines = [ln for ln in lines if len(ln.rstrip()) > 65]
    if len(long_lines) < 6:
        return None
    for pos in range(38, 72):
        n = ok = 0
        for ln in long_lines:
            if len(ln) <= pos + 1:
                continue
            n += 1
            if ln[pos - 1: pos + 2].strip() == "":
                ok += 1
        if n >= 6:
            frac = ok / n
            if frac > best:
                best, cand = frac, pos
    return cand if best >= 0.95 else None


def page_lines(page):
    """Return column-ordered lines for one -layout page."""
    lines = page.split("\n")
    g = gutter(lines)
    if g is None:
        return [ln.rstrip() for ln in lines]
    left, right = [], []
    for ln in lines:
        left.append(ln[:g].rstrip())
        right.append(ln[g:].rstrip())
    return left + right


def pick_speaker_re(txt):
    """Markup-era dispatch: modern (2025+) files label non-'Hon.' members as
    'X. Surname:'. Old files never do, so they keep the original regex."""
    hits = 0
    for page in txt.split("\f"):
        for raw in page_lines(page):
            if ERA_PROBE.match(raw.strip()):
                hits += 1
                if hits >= ERA_MIN_HITS:
                    return SPEAKER_MODERN
    return SPEAKER


def extract_file(pdf, date, prov="PE"):
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    speaker_re = pick_speaker_re(txt)
    out = []
    turn = 0
    speaker = None
    para, units = [], []

    def end_para():
        nonlocal para
        if para:
            body = " ".join(para)
            body = re.sub(r"(\w)-\s+(?=[a-z])", r"\1", body)   # de-hyphenate wraps
            body = BRACKET.sub(" ", body)
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                units.append(body)
            para = []

    def close():
        nonlocal units, speaker, turn, para
        end_para()
        if speaker and units and not is_chair(speaker):
            pack_turn(prov, date, turn, speaker, units, out)
            turn += 1
        speaker, units, para = None, [], []

    for page in txt.split("\f"):
        for raw in page_lines(page):
            s = raw.strip()
            if not s:
                end_para()
                continue
            if HEADERLINE.search(s) or DOTLEADER.search(s) or TIMESTAMP.match(s):
                continue
            indent = len(raw) - len(raw.lstrip())
            if ALLCAPS.match(s) and len(s.split()) <= 8:
                close()
                continue
            m = speaker_re.match(s)
            if m:
                close()
                speaker = m.group(1).strip()
                rest = m.group(2).strip()
                if rest:
                    para.append(rest)
                continue
            if speaker:
                if indent >= 8 and len(s) <= 40 and not s[-1:] in ".?!,;:" \
                        and len(s.split()) <= 6:
                    # centered topic heading inside a column
                    close()
                    continue
                para.append(s)
    close()
    return out, len(txt.split())


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    with open(out_path, "w") as fh:
        for pdf in sorted(raw_dir.glob("*.pdf")):
            m = re.match(r"(\d{4}-\d{2}-\d{2})", pdf.name)
            if not m:
                print(f"SKIP {pdf.name}", file=sys.stderr)
                continue
            try:
                recs, rw = extract_file(pdf, m.group(1))
            except Exception as e:
                print(f"FAIL {pdf.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            for r in recs:
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments; kept {kept_words}/{raw_words} raw words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
