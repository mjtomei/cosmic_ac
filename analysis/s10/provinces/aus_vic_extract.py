#!/usr/bin/env python3
"""Victoria (AU) Hansard HTML -> shared segment schema.

Input files are the LDMS=Y "query cell" bodies saved by aus_vic_harvest.py:
the <div class="speech-content"> of one (chamber, sitting date, activity type)
query, containing every matching ISYS document's full text concatenated.  The
first line of each file is an HTML comment carrying date/chamber/activity,
because the Victorian search app exposes no per-day URL to recover them from.

Two markup eras, both present in the study windows:

  LEGACY (1991 - mid-2015; the whole 2006-2010 window).  One <pre> block per
    ISYS document holding print-Hansard column text: hard-wrapped at ~78
    columns and WORD-JUSTIFIED, so runs of 2-6 spaces appear inside sentences
    and no paragraph structure survives.  Page breaks are "<hr /> Page 765".
    A turn opens at line start with
        "Mr  HULLS  (Attorney-General)  --  I move:"
        "Mr CLARK (Box Hill) --  I am sure the Attorney-General ..."
        "Mr HULLS  -- Whilst it might be smart for those opposite ..."
    i.e. title + ALL-CAPS surname, optional (electorate/office), then " -- ".
    Third-person narration in the same shape but WITHOUT the dash ("Mr HOWARD
    (Buninyong) presented report") is procedural and is not a turn.

  MODERN (mid-2015 to late 2018).  No <pre>; ordinary
    <p> paragraphs, speaker marked by leading bold spans:
        <p><b>Mr</b>&nbsp;<b>BROOKS</b> (Bundoora)&nbsp;&mdash; I rise to ...
    Once entity-decoded and de-tagged these render as exactly the same
    "Mr BROOKS (Bundoora) - text" shape, so ONE speaker regex serves the eras.

  59th PARLIAMENT (late 2018 onward, i.e. Dec 2018 + all of 2019).  No markup
    at all inside the body -- one plain-text line per ISYS document, the whole
    speech on that line, opened by
        "Mr PALLAS (Werribee-Treasurer, Minister for ...) (16:29:34): I move:"
    i.e. a COLON separator after a wall-clock timestamp rather than a dash, and
    a portfolio list inside the parenthetical that runs well past 80 chars.
    Missing this era silently emptied 2019 on the first extraction pass.

  60th PARLIAMENT (2023 onward; the whole 2025-2026 extension window).  Back to
    <p> markup, but the honorific is GONE: Hansard now prints the given name
    plus an ALL-CAPS surname, keeping the 59th's timestamp-then-colon:
        "Jacinta ALLAN (Bendigo East - Premier) (12:09): I move:"
    Every earlier era's speaker line begins with a title, so the title-anchored
    SPEAKER pattern matches none of these and 2025-2026 would have come out
    empty exactly the way 2019 did.  Handled by SPEAKER_60, tried first but
    only in files that carry the no-title form (era60 in extract_file), so the
    three older eras produce byte-identical output.

Because the legacy era destroys paragraph boundaries, sentences() is used as
the packing unit for both eras (as in sk_extract.py), keeping window sizes
comparable across the two windows -- important, since the two eras line up
exactly with the two drift windows and any packing difference would be
confounded with the effect under study.

Chair and procedural voices are dropped via prov_common.is_chair() plus a
Victorian extension (President, Deputy President, Acting Speaker, Chair of
Committees, Serjeant-at-Arms, "Honourable members interjecting", "A member").

Usage: python3 aus_vic_extract.py RAW_DIR OUT_JSONL [GLOB]
       (GLOB defaults to *.html; pass "AS_*.html" for the Assembly alone)
"""
import html as htmllib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences

HEADER = re.compile(r"^<!--(\d{4}-\d{2}-\d{2}) (\w+) (.*?)-->")
TAG = re.compile(r"<[^>]+>")

# Title + ALL-CAPS surname [+ (electorate/office)] + em/en/double dash.
SPEAKER = re.compile(
    r"^\s{0,10}((?:The|Mr|Mrs|Ms|Miss|Dr|Hon|Sir|Prof)\.?\s+"
    r"[A-Z][A-Za-z'’.\-]*(?:\s+[A-Z][A-Za-z'’.\-]*){0,3})"
    r"\s*(?:\(([^)]{1,200})\))?"          # electorate and/or portfolio list
    r"\s*(?:\(\d{1,2}:\d{2}(?::\d{2})?\))?"   # 59th-Parliament timestamp
    r"\s*(?:--|—|–|:)\s*(.*)$")
