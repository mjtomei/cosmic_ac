#!/usr/bin/env python3
"""BC Hansard HTML -> shared segment schema.

Two eras in scope:
  - legacy (.htm, 2006-2016): Dreamweaver-era markup; speech paragraphs are
    <p> chunks, a new turn opens with <b>Name:</b> at paragraph start;
    center-aligned paragraphs are section headings (end turn) except
    "[ Page NNNN ]" markers (skip only); right-aligned paragraphs are webcast
    timestamps (skip only); plain narration ("Motion approved.") matched by
    a procedural regex ends the turn. TOC and division lists live in
    <table> blocks, which are removed wholesale.
  - modern (.html, 2017-2019): semantic classes (SpeakerBegins/SpeakerContinues
    etc.); parsed from paragraph class attributes; name in span.attribution.
  - 2025+ (.html, 43rd Parliament, new publishing system): same paragraph-class
    scheme, but name in span.Speaker-Name and renamed heading classes.
    Added 2026-08 for the 2025+ extension; dispatched on the span.Speaker-Name
    signature. The two older branches are byte-identical (re-verified on 17
    files spanning 2006-2019).

Units for packing are the original paragraphs.

Usage: python3 bc_extract.py RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn

TAG = re.compile(r"<[^>]+>")
DATE_FROM_NAME = re.compile(r"(\d{4})(\d{2})(\d{2})[ap]m-")
BOLD_SPK = re.compile(
    r"^(?:\s|&nbsp;)*<b>(?:\s|&nbsp;)*([^<:]{1,60}?)\s*:?\s*</b>\s*:?",
    re.I | re.S)
PAGE_MARK = re.compile(r"^\[?\s*Page\s+\d+\s*\.?\s*\]?$", re.I)
TIME_MARK = re.compile(r"^\[\d{3,4}\]$")
PROC = re.compile(
    r"^(Motion (approved|negatived)|Interjections?\.?|Applause|Laughter"
    r"|Division|Amendment (approved|negatived)|Leave granted\.?"
    r"|The House (met|adjourned|recessed|resumed|divided).*"
    r"|The committee (rose|met|recessed).*|Committee of Supply.*"
    r"|Bill .{0,200}(read a (first|second|third)|introduced).*"
    r"|.{0,120}(moved adjournment|in the chair)\.?"
    r"|.{0,100}presented a (bill|report|petition).*"
    r"|On the (motion|amendment).*|Point of order.*"
    r"|.{0,80}tabled the following.*|Motions? without notice"
    r"|Prayers.*|Introductions by Members|Question of privilege.*)$",
    re.I | re.S)


def clean(raw):
    t = TAG.sub(" ", raw)
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def read_html(path):
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", "replace")


def extract_legacy(h, prov, date):
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<table\b.*?</table>", " ", h, flags=re.S | re.I)
    if "<body" in h.lower():
        h = re.split(r"<body[^>]*>", h, flags=re.I)[-1]

    out = []
    turn = 0
    speaker = None
    paras = []

    def close():
        nonlocal paras, speaker, turn
        if speaker and paras and not is_chair(speaker):
            pack_turn(prov, date, turn, speaker, paras, out)
            turn += 1
        paras, speaker = [], None

    for chunk in re.split(r"<p\b", h)[1:]:
        attrs, _, rest = chunk.partition(">")
        align = ""
        m = re.search(r"align\s*=\s*[\"']?(\w+)", attrs, re.I)
        if m:
            align = m.group(1).lower()
        m = re.search(r"text-align\s*:\s*(\w+)", attrs, re.I)
        if m:
            align = m.group(1).lower()
        text = clean(rest)
        if not text:
            continue
        if align == "right":                       # webcast timestamp anchor
            continue
        if PAGE_MARK.match(text) or TIME_MARK.match(text):
            continue
        if align == "center":                      # section heading
            close()
            continue
        bm = BOLD_SPK.match(rest)
        if bm:
            close()
            speaker = clean(bm.group(1)).rstrip(":").strip()
            body = clean(rest[bm.end():])
            if body:
                paras.append(body)
            continue
        if text.startswith("[") and text.endswith("]"):
            continue
        if PROC.match(text):
            close()
            continue
        if speaker:
            paras.append(text)
    close()
    return out


ATTR_SPAN = re.compile(
    r"<span[^>]*class=[\"'][Aa]ttribution[\"'][^>]*>(.*?)</span>", re.S)
# normalized class-name sets (lowercase, non-letters stripped)
CLS_HEADING = {"subjectheading", "procedureheading", "proceduralheading",
               "proceedingheading", "headingcontinued", "chairchange",
               "chairchangemidspeech", "styleline", "stylelinetime"}
CLS_SKIP_PREFIX = ("toclevel", "divisionname", "divisionheader", "timeline",
                   "blockquote", "amendment", "motion", "logo", "footer",
                   "title", "date", "sitting", "parliamentsession",
                   "timestamp")


def extract_modern(h, prov, date):
    out = []
    turn = 0
    speaker = None
    paras = []

    def close():
        nonlocal paras, speaker, turn
        if speaker and paras and not is_chair(speaker):
            pack_turn(prov, date, turn, speaker, paras, out)
            turn += 1
        paras, speaker = [], None

    for chunk in re.split(r"<p\b", h)[1:]:
        attrs, _, rest = chunk.partition(">")
        m = re.search(r"class\s*=\s*[\"']([^\"']+)", attrs, re.I)
        cls = re.sub(r"[^a-z]", "", (m.group(1) if m else "").lower())
        rest = rest.split("</p>")[0]
        if cls == "speakerbegins":
            close()
            am = ATTR_SPAN.search(rest)
            name = clean(am.group(1)).rstrip(":").strip() if am else ""
            body = clean(ATTR_SPAN.sub(" ", rest)) if am else clean(rest)
            if name:
                speaker = name
                if body:
                    paras.append(body)
        elif cls == "speakercontinues":
            if speaker:
                text = clean(rest)
                if text:
                    paras.append(text)
        elif cls in CLS_HEADING:
            close()
        elif cls.startswith(CLS_SKIP_PREFIX) or cls:
            continue
        else:                       # class-less paragraph inside a turn
            text = clean(rest)
            if speaker and text:
                paras.append(text)
    close()
    return out


# --- 2025+ era (43rd Parliament, new Hansard publishing system) -------------
# Same paragraph-class scheme as the 2017-2019 "modern" era, but the speaker's
# name moved from <span class="attribution">Name: </span> to
# <span class="Speaker-Name">Name</span><span class="Bold">:</span>, and the
# heading class names were renamed (procedure-heading -> Business-Heading etc.).
# Dispatched on the span.Speaker-Name signature, which no earlier era carries;
# the two existing branches are untouched.
# the name is sometimes split across consecutive Speaker-Name spans
# ("A "+"Voice", "Jeremy "+"Valeriote"), so consume the whole leading run
NAME_SPAN = re.compile(
    r"(?:\s|<a\b[^>]*>|</a>)*"
    r"<span[^>]*class=[\"']Speaker-Name[\"'][^>]*>(.*?)</span>", re.S | re.I)


BOLD_TAIL = re.compile(
    r"(?:\s|</span>)*"          # closes any span nested inside Speaker-Name
    r"<span[^>]*class=[\"']Bold[\"'][^>]*>\s*([A-Za-z'’.\- ]{0,30}:)\s*</span>",
    re.S | re.I)


def speaker_name(rest):
    """Split a SpeakerBegins paragraph into (name, remaining html)."""
    pos, parts = 0, []
    while True:
        m = NAME_SPAN.match(rest, pos)
        if not m:
            break
        parts.append(m.group(1))
        pos = m.end()
    if not parts:
        return None, rest
    name = clean(" ".join(parts)).rstrip(":").strip()
    # the colon normally sits in a following <span class="Bold">:</span>; in a
    # handful of files part of the surname is stranded in that span too
    # ("<Speaker-Name><Bold>Rob</Bold></Speaker-Name><Bold> Botterell: </Bold>")
    m = BOLD_TAIL.match(rest, pos)
    if m:
        extra = clean(m.group(1)).rstrip(":").strip()
        if extra:
            name = (name + " " + extra).strip()
        pos = m.end()
    return name, rest[pos:]
CLS2025_HEADING = {
    "subjectheading", "subjectheadingnotoc", "businessheading",
    "businessheadingnotoc", "proceedings", "proceedingsnotoc",
    "proceedingsinroom", "chairchange", "chairchangemidspeech",
    "styleline", "stylelinetoc", "headingleft", "headingboldleft",
    "headingcontinued", "procedureheading", "proceduralheading",
    "proceedingheading",
}


def extract_modern2025(h, prov, date):
    out = []
    turn = 0
    speaker = None
    paras = []

    def close():
        nonlocal paras, speaker, turn
        if speaker and paras and not is_chair(speaker):
            pack_turn(prov, date, turn, speaker, paras, out)
            turn += 1
        paras, speaker = [], None

    for chunk in re.split(r"<p\b", h)[1:]:
        attrs, _, rest = chunk.partition(">")
        m = re.search(r"class\s*=\s*[\"']([^\"']+)", attrs, re.I)
        cls = re.sub(r"[^a-z]", "", (m.group(1) if m else "").lower())
        rest = rest.split("</p>")[0]
        if cls in ("speakerbegins", "speakerbeginstoc"):
            close()
            name, tail = speaker_name(rest)
            if name:
                body = clean(tail).lstrip(": ").strip()
                speaker = name
                if body:
                    paras.append(body)
        elif cls.startswith("speakercontinues"):
            if speaker:
                text = clean(rest)
                if text:
                    paras.append(text)
        elif cls in CLS2025_HEADING:
            close()
        elif cls.startswith(CLS_SKIP_PREFIX) or cls:
            continue
        else:                       # class-less paragraph inside a turn
            text = clean(rest)
            if speaker and text:
                paras.append(text)
    close()
    return out


def extract_file(path, prov="BC"):
    name = Path(path).name
    m = DATE_FROM_NAME.search(name)
    date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    h = read_html(path)
    if re.search(r"<span[^>]*class=[\"']Speaker-Name[\"']", h, re.I):
        recs = extract_modern2025(h, prov, date)
    elif "SpeakerBegins" in h or "speaker-begins" in h:
        recs = extract_modern(h, prov, date)
    else:
        recs = extract_legacy(h, prov, date)
    raw_words = len(clean(re.sub(r"<(script|style)\b.*?</\1>", " ", h,
                                 flags=re.S | re.I)).split())
    return recs, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    with open(out_path, "w") as fh:
        for f in sorted(list(raw_dir.glob("*.htm")) + list(raw_dir.glob("*.html"))):
            try:
                recs, rw = extract_file(f)
            except Exception as e:
                print(f"FAIL {f.name}: {e}", file=sys.stderr)
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
