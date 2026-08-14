#!/usr/bin/env python3
"""Northern Ireland Assembly Official Report (plenary) -> shared segment schema.

Two eras, two entirely different sources:

  * 2006-2010 -- static HTML on archive.niassembly.gov.uk, a Word export with
    stable class names across all three sub-archives (the 2006 Assembly, the
    2006-07 Transitional Assembly, and the restored Assembly from May 2007).
    A turn opens with <p class="B1SpeakersName"><strong>Name</strong>: ...;
    continuation paragraphs are B3BodyText / B3BodyTextnoindent.
  * 2012-2026 -- data.niassembly.gov.uk's Hansard open-data API, one JSON
    document per sitting (GetHansardComponentsByReportId_JSON).  Components
    arrive in document order; a Speaker component opens a turn and the
    Spoken Text components that follow are its paragraphs.

    The API itself has two markup eras.  From 2015 the ComponentType carries a
    parenthesised role -- "Speaker (MlaName)", "Speaker (Speaker)",
    "Speaker (DeputySpeaker)" -- and the chair is identified from that role.
    Before that (its earliest report is 10 September 2012) the type is the bare
    string "Speaker" and the role is not encoded anywhere, so the chair has to
    be identified from the printed label, exactly as the 2006-2010 archive era
    already does: "Mr Speaker:", "Mr Deputy Speaker:", "Mr Principal Deputy
    Speaker:" all match CHAIR.  No file from 2015 onwards contains a bare
    "Speaker" component (checked across all 248 built api_*.json files), so
    this branch cannot reach the already-built corpus.

Excluded in both eras: the chair (Speaker, Deputy/Principal Deputy/Acting
Speaker, Madam Speaker), headings, motions as tabled, tabled oral/written
questions, division and roll lists, the table of contents, and time markers.
Quoted matter (Q1QuoteIndented / ComponentType "Quote") is also dropped -- it
is read aloud but not the member's own production, which is what a register
measurement needs; the surrounding turn continues across it.

Usage: python3 ni_extract.py RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import MAX_WORDS, pack_turn, sentences

TAG = re.compile(r"<[^>]+>")
BR = re.compile(r"\r?<BR\s*/?>\r?", re.I)

# --- chair / non-member voices, both eras -----------------------------------
CHAIR = re.compile(
    r"^(mr|madam|the)?\s*(principal\s+)?(deputy\s+)?speaker\b"
    r"|^madam\s+principal\s+deputy\s+speaker"
    r"|presiding\s+officer|^the\s+chairperson\s*$|^some\s+members"
    r"|^a\s+member\s*$|^members\s*$|^the\s+clerk", re.I)

OFFICE_NAME = re.compile(r"^The\s+.*\(([^)]+)\)\s*$")
DATE_FROM_API = re.compile(r"api_(\d{4}-\d{2}-\d{2})")


def api_speaker(label):
    """'The Minister of Health (Mr Hamilton):' -> 'Mr Hamilton'.

    The 2006-2010 archive labels ministers by office only, so this cannot make
    the two eras fully commensurable; it does at least keep a minister's API-era
    contributions filed under the same name as their backbench ones.
    """
    n = label.strip().rstrip(":").strip()
    m = OFFICE_NAME.match(n)
    return (m.group(1).strip() if m else n)



# --- 2006-2010 archive HTML -------------------------------------------------
BODY_CLS = {"b3bodytext", "b3bodytextnoindent"}
QUOTE_CLS = {"q1quoteindented", "q2quotecentred", "q1quoteindentednospace"}
NEUTRAL_CLS = {"timeperiod"}          # skip, but do not end the turn
PARA_RE = re.compile(r'<p\s+class="([^"]+)"[^>]*>(.*?)</p>', re.S | re.I)
STRONG = re.compile(r"<strong>(.*?)</strong>\s*:?\s*", re.S | re.I)
# arch_* is the frozen archive site (cp1252); live_* is the same Word-export
# markup served by the modern CMS on the live per-day pages (UTF-8), which is
# how ni_gap_extract.py reaches 2011-12-12 .. 2012-03-27
DATE_FROM_NAME = re.compile(r"(?:arch|live)_(\d{4}-\d{2}-\d{2})")


def clean(raw):
    t = TAG.sub(" ", BR.sub(" ", raw))
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).replace(" ", " ").strip()


def units_of(text):
    """One paragraph -> packing units, sentence-split if over the window."""
    if not text:
        return []
    return sentences(text) if len(text.split()) > MAX_WORDS else [text]


def extract_archive(path, prov="NI", encoding="cp1252"):
    date = DATE_FROM_NAME.search(path.name).group(1)
    h = path.read_bytes().decode(encoding, "replace")
    out, turn, speaker, units = [], 0, None, []
    raw_words = 0

    def close():
        nonlocal units, speaker, turn
        if speaker and units:
            pack_turn(prov, date, turn, speaker, units, out)
            turn += 1
        units, speaker = [], None

    for m in PARA_RE.finditer(h):
        cls = re.sub(r"[^a-z0-9]", "", m.group(1).lower())
        body = m.group(2)
        text = clean(body)
        raw_words += len(text.split())
        if cls in NEUTRAL_CLS or cls in QUOTE_CLS:
            continue
        if cls == "b1speakersname":
            close()
            s = STRONG.search(body)
            if not s:
                continue
            name = clean(s.group(1)).rstrip(":").strip()
            if not name or CHAIR.match(name):
                continue
            speaker = api_speaker(re.sub(r"\s+", " ", name))
            rest = clean(body[s.end():]).lstrip(": ").strip()
            units.extend(units_of(rest))
        elif cls in BODY_CLS:
            if speaker:
                units.extend(units_of(text))
        else:                       # headings, motions, questions, divisions
            close()
    close()
    return out, raw_words


# --- 2015-2019 open-data JSON ----------------------------------------------
CHAIR_TYPE = re.compile(
    r"^Speaker \((Speaker|DeputySpeaker|PrincipalDeputySpeaker|ActingSpeaker"
    r"|TemporarySpeaker|Special)\)$")
# "Speaker (MlaName)" from 2015 on; bare "Speaker" in the 2012-2014 documents
SPEAKER_TYPE = re.compile(r"^Speaker(?: \(|$)")
BODY_TYPE = {"Spoken Text"}
NEUTRAL_TYPE = {"Time"}
def extract_api(path, prov="NI"):
    date = DATE_FROM_API.search(path.name).group(1)
    doc = json.load(open(path))["AllHansardComponentsList"]
    comps = doc["HansardComponent"] if isinstance(doc, dict) else doc
    out, turn, speaker, pid, units = [], 0, None, None, []
    raw_words = 0

    def close():
        nonlocal units, speaker, pid, turn
        if speaker and units:
            before = len(out)
            pack_turn(prov, date, turn, speaker, units, out)
            for r in out[before:]:
                r["person_id"] = pid
            turn += 1
        units, speaker, pid = [], None, None

    for c in comps:
        ctype = c.get("ComponentType") or ""
        text = clean(c.get("ComponentText") or "")
        raw_words += len(text.split())
        if ctype in NEUTRAL_TYPE or ctype == "Quote":
            continue
        if SPEAKER_TYPE.match(ctype):
            close()
            if CHAIR_TYPE.match(ctype):
                continue
            name = api_speaker(text)
            if not name or CHAIR.match(name):
                continue
            speaker, pid = name, c.get("RelatedItemId")
        elif ctype in BODY_TYPE:
            if speaker:
                for para in BR.split(c.get("ComponentText") or ""):
                    units.extend(units_of(clean(para)))
        else:                       # Header, Question, Division, Procedure Line
            close()
    close()
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept = 0
    files = sorted(list(raw_dir.glob("arch_*.htm")) + list(raw_dir.glob("api_*.json")))
    with open(out_path, "w") as fh:
        for f in files:
            try:
                recs, rw = (extract_archive(f) if f.suffix == ".htm"
                            else extract_api(f))
            except Exception as e:
                print(f"FAIL {f.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            for r in recs:
                kept += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"files {len(files)}; wrote {n} segments; kept {kept}/{raw_words} "
          f"raw document words ({kept/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