# Require a run of capitals somewhere in the name, so prose like
# "The Government -- " or "Mr Speaker -- " is rejected while HULLS, GUY,
# McINTOSH and D'AMBROSIO are all accepted.
CAPS = re.compile(r"[A-Z]{3,}")

# 60th PARLIAMENT (2023 onward; the whole 2025-2026 extension window).  Same
# <p> delivery markup as the MODERN era, but Hansard dropped the honorific and
# now prints "given name + ALL-CAPS SURNAME", with the 59th Parliament's
# timestamp-then-colon separator:
#     "Jacinta ALLAN (Bendigo East - Premier) (12:09): I move:"
#     "Bev McARTHUR (Western Victoria) (13:39): I was interested to read ..."
# SPEAKER above requires a leading title, so on its own it matches NONE of
# these and the whole period would come out empty -- the same silent-zero
# failure the 59th Parliament caused in 2019.  This pattern is tried FIRST but
# only in files whose lines actually carry the no-title form (see era60 in
# extract_file), so the three earlier eras are untouched.
SPEAKER_60 = re.compile(
    r"^\s{0,10}((?!(?:The|Mr|Mrs|Ms|Miss|Dr|Hon|Sir|Prof)[\s.])"
    r"[A-Z][A-Za-z'’.\-]*(?:\s+[A-Z][A-Za-z'’.\-]*){0,3})"
    r"\s*\(([^)]{1,300})\)"                   # electorate and/or portfolio list
    r"\s*\((\d{1,2}:\d{2}(?::\d{2})?)\)"      # wall-clock timestamp
    r"\s*:\s*(.*)$")


# The 60th Parliament's CONTINUATION form: once a member has the call, later
# paragraphs of the same exchange (committee stage, interjected replies) are
# re-attributed with the bare name and no timestamp --
#     "Jaclyn SYMES: I will not be supporting this amendment ..."
# The earlier eras have the same habit ("Mr PALLAS: ...") and the title-anchored
# SPEAKER pattern already catches those, so 2025-2026 needs this to stay
# comparable: without it those paragraphs are either dropped or, worse, glued
# onto whoever spoke last.  The first token must be Title case, which keeps
# ALL-CAPS bill headings ("STATE TAXATION ACTS AMENDMENT BILL: ...") out.
SPEAKER_60B = re.compile(
    r"^\s{0,10}((?!(?:The|Mr|Mrs|Ms|Miss|Dr|Hon|Sir|Prof)[\s.])"
    r"[A-Z][a-z][A-Za-z'’\-]*(?:\s+[A-Z][A-Za-z'’\-]*){1,2})\s*:\s+(\S.*)$")


# Same continuation form, but with the surname in TITLE case -- how the 60th
# Parliament prints interjections and points of order:
#     "Brad Rowswell: On a point of order, Speaker, ..."
# There is no capitalisation cue left to separate these from ordinary prose, so
# they are accepted only when the name is one already seen speaking in this
# corpus (match60/match60b supply the roster).  On the 2025-2026 window that
# rule fires on 3,817 lines and rejects 1.  The older eras print the same
# interjections WITH a title, where SPEAKER already catches them and
# norm_speaker folds "Mr McIntosh" onto "Mr McINTOSH"; this is that fold.
SPEAKER_60C = re.compile(
    r"^\s{0,10}((?!(?:The|Mr|Mrs|Ms|Miss|Dr|Hon|Sir|Prof)[\s.])"
    r"[A-Z][a-z][A-Za-z'’\-]*(?:\s+[A-Z][A-Za-z'’\-]*){1,2})\s*:\s+(\S.*)$")


def match60(line):
    """SPEAKER_60 match whose surname really is an ALL-CAPS surname."""
    m = SPEAKER_60.match(line)
    return m if m and CAPS.search(m.group(1).split()[-1]) else None


def match60b(line):
    """SPEAKER_60B (continuation) match, same ALL-CAPS-surname requirement."""
    m = SPEAKER_60B.match(line)
    return m if m and CAPS.search(m.group(1).split()[-1]) else None


def match60c(line, roster):
    """SPEAKER_60C (title-case interjection) match against a known roster."""
    m = SPEAKER_60C.match(line)
    return m if m and norm_speaker_60(m.group(1)).upper() in roster else None


def norm_speaker_60(name):
    """'Bev McARTHUR' -> 'Bev MCARTHUR'; surname cased like the older eras."""
    toks = re.sub(r"\s+", " ", name).strip().split()
    return " ".join(toks[:-1] + [toks[-1].upper()])

