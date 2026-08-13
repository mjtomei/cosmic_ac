#!/usr/bin/env python3
"""NSW Hansard whole-day PDFs -> shared segment schema.

Source: https://api.parliament.nsw.gov.au/api/hansard/search/daily/pdf/{PdfDocId}
one file per chamber-day, filename {YYYY-MM-DD}_{LA|LC}_{docid}.pdf, so the
sitting date and chamber come from the filename and are never parsed out of the
text.  The PDFs carry a real text layer; `pdftotext -layout` is used because the
LAYOUT, not blank lines, is what separates the kinds of block:

  speech          first line indented ~8-11 columns, wrapped lines at column 0
  centred heading indented 22+ columns ("QUESTION TIME", "Agreement in
                  Principle", bill titles) -- ends the current turn
  division list   "Ayes, 49" / "Noes, 38" / "Pairs" followed by 3-column tables
                  of member names -- the rubric is caught by the Ayes/Noes/Pairs
                  regex, the name rows by the >=2-runs-of-5+-spaces test that no
                  wrapped prose line ever satisfies

The two drift windows are typeset differently and BOTH have to work: 2006-2010
puts a blank line between paragraphs, 2015-2019 does not and marks a new
paragraph by first-line indent alone.  Splitting on indent covers both; relying
on blank lines silently merged whole 950-word speeches into a single unit, which
defeated the 360-word window cap.  2015-2019 files also open with a cover page
and a dot-leader table of contents (stripped), and moved the running head from
"8180   LEGISLATIVE ASSEMBLY   4 June 2008" to
"Wednesday, 5 June 2019   Legislative Assembly   Page 1500" -- both are caught
structurally (chamber name + two or more runs of 5+ spaces) rather than by
literal pattern.  A paragraph broken by a page turn becomes two units inside the
same turn, which changes nothing after packing.

Speaker labels.  NSW Hansard prints the member holding the floor in CAPITALS
with electorate and time ("Mr GEORGE SOURIS (Upper Hunter) [10.04 a.m.]:") and
resumes after each interruption with a bare capitalised label
("Ms KRISTINA KENEALLY:").  Interjectors are printed in Mixed Case
("Mr Brad Hazzard:").  Both are member speech and both open a turn; an
interjection therefore splits a long speech into two turns, which is what
actually happened in the chamber.

Chair exclusion is NSW-specific and deliberately does NOT use
prov_common.is_chair(): that helper treats any "The ..." label as procedural,
which is right for BC/AB/SK but catastrophic here, because every Legislative
Council member is styled "The Hon. FIRSTNAME SURNAME".  CHAIR below matches the
office (Speaker/President/Chair/Clerk/Serjeant, with their deputy and acting
forms) and the collective voices, and nothing else.

Usage: python3 aus_nsw_extract.py RAW_DIR OUT_JSONL [--workers N]
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import pack_turn

DATE_CH = re.compile(r"^(\d{4}-\d{2}-\d{2})_(LA|LC)_")

# --- page furniture -------------------------------------------------------
# Running heads changed style between the windows -- 2006-2010 is
# "8180        LEGISLATIVE ASSEMBLY        4 June 2008" (or mirrored), 2015-2019
# is "Wednesday, 5 June 2019     Legislative Assembly     Page 1500" -- so they
# are recognised structurally instead: the chamber name plus at least two runs
# of five or more spaces. Wrapped speech never has those gaps.
HOUSE = re.compile(r"Legislative\s+(?:Assembly|Council)", re.I)
GAPS = re.compile(r"\S\s{5,}\S")
FOLIO = re.compile(r"^\f?\s*(?:Page\s+)?\d{1,5}\s*$", re.I)
BLANKISH = re.compile(r"^\s*[_—\-]{3,}\s*$")
TOC_LINE = re.compile(r"\.{5,}\s*\d{1,5}\s*$")   # table-of-contents dot leaders


def is_running_head(ln):
    return bool(HOUSE.search(ln)) and len(GAPS.findall(ln)) >= 2

# --- block classifiers ----------------------------------------------------
DIVISION = re.compile(r"^\s*(Ayes|Noes|Pairs|Tellers)\b", re.I | re.M)
PROC = re.compile(
    r"^(?:Question(?:\s|—|-).*|Question (?:resolved|put|time concluded).*"
    r"|Motions? (?:agreed to|negatived|lost|passed|withdrawn).*"
    r"|Amendments? (?:agreed to|negatived|lost|withdrawn|by leave).*"
    r"|The (?:House|Committee|Council|Assembly) (?:divided|adjourned|resumed|met"
    r"|proceeded|rose|took|reported|continued|will now).*"
    r"|Bills? (?:read a (?:first|second|third) time|received|introduced|returned"
    r"|passed|reported|agreed to|declared|set down|remaining stages).*"
    r"|Debate (?:adjourned|resumed|interrupted|continued).*"
    r"|Consideration in [Dd]etail.*|Pursuant to (?:sessional|standing|resolution).*"
    r"|General Business Notices? of Motions?.*|Petitions? received.*"
    r"|Agreement in principle set down.*|Third reading (?:agreed to|set down).*"
    r"|Leave granted.*|Interjections?\b.*|Time expired.*"
    r"|Government Business Notices? of Motions?.*"
    r"|\[.*\]$"
    r"|The (?:Speaker|President|Deputy|Acting|Chair|Clerk|Serjeant|Sergeant)\b"
    r"(?![^:\n]{0,60}:).*)",
    re.S)

# --- speaker labels -------------------------------------------------------
# Honorific tokens may stack in either order and some end in "." -- "The Hon.",
# "Reverend the Hon. Dr".  They are matched as repeated whole tokens rather than
# with a trailing \b, because \b after "Hon\." can never match (both sides of the
# position are non-word characters) -- that bug silently swallowed every
# mixed-case Legislative Council interjection into the previous member's turn.
HON = (r"(?:[Tt]he|Reverend|Revd|Rev\.|Hon\.|Honourable|Mr|Mrs|Ms|Miss|Dr"
       r"|Sir|Dame|Professor|Prof\.)")
# suffixes after the name: "(Upper Hunter)", "[10.04 a.m.]", ", in reply",
# ", by leave", "on behalf of ...", in any order and with stray commas
SUFFIX = (r"(?:\s*,?\s*(?:\([^)\n]{1,70}\)|\[[^\]\n]{1,40}\]"
          r"|in reply|by leave|on behalf of [^:\n]{0,40}))*")
LABEL = re.compile(
    r"^(?P<name>(?:" + HON + r"\s+)*"
    r"[A-Z][A-Za-z'’‘\-\.]*(?:\s+[A-Za-z'’‘\-\.]+){0,4})"
    + SUFFIX + r"\s*:(?=\s|—|$)")
# bare "The" is NOT an honorific for the person test -- otherwise "The Australian
# Bureau of Statistics stated:" reads as a speaker.
HONOR_START = re.compile(
    r"^(?:[Tt]he\s+)?(?:Reverend|Revd|Rev\.|Hon\.|Honourable|Mr|Mrs|Ms|Miss"
    r"|Dr|Sir|Dame|Professor|Prof\.)")

CHAIR = re.compile(
    # optional honorific(s) -- the chair is styled "Mr SPEAKER", "Madam DEPUTY
    # SPEAKER", "The PRESIDENT", "Mr ACTING-SPEAKER" depending on era and house
    r"^(?:(?:the|mr|madam|mrs|ms|miss|hon)\.?\s+)*"
    r"(?:temporary\s+|acting[\s\-]*|deputy[\s\-]*|assistant[\s\-]*)*"
    r"(?:speaker|president|chair(?:man|person|woman)?|clerk|serjeant|sergeant"
    r"|presiding officer|usher)\b"
    r"|^(?:an?|some|several|many|government|opposition|honourable|hon\.?)\s+"
    r"(?:honourable\s+|hon\.?\s+|government\s+|opposition\s+)*members?\b"
    r"|^members?\b|^voices?\b|^interjections?\b|^a voice\b"
    r"|^(?:his|her) (?:excellency|honour)\b|^the governor\b",
    re.I)

MIN_LABEL_TOKENS = 1
MAX_LABEL_TOKENS = 6


def is_chair(name):
    return bool(CHAIR.search(name.strip()))


STRIP_HON = re.compile(
    r"^(?:(?:[Tt]he|Reverend|Revd|Rev\.|Hon\.|Honourable|Mr|Mrs|Ms|Miss|Dr"
    r"|Sir|Dame|Professor|Prof\.)\s+)+")


def speaker_key(name):
    """Case- and honorific-free key.

    NSW prints the member holding the floor in CAPS and the same member
    interjecting in Mixed Case, so the printed label alone splits one person
    into two speakers.  `speaker` keeps the printed form (as the Canadian
    provincial extractors do); `speaker_key` is what joins them.
    """
    return re.sub(r"\s+", " ", STRIP_HON.sub("", name)).strip().lower()


def clean_para(lines):
    """Join a block's lines, healing hyphens broken across the line wrap.

    These PDFs come from Word, so an end-of-line hyphen is nearly always a real
    hyphen in a compound ("Murray-Darling"), not soft hyphenation -- so the
    space is dropped and the hyphen kept.
    """
    buf = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if buf.endswith("-") and ln[:1].isalpha():
            buf += ln
        elif buf:
            buf += " " + ln
        else:
            buf = ln
    return re.sub(r"\s+", " ", buf).strip()


def indent(line):
    return len(line) - len(line.lstrip(" "))


def pdf_text(path):
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                       capture_output=True, text=True, errors="replace")
    return r.stdout


HEAD_INDENT = 22    # centred headings sit at column 22+
PARA_INDENT = 4     # a paragraph's first line is indented ~8-11, its wrapped
                    # continuation lines sit at column 0


def units(txt):
    """Strip page furniture and cut the day into ('head'|'para', text) units.

    Paragraph breaks CANNOT be taken from blank lines: the 2006-2010 files put a
    blank line between paragraphs but the 2015-2019 files do not -- there the
    only signal is the first-line indent.  Splitting on indent alone works for
    both eras (and is what keeps a 950-word speech from arriving as one unit,
    which would defeat the 360-word window cap).
    """
    out, cur, kind = [], [], None

    def flush():
        nonlocal cur, kind
        if cur:
            t = clean_para(cur)
            if t:
                out.append((kind, t))
        cur, kind = [], None

    for ln in txt.split("\n"):
        ln = ln.replace("\f", "").rstrip()
        if not ln.strip():
            flush()
            continue
        if (is_running_head(ln) or FOLIO.match(ln) or BLANKISH.match(ln)
                or TOC_LINE.search(ln)):
            flush()
            continue
        if len(GAPS.findall(ln)) >= 2:     # division name table / Pairs columns
            flush()
            continue
        ind = indent(ln)
        k = "head" if ind >= HEAD_INDENT else "para"
        if kind != k or (k == "para" and ind >= PARA_INDENT):
            flush()
            kind = k
        cur.append(ln)
    flush()
    return out


def split_label(text):
    """Return (speaker, remainder) if the paragraph opens a turn, else None."""
    m = LABEL.match(text)
    if not m:
        return None
    name = re.sub(r"\s+", " ", m.group("name")).strip(" .")
    toks = name.split()
    if not (MIN_LABEL_TOKENS <= len(toks) <= MAX_LABEL_TOKENS):
        return None
    # must look like a person or an office: an ALL-CAPS surname (the member
    # holding the floor), an honorific, or a chair title.
    allcaps = any(len(t) >= 2 and t.isupper() and t.isalpha() for t in toks)
    honor = bool(HONOR_START.match(name))
    if not (allcaps or honor or is_chair(name)):
        return None
    return name, text[m.end():].strip()


def extract_file(path):
    path = Path(path)
    m = DATE_CH.match(path.name)
    if not m:
        return [], 0
    date, chamber = m.group(1), m.group(2)
    txt = pdf_text(path)
    raw_words = len(txt.split())
    out, turn = [], 0
    speaker, body = None, []

    def close():
        nonlocal speaker, body, turn
        if speaker and body and not is_chair(speaker):
            before = len(out)
            # pack under "NSWLA"/"NSWLC" so ids stay unique -- both chambers sit
            # on the same dates and turn numbering restarts per file, so a plain
            # "NSW{date}#t0w0" collides across the two houses
            pack_turn("NSW" + chamber, date, turn, speaker, body, out)
            key = speaker_key(speaker)
            for r in out[before:]:
                r["prov"] = "NSW"
                r["chamber"] = chamber
                r["speaker_key"] = key
            turn += 1
        speaker, body = None, []

    for kind, text in units(txt):
        if kind == "head" or DIVISION.match(text):
            close()                          # centred heading / division rubric
            continue
        lab = split_label(text)
        if lab:
            close()
            name, rest = lab
            speaker = name
            if rest:
                body.append(rest)
            continue
        if PROC.match(text):
            close()
            continue
        if speaker:
            body.append(text)
    close()
    return out, raw_words


def _work(p):
    try:
        return extract_file(p)
    except Exception as e:                                    # noqa: BLE001
        print(f"FAIL {p}: {e}", file=sys.stderr)
        return [], 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir")
    ap.add_argument("out_jsonl")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    paths = sorted(str(p) for p in Path(args.raw_dir).glob("*.pdf"))
    print(f"{len(paths)} sitting files", file=sys.stderr)
    n = raw = kept = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex, \
            open(args.out_jsonl, "w") as fh:
        for recs, rw in ex.map(_work, paths, chunksize=4):
            raw += rw
            for r in recs:
                kept += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments; kept {kept}/{raw} raw words "
          f"({kept/max(raw,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
