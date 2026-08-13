#!/usr/bin/env python3
"""Saskatchewan Hansard PDF -> shared segment schema.

pdftotext WITHOUT -layout gives usable reading order for the two-column body.
Structure: cover page + member/cabinet rosters (no speaker markers, ignored
naturally), ALL-CAPS section headings, running headers ("Saskatchewan
Hansard", date, page number), speaker turns at "Name: — " (colon + em-dash;
some eras plain "Name: "). Turns end at next speaker or ALL-CAPS heading.

Two eras (2026-08, for the 2025+ extension; the 2006-2019 path is untouched
and re-verified byte-identical on 10 files spanning both old windows):
the 30th Legislature dropped Mr./Ms. honorifics from speaker labels and its
PDFs need `pdftotext -raw` for column-major reading order.  See is_2025_era.

Usage: python3 sk_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences, dehyphenate

# "Hon. Mr. Yates: — ", "The Speaker: — ", "Mr. Wall: — ", "Ms. Sarauer: — "
SPEAKER = re.compile(
    r"^((?:Hon\.\s)?(?:Mr\.|Mrs\.|Ms\.?|Miss|Dr\.|Rev\.)\s?[A-Z][A-Za-z'’\-. ]{1,40}"
    r"|The\s[A-Z][A-Za-z'’\-. ]{2,40}"
    r"|Hon\.\s[A-Z][A-Za-z'’\-. ]{2,40}"
    r"|(?:An|Some)\s[A-Z][A-Za-z'’\-. ]{2,40}"
    r"):\s*—\s*(.*)$")
HEADER = re.compile(
    r"^(Saskatchewan Hansard|\d{1,5}|"
    r"(?:January|February|March|April|May|June|July|August|September|October"
    r"|November|December) \d{1,2}, \d{4})$")
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.'’\-()&]{3,}$")
TIMESTAMP = re.compile(r"^\[?\d{1,2}:\d{2}\]?$|^\(\d{4}\)$")
INLINE_BRACKET = re.compile(r"\[[^\]\[]{0,200}\]")
DATE_FROM_NAME = re.compile(r"(?:^|_)x?(\d{2}|\d{4})(\d{2})(\d{2})\D")

# --- 2025+ era (30th Legislature, new Hansard production) -------------------
# Two changes, both detected from the text itself, never by date:
#  1. members are labelled by FULL NAME with no Mr./Ms. honorific
#     ("Vicki Mowat: — ", "Speaker Goudy: — "), which the original SPEAKER
#     regex cannot see; unmatched labels silently glued one member's speech
#     onto the previous member's turn.
#  2. pdftotext's default block ordering interleaves the two columns
#     paragraph-by-paragraph on these PDFs (it did not on the older ones);
#     -raw restores column-major order.  -raw is used ONLY for this era.
# Signature: more bare full-name labels than honorific labels in the default
# text.  Verified to be false for every 2006-2019 file in sk_raw/.
BARE_LABEL = re.compile(
    r"(?m)^(?!The\s)(?:Hon\.\s)?[A-Z][a-z]+\s[A-Z][A-Za-z'’\-]+:\s*—")
HONORIFIC_LABEL = re.compile(
    r"(?m)^(?:Hon\.\s)?(?:Mr|Mrs|Ms|Miss|Dr|Rev)\.?\s?[A-Z][A-Za-z'’\-]+:\s*—")
NAMEWORD = r"[A-Z][A-Za-z'’\-.]*"
SPEAKER_2025 = re.compile(
    r"^((?:Hon\.\s)?" + NAMEWORD + r"(?:\s(?:" + NAMEWORD +
    r"|of|the|for)){0,5}):\s*—\s*(.*)$")


def is_2025_era(txt):
    return len(BARE_LABEL.findall(txt)) > len(HONORIFIC_LABEL.findall(txt))


def extract_file(pdf, prov="SK"):
    name = Path(pdf).name.split("_", 1)[-1]     # strip session prefix
    m = DATE_FROM_NAME.search("_" + name.lstrip("x"))
    y, mo, d = m.group(1), m.group(2), m.group(3)
    if len(y) == 2:
        y = ("19" if int(y) > 40 else "20") + y
    date = f"{y}-{mo}-{d}"
    txt = subprocess.run(["pdftotext", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    spk_re = SPEAKER
    if is_2025_era(txt):
        spk_re = SPEAKER_2025
        txt = subprocess.run(["pdftotext", "-raw", str(pdf), "-"],
                             capture_output=True, text=True, check=True).stdout
    txt = dehyphenate(txt)
    # some SK PDFs' text layer maps curly apostrophes/quotes to U+201F/U+201E
    txt = txt.replace("‟", "’").replace("„", "“")

    out = []
    turn = 0
    speaker = None
    parts = []
    in_bracket = False

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not is_chair(speaker):
            body = INLINE_BRACKET.sub(" ", " ".join(parts))
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                pack_turn(prov, date, turn, speaker, sentences(body), out)
                turn += 1
        parts, speaker = [], None

    for ln in txt.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if HEADER.match(s) or TIMESTAMP.match(s):
            continue
        if in_bracket:
            if "]" in s:
                in_bracket = False
            continue
        if s.startswith("[") and "]" not in s:
            in_bracket = True
            continue
        if s.startswith("[") and s.endswith("]"):
            continue
        if ALLCAPS.match(s):          # section heading -> end turn
            close()
            continue
        sm = spk_re.match(s)
        if sm:
            close()
            speaker = sm.group(1).strip()
            rest = sm.group(2).strip()
            if rest:
                parts.append(rest)
            continue
        if speaker:
            parts.append(s)
    close()
    return out, len(txt.split())


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    with open(out_path, "w") as fh:
        for pdf in sorted(raw_dir.glob("*.pdf")):
            try:
                recs, rw = extract_file(pdf)
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