# Victorian chair / collective / procedural voices, on top of prov_common's.
VIC_CHAIR = re.compile(
    r"president|deputy speaker|acting speaker|chair of committees|serjeant"
    r"|sergeant|honourable member|honorable member|a member|members interject"
    r"|the clerk|usher", re.I)

# "Mr SCOTT (Minister for Finance) tabled following statement ..." -- Hansard's
# third-person narration of tabled matter, which is NOT the member speaking.
NARR = re.compile(
    r"^\s{0,10}(?:Mr|Mrs|Ms|Miss|Dr|Hon|Sir|The)\.?\s+"
    r"(?:(?!--|—|–)[^\n]){0,80}?"          # stop before any speech dash
    r"\b(?:tabled|presented|laid|brought up)\b", re.I)
PAGE = re.compile(r"^\s*Page\s+\d+\s*$", re.I)
# legacy print-Hansard section headings are centred (deep indent, short line)
HEADING = re.compile(r"^ {15,}\S.{0,70}$")
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.'’\-()&/]{4,}$")
STAGE = re.compile(
    r"^\s*(Honourable members? interjecting|Members? interjecting"
    r"|Business interrupted|Sitting suspended|Sitting continued|House divided"
    r"|Motion agreed to|Bill (read|agreed)|Debate adjourned|Tabled\.?"
    r"|Ordered that|The (SPEAKER|PRESIDENT|ACTING SPEAKER|DEPUTY)\b"
    r"|Question (agreed to|put|resolved)|Interjection|Applause|Laughter)",
    re.I)


def clean(fragment):
    t = TAG.sub(" ", fragment)
    t = htmllib.unescape(t)
    return t


TITLE = re.compile(r"^((?:Mr|Mrs|Ms|Miss|Dr|Hon|Sir|Prof|The)\.?)\s+(.*)$", re.I)


def norm_speaker(name):
    """Canonical form: title + ALL-CAPS surname.

    Hansard prints the surname in caps in ordinary speech but in title case in
    interjections and points of order; without this, "Mr McIntosh" and
    "Mr McINTOSH" would be two different speakers.
    """
    n = re.sub(r"\s+", " ", name).strip()
    m = TITLE.match(n)
    return f"{m.group(1)} {m.group(2).upper()}" if m else n.upper()


def is_chair_vic(name):
    return is_chair(name) or bool(VIC_CHAIR.search(name))


def units_from_legacy(pre):
    """<pre> document -> lines with page furniture removed."""
    t = clean(re.sub(r"<hr\s*/?>\s*Page\s+\d+", "\n", pre, flags=re.I))
    return [ln for ln in t.split("\n") if not PAGE.match(ln)]


def units_from_modern(body):
    """<p> paragraphs -> one logical line each, grouped per ISYS document.

    The modern template emits no per-document wrapper, but consecutive
    documents are separated by a long run of blank lines (>=9 newlines matches
    the document count exactly on a checked 50-document cell), so turns do not
    leak across a document boundary onto the wrong member.
    """
    docs = []
    for part in re.split(r"\n{9,}", body):
        lines = []
        for chunk in re.split(r"<p\b", part)[1:]:
            _, _, rest = chunk.partition(">")
            txt = re.sub(r"\s+", " ", clean(rest.split("</p>")[0])).strip()
            if txt:
                lines.append(txt)
        if lines:
            docs.append(lines)
    return docs


def units_from_plain(body):
    """59th-Parliament cells: no markup at all, one document per text line."""
    return [[ln] for ln in clean(body).split("\n") if ln.strip()]


def roster_of(docs):
    """Names seen opening a 60th-Parliament turn, upper-cased."""
    out = set()
    for doc in docs:
        for ln in doc:
            m = match60(ln) or match60b(ln)
            if m:
                out.add(norm_speaker_60(m.group(1)).upper())
    return out


def names_in(path):
    """Roster contribution of one file (used to build the corpus-wide roster
    before extraction; empty for every pre-60th-Parliament file)."""
    try:
        return roster_of(docs_of(path))
    except Exception:
        return set()


