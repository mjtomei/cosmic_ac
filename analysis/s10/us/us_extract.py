#!/usr/bin/env python3
"""US Congressional Record (GovInfo CREC zips) -> shared segment schema.

US-specific handling, in order of how much damage getting it wrong would do:

  1. EXTENSIONS OF REMARKS ARE NOT SPEECH. Extensions are written material
     inserted into the Record by members who never uttered it on the floor.
     They are the single largest contaminant in CREC for a study of *spoken*
     language, they are exactly the genre most likely to be ghost-drafted,
     and including them would inflate any AI estimate for the wrong reason.
     mods.xml tags them granuleClass=EXTENSIONS; they are dropped.
  2. DAILYDIGEST is an editorial summary written by Record staff. Dropped.
  3. Only granuleClass HOUSE and SENATE are kept, and each segment carries
     `chamber` so the two can be analysed apart -- they have different
     insertion conventions and different speech norms.
  4. Residual "revise and extend" contamination remains and CANNOT be fully
     removed: House members may revise remarks within five legislative days,
     and the Record does not mark what changed. The Senate's old bullet
     convention for inserted statements does not survive into the HTML.
     This is a stated limitation, not a solved problem -- see the
     `revise_extend_flag` field, which marks granules containing an explicit
     leave-to-revise request so their share can at least be measured.
  5. Chair and clerk voices (SPEAKER, PRESIDING OFFICER, ACTING PRESIDENT,
     CHAIR, Clerk, VICE PRESIDENT) are procedural and are excluded.

Usage: python us_extract.py ZIP_DIR OUT_JSONL [--workers N]
"""
import argparse
import html
import io
import json
import re
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

MAX_WORDS = 360
MIN_WORDS = 50
NS = {"m": "http://www.loc.gov/mods/v3"}
KEEP = {"HOUSE", "SENATE"}

TAG = re.compile(r"<[^>]+>")
PAGEMARK = re.compile(r"\[\[Page [^\]]+\]\]")
HEADER_END = re.compile(r"through the Government Publishing Office \[www\.gpo\.gov\]")
# "  Mr. TONKO.", "  Mrs. CAROLYN B. MALONEY of New York.", "  Ms. CLARKE of New York."
# Surnames are set in caps, but caps-with-lowercase happens: McCONNELL,
# MacARTHUR, O'ROURKE. Requiring [A-Z][A-Z]+ dropped every one of them --
# and because an unmatched speaker line cascades (every later paragraph of
# that turn is discarded with it), a handful of Mc- names cost far more text
# than their own turns. So match loosely and validate with is_surname().
SPEAKER = re.compile(
    r"^  ((?:Mr|Mrs|Ms|Miss)\.?)\s+"
    r"([A-Z][A-Za-z'\-]*(?:\s+[A-Z]\.)*(?:\s+[A-Z][A-Za-z'\-]*)*)"
    r"(\s+of\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)?\.\s")


def is_surname(t):
    """Caps-dominant token: real surname, not the vocative 'Mr. Speaker.'"""
    up = sum(c.isupper() for c in t)
    lo = sum(c.islower() for c in t)
    return up >= 2 and up > lo
# Case-SENSITIVE: the Record prints chair titles in caps ("The PRESIDING
# OFFICER."). Matching case-insensitively swallowed bill text beginning "The
# Chairman of the Committee on the Budget..." -- 1,493 paragraphs averaging
# 117 words on a single Senate day -- and, worse, each false match reset the
# current speaker and discarded the remainder of a member's turn.
CHAIR = re.compile(
    r"^  The (?:SPEAKER|PRESIDING OFFICER|ACTING PRESIDENT|VICE PRESIDENT|"
    r"CHAIR|ACTING CHAIR|CHAIRMAN|PRESIDENT pro tempore|CLERK|Clerk)\b")
REVEXT = re.compile(r"revise and extend (?:his|her|their|my) remarks", re.I)
HEADING = re.compile(r"^\s{3,}[A-Z0-9][A-Z0-9 ,.'\-()/&]{5,}$")


def granules(zf):
    """accessId -> (granuleClass, [member names]) from mods.xml."""
    name = next((n for n in zf.namelist() if n.endswith("mods.xml")), None)
    if not name:
        return {}
    try:
        root = ET.parse(io.BytesIO(zf.read(name))).getroot()
    except ET.ParseError:
        return {}
    out = {}
    for rel in root.findall(".//m:relatedItem", NS):
        gc = rel.findtext(".//m:granuleClass", default=None, namespaces=NS)
        aid = rel.findtext(".//m:accessId", default=None, namespaces=NS)
        if not gc or not aid:
            continue
        # <congMember bioGuideId=".." party="D" state="DE" role="SPEAKING">
        #   <name type="parsed">Ms. BLUNT ROCHESTER</name>
        # The "parsed" name is exactly the form that appears in the running
        # text, so it joins to the speaker line without any name matching.
        names = []
        for cm in rel.iter():
            if not cm.tag.endswith("congMember"):
                continue
            bid = cm.get("bioGuideId")
            if not bid:
                continue
            parsed = ""
            for nm in cm.iter():
                if nm.tag.endswith("name") and nm.get("type") == "parsed":
                    parsed = (nm.text or "").strip()
                    break
            if parsed:
                names.append((parsed, bid, cm.get("party", ""),
                              cm.get("state", "")))
        out[aid] = (gc, names)
    return out


