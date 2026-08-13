#!/usr/bin/env python3
"""Senedd Cymru / Welsh Parliament Record of Proceedings -> segment schema.

Two eras, because the Record moved systems in May 2016:

  * 2016-05-11 onward -- record.senedd.wales publishes a bilingual XML export
    per sitting.  One <XML_Plenary-*_Bilingual> record per contribution, with
    <contribution_verbatim> = AS SPOKEN and <contribution_translated> = the
    other language, plus an explicit <contribution_language> (En/Cy).  That
    label is the record's own, so it is used directly rather than detected.
  * 2006-2010 and 2015 -- nothing survives in HTML; the Record exists only as
    ModernGov PDFs.  These are two parallel columns, spoken language on the
    left and the translation on the right, so the left half of each page is
    cropped out with pdftotext (-x 0 -W <half>) and the language of the
    resulting text is detected (wales_lang, calibrated at 98.6% against the
    XML era's own labels -- see wales_calibrate_lang.py).

ENGLISH ONLY IS SCORED.  Welsh-majority segments are kept in the corpus with
lang="cy" and scoreable=false so their share stays measurable.

Excluded: the Llywydd / Presiding Officer and their deputies, agenda headings,
motions and amendments as tabled, oral questions as tabled (contribution_type
"O"; "Qn Name:" paragraphs in the PDFs), vote outcomes, and procedural text.

Usage: python3 wales_extract.py RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import MAX_WORDS, MIN_WORDS, pack_turn, sentences
from wales_lang import is_welsh

TAG = re.compile(r"<[^>]+>")
CHAIR = re.compile(
    r"llywydd|presiding officer|deputy presiding|^the chair|cadeirydd"
    r"|temporary deputy", re.I)
SUFFIX = re.compile(r"\s+(AC|AM|MS|AS)\s*$", re.I)


def clean(raw):
    return re.sub(r"\s+", " ", htmllib.unescape(TAG.sub(" ", raw or ""))).strip()


def units_of(text):
    if not text:
        return []
    return sentences(text) if len(text.split()) > MAX_WORDS else [text]


def emit(out, prov, date, turn, speaker, units, lang, source, member_id=None):
    """Pack a turn and stamp the language fields; Welsh is never scoreable."""
    before = len(out)
    pack_turn(prov, date, turn, speaker, units, out)
    for r in out[before:]:
        r["lang"] = lang
        r["lang_source"] = source
        r["member_id"] = member_id
        if lang != "en":
            r["scoreable"] = False
    return len(out) > before


# --------------------------------------------------------------------------
# 2016-2019: bilingual XML export
# --------------------------------------------------------------------------
RECORD = re.compile(r"<XML_[^>]*_Bilingual>(.*?)</XML_[^>]*_Bilingual>", re.S)


def field(block, name):
    m = re.search(f"<{name}>(.*?)</{name}>", block, re.S)
    return htmllib.unescape(m.group(1)) if m else ""


def paras_from_html(raw):
    """contribution_verbatim is escaped HTML: <p> blocks."""
    out = []
    for part in re.split(r"</p\s*>", raw, flags=re.I):
        t = clean(part)
        if t:
            out.extend(units_of(t))
    return out


def extract_xml(path, prov="WAL"):
    date = re.search(r"xml_(\d{4}-\d{2}-\d{2})", path.name).group(1)
    x = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for b in RECORD.findall(x):
        rows.append((
            int(field(b, "Contribution_Order_ID") or 0),
            field(b, "contribution_type"),
            field(b, "contribution_language"),
            field(b, "Member_Id"),
            SUFFIX.sub("", field(b, "Member_name_English")).strip(),
            field(b, "Agenda_Item_ID"),
            field(b, "contribution_verbatim"),
        ))
    rows.sort(key=lambda r: r[0])
    raw_words = sum(len(clean(r[6]).split()) for r in rows)

    out, turn, cur, units = [], 0, None, []

    def close():
        nonlocal units, cur, turn
        if cur and units:
            if emit(out, prov, cur[3], turn, cur[1], units,
                    "cy" if cur[2] == "Cy" else "en", "record-label", cur[0]):
                turn += 1
        units, cur = [], None

    for _, ctype, lang, mid, name, item, verbatim in rows:
        if ctype != "C" or not mid or not name or CHAIR.search(name):
            close()
            continue
        key = (mid, name, lang, date, item)
        if key != cur:
            close()
            cur = key
        units.extend(paras_from_html(verbatim))
    close()
    return out, raw_words


# --------------------------------------------------------------------------
# 2006-2010 and 2015: two-column bilingual PDF, left column = as spoken
# --------------------------------------------------------------------------
SPK = re.compile(
    r"^(?:(Q|C)\d+\s+)?"                       # tabled-question number, if any
    r"((?:The|Y|Yr)\s+[A-Z][^:]{0,58}|[A-Z][\w’'.\-]*(?:\s+[A-Z\w’'.\-]{1,20}){0,4})"
    r":\s+(?=\S)")
PAGENO = re.compile(r"^\s*\d{1,4}\s*$")
BAD_LABEL = re.compile(r"[.,;?!]|\bhttp\b")
# Division and procedural blocks also open with "Label: ..." shapes.
PROC_LABEL = re.compile(
    r"^(the following|pleidleisiodd|ymataliodd|gwrthodwyd|derbyniwyd|cynnig"
    r"|motion|amendment|gwelliant|question|cwestiwn|division|vote|result"
    r"|daeth|cyfarfu|ailymgynullodd|the meeting|the assembly|the record"
    r"|ataliwyd|the sitting|the debate|plaid|against|for\b|abstain)", re.I)
OFFICE_NAME = re.compile(r"^(?:The|Y|Yr)\s+.*\(([^)]+)\)\s*$")


def member_name(label):
    """'The Minister for Health and Social Services (Brian Gibbons)' ->
    'Brian Gibbons', so a minister files under the same name as when they speak
    from the back benches and as the XML era's Member_name_English."""
    m = OFFICE_NAME.match(label)
    return m.group(1).strip() if m else label


