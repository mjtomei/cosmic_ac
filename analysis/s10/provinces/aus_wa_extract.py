#!/usr/bin/env python3
"""Western Australia Hansard whole-day PDF -> shared segment schema.

Source: the Domino "Daily Transcript" attachment for each sitting day,
"{A|C}{parliament} S{session} {YYYYMMDD} All.pdf" (A = Legislative Assembly,
C = Legislative Council).  pdftotext WITHOUT -layout gives correct reading
order -- the body is single-column.  Markup is stable across both drift
windows (37th-40th Parliaments, 2006-2019); there is no era split.

Page furniture: a cover page (ALL-CAPS), a running header
"[ASSEMBLY - Tuesday, 9 May 2006]" (em-dash in later years) with a bare page
number, and "__________" rules.  A trailing "QUESTIONS ON NOTICE" section
("Questions and answers are as supplied to Hansard.") carries WRITTEN answers,
not speech, and is truncated away.

Speaker labels.  WA Hansard sets the member holding the floor in SMALL CAPS,
which pdftotext renders as an upper-case surname, and sets INTERJECTIONS in
ordinary case.  That makes the two mechanically separable:

    MR A.J. SIMPSON (Darling Range - Minister for Local Government) [2.01 pm]:
    MR J.B. D'ORAZIO (Ballajura) [2.04 pm] - by leave:
    Mr D.C. NALDER:            <- same member continuing (question time)
    Mr J.H.D. Day:             <- INTERJECTION, dropped
    HON KEN TRAVERS (North Metropolitan) [10.05 am]:      <- Council form

CAPS() implements the test (>=2 upper-case letters, <=2 lower-case, more upper
than lower) so that McGINTY / MacTIERNAN / D'ORAZIO count as speech while
McGrath / MacTiernan / D'Orazio count as interjections.

Chair and procedural voices all take the form "The SPEAKER:",
"THE SPEAKER (Mr M.W. Sutherland):", "The DEPUTY SPEAKER:",
"The ACTING SPEAKER (...):" and, in the Council, PRESIDENT / DEPUTY PRESIDENT /
CHAIRMAN / DEPUTY CHAIRMAN / Clerk -- prov_common.is_chair()'s "^the " rule
catches all of them; CHAIR_EXTRA below adds the bare-title and collective forms.

Turns close at ALL-CAPS section headings and at the procedural / division
furniture in PROC (divisions in particular are followed by bare member-name
roll lines, which ROLL drops).

Units for packing are sentences of the joined turn text (the PDF wraps lines
mid-sentence).  Both chambers sit on the same dates and turn numbering restarts
per file, so pack_turn() is called with a chamber-qualified prov ("WALA" /
"WALC") -- giving seg_ids like "WALA2016-05-10#t0w0" -- and the prov field is
then reset to the plain "WA" the schema requires.

Usage: python3 aus_wa_extract.py RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences, dehyphenate

TITLE = (r"(?:MR|MRS|MS|MISS|DR|HON|REV|PROF|SIR|MADAM|"
         r"Mr|Mrs|Ms|Miss|Dr|Hon|Rev|Prof|Sir|Madam)")
# Title + optional initials/given name + surname, then optional (electorate -
# office), optional [time], optional "- by leave" / "- in reply", then colon.
SPEAKER = re.compile(
    rf"^({TITLE}\.?\s+(?:[A-Z]\.\s*){{0,6}}"
    r"(?:[A-Z][A-Za-z]{1,15}\s+)?"                      # optional given name
    r"([A-Za-z’'\-]+(?:[ \-][A-Za-z’'\-]+){0,2}))"
    r"\s*(?:\([^)]{0,160}\))?"                          # (electorate - office)
    r"\s*(?:\[[^\]]{0,40}\])?"                          # [2.01 pm]
    r"\s*(?:[-—–]\s*)?"
    # question-time forms: "... replied:", "... to the Minister for Health:"
    r"(?:by leave|in reply|by interruption|replied|answered"
    r"|to the [A-Za-z ,’'\-]{0,80}|to [A-Z][A-Za-z ,’'\-]{0,80})?"
    r"\.?\s*:\s*(.*)$")
# Chair turns are labelled "The <OFFICE>:" / "THE <OFFICE> (Mr X):" -- no
# member title, so SPEAKER does not see them.  The office word is rendered in
# caps by pdftotext (it is small caps in the PDF), which keeps this from
# matching ordinary prose that happens to contain a colon.
CHAIRLINE = re.compile(
    r"^(?:The|THE)\s+(?:ACTING|DEPUTY|TEMPORARY)?\s*"
    r"(?:SPEAKER|PRESIDENT|CHAIRMAN|CHAIRWOMAN|CHAIRPERSON|CHAIR|CLERK|"
    r"SERJEANT|SERGEANT)\b[^:]{0,80}:")
# Collective / anonymous interjection lines: dropped, but they do not end the
# turn (the member usually keeps the floor across them).
INTERJ = re.compile(
    r"^(?:(?:Several|Some|Various|Government|Opposition)\s+)?"
    r"(?:members?|an?\s+(?:opposition|government)\s+member|a\s+member)\s+"
    r"interjected\.?$|^Interjections?\.?$|^Withdrawal of Remark$|"
    r"^Several members? spoke at once\.?$", re.I)
# Chair / collective voices not already caught by prov_common.is_chair()
CHAIR_EXTRA = re.compile(
    r"^(?:the\s+)?(?:speaker|president|chairman|chairwoman|chairperson|chair|"
    r"deputy\s+(?:speaker|president|chairman)|acting\s+(?:speaker|president|"
    r"chairman)|clerk|serjeant|sergeant|usher|black\s+rod|governor|"
    r"several\s+members|members|a\s+member|an?\s+(?:opposition|government)\s+"
    r"member|withdrawal\s+of\s+remark)\b", re.I)

HEADER = re.compile(
    r"^(?:\[(?:ASSEMBLY|COUNCIL|LEGISLATIVE ASSEMBLY|LEGISLATIVE COUNCIL|"
    r"COUNCIL/ASSEMBLY|ASSEMBLY/COUNCIL)\b[^\]]*\]|_{3,}|\d{1,5}\.?|"
    r"\(\d{1,3}\)(?:\s*[-—–]\s*\(\d{1,3}\))?|\([a-z]{1,3}\)|\([ivx]{1,5}\)|"
    r"Extract from Hansard.*|Reprinted from Hansard.*|p\d+[a-z]?-\d+[a-z]?)$",
    re.I)
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.'’–—\-()&/\"]{3,}$")
TIMESTAMP = re.compile(r"^\[?\d{1,2}[.:]\d{2}\s*[ap]\.?m\.?\]?$")
INLINE_BRACKET = re.compile(r"\[[^\]\[]{0,300}\]")
# bare roll-call / list line: "Mr D.A. Templeman (Teller)", "Hon Ken Travers"
ROLL = re.compile(
    rf"^{TITLE}\.?\s+(?:[A-Z]\.\s*){{0,6}}[A-Z][A-Za-z’'\-]+"
    r"(?:[ \-][A-Z][A-Za-z’'\-]+){0,2}(?:\s*\(Teller\))?$")
PROC = re.compile(
    r"^(?:Division|Divisions|Question put.*|Questions? (?:thus |put and )?"
    r"(?:passed|negatived|resolved).*|Ayes? \(\d+\)|Noes? \(\d+\)|Pairs|"
    r"Motions?|Amendments? (?:to Motion|to the Motion)?|Amendment on the "
    r"Amendment|Consideration in Detail|In Committee|Committee|Recommittal|"
    r"(?:First|Second|Third) Reading.*|Introduction and First Reading|"
    r"Receipt and First Reading|Returned|Assent|Declaration.*|"
    r"Statement by .{0,60}|Grievance|Point of Order|Points of Order|"
    r"Personal Explanation|Speakers? Ruling|President'?s Ruling|"
    r"Speaker'?s Ruling|Standing Orders? Suspension.*|Suspension of Standing "
    r"Orders.*|Adjournment.*|Notice of Motion.*|Withdrawal of Notice.*|"
    r"Council'?s? Amendments?.*|Assembly'?s? Amendments?.*|Presentation|"
    r"Report|Reports|Tabling.*|Petition.*|Resumed from.*|Debate (?:adjourned|"
    r"resumed|interrupted).*|Bill read a.*|Bills? returned.*|Sitting suspended"
    r".*|House adjourned.*|Council adjourned.*|Leave granted.*|"
    r"Order of Business.*|Urgency Motion|Matter of Public Interest|"
    r"Questions? (?:with|without) Notice.*|Question on Notice.*|"
    r"Cognate Debate|Second Reading Debate.*|Standing Committee.*|"
    r"Quorum|Prayers?\.?|Closing Comments|Third Reading Debate.*|"
    # consideration-in-detail / committee-stage furniture
    r"Clauses?\s+[\dA-Za-z, ]{0,24}put and passed\.?|Clause\s+\d+[A-Z]?\s*:.*|"
    r"Clauses?\s+\d+[A-Z]?(?:\s+to\s+\d+[A-Z]?)?\s*[-—–:].*|"
    r"(?:New|Postponed)\s+clauses?\b.*|Title put and passed\.?|"
    r"Schedule put and passed\.?|Preamble put and passed\.?|"
    r"Progress reported.*|Committee (?:resumed|interrupted).*|"
    r"Title\.?|Schedule\.?|Preamble\.?)$",
    re.I)
QON = re.compile(r"^QUESTIONS ON NOTICE$")
# pdftotext sometimes concatenates an interrupting label onto the tail of the
# previous line ("...no doubting his passion The SPEAKER: I apologise, ...", or
# "...in the future. Clause put and passed. Clause 6: Section 5 replaced
# Mr R.F. JOHNSON: This clause..."). Break such lines apart before parsing so
# the ^-anchored rules below can see each label.
SPLIT_BEFORE = re.compile(
    r"(?<=\S)\s+(?="
    r"(?:The|THE)\s+(?:ACTING\s+|DEPUTY\s+|TEMPORARY\s+)?"
    r"(?:SPEAKER|PRESIDENT|CHAIRMAN|CHAIRWOMAN|CHAIRPERSON|CHAIR|CLERK|"
    r"SERJEANT|SERGEANT)\b[^:]{0,60}:"
    rf"|{TITLE}\.?\s+(?:[A-Z]\.\s*){{0,6}}(?:[A-Z][A-Za-z’'\-]*\s+){{0,2}}"
    r"[A-Z]{2,}[A-Za-z’'\-]*(?:\s*\([^)]{0,120}\))?(?:\s*\[[^\]]{0,30}\])?"
    r"\s*(?:[-—–]\s*)?(?:by leave|in reply|replied|answered)?\s*:"
    r"|(?:Several|Some|Various|Government|Opposition)\s+"
    r"(?:opposition\s+|government\s+)?members?\s+interjected\."
    r"|Clauses?\s+[\dA-Za-z, ]{0,24}put and passed\."
    r"|Clause\s+\d+[A-Z]?\s*:"
    r"|(?:New|Postponed)\s+clause\b"
    r"|Title put and passed\.|Schedule put and passed\.|Preamble put and passed\."
    r"|Question put and (?:passed|negatived)\.|Progress reported"
    r"|Committee (?:resumed|interrupted)\b|Sitting suspended\b"
    r"|Debate (?:adjourned|resumed)\b|Bill read a (?:first|second|third) time"
    r")")
DATE_FROM_NAME = re.compile(r"(?:^|[ _+])([AC])(\d{2})[ _+]S\d+[ _+](\d{4})(\d{2})(\d{2})",
                            re.I)

# ---------------------------------------------------------------------------
# ERA 2: the 42nd Parliament (2025 onward).
#
# The Domino route is unchanged -- the ($lookupDailyTrans**ByDate) views and the
# ?opendocument day stub still serve one whole-day PDF per sitting day -- but the
# Hansard production system changed with the 42nd Parliament and BOTH the
# attachment name and the typography moved:
#
#   name  "A39 S1 20160510 All.pdf"  ->  "Legislative Assembly_2025_06_18.pdf"
#                                    ->  "Legislative Assembly-20260618.pdf" (Jun 2026)
#   label "MR A.J. SIMPSON (Darling Range - Minister for Local Government) [2.01 pm]:"
#      ->  "Mr Paul Papalia (Secret Harbour—Minister for Veterans) (12:03 pm):"
#
# The small-caps surname is gone, so caps() can no longer separate a member
# holding the floor from an interjection -- both now read "Mr Reece Whitby:".
# What replaced it is a font weight: the speaker label of a real turn is set in
# Times-Bold, an interjection's label is not.  pdftotext discards that, so this
# era is parsed from `pdftohtml -xml` instead, which emits <b> and per-line
# geometry; lines are rebuilt by (page, top) and flagged bold if their leading
# run is bold.  Everything downstream (chair exclusion, PROC/ALLCAPS turn
# closing, sentence packing, chamber-qualified seg_ids) is the era-1 logic.
#
# Era 1 is dispatched on DATE_FROM_NAME and is untouched.
# ---------------------------------------------------------------------------
DATE_FROM_NAME_42 = re.compile(
    r"^(Legislative Assembly|Legislative Council)[ _+\-]*"
    r"(?:(\d{4})[_\-](\d{2})[_\-](\d{2})|(\d{4})(\d{2})(\d{2}))", re.I)
XML_TEXT = re.compile(r'<text top="(-?\d+)" left="(-?\d+)"[^>]*>(.*?)</text>', re.S)
XML_PAGE = re.compile(r'<page number="(\d+)"')
# running header, page number on either side: "1240ASSEMBLY—Wednesday 18 June 2025"
HEADER_42 = re.compile(
    r"^\d{0,6}\s*(?:ASSEMBLY|COUNCIL)\s*[—–\-]\s*\w+day,?\s+\d{1,2}\s+"
    r"\w+\s+\d{4}\s*\d{0,6}$", re.I)
SPEAKER_42 = re.compile(
    r"^((?:Mr|Mrs|Ms|Miss|Dr|Hon|Rev|Prof|Sir|Madam)\.?\s+"
    r"(?:[A-Z][A-Za-z’'\-]*\.?\s+){0,3}[A-Z][A-Za-z’'\-]+)"
    r"((?:\s*\([^)]{0,160}\)){0,3})"
    r"(?:\s*[-—–]?\s*(?:in reply|by leave|by interruption|replied|answered))?"
    r"\s*:\s*(.*)$")
CHAIRLINE_42 = re.compile(
    r"^The\s+(?:Acting\s+|ACTING\s+|Deputy\s+|DEPUTY\s+|Temporary\s+|TEMPORARY\s+)?"
    r"(?:Speaker|SPEAKER|President|PRESIDENT|Chair(?:man|woman|person)?|"
    r"CHAIR(?:MAN|WOMAN|PERSON)?|Clerk|CLERK|Serjeant|SERJEANT)\b[^:]{0,80}:")
# "Mr Basil Zempilas interjected." / "Several members interjected."
INTERJECTED_42 = re.compile(r"^.{0,80}\binterjected\.?$")


def bold_lines(pdf):
    """[(line_text, bold_leading)] in reading order from pdftohtml -xml.

    Each <text> element is a run of uniform font; runs sharing a page and a
    baseline (`top`, +/- 3 px) are one visual line, ordered by `left`.  A line
    is `bold_leading` when its first run is bold, which is how the 42nd
    Parliament's Hansard marks the member who holds the floor.
    """
    xml = subprocess.run(
        ["pdftohtml", "-xml", "-i", "-stdout", str(pdf)],
        capture_output=True, text=True).stdout
    frags, page = [], 0
    for chunk in re.split(r'(<page number="\d+")', xml):
        pm = XML_PAGE.match(chunk)
        if pm:
            page = int(pm.group(1))
            continue
        for m in XML_TEXT.finditer(chunk):
            inner = m.group(3)
            txt = htmllib.unescape(re.sub(r"<[^>]+>", "", inner))
            if not txt.strip():
                continue
            frags.append((page, int(m.group(1)), int(m.group(2)), txt,
                          inner.lstrip().startswith("<b>")))
    frags.sort(key=lambda f: (f[0], f[1], f[2]))
    out, cur = [], []
    for f in frags:
        if cur and (f[0] != cur[0][0] or abs(f[1] - cur[0][1]) > 3):
            out.append(cur)
            cur = []
        cur.append(f)
    if cur:
        out.append(cur)
    return [(re.sub(r"\s+", " ", "".join(x[3] for x in ln)).strip(), ln[0][4])
            for ln in out if "".join(x[3] for x in ln).strip()]


def extract_file_42(pdf, prov="WA"):
    """Era 2 (42nd Parliament, 2025+): bold-run speaker labels."""
    name = Path(pdf).name.replace("%20", " ")
    m = DATE_FROM_NAME_42.match(name)
    house = m.group(1).lower()
    y, mo, d = (m.group(2), m.group(3), m.group(4)) if m.group(2) \
        else (m.group(5), m.group(6), m.group(7))
    date = f"{y}-{mo}-{d}"
    code = "LA" if "assembly" in house else "LC"
    chamber = "Legislative Assembly" if code == "LA" else "Legislative Council"

    out, parts = [], []
    turn = 0
    speaker = None
    raw_words = 0

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not chair(speaker):
            body = INLINE_BRACKET.sub(" ", " ".join(parts))
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                pack_turn(prov + code, date, turn, speaker, sentences(body), out)
                turn += 1
        parts, speaker = [], None

    def add(text):
        """Append a body line, re-joining a word hyphenated across lines."""
        if parts and parts[-1].endswith("-") and text[:1].islower():
            parts[-1] = parts[-1][:-1] + text
        else:
            parts.append(text)

    for s, bold in bold_lines(pdf):
        raw_words += len(s.split())
        if HEADER_42.match(s) or HEADER.match(s) or TIMESTAMP.match(s):
            continue
        if s.startswith("[") and s.endswith("]"):
            continue
        if INTERJ.match(s) or INTERJECTED_42.match(s):
            continue
        if bold and CHAIRLINE_42.match(s):         # chair holds the floor
            close()
            continue
        sm = SPEAKER_42.match(s)
        if sm and bold:                            # member takes the floor
            close()
            speaker = re.sub(r"\s+", " ", sm.group(1)).strip()
            rest = sm.group(3).strip()
            if rest:
                parts.append(rest)
            continue
        if sm:                                     # unbolded label = interjection
            continue
        if PROC.match(s) or ALLCAPS.match(s):      # heading / division block
            close()
            continue
        if ROLL.match(s):                          # division roll-call name
            continue
        if speaker:
            add(s)
    close()
    for r in out:
        r["prov"] = prov
        r["chamber"] = chamber
    return out, raw_words


def caps(surname):
    """True if the surname is set in small caps (member speaking, not an
    interjection): McGINTY / MacTIERNAN / D'ORAZIO yes, McGrath / Day no."""
    letters = [c for c in surname if c.isalpha()]
    u = sum(1 for c in letters if c.isupper())
    l = len(letters) - u
    return u >= 2 and l <= 2 and u > l


