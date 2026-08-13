#!/usr/bin/env python3
"""Scottish Parliament Official Report (plenary) -> shared segment schema.

Source is the parliament's own open-data API, one JSON document per calendar
year: https://data.parliament.scot/api/orsplenarymeeting?year=YYYY .  Each
element is a single Official Report *contribution* (roughly a paragraph) with
its meeting, item of business, person, and edited text already separated, so
there is no HTML scraping to do -- only filtering and packing.

Filtering:
  - Detail.SpeakerName / Person null  -> narration, motions as tabled, division
    lists, "On resuming--", schedule text.  Dropped.
  - Detail.SpeakerOffice or SpeakerDisplayName naming a chair (Presiding
    Officer, Deputy Presiding Officer, Convener, Deputy Convener) -> dropped.
    Note this is role-based, so a Presiding Officer's contributions made as a
    constituency member (SpeakerDisplayName "Alex Fergusson (Galloway ...)")
    are KEPT, which is what we want.
  - Collective/procedural voices ("Members", "Some members") -> dropped.
  - EditedTextHTML is preferred over EditedText: the plain field drops the
    whitespace that <br/> carried, welding sentences together.

Turns: consecutive kept contributions by the same speaker inside one meeting,
in ContributionID order (verified equal to (item DisplayOrder, contribution
DisplayOrder) order).  A change of item of business also closes a turn.
Contributions are the packing units, windows <=360 words, minimum 50.

Usage: python3 scot_extract.py RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import MAX_WORDS, pack_turn, sentences

TAG = re.compile(r"<[^>]+>")
NBSP_BR = re.compile(r"<br\s*&nbsp;\s*/?>", re.I)
BR = re.compile(r"<br\s*/?>", re.I)
PARA_BREAK = re.compile(r"(?:</p>|(?:\s*<br\s*/?>\s*){2,})", re.I)
CHAIR_OFFICE = re.compile(
    r"presiding officer|^the convener|^the deputy convener|^the chair", re.I)
CHAIR_DISPLAY = re.compile(
    r"^\s*(?:\d+\.\s*)?the\s+(deputy\s+)?(presiding\s+officer|convener|chair)"
    r"\b", re.I)
COLLECTIVE = re.compile(
    r"^\s*(some\s+)?members?\s*$|^\s*a\s+member\s*$|^\s*members?\s+"
    r"(indicated|agreed)", re.I)


def clean(raw):
    t = TAG.sub(" ", NBSP_BR.sub(" ", raw))
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def paragraphs(raw):
    """EditedTextHTML -> packing units.

    A 'contribution' in this API is frequently a whole speech (max seen: 8,207
    words), so the contribution itself cannot be the unit.  Two markup eras
    carry the paragraph structure: pre-2011 rows use '<br/><br/>' between
    paragraphs, 2015+ rows use '<p>' blocks with single '<br />' inside.  Split
    on both, then sentence-split any paragraph still over the window size so
    packing can never emit a segment wider than MAX_WORDS.
    """
    units = []
    for part in PARA_BREAK.split(NBSP_BR.sub(" ", raw or "")):
        text = clean(BR.sub(" ", part))
        if not text:
            continue
        if len(text.split()) > MAX_WORDS:
            units.extend(sentences(text))
        else:
            units.append(text)
    return units


def is_chair(rec):
    d = rec["Detail"]
    off = d.get("SpeakerOffice") or ""
    disp = d.get("SpeakerDisplayName") or ""
    name = d.get("SpeakerName") or ""
    return bool(CHAIR_OFFICE.search(off) or CHAIR_DISPLAY.match(disp)
                or CHAIR_DISPLAY.match(name))


def person_name(person):
    """'Sturgeon, Nicola' -> 'Nicola Sturgeon'.  Person.ID is 1:1 with this
    field (181 ids / 181 names in 2016), so it is the stable speaker identity;
    Detail.SpeakerName is a *role* label in ~10% of rows ('The First
    Minister'), which would fragment a speaker's history."""
    n = (person.get("ParliamentaryName") or "").strip()
    if "," in n:
        surname, _, rest = n.partition(",")
        return f"{rest.strip()} {surname.strip()}".strip()
    return n


def contributions(recs):
    """Yield (meeting_id, date, speaker, person_id, item_id, units) in order."""
    for r in sorted(recs, key=lambda r: (r["Meeting"]["ID"],
                                         r["Detail"]["ContributionID"])):
        d = r["Detail"]
        label = (d.get("SpeakerName") or "").strip()
        if not label or r.get("Person") is None:
            continue
        if COLLECTIVE.match(label) or is_chair(r):
            continue
        # No ParliamentaryName => not a member: Time for Reflection guests,
        # the Lord Advocate before appointment, ceremonial addresses.
        name = person_name(r["Person"])
        if not name:
            continue
        units = paragraphs(d.get("EditedTextHTML") or "") \
            or ([clean(d.get("EditedText") or "")] if d.get("EditedText") else [])
        units = [u for u in units if u]
        if not units:
            continue
        date = (r["Time"]["Start"] or "")[:10]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", date):
            continue
        yield (r["Meeting"]["ID"], date, name, r["Person"]["ID"],
               r["ItemOfBusiness"]["ID"], units)


def extract_year(path, prov="SCO"):
    recs = json.load(open(path))
    raw_words = sum(len(clean(BR.sub(" ", r["Detail"].get("EditedTextHTML")
                                     or r["Detail"].get("EditedText") or "")).split())
                    for r in recs)
    out = []
    turn = 0
    cur = None          # (meeting, date, speaker, item)
    units = []

    def close():
        nonlocal units, cur, turn
        if cur and units:
            before = len(out)
            pack_turn(prov, cur[1], turn, cur[2], units, out)
            for r in out[before:]:
                r["person_id"] = cur[3]
            turn += 1
        units, cur = [], None

    for meeting, date, name, pid, item, paras in contributions(recs):
        key = (meeting, date, name, pid, item)
        if key != cur:
            close()
            cur = key
        units.extend(paras)
    close()
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    with open(out_path, "w") as fh:
        for f in sorted(raw_dir.glob("orsplenarymeeting_*.json")):
            recs, rw = extract_year(f)
            raw_words += rw
            for r in recs:
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
            print(f"{f.name}: {len(recs)} segments", file=sys.stderr)
    print(f"wrote {n} segments; kept {kept_words}/{raw_words} contribution words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