def body_of(raw):
    t = html.unescape(TAG.sub("", raw))
    m = HEADER_END.search(t)
    if m:
        t = t[m.end():]
    return PAGEMARK.sub("", t)


def paragraphs(text):
    """CREC wraps at ~72 cols; a new paragraph starts with exactly two spaces."""
    out, buf = [], []
    for line in text.split("\n"):
        if not line.strip():
            if buf:
                out.append(" ".join(buf))
                buf = []
            continue
        # Headings are centred all-caps and often wrap over two lines, so
        # consecutive heading lines are merged rather than emitted twice.
        if HEADING.match(line.rstrip()):
            if buf:
                out.append(" ".join(buf))
                buf = []
            if out and isinstance(out[-1], tuple):
                out[-1] = ("HEAD", out[-1][1] + " " + line.strip())
            else:
                out.append(("HEAD", line.strip()))
            continue
        if line.startswith("  ") and not line.startswith("   ") and buf:
            out.append(" ".join(buf))
            buf = []
        buf.append(line.strip())
    if buf:
        out.append(" ".join(buf))
    return out


def extract_zip(path):
    path = Path(path)
    date = path.stem.replace("CREC-", "")
    recs = []
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        print(f"BAD ZIP {path.name}", file=sys.stderr)
        return []
    gran = granules(zf)
    for name in zf.namelist():
        if not name.endswith(".htm"):
            continue
        aid = Path(name).stem
        gc, members = gran.get(aid, (None, []))
        if gc not in KEEP:
            continue          # drops EXTENSIONS and DAILYDIGEST
        try:
            text = body_of(zf.read(name).decode("utf-8", "replace"))
        except Exception:
            continue
        rev = bool(REVEXT.search(text))
        section = ""
        speaker = ""
        person_id = party = state = ""
        turn = 0
        buf, words, widx = [], 0, 0
        turn_id = ""
        bio = {re.sub(r"^(Mr|Mrs|Ms|Miss)\.?\s+", "", n).upper(): (b, pa, st)
               for n, b, pa, st in members}

        def flush():
            nonlocal buf, words, widx
            if not buf or not speaker:
                buf, words = [], 0
                return
            txt = " ".join(buf)
            recs.append({
                "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
                "date": date, "file": aid, "page": aid.split("-Pg")[-1],
                "speaker": speaker, "section": section[:120],
                "person_id": person_id, "party": party, "state": state,
                "lang": "en",
                "chamber": gc, "granule_class": gc,
                "revise_extend_flag": rev,
                "n_words": words, "orig_frac": 1.0,
                "translated": False,
                "scoreable": words >= MIN_WORDS, "text": txt,
            })
            widx += 1
            buf, words = [], 0

        for p in paragraphs(text):
            if isinstance(p, tuple):
                section = p[1]
                continue
            if CHAIR.match("  " + p) or CHAIR.match(p):
                flush()
                speaker = ""
                continue
            m = SPEAKER.match("  " + p.lstrip()[:80] + " ")
            if m and not is_surname(m.group(2)):
                m = None
            if m:
                flush()
                surname = m.group(2).strip()
                speaker = f"{m.group(1)} {surname}{m.group(3) or ''}".strip()
                meta = bio.get(surname.upper(), ("", "", ""))
                person_id, party, state = meta
                turn_id = f"US{date}-{aid.split('-Pg')[-1]}#t{turn}"
                turn += 1
                widx = 0
                p = p[m.end() - 2:].strip() or ""
                if not p:
                    continue
            if not speaker:
                continue
            w = len(p.split())
            if words + w > MAX_WORDS and words >= MIN_WORDS:
                flush()
            buf.append(p)
            words += w
        flush()
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_dir")
    ap.add_argument("out_jsonl")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    paths = sorted(str(p) for p in Path(args.zip_dir).glob("*.zip"))
    print(f"{len(paths)} sitting-day zips", file=sys.stderr)
    n = sc = 0
    ch = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex, \
            open(args.out_jsonl, "w") as fh:
        for recs in ex.map(extract_zip, paths, chunksize=2):
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
                sc += r["scoreable"]
                ch[r["chamber"]] = ch.get(r["chamber"], 0) + r["n_words"]
    print(f"wrote {n} segments ({sc} scoreable); words by chamber: {ch}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
