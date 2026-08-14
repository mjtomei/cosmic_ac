#!/usr/bin/env python3
"""Northern Ireland Assembly plenary, 2011-12-12 .. 2012-07-03 -> shared schema.

This is the window ni_manifest_fill.py left open: after archive.niassembly.gov.uk
froze (last sitting 2011-12-06) and before the Hansard API's first report
(2012-09-10).  The source is the Assembly's own live per-day page, which serves
the whole Official Report inline -- see ni_manifest_gap.py for the enumeration
and for why the PDF is not used.

TWO MARKUP GENERATIONS, ONE DOCUMENT

  * 2011-12-12 .. 2012-03-27 (23 sitting days).  The page still carries the
    Word export's class names, the same vocabulary the frozen archive uses:
    B1SpeakersName / B3BodyText / B3BodyTextnoindent / Q1QuoteIndented /
    Q3Motion / TimePeriod / OralAnswers-* / H3SubHeading.  These days are
    handed straight to ni_extract.extract_archive() -- literally the parser
    that produced 2006-2011 -- with the encoding switched to UTF-8.  No new
    rules at all.

  * 2012-04-16 .. 2012-07-03 (21 sitting days).  The CMS emits the same
    document with every class attribute stripped.  The structure survives in
    the markup itself, and maps one-for-one onto the class vocabulary:

      <p><strong>Name</strong>: text        speaker turn  (B1SpeakersName)
      <p><strong>Name:</strong> text        the same, colon inside the strong
      <p><strong>2.30 pm</strong>           time marker   (TimePeriod)
      <p>text                               body          (B3BodyText)
      <p><em>text</em>                      quoted matter, motions as tabled,
                                            divisions, procedural directions
      <p>N. <strong>Name </strong>asked ...  tabled oral question
      <p>...<a href="#a4">...</a>           table of contents
      <h1>/<h2>/<h3>                        headings

    Same exclusions as both neighbours: the chair and collective voices, the
    table of contents, headings, tabled questions, divisions, motions as
    tabled, and quoted matter.  A turn survives a time marker and a quotation
    and ends at a heading, a tabled question, a motion or direction, or the
    next label.

WHAT THE STRIPPED CLASSES COST, MEASURED

  One distinction does not survive the strip.  Q1QuoteIndented (quoted matter:
  dropped, but the surrounding turn continues across it) and Q3Motion /
  B3BodyTextItalic / division text (dropped, and the turn ends) are both just
  <em> now.  The recovered signal is the opening quotation mark, and it is
  worth having: on the 23 class-bearing days, closing at every italic block
  loses 13,478 words of members' own speech that resumes after a quotation,
  and never closing hands 8,227 words of motion text and its aftermath to the
  preceding speaker.

  The rule was chosen by simulation on those 23 days, which carry both the
  classes and the markup: rewrite every italic-class paragraph into the
  <p><em>...</em></p> the live CMS emits from 2012-04-16 (verified against the
  real pages -- 296 of 305 procedural lines there are <em>-wrapped), strip the
  classes, and score this parser against ni_extract.extract_archive on the
  original.  Against 7,236 segments / 1,062,306 words of class-based parse:

      always close at an italic block   -5.96% words, 96.9% token overlap
      close unless it opens on a quote  -0.40% words, 98.9% token overlap
      never close                       +7.80% words, 96.2% token overlap

  with the same speaker set on every day either way.  The middle rule is the
  one below.  Residual per-day error is 0.9% of words at the median, 7.5% on
  the worst single day.

  The class-bearing half needs no such argument: on 2011-12-05 and 2011-12-06,
  which the frozen archive also holds, the live page reproduces the archive's
  extraction exactly -- 540 segments, identical seg_ids, speakers and text.

Usage: python3 ni_gap_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ni_extract import CHAIR, api_speaker, clean, extract_archive, units_of
from prov_common import pack_turn

# element-level walk of the day page's <main>; <p> never nests
BLOCK = re.compile(r"<(p|h[1-6])\b[^>]*>(.*?)</\1>", re.S | re.I)
MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.S | re.I)
ANCHOR = re.compile(r"^\s*(?:<a\s+name=[^>]*>\s*</a>\s*)+", re.I)
LEAD_STRONG = re.compile(r"^\s*<strong>(.*?)</strong>", re.S | re.I)
TABLED_Q = re.compile(r"^\s*\d{1,3}\.\s*<strong>", re.I)
TIME = re.compile(r"^\d{1,2}[.:]\d{2}\s*(?:am|pm|noon|midnight)$", re.I)
# A table-of-contents entry is a bold section name -- sometimes with the colon
# inside the <strong>, which would otherwise read as a speaker label -- over a
# list of in-page links.  Across all 46 day pages, 288 paragraphs carry an
# in-page anchor and every one of them is the table of contents, so the anchor
# alone identifies it.
IN_PAGE_LINK = re.compile(r"<a\s+href=\"#", re.I)
# a paragraph is italic matter if removing the <em>/<i> spans empties it
EM = re.compile(r"<(em|i)\b[^>]*>.*?</\1>", re.S | re.I)
LEFTOVER = re.compile(r"[^\s.,;:—\-–\[\]()]")
CLASSED = re.compile(r'<p class="B1SpeakersName"', re.I)
# an opening quotation mark: the one surviving mark of quoted matter
QUOTED = re.compile("^[“‘\"']")


def is_italic_block(inner):
    if not re.search(r"<(em|i)\b", inner, re.I):
        return False
    return not LEFTOVER.search(clean(EM.sub(" ", inner)))


def extract_plain(path, prov="NI"):
    """The class-stripped generation, 2012-04-16 onwards."""
    date = re.search(r"live_(\d{4}-\d{2}-\d{2})", path.name).group(1)
    doc = path.read_bytes().decode("utf-8", "replace")
    m = MAIN.search(doc)
    body = m.group(1) if m else doc
    out, turn, speaker, units = [], 0, None, []
    raw_words = 0

    def close():
        nonlocal units, speaker, turn
        if speaker and units:
            pack_turn(prov, date, turn, speaker, units, out)
            turn += 1
        units, speaker = [], None

    for blk in BLOCK.finditer(body):
        tag, inner = blk.group(1).lower(), ANCHOR.sub("", blk.group(2))
        text = clean(inner)
        raw_words += len(text.split())
        if tag != "p":                          # heading
            close()
            continue
        if not text:
            continue
        if is_italic_block(inner):
            # Quoted matter, motions as tabled and procedural directions are
            # all italic here and all dropped; they differ only in whether the
            # turn survives them.  An opening quotation mark is the one
            # surviving signal of Q1QuoteIndented, and the turn continues
            # across it exactly as it does in the class-bearing generation.
            if not QUOTED.match(text):
                close()
            continue
        if TABLED_Q.match(inner):               # "1. Mr X asked the Minister"
            close()
            continue
        s = LEAD_STRONG.match(inner)
        if not s:
            if speaker:                         # ordinary body paragraph
                units.extend(units_of(text))
            continue
        name = clean(s.group(1))
        rest = clean(inner[s.end():])
        if not (name.endswith(":") or rest.startswith(":")):
            # a bare bold paragraph: a time marker keeps the turn alive (as
            # TimePeriod does in the class-bearing generation), anything else
            # -- a contents entry, a division heading -- ends it
            if not (TIME.match(name) and not rest):
                close()
            continue
        if IN_PAGE_LINK.search(inner):              # "Assembly Business:" + links
            close()
            continue
        close()
        name = name.rstrip(":").strip()
        if not name or CHAIR.match(name):
            continue
        speaker = api_speaker(re.sub(r"\s+", " ", name))
        units.extend(units_of(rest.lstrip(":").strip()))
    close()
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    skip = {d.strip() for d in sys.argv[3].split(",")} if len(sys.argv) > 3 else set()
    n = raw_words = kept = 0
    per = {}
    with open(out_path, "w") as fh:
        for f in sorted(raw_dir.glob("live_*.htm")):
            date = re.search(r"live_(\d{4}-\d{2}-\d{2})", f.name).group(1)
            if date in skip:
                print(f"SKIP {date} (control day, already in the corpus)",
                      file=sys.stderr)
                continue
            classed = bool(CLASSED.search(f.read_bytes().decode("utf-8", "replace")))
            try:
                recs, rw = (extract_archive(f, encoding="utf-8") if classed
                            else extract_plain(f))
            except Exception as e:              # noqa: BLE001
                print(f"FAIL {f.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            w = sum(r["n_words"] for r in recs)
            per[date] = (len(recs), w, "classed" if classed else "plain")
            if not recs:
                print(f"EMPTY {date}: no member turns extracted", file=sys.stderr)
            for r in recs:
                kept += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    for d in sorted(per):
        segs, w, gen = per[d]
        print(f"  {d} {gen:7s} {segs:5d} segs {w:7d} words", file=sys.stderr)
    print(f"days {len(per)}; wrote {n} segments; kept {kept}/{raw_words} raw "
          f"document words ({kept/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