def docs_of(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    m = HEADER.match(raw)
    if not m:
        raise ValueError("no header comment")
    body = raw[m.end():]
    pres = re.findall(r"<pre[^>]*>(.*?)</pre>", body, re.S)
    if pres:
        return [units_from_legacy(p) for p in pres]
    if re.search(r"<p\b", body):
        return units_from_modern(body)
    return units_from_plain(body)


def extract_file(path, prov="VIC", roster=frozenset()):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    m = HEADER.match(raw)
    if not m:
        raise ValueError("no header comment")
    date, chamber, _activity = m.group(1), m.group(2), m.group(3)
    body = raw[m.end():]
    ch = "LA" if chamber.upper().startswith("ASSEM") else "LC"
    # Turn numbering restarts per file and a sitting day is spread over ~10
    # activity-cell files per chamber, so the cell tag must enter the seg_id.
    cell = re.sub(r"^[A-Z]{2}_\d{4}-\d{2}-\d{2}_", "", Path(path).stem)
    tag = f"{prov}{ch}:{cell}:"

    pres = re.findall(r"<pre[^>]*>(.*?)</pre>", body, re.S)
    if pres:
        docs = [units_from_legacy(p) for p in pres]
    elif re.search(r"<p\b", body):
        docs = units_from_modern(body)
    else:
        docs = units_from_plain(body)

    # 60th-Parliament signature: at least one line opens with the no-honorific
    # "Given SURNAME (electorate) (hh:mm):" form.  Checked per file, so the
    # legacy / modern / 59th eras never see the extra pattern.
    era60 = any(match60(ln) for doc in docs for ln in doc)
    # roster for the title-case interjection form: the corpus-wide roster main()
    # collected, plus whoever speaks in this file (so the file stands alone).
    known = (set(roster) | roster_of(docs)) if era60 else frozenset()

    out = []
    turn = 0
    speaker = None
    parts = []

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not is_chair_vic(speaker):
            txt = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if txt:
                before = len(out)
                # chamber-qualified turn ids: both houses sit on the same dates
                pack_turn(tag, date, turn, speaker, sentences(txt), out)
                for r in out[before:]:
                    r["prov"] = prov
                    r["chamber"] = ch
                turn += 1
        parts, speaker = [], None

    for lines in docs:
        # No close() at the document boundary: ISYS splits a single member's
        # speech across documents when the chair interrupts, and a turn that
        # genuinely ends is closed by the next speaker marker, a narration line
        # or a heading anyway.
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            if NARR.match(ln):                # third-person procedural report
                close()
                continue
            if era60:
                s6 = match60(ln)
                if s6:
                    close()
                    speaker = norm_speaker_60(s6.group(1))
                    rest = s6.group(4).strip()
                    if rest:
                        parts.append(rest)
                    continue
                s6 = match60b(ln) or match60c(ln, known)
                if s6:
                    close()
                    speaker = norm_speaker_60(s6.group(1))
                    rest = s6.group(2).strip()
                    if rest:
                        parts.append(rest)
                    continue
            sm = SPEAKER.match(ln)
            if sm and (CAPS.search(sm.group(1))
                       or not sm.group(1).lower().startswith("the")):
                close()
                speaker = norm_speaker(sm.group(1))
                rest = sm.group(3).strip()
                if rest:
                    parts.append(rest)
                continue
            if STAGE.match(s) or HEADING.match(ln) or ALLCAPS.match(s):
                close()                       # section heading ends the turn
                continue
            if speaker:
                parts.append(s)
    close()
    raw_words = len(clean(body).split())
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    pat = sys.argv[3] if len(sys.argv) > 3 else "*.html"
    n = raw_words = kept_words = 0
    seen = set()
    dup = 0
    bad = Counter()
    files = sorted(raw_dir.glob(pat))
    # Pre-pass: the 60th Parliament's title-case interjections ("Brad Rowswell:
    # On a point of order ...") are only accepted for names seen speaking
    # somewhere in the corpus.  Empty for every pre-60th-Parliament file, so
    # the older eras are unaffected.
    roster = set()
    for f in files:
        roster |= names_in(f)
    with open(out_path, "w") as fh:
        for f in files:
            try:
                recs, rw = extract_file(f, roster=roster)
            except Exception as e:
                bad[str(e)] += 1
                continue
            raw_words += rw
            for r in recs:
                # member-bin cells overlap (MemberName is multi-valued in ISYS)
                key = (r["date"], r["chamber"], r["speaker"], r["text"][:400])
                if key in seen:
                    dup += 1
                    continue
                seen.add(key)
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments; dropped {dup} duplicate windows; "
          f"kept {kept_words}/{raw_words} raw words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)
    for k, v in bad.most_common(5):
        print(f"FAIL {v}x {k}", file=sys.stderr)


if __name__ == "__main__":
    main()
