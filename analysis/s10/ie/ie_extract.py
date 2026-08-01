#!/usr/bin/env python3
"""Dáil Éireann (Oireachtas Akoma Ntoso XML) -> the NB/UK segment schema.

Akoma Ntoso gives <speech by="#PersonId" as="#Role"> with <from> (display
name) and <p> children, nested inside <debateSection> elements whose <heading>
supplies the section. Same output fields as uk_extract.py so every downstream
script runs unchanged.

Two Ireland-specific handles:
  - the chamber is bilingual; Irish-language speech is a minority but real,
    so each segment is language-scored and `lang` recorded. English-only is
    the default for the protocol (matching NB's original-English rule).
  - the `as` attribute carries the speaking role, which makes chair exclusion
    exact rather than name-pattern guesswork.

Usage: python ie_extract.py XML_DIR OUT_JSONL [--workers N]
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
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
CHAIR_ROLE = re.compile(r"chairman|ceann_comhairle|leas_cheann|acting_chair|chair",
                        re.I)
CHAIR_NAME = re.compile(r"^(an )?(ceann comhairle|leas-cheann comhairle|"
                        r"acting chairman|acting chair|chairman|deputy speaker)",
                        re.I)
# language ID: English vs Irish function words
EN = {"the","of","to","and","in","is","that","for","it","we","this","are",
      "have","be","will","with","on","as","has","was","our","not","by","from"}
GA = {"agus","an","na","ar","go","is","le","i","do","se","si","ta","nil",
      "chun","seo","sin","aon","mar","ach","nach","ag","don","faoi","tha"}


def strip_ns(tag):
    return tag.rsplit("}", 1)[-1]


def text_of(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def lang_of(text):
    words = re.findall(r"[a-zA-ZáéíóúÁÉÍÓÚ']+", text.lower())
    if not words:
        return "none"
    en = sum(w in EN for w in words)
    ga = sum(w in GA for w in words)
    if en >= ga * 1.5 and en >= max(1, 0.04 * len(words)):
        return "en"
    if ga > en:
        return "ga"
    return "mixed"


def walk(el, section, out, date, fname, counter):
    for child in el:
        tag = strip_ns(child.tag)
        if tag == "debateSection":
            head = ""
            for gc in child:
                if strip_ns(gc.tag) == "heading":
                    head = text_of(gc)[:120]
                    break
            walk(child, head or section, out, date, fname, counter)
        elif tag == "speech":
            role = child.get("as") or ""
            person = (child.get("by") or "").lstrip("#")
            disp = ""
            paras = []
            for gc in child:
                t = strip_ns(gc.tag)
                if t == "from":
                    disp = text_of(gc)
                elif t == "p":
                    p = text_of(gc)
                    if p:
                        paras.append(p)
            if not paras:
                continue
            if CHAIR_ROLE.search(role) or CHAIR_NAME.match(disp):
                continue
            speaker = re.sub(r"\s*\(.*?\)\s*$", "", disp).strip() or person
            turn_id = f"IE{date}#t{counter[0]}"
            counter[0] += 1
            buf, words, widx = [], 0, 0

            def flush():
                nonlocal buf, words, widx
                if not buf:
                    return
                txt = " ".join(buf)
                out.append({
                    "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
                    "date": date, "file": fname, "page": "",
                    "speaker": speaker, "section": section,
                    "person_id": person, "lang": lang_of(txt),
                    "n_words": words, "orig_frac": 1.0,
                    "scoreable": words >= MIN_WORDS,
                    "text": txt,
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
        else:
            walk(child, section, out, date, fname, counter)


def extract_file(path):
    path = Path(path)
    m = DATE_RE.search(path.name)
    if not m:
        return []
    date = m.group(1)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"PARSE FAIL {path.name}: {e}", file=sys.stderr)
        return []
    out = []
    walk(root, "", out, date, path.name, [0])
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