BBOX_WORD = re.compile(r'xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)"')


def find_gutter(path, w):
    """x of the white gap between the two columns.

    Not w/2: the pre-2011 Record splits at x~295 of 506 but the 2015 Record,
    which carries a timestamp gutter on the left, splits at x~285 of 551.  A
    fixed half-page crop leaks the right (translation) column into the 2015
    text.  So build an ink-occupancy profile from -bbox word boxes over a
    sample of pages and take the sparsest 5pt bin in the middle of the page.
    """
    out = subprocess.run(["pdftotext", "-bbox", "-f", "3", "-l", "14",
                          str(path), "-"],
                         capture_output=True, text=True, timeout=300).stdout
    words = [(float(a), float(b)) for a, b in BBOX_WORD.findall(out)]
    if not words:
        return w / 2
    right = max(b for _, b in words)
    bins = [0] * (int(right // 5) + 2)
    for a, b in words:
        for i in range(int(a // 5), min(int(b // 5) + 1, len(bins))):
            bins[i] += 1
    mid = [(bins[i], i * 5) for i in range(len(bins))
           if 0.3 * right < i * 5 < 0.7 * right]
    return min(mid)[1] if mid else w / 2


def pdf_left_column(path):
    """Left column of every page, layout-preserved.  Cropping is used rather
    than -layout's own column detection because the pre-2011 PDFs have unstable
    per-contribution x-offsets that defeat it."""
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True,
                          text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (595.0, 842.0)
    cut = find_gutter(path, w)
    r = subprocess.run(
        ["pdftotext", "-layout", "-x", "0", "-y", "0",
         "-W", str(int(cut)), "-H", str(int(h) + 1), str(path), "-"],
        capture_output=True, text=True, timeout=600)
    return r.stdout


def pdf_paragraphs(text):
    """Blank-line separated blocks; page numbers dropped, headings flagged.

    A heading in these PDFs is centred, so every one of its lines carries a
    deep indent; body text starts at the left margin.  Headings must close the
    open turn, page numbers must not (paragraphs run across page breaks).
    """
    for block in re.split(r"\n\s*\n", text):
        # A page number can sit inside a block when the paragraph runs across
        # the page break, so drop the numeric lines first, not the block.
        lines = [l for l in block.split("\n")
                 if l.strip() and not PAGENO.match(l)]
        if not lines:
            continue
        indent = min(len(l) - len(l.lstrip()) for l in lines)
        body = re.sub(r"\s+", " ", " ".join(l.strip() for l in lines)).strip()
        if not body:
            continue
        yield ("heading" if indent >= 20 else "body"), body


# --- 2015 layout: timestamp gutter, speaker on its own line ----------------
# 13:45   Andrew R.T. Davies Bywgraffiad Biography
#         Arweinydd yr Wrthblaid / The Leader of the Opposition
#         Presiding Officer, I make a declaration of interest ...
TIMED = re.compile(r"^\s*\d{1,2}[:.]\d{2}\s+(\S.*)$")
BIOG = re.compile(r"\s*Bywgraff\w*(\s+Biog\w*)?\s*$")
ROLE = re.compile(r"^[^.?!]{3,90}\s/\s[^.?!]{3,90}$")
RUNNING = re.compile(
    r"Cofnod y Trafodion|Record of Proceedings|Senedd Cym|National Assembly"
    r"|Cynulliad Cenedlaethol|The Senedd", re.I)


def extract_pdf_modern(path, date, text, prov="WAL"):
    out, turn, speaker, units, para = [], 0, None, [], []
    expect_role = False

    def flush_para():
        nonlocal para
        if para:
            units.extend(units_of(re.sub(r"\s+", " ", " ".join(para)).strip()))
        para = []

    def close():
        nonlocal units, speaker, turn
        flush_para()
        if speaker and units:
            joined = " ".join(units)
            if emit(out, prov, date, turn, speaker, units,
                    "cy" if is_welsh(joined) else "en", "detected"):
                turn += 1
        units, speaker = [], None

    for line in text.split("\n"):
        if RUNNING.search(line):
            continue
        if not line.strip():
            flush_para()
            continue
        m = TIMED.match(line)
        if m:
            head = m.group(1).rstrip()
            named = BIOG.search(head)
            close()
            expect_role = False
            if not named:            # a timed procedural line, not a speaker
                continue
            name = BIOG.sub("", head).strip()
            if not name or CHAIR.search(name) or PROC_LABEL.match(name):
                continue
            speaker = member_name(name)
            expect_role = True
            continue
        if expect_role:
            expect_role = False
            if ROLE.match(line.strip()):
                continue             # bilingual job title under the name
        if speaker:
            para.append(line.strip())
    close()
    return out


def extract_pdf(path, prov="WAL"):
    date = re.search(r"pdf_(\d{4}-\d{2}-\d{2})", path.name).group(1)
    text = pdf_left_column(path)
    raw_words = len(text.split())
    if "Bywgraff" in text:
        return extract_pdf_modern(path, date, text, prov), raw_words
    out, turn, speaker, units = [], 0, None, []

    def close():
        nonlocal units, speaker, turn
        if speaker and units:
            joined = " ".join(units)
            lang = "cy" if is_welsh(joined) else "en"
            if emit(out, prov, date, turn, speaker, units, lang, "detected"):
                turn += 1
        units, speaker = [], None

    for kind, body in pdf_paragraphs(text):
        if kind == "heading":
            close()
            continue
        m = SPK.match(body)
        if m:
            close()
            if m.group(1):          # "Q7 Name:" -- the tabled question text
                continue
            name = m.group(2).strip()
            if (BAD_LABEL.search(name) or CHAIR.search(name)
                    or PROC_LABEL.match(name)):
                continue
            speaker = member_name(name)
            units.extend(units_of(body[m.end():].strip()))
        elif speaker:
            units.extend(units_of(body))
    close()
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    files = sorted(list(raw_dir.glob("xml_*.xml")) + list(raw_dir.glob("pdf_*.pdf")))
    n = raw_words = kept = 0
    with open(out_path, "w") as fh:
        for i, f in enumerate(files):
            try:
                recs, rw = (extract_xml(f) if f.suffix == ".xml"
                            else extract_pdf(f))
            except Exception as e:
                print(f"FAIL {f.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            for r in recs:
                kept += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(files)}", file=sys.stderr)
    print(f"files {len(files)}; wrote {n} segments; kept {kept}/{raw_words} "
          f"raw document words ({kept/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
