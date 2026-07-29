#!/usr/bin/env python3
"""S10 pilot: extract NB Hansard PDFs into language-tagged paragraphs.

NB's Journal of Debates prints aligned paragraph pairs in two columns; the
side each language occupies varies by paragraph (hypothesis: left = as
spoken, right = translation). We extract per-column paragraphs with font
info, language-ID each, and pair them by vertical overlap so every English
paragraph carries an `orig_en` flag (True when the English sits in the left
column of its pair).

Output: paragraphs.jsonl — one record per paragraph occurrence:
  {file, date, page, side, y0, y1, lang, bold_lead, text}
plus pair tagging fields {pair_lang_other, orig}.

Usage:
  python extract.py PDF_DIR OUT_JSONL [--one FILE] [--workers N]
"""
import argparse
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pdfplumber

EN_STOP = {"the", "of", "to", "and", "in", "is", "that", "for", "it", "we",
           "this", "are", "have", "be", "will", "with", "on", "as", "has",
           "was", "our", "not", "by", "from", "you", "they", "their"}
FR_STOP = {"le", "la", "les", "de", "des", "du", "et", "est", "que", "une",
           "un", "dans", "pour", "nous", "vous", "avec", "sur", "qui", "ce",
           "cette", "sont", "pas", "au", "aux", "se", "plus", "par", "leur"}
FR_CHARS = set("éèêëàâçîïôûùœ")

LINE_TOL = 2.5        # pts: words within this vertical distance share a line
PARA_GAP = 6.0        # pts: vertical gap larger than this starts a paragraph
HEADER_FRAC = 0.075   # strip words above this fraction of page height
FOOTER_FRAC = 0.93    # strip words below this fraction


def lang_of(text: str) -> str:
    words = re.findall(r"[a-zA-ZÀ-ÿ'’]+", text.lower())
    if not words:
        return "none"
    en = sum(w in EN_STOP for w in words)
    fr = sum(w in FR_STOP for w in words)
    fr += sum(1 for c in text.lower() if c in FR_CHARS) * 0.5
    total = len(words)
    if en == 0 and fr == 0:
        return "unknown"
    if en >= fr * 1.5 and en >= max(1, 0.05 * total):
        return "en"
    if fr >= en * 1.5 and fr >= max(1, 0.05 * total):
        return "fr"
    return "mixed"


def column_paragraphs(words, side):
    """Group a column's words into paragraphs; return list of dicts."""
    if not words:
        return []
    words = sorted(words, key=lambda w: (w["top"], w["x0"]))
    lines = []
    for w in words:
        if lines and abs(w["top"] - lines[-1]["top"]) <= LINE_TOL:
            lines[-1]["words"].append(w)
        else:
            lines.append({"top": w["top"], "bottom": w["bottom"], "words": [w]})
    paras = []
    for ln in lines:
        ln["words"].sort(key=lambda w: w["x0"])
        ln["text"] = " ".join(w["text"] for w in ln["words"])
        ln["bold"] = any("Bold" in w.get("fontname", "") for w in ln["words"][:3])
        if paras and (ln["top"] - paras[-1]["bottom"]) < PARA_GAP:
            paras[-1]["lines"].append(ln)
            paras[-1]["bottom"] = max(paras[-1]["bottom"], ln["bottom"])
        else:
            paras.append({"top": ln["top"], "bottom": ln["bottom"], "lines": [ln]})
    out = []
    for p in paras:
        text = " ".join(ln["text"] for ln in p["lines"])
        out.append({
            "side": side, "y0": round(p["top"], 1), "y1": round(p["bottom"], 1),
            "bold_lead": p["lines"][0]["bold"], "text": text,
        })
    return out


def is_two_column(words, width):
    """Debate pages have a clear mid-page gutter; front matter does not."""
    if len(words) < 60:
        return False
    mid = width / 2
    crossing = sum(1 for w in words if w["x0"] < mid - 5 < mid + 5 < w["x1"])
    return crossing <= 2


def extract_pdf(pdf_path: str):
    try:
        return _extract_pdf(pdf_path)
    except Exception as e:
        print(f"FAILED {pdf_path}: {e}", file=sys.stderr)
        return []


def _extract_pdf(pdf_path: str):
    path = Path(pdf_path)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    date = m.group(1) if m else "unknown"
    records = []
    with pdfplumber.open(path) as pdf:
        for pageno, page in enumerate(pdf.pages, 1):
            try:
                words = page.extract_words(extra_attrs=["fontname"])
            except Exception:
                continue
            h, wd = page.height, page.width
            words = [w for w in words
                     if w["top"] > h * HEADER_FRAC and w["bottom"] < h * FOOTER_FRAC]
            if not is_two_column(words, wd):
                continue
            mid = wd / 2
            left = [w for w in words if (w["x0"] + w["x1"]) / 2 < mid]
            right = [w for w in words if (w["x0"] + w["x1"]) / 2 >= mid]
            paras = column_paragraphs(left, "L") + column_paragraphs(right, "R")
            for p in paras:
                p["lang"] = lang_of(p["text"])
                p["file"] = path.name
                p["date"] = date
                p["page"] = pageno
            # pair L/R paragraphs by vertical overlap to tag orig vs translation
            lps = [p for p in paras if p["side"] == "L"]
            rps = [p for p in paras if p["side"] == "R"]
            for lp in lps:
                best, best_ov = None, 0.0
                for rp in rps:
                    ov = min(lp["y1"], rp["y1"]) - max(lp["y0"], rp["y0"])
                    if ov > best_ov:
                        best, best_ov = rp, ov
                span = max(lp["y1"] - lp["y0"], 1.0)
                if best is not None and best_ov > 0.5 * span:
                    lp["pair_lang_other"] = best["lang"]
                    best["pair_lang_other"] = lp["lang"]
            for p in paras:
                other = p.get("pair_lang_other", "none")
                if p["lang"] in ("en", "fr"):
                    # original iff on the left with a translation on the right,
                    # or unpaired (single-language passage)
                    p["orig"] = (p["side"] == "L") or (other == p["lang"]) or (other == "none")
                else:
                    p["orig"] = False
            records.extend(paras)
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf_dir")
    ap.add_argument("out_jsonl")
    ap.add_argument("--one", help="extract a single file only")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    pdfs = sorted(Path(args.pdf_dir).glob("*.pdf"))
    if args.one:
        pdfs = [p for p in pdfs if args.one in p.name]
    print(f"extracting {len(pdfs)} PDFs", file=sys.stderr)

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        all_recs = list(ex.map(extract_pdf, [str(p) for p in pdfs]))

    n = 0
    with open(args.out_jsonl, "w") as f:
        for recs in all_recs:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} paragraphs to {args.out_jsonl}", file=sys.stderr)


if __name__ == "__main__":
    main()
