#!/usr/bin/env python3
"""South Australian Hansard (House of Assembly + Legislative Council) -> shared
segment schema.

Everything here is fetched from the Internet Archive's copies of
hansardsearch.parliament.sa.gov.au: the live host answers 403 at the Azure
Front Door WAF on every path, from every request shape tried (see
recon_au_sa.json). Two source formats, in aus_sa_raw/:

  {lh|uh}_{YYYY-MM-DD}.pdf        full sitting-day Hansard, text layer clean
  {lh|uh}_{YYYY-MM-DD}_x{NNN}.xml one <hansard> subject fragment of a day,
                                  used only for days with no archived PDF

PDF, two eras with different turn markers:
  - pre-Oct-2007 (and 2006): narrow two-column body, no per-turn clock.
    Turns open at line start as "Mr PISONI (Unley):" / "The Hon. M.J.
    ATKINSON:" -- the SPEAKING member's surname is set in CAPITALS.
    Interjections are set in Title Case ("Ms Chapman interjecting:",
    "Mr Pisoni: You are out there...") and so are dropped for free by the
    all-caps requirement.
  - Oct-2007 onward: same header plus a clock, "Mrs REDMOND (Heysen)
    (11:01):"; ministers carry long role parentheticals that WRAP across
    lines, so header lines are re-joined before matching.
  Page furniture is a running "HOUSE OF ASSEMBLY"/"LEGISLATIVE COUNCIL"
  banner, the weekday date, and a bare page number. ALL-CAPS lines are
  subject headings and end a turn, as do division blocks (AYES/NOES/name
  rosters), petition/motion dispositions and the adjournment line.
  Sentences are the packing units (PDF-derived text, per sk_extract.py).

XML (hansard_1_0.xsd) is the richer format: <proceeding>/<subject>/<talker
role= kind=> with <name>, <electorate>, and <text> children.  role="member"
plus kind in {speech, question, answer} is the speech filter; <by> (the
rendered "Mrs REDMOND (Heysen) (11:01):" header), <timeStamp> and <interject>
(another member's voice inside the turn) are stripped from the body, while
<inserted> (matter tabled into the record rather than spoken) is dropped, mirroring the
PDF cut at "...inserted in Hansard without my reading it". Paragraphs are the
units.

Chair exclusion is SA-specific: prov_common.is_chair() would reject every
"The Hon. ..." minister via its "^the " rule, so CHAIR below tests the name
part only, for SPEAKER/PRESIDENT/CHAIR/CLERK/Black Rod/Governor plus the
collective voices.

Usage: python3 aus_sa_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import pack_turn, sentences, dehyphenate

PROV = "SA"
CHAMBER = {"lh": "House of Assembly", "uh": "Legislative Council"}
# pack_turn() numbers turns per file, and both chambers sit on the same dates,
# so the prov passed to it is chamber-qualified to keep seg_ids unique; the
# schema's `prov` field is reset to plain "SA" afterwards.
PACK_PROV = {"lh": "SAHA", "uh": "SALC"}

# --- speaker headers -------------------------------------------------------
TITLE = r"(?:The\s+)?(?:Hon\.|Mr|Mrs|Ms|Miss|Dr|Prof|Rev|Sir)\.?\s+"
SURNAME = r"(?:(?:[A-Z]\.){1,4}\s*)?(?:Mc|Mac|O’|O')?[A-Z][A-Z’'’]+(?:[-\s](?:Mc|Mac)?[A-Z][A-Z’'’]+){0,3}"
# "The SPEAKER", "The PRESIDENT", "The CHAIR" -- title-less but always "The "
NAME = r"(?:%s%s|The\s+%s)" % (TITLE, SURNAME, SURNAME)
HDR = re.compile(
    r"^(%s)\s*((?:\([^()]{1,400}\)\s*){0,2}?)"
    r"(?:\((\d{1,2}[:.]\d{2})\)\s*)?:(?!\S)" % NAME)
# a header whose role parenthetical is still open at end of line
OPEN_HDR = re.compile(r"^%s\s*\([^)]*$" % NAME)

CHAIR = re.compile(
    r"speaker|president|chair|clerk|sergeant|black rod|usher|governor"
    r"|honourable member|members? interjecting|a voice|voices", re.I)

# --- page furniture / non-speech -------------------------------------------
DAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
MONTHS = ("January|February|March|April|May|June|July|August|September"
          "|October|November|December")
FURNITURE = re.compile(
    r"^(?:Page\s+\d+"
    r"|\d{1,5}"
    r"|HOUSE OF ASSEMBLY|LEGISLATIVE COUNCIL|ESTIMATES COMMITTEE [A-Z]"
    r"|(?:%s)\s+\d{1,2}\s+(?:%s)\s+\d{4}"
    r"|(?:%s),?\s+\d{1,2}\s+(?:%s)\s+\d{4}"
    r"|\[?\d{1,2}[:.]\d{2}\s*(?:a\.?m\.?|p\.?m\.?)?\]?)\.?$" % (DAYS, MONTHS, DAYS, MONTHS),
    re.I)
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.:;’'’()&/—–-]{3,}$")
PROC = re.compile(
    r"^(?:The (?:house|council|committee) divided"
    r"|AYES\s*\(|NOES\s*\(|PAIRS\b|Majority of\b"
    r"|Motion (?:carried|negatived|lost|agreed)"
    r"|Amendment (?:carried|negatived|lost|agreed)"
    r"|Question (?:agreed to|resolved|put|carried|negatived)"
    r"|Clause(?:s)? (?:passed|as amended|and title)"
    r"|Bill(?:s)? (?:read a|passed|taken through|referred)"
    r"|Petition received"
    r"|Petitions? (?:signed|received)"
    r"|A petition signed"
    r"|Read a (?:first|second|third) time"
    r"|Report(?:s)? received"
    r"|Papers? (?:laid|tabled)"
    r"|The following papers"
    r"|In committee\b|The committee divided"
    r"|At \d{1,2}[.:]\d{2}"
    r"|The (?:house|council) adjourned"
    r"|Sitting suspended|Business of the (?:house|council)"
    r"|Adjourned debate|Adjourned on motion"
    r"|Prayers?\b|Members? interjecting|An honourable member"
    r"|Honourable members?:"
    r"|The (?:SPEAKER|PRESIDENT|CHAIR|DEPUTY|ACTING|CLERK)\b[^:]*$"
    r"|\(Continued from)", re.I)
# Written answers to questions on notice: departmental prose tabled under a
# minister's name, not speech. Both eras introduce the answering turn with
# "In reply to Mr X (date)." or a numbered "180. Mr HAMILTON-SMITH:" question,
# so the turn that follows either marker is dropped.
WRITTEN = re.compile(
    r"^(?:In reply to\b"
    r"|\d{1,4}\.\s+(?:The\s+)?(?:Hon\.|Mr|Mrs|Ms|Miss|Dr|Prof)\b)")
XML_WRITTEN_PROCEEDINGS = {"answers to questions", "questions on notice",
                           "written answers", "answers"}
# "I seek leave to have the second reading explanation inserted in Hansard
# without my reading it. Leave granted." -- everything after that inside the
# turn is a departmental explanation of clauses that was never spoken. It runs
# to 20,000 words and is the single largest register contaminant in SA
# Hansard, so the turn is cut at the marker. (The XML marks the same matter
# with <inserted>, which is dropped there.)
INSERT_CUT = re.compile(
    r"seek leave to (?:have|insert)\b.{0,200}?"
    r"(?:inserted|incorporated|insertion)\b[^.]{0,140}\."
    r"(?:\s*Leave granted\.)?", re.I | re.S)
# belt and braces: the inserted block always opens with this rubric
EXPL_CUT = re.compile(r"\bExplanation of Clauses\b")
# Interjections from the floor are typeset with the interjector's surname in
# Title Case ("Mr Williams: Yes; revenues include borrowings.", "Ms Chapman
# interjecting:") against the CAPITALS used for whoever holds the floor. They
# are another member's voice inside the current turn, so the line is dropped
# without closing the turn -- the interrupted speaker carries on afterwards.
INTERJECT = re.compile(
    r"^(?:The\s+)?(?:Hon\.|Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+"
    r"(?:(?:[A-Z]\.){1,3}\s*)?[A-Z][a-z][\w’'-]*"
    r"(?:[-\s][A-Z][a-z][\w’'-]*){0,2}"
    r"(?:\s+interjecting)?:")


def is_sa_chair(name):
    return bool(CHAIR.search(name))


def clean_name(raw):
    n = re.sub(r"\s+", " ", raw).strip().rstrip(":").strip()
    return n


# --------------------------------------------------------------------------
def extract_pdf(path, ch, date):
    txt = subprocess.run(["pdftotext", str(path), "-"],
                         capture_output=True, text=True).stdout
    raw_words = len(txt.split())
    txt = dehyphenate(txt)

    lines = []
    for ln in txt.split("\n"):
        s = ln.strip()
        if not s or FURNITURE.match(s):
            continue
        lines.append(s)

    # re-join speaker headers whose role parenthetical wrapped
    joined = []
    i = 0
    while i < len(lines):
        s = lines[i]
        if OPEN_HDR.match(s):
            j = i + 1
            while j < len(lines) and j - i <= 4 and "):" not in s and ")" not in s.split("(", 1)[-1]:
                s = s + " " + lines[j]
                j += 1
            i = j
        else:
            i += 1
        joined.append(s)

    out = []
    turn = 0
    speaker = None
    parts = []
    written_next = False

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not is_sa_chair(speaker):
            body = re.sub(r"\s+", " ", " ".join(parts)).strip()
            cut = INSERT_CUT.search(body)
            if cut:
                body = body[:cut.end()].strip()
            cut = EXPL_CUT.search(body)
            if cut:
                body = body[:cut.start()].strip()
            if body:
                pack_turn(PACK_PROV[ch], date, turn, speaker,
                          sentences(body), out)
                turn += 1
        parts, speaker = [], None

    for s in joined:
        m = HDR.match(s)
        if m:
            close()
            if written_next:              # tabled answer, not speech
                written_next = False
                continue
            speaker = clean_name(m.group(1))
            rest = s[m.end():].strip()
            if rest:
                parts.append(rest)
            continue
        if INTERJECT.match(s):        # another member's voice mid-turn
            continue
        if WRITTEN.match(s):
            close()
            written_next = True
            continue
        if ALLCAPS.match(s) or PROC.match(s):
            close()
            written_next = False
            continue
        if speaker:
            parts.append(s)
    close()
    for r in out:
        r["prov"] = PROV
        r["chamber"] = CHAMBER[ch]
        r["source"] = "pdf"
    return out, raw_words


# --------------------------------------------------------------------------
SPEECH_KINDS = {"speech", "question", "answer", "statement", "continue",
                "explanation", "ministerialstatement", "personalexplanation"}


def node_text(el, drop):
    buf = []
    if el.tag not in drop and el.text:
        buf.append(el.text)
    for kid in el:
        if kid.tag in drop:
            if kid.tail:
                buf.append(kid.tail)
            continue
        buf.append(node_text(kid, drop))
        if kid.tail:
            buf.append(kid.tail)
    return " ".join(x for x in buf if x)


def extract_xml(path, ch, date):
    data = Path(path).read_text(encoding="utf-8", errors="replace")
    raw_words = len(re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", data,
                                                   flags=re.S)).split())
    try:
        root = ET.fromstring(re.sub(r"<!--.*?-->", " ", data, flags=re.S))
    except ET.ParseError as e:
        print(f"PARSE FAIL {Path(path).name}: {e}", file=sys.stderr)
        return [], raw_words

    out = []
    turn = 0
    frag = Path(path).stem.split("_x")[-1]
    written = set()
    for proc in root.iter("proceeding"):
        pn = proc.find("name")
        if pn is not None and (pn.text or "").strip().lower() in XML_WRITTEN_PROCEEDINGS:
            written.update(id(t) for t in proc.iter("talker"))

    for talker in root.iter("talker"):
        if id(talker) in written:          # tabled answers, not speech
            continue
        if (talker.get("role") or "").lower() != "member":
            continue
        kind = re.sub(r"[^a-z]", "", (talker.get("kind") or "").lower())
        if kind and kind not in SPEECH_KINDS:
            continue
        nm = talker.find("name")
        speaker = clean_name(nm.text or "") if nm is not None and nm.text else ""
        if not speaker or is_sa_chair(speaker):
            continue
        paras = []
        for t in talker.findall("text"):
            if t.find("heading") is not None:
                continue
            body = node_text(t, {"by", "timeStamp", "interject", "heading",
                                 "inserted"})
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                paras.append(body)
        if not paras:
            continue
        n0 = len(out)
        pack_turn(PACK_PROV[ch], date, f"x{frag}t{turn}", speaker, paras, out)
        turn += 1
        for r in out[n0:]:
            r["prov"] = PROV
            r["chamber"] = CHAMBER[ch]
            r["source"] = "xml"
    return out, raw_words


# --------------------------------------------------------------------------
NAME_RE = re.compile(r"^(lh|uh)_(\d{4}-\d{2}-\d{2})")


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    seen = set()
    files = sorted(list(raw_dir.glob("*.pdf")) + list(raw_dir.glob("*.xml")))
    with open(out_path, "w") as fh:
        for f in files:
            m = NAME_RE.match(f.name)
            if not m:
                continue
            ch, date = m.group(1), m.group(2)
            try:
                if f.suffix == ".pdf":
                    recs, rw = extract_pdf(f, ch, date)
                else:
                    recs, rw = extract_xml(f, ch, date)
            except Exception as e:
                print(f"FAIL {f.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            for r in recs:
                if r["seg_id"] in seen:
                    continue
                seen.add(r["seg_id"])
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments; kept {kept_words}/{raw_words} raw words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
