#!/usr/bin/env python3
"""Canadian House of Commons (ourcommons.ca Hansard XML) -> shared segment schema.

Structure: <Intervention Type="Debate"> wrapping <PersonSpeaking><Affiliation>
(the speaker, with a Type code) and <Content> of <ParaText> paragraphs.
Sitting date comes from <ExtractedItem Name="Date">.

Canada-specific handling:
  - The chamber is bilingual AND the -E edition TRANSLATES French speech
    into English. <FloorLanguage language="FR">[Translation] marks where
    this begins, so the English text that follows is translator-authored,
    not member-authored — the same trap as the NB parallel columns, and
    ~25% of scoreable segments. Each segment carries `floor_lang` and
    `translated`; `orig_frac` is 0.0 for translated spans, and the protocol
    run uses member-authored English only.
  - Chair/procedural voices are excluded by Affiliation Type code and by
    role name (Speaker, Acting Clerk, Chair of Committees, etc).
  - <Affiliation> also appears *inside* ParaText as inline riding/member
    references; those are flattened into the text, not treated as speakers.

Usage: python ca_extract.py XML_DIR OUT_JSONL [--workers N]
"""
import argparse
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

MAX_WORDS = 360
MIN_WORDS = 50
MONTHS = {m: i for i, m in enumerate(
    ["January","February","March","April","May","June","July","August",
     "September","October","November","December"], 1)}
DATE_TXT = re.compile(r"(\w+),?\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})")
CHAIR = re.compile(r"speaker|clerk|chair|pr[ée]sident|greffier|presiding officer|deputy chair|assistant deputy", re.I)
EN = {"the","of","to","and","in","is","that","for","it","we","this","are",
      "have","be","will","with","on","as","has","was","our","not","by"}
FR = {"le","la","les","de","des","du","et","est","que","une","un","dans",
      "pour","nous","vous","avec","sur","qui","ce","cette","sont","pas","au"}


def text_of(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def lang_of(t):
    words = re.findall(r"[a-zA-ZÀ-ÿ']+", t.lower())
    if not words:
        return "none"
    en = sum(w in EN for w in words)
    fr = sum(w in FR for w in words)
    if en >= fr * 1.5 and en >= max(1, 0.04 * len(words)):
        return "en"
    if fr > en:
        return "fr"
    return "mixed"


def extract_file(path):
    path = Path(path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"PARSE FAIL {path.name}: {e}", file=sys.stderr)
        return []
    date = ""
    for it in root.iter("ExtractedItem"):
        if it.get("Name") == "Date":
            m = DATE_TXT.search(it.text or "")
            if m and m.group(2) in MONTHS:
                date = f"{m.group(4)}-{MONTHS[m.group(2)]:02d}-{int(m.group(3)):02d}"
            break
    if not date:
        return []
    out = []
    section = ""
    order = ""
    turn = 0
    floor = "EN"   # <FloorLanguage> marks the language actually spoken;
                   # in the -E edition, FR spans are TRANSLATIONS, not
                   # member-authored English (same trap as the NB columns)
    for el in root.iter():
        tag = el.tag
        if tag == "FloorLanguage":
            floor = (el.get("language") or "EN").upper()
            continue
        if tag == "SubjectOfBusinessTitle":
            section = text_of(el)[:120]
            continue
        if tag == "OrderOfBusinessTitle":
            # The PARENT rubric -- "Oral Questions", "Statements by Members",
            # "Government Orders". SubjectOfBusinessTitle under Oral Questions
            # is only the topic ("Carbon Pricing"), so without this there is no
            # way to tell unscripted Question Period from set-piece debate.
            order = text_of(el)[:80]
            continue
        if tag != "Intervention":
            continue
        ps = el.find("PersonSpeaking")
        speaker = ""
        if ps is not None:
            aff = ps.find("Affiliation")
            if aff is not None:
                speaker = (aff.text or "").strip().rstrip(":").strip()
        if not speaker or CHAIR.search(speaker):
            continue
        content = el.find("Content")
        if content is None:
            continue
        paras = [text_of(p) for p in content.findall("ParaText")]
        paras = [p for p in paras if p]
        if not paras:
            continue
        turn_id = f"CA{date}#t{turn}"
        turn += 1
        buf, words, widx = [], 0, 0

        def flush():
            nonlocal buf, words, widx
            if not buf:
                return
            txt = " ".join(buf)
            out.append({
                "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
                "date": date, "file": path.name, "page": "",
                "speaker": speaker, "section": section, "order": order,
                "person_id": "", "lang": lang_of(txt),
                "floor_lang": floor,
                "translated": floor != "EN",
                "n_words": words, "orig_frac": 1.0 if floor == "EN" else 0.0,
                "scoreable": words >= MIN_WORDS, "text": txt,
            })
            widx += 1
            buf, words = [], 0

        for p in paras:
            w = len(p.split())
            if words + w > MAX_WORDS and words >= MIN_WORDS:
                flush()
            buf.append(p)
            words += w
        flush()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml_dir")
    ap.add_argument("out_jsonl")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    paths = sorted(str(p) for p in Path(args.xml_dir).glob("*.xml"))
    print(f"{len(paths)} sitting files", file=sys.stderr)
    n = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex, \
            open(args.out_jsonl, "w") as fh:
        for recs in ex.map(extract_file, paths, chunksize=4):
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments", file=sys.stderr)


if __name__ == "__main__":
    main()
