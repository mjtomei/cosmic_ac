#!/usr/bin/env python3
"""Queensland Legislative Assembly Record of Proceedings (Hansard) PDF ->
shared segment schema.

FILE = ONE SITTING DAY. The path suffix "_WEEKLY" is a legacy label, not a
week: 2019_02_12/13/14_WEEKLY.PDF all exist while the Monday 404s, and every
running header inside a given file carries a single date. The extractor still
reads the date off the running headers page by page (falling back to the
filename) so a multi-day file would be split correctly; extract_file() also
reports the set of header dates it saw so the caller can flag any file where
they disagree with the filename.

LAYOUT. `pdftotext -layout` beats plain pdftotext here: the body is single
column, and -layout preserves the indentation that carries the structure.
  indent 0        continuation line of the current paragraph
  indent ~5-9     first line of a new paragraph (or of a speaker turn)
  indent >=14     CENTRED line: section heading ("MINISTERIAL STATEMENTS"),
                  subheading ("Weather Events, Floods"), or the wrapped
                  second half of a running header
Running header = the first 1-3 non-blank lines of each page, some mix of
"12 Feb 2019", the section title, and a bare page number; the title can wrap
across two centred lines with the date/page line between them. Those leading
lines are dropped without closing the current turn, so a speech that spans a
page break stays one turn. Front matter (ISSN block, Table of Contents, the
per-page dotted TOC lines) carries no speaker label and so never opens a turn;
the trailing ATTENDANCE roster likewise.

SPEAKER TURNS. A turn opens on a paragraph whose head matches a Queensland
Hansard speech label, i.e. an honorific plus an ALL-CAPS surname, optionally
with initials, electorate/party, portfolio and a timestamp:
  "Mr NICHOLLS: ..."
  "Hon. AM PALASZCZUK (Inala-ALP) (Premier and Minister for Trade) (9.32 am): ..."
  "Hon. MC de BRENNI (Springwood-ALP) (Minister for Housing ...) (3.04 pm): ..."
  "Mrs FRECKLINGTON (Nanango-LNP) (Leader of the Opposition) (2.31 pm): ..."
The CAPITALISATION OF THE SURNAME IS THE SIGNAL. Queensland Hansard sets the
member who holds the floor in caps and INTERJECTORS in ordinary case
("Mr Springborg: You promised.", "Mr Horan interjected."), so a mixed-case
surname is dropped rather than opening a turn. Turns end at the next label or
at a centred heading.

EXCLUSIONS: chair and collective voices (Mr/Madam SPEAKER, DEPUTY/ACTING/
TEMPORARY SPEAKER, CHAIR, CLERK, honourable/government/opposition members, a
government/opposition member) via is_chair(); interjection lines; divisions,
tabled-paper notes, "(Time expired)"-style directions, "read prayers", and
bracketed stage directions.

Usage: python3 aus_qld_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences, dehyphenate

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_D = r"(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})"
# the running header carries the sitting date in abbreviated form at the very
# start or the very end of the line ("12 Feb 2019  Legislative Assembly" /
# "18  Ministerial Statements  12 Feb 2019"). Anchoring both ends keeps prose
# dates ("Letter, dated 30 November 2018, ...") from being read as the header.
HDR_DATE = re.compile(r"^(?:\d{1,4}\s+)?" + _D + r"\b|\b" + _D + r"$")
PAGENUM = re.compile(r"^\d{1,4}$")
HEADING_INDENT = 14
PARA_INDENT = 3

# honorific + ALL-CAPS surname (initials, particles and Mc/O' allowed), then
# any run of (electorate-party) / (portfolio) / (time) brackets, then ":".
TITLE = r"(?:Mr|Mrs|Ms|Miss|Dr|Rev|Prof|Sir|Madam)\.?\s+"
HON = r"(?:Hon\.?\s+(?:" + TITLE + r")?|" + TITLE + r")"
NAME = r"(?:[A-Z]{1,3}\s+)?(?:(?:de|van|von|le|du|da|di|el)\s+)?[A-Za-z’'\-]{2,30}"
BRACKETS = r"(?:\s*\([^()]{0,160}\)){0,4}"
SPEAKER = re.compile(r"^(" + HON + NAME + r"(?:\s+" + NAME + r")?" + BRACKETS +
                     r"(?:,\s*by leave[^:]{0,60})?)\s*:\s*(.*)$", re.S)

INTERJECTED = re.compile(
    r"^(?:An?|Some)?\s*\w[\w’'\-. ]{0,60}\s+interjected\.?$", re.I)
# collective / officer voices that carry a colon but no member label
COLLECTIVE = re.compile(
    r"^(The [A-Z][A-Za-z ]{2,30}|An? (?:honourable|government|opposition) member"
    r"|Honourable members|Government members|Opposition members|Members"
    r"|A member|Some honourable members)\s*:", re.I)
SKIP_PARA = re.compile(
    r"^(Tabled paper|Division\b|Resolved in the|Question put|Question resolved"
    r"|Motion agreed to|Bill read a|Ordered to be|Non-government amendment"
    r"|Sitting suspended|The House (adjourned|divided)|Whereupon the"
    r"|AYES|NOES|PAIRS|ATTENDANCE|Clause \d|Amendment agreed"
    # "Leave granted." precedes material INCORPORATED IN HANSARD (tables,
    # dot-point briefs, letters) that was never spoken; closing the turn here
    # drops it, since nothing is attributed again until the next member label.
    r"|Leave granted|Leave not granted|The following .{0,40}(tabled|incorporated)"
    r"|Hon\. \w+ .{0,80} read prayers|Mr Speaker \(|Madam Speaker \()", re.I)
STAGE = re.compile(r"^[\[(](?:Time expired|Interruption|Continued|Honourable"
                   r"|Laughter|Applause)[^\])]{0,80}[\])]\.?$", re.I)
INLINE_BRACKET = re.compile(r"\[[^\]\[]{0,200}\]")

# Queensland-specific chair / collective voices on top of prov_common.is_chair
QLD_CHAIR = re.compile(
    # "deputy"/"temporary" alone catch truncated chair labels in the source
    # ("Madam DEPUTY (Ms Grace): Order!"); no member surname contains them.
    r"\b(speaker|chairman|chairwoman|chair|clerk|serjeant|sergeant|governor"
    r"|deputy|temporary"
    r"|honourable members?|government members?|opposition members?"
    r"|members? interjected|a government member|an opposition member"
    r"|a member|members|an honourable member)\b", re.I)


def qld_is_chair(name):
    return is_chair(name) or bool(QLD_CHAIR.search(name))


def header_date(line):
    """YYYY-MM-DD from a running-header line, else None."""
    m = HDR_DATE.search(line.strip())
    if not m:
        return None
    d, mo, y = (m.group(1), m.group(2), m.group(3)) if m.group(1) else \
               (m.group(4), m.group(5), m.group(6))
    return f"{y}-{MONTHS[mo]:02d}-{int(d):02d}"


def bare_surname(label):
    """'Hon. YM D’ATH (Redcliffe—ALP) (Attorney-General)' -> 'D’ATH'."""
    core = re.sub(r"\(.*", " ", label)                       # drop brackets
    core = re.sub(r",\s*by leave.*", " ", core, flags=re.I)
    core = re.sub(r"^\s*Hon\.?\s+", "", core)
    core = re.sub(r"^\s*" + TITLE, "", core)
    core = re.sub(r"^\s*[A-Z]{1,3}\s+", "", core)            # leading initials
    return core.strip(" .,")


def surname_is_caps(label):
    """QLD Hansard: floor-holder surname in CAPS, interjector in mixed case."""
    letters = [c for c in bare_surname(label) if c.isalpha()]
    if len(letters) < 2:
        return False
    return sum(c.isupper() for c in letters) / len(letters) >= 0.6


def page_paragraphs(page):
    """(text, is_heading) paragraphs for one page, running header stripped."""
    lines = [ln.rstrip() for ln in page.split("\n")]
    idx = [i for i, ln in enumerate(lines) if ln.strip()]
    # strip the running header: leading centred / page-number / date lines
    drop = set()
    for i in idx[:4]:
        s = lines[i].strip()
        ind = len(lines[i]) - len(lines[i].lstrip())
        if (PAGENUM.match(s) or set(s) <= set("_-— ") or header_date(s)
                or (ind >= HEADING_INDENT and len(s) <= 95)):
            drop.add(i)
        else:
            break

    out, buf, buf_head = [], [], False
    for i, ln in enumerate(lines):
        if i in drop or not ln.strip():
            if buf:
                out.append((" ".join(buf), buf_head))
                buf, buf_head = [], False
            continue
        ind = len(ln) - len(ln.lstrip())
        s = ln.strip()
        head = ind >= HEADING_INDENT and len(s) <= 95
        if ind >= PARA_INDENT or head:
            if buf:
                out.append((" ".join(buf), buf_head))
                buf, buf_head = [], False
            buf_head = head
        if head and buf:                     # wrapped heading continuation
            buf.append(s)
            continue
        buf.append(s)
    if buf:
        out.append((" ".join(buf), buf_head))
    return out


def extract_file(pdf, prov="QLD"):
    name = Path(pdf).name
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})", name)
    file_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    txt = dehyphenate(txt)

    out = []
    turn = 0
    speaker = None
    speaker_full = None
    parts = []
    date = file_date
    seen_dates = Counter()

    def close():
        nonlocal parts, speaker, speaker_full, turn
        # chair test runs on the BARE SURNAME: portfolio titles inside the
        # brackets ("Minister Assisting...", "Acting Premier") must not be
        # mistaken for chair roles.
        if speaker and parts and not qld_is_chair(speaker):
            body = INLINE_BRACKET.sub(" ", " ".join(parts))
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                before = len(out)
                pack_turn(prov, date, turn, speaker, sentences(body), out)
                for r in out[before:]:
                    r["speaker_full"] = speaker_full
                turn += 1
        parts, speaker, speaker_full = [], None, None

    for page in txt.split("\f"):
        # page date from the running header (first few non-blank lines)
        nonblank = [l for l in page.split("\n") if l.strip()][:4]
        for l in nonblank:
            pd = header_date(l)
            if pd:
                seen_dates[pd] += 1
                if pd != date:
                    close()
                    date = pd
                    turn = 0
                break

        for para, is_head in page_paragraphs(page):
            if is_head:
                close()
                continue
            if (SKIP_PARA.match(para) or STAGE.match(para)
                    or INTERJECTED.match(para) or COLLECTIVE.match(para)):
                close()
                continue
            sm = SPEAKER.match(para)
            if sm and len(sm.group(1)) <= 200:
                label = sm.group(1).strip()
                if not surname_is_caps(label):       # interjection
                    close()
                    continue
                close()
                speaker = bare_surname(label)
                speaker_full = re.sub(
                    r"\s*\(\s*\d{1,2}[.:]\d{2}\s*[ap]\.?m\.?\s*\)", "",
                    label).strip(" ,")
                rest = sm.group(2).strip()
                if rest:
                    parts.append(rest)
                continue
            if speaker:
                parts.append(para)
    close()
    return out, len(txt.split()), seen_dates, file_date


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    mismatch = []
    with open(out_path, "w") as fh:
        for pdf in sorted(raw_dir.glob("*.[pP][dD][fF]")):
            try:
                recs, rw, seen, fdate = extract_file(pdf)
            except Exception as e:
                print(f"FAIL {pdf.name}: {e}", file=sys.stderr)
                continue
            if seen and set(seen) != {fdate}:
                mismatch.append((pdf.name, fdate, dict(seen)))
            raw_words += rw
            for r in recs:
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    for mm in mismatch[:20]:
        print(f"DATEMISMATCH {mm}", file=sys.stderr)
    print(f"files with header dates != filename date: {len(mismatch)}",
          file=sys.stderr)
    print(f"wrote {n} segments; kept {kept_words}/{raw_words} raw words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