def chair(name):
    return is_chair(name) or bool(CHAIR_EXTRA.match(name.strip()))


def extract_file(pdf, prov="WA"):
    name = Path(pdf).name
    m = DATE_FROM_NAME.search(" " + name.replace("%20", " "))
    if not m:
        if DATE_FROM_NAME_42.match(name.replace("%20", " ")):
            return extract_file_42(pdf, prov)      # 42nd Parliament, 2025+
        raise ValueError(f"cannot parse date from {name}")
    house, _parl, y, mo, d = m.groups()
    date = f"{y}-{mo}-{d}"
    code = "LA" if house.upper() == "A" else "LC"
    chamber = "Legislative Assembly" if code == "LA" else "Legislative Council"
    txt = subprocess.run(["pdftotext", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    txt = dehyphenate(txt)

    lines = txt.split("\n")
    for i, ln in enumerate(lines):                 # drop written answers
        if QON.match(ln.strip()):
            lines = lines[:i]
            break

    out = []
    turn = 0
    speaker = None
    parts = []
    in_bracket = False

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not chair(speaker):
            body = INLINE_BRACKET.sub(" ", " ".join(parts))
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                # chamber-qualified prov keeps seg_ids unique when both houses
                # sit on the same date; the prov FIELD is reset to "WA" below
                pack_turn(prov + code, date, turn, speaker, sentences(body), out)
                turn += 1
        parts, speaker = [], None

    sublines = []
    for ln in lines:
        sublines.extend(SPLIT_BEFORE.sub("\n", ln).split("\n"))

    for ln in sublines:
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
        if INTERJ.match(s):
            continue
        if CHAIRLINE.match(s):                     # chair holds the floor
            close()
            continue
        sm = SPEAKER.match(s)
        if sm and (caps(sm.group(2)) or chair(sm.group(1))):
            close()
            if caps(sm.group(2)):
                # normalise the title so "MR D.A. TEMPLEMAN" (speech opener)
                # and "Mr D.A. TEMPLEMAN" (continuation) are one speaker
                nm = re.sub(r"\s+", " ", sm.group(1)).strip().split(" ", 1)
                speaker = nm[0].capitalize() + (" " + nm[1] if len(nm) > 1 else "")
                rest = sm.group(3).strip()
                if rest:
                    parts.append(rest)
            continue
        if sm:                                     # interjection -> drop line
            continue
        if PROC.match(s) or ALLCAPS.match(s):      # heading / division block
            close()
            continue
        if ROLL.match(s):                          # division roll-call name
            continue
        if speaker:
            parts.append(s)
    close()
    for r in out:
        r["prov"] = prov                           # schema value stays plain "WA"
        r["chamber"] = chamber
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
