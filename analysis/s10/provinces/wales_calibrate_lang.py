#!/usr/bin/env python3
"""Calibrate wales_lang's Welsh detector against the Record's own labels.

The 2016+ bilingual XML carries <contribution_language> per contribution, so
the detector needed only for the PDF era (2006-2010, 2015) can be scored on
tens of thousands of labelled utterances from the same corpus and the same
speakers.  Prints a threshold sweep; wales_lang.THRESHOLD should match the
best row.

Usage: python3 wales_calibrate_lang.py [RAW_DIR]
"""
import glob
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wales_lang import scores

RECORD = re.compile(r"<XML_[^>]*_Bilingual>(.*?)</XML_[^>]*_Bilingual>", re.S)


def field(b, t):
    m = re.search(f"<{t}>(.*?)</{t}>", b, re.S)
    return html.unescape(m.group(1)) if m else ""


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else "wales_raw"
    pairs = []
    for fn in sorted(glob.glob(f"{raw}/*.xml")):
        for b in RECORD.findall(Path(fn).read_text(encoding="utf-8", errors="replace")):
            if field(b, "contribution_type") != "C":
                continue
            t = re.sub(r"\s+", " ",
                       html.unescape(re.sub(r"<[^>]+>", " ",
                                            field(b, "contribution_verbatim")))).strip()
            if len(t.split()) >= 10:
                pairs.append((field(b, "contribution_language") == "Cy", t))
    print(f"labelled contributions (>=10 words): {len(pairs)}")
    print(f"{'thresh':>7} {'acc':>7} {'cy-rec':>7} {'cy-prec':>8} {'fp':>6} {'fn':>6}")
    for th in (-0.10, -0.05, 0.0, 0.05, 0.10):
        tp = fp = tn = fn = 0
        for gold, t in pairs:
            cy, en = scores(t)
            pred = (cy - en) > th
            tp += pred and gold
            fp += pred and not gold
            tn += (not pred) and (not gold)
            fn += (not pred) and gold
        print(f"{th:>+7.2f} {(tp+tn)/len(pairs):>7.4f} {tp/max(tp+fn,1):>7.4f} "
              f"{tp/max(tp+fp,1):>8.4f} {fp:>6} {fn:>6}")


if __name__ == "__main__":
    main()
