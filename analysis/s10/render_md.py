#!/usr/bin/env python3
"""Render a markdown file to PDF (single column, print-legible tables).

Same toolchain as the paper build (markdown + weasyprint) but a simpler
single-column stylesheet: these are working documents, not the paper. Tables
are the load-bearing element here, so they get explicit break-avoidance and
a smaller face than the body text.

Usage: python render_md.py IN.md [OUT.pdf] [--title "..."]
"""
import argparse
import os
import re

import markdown
from weasyprint import CSS, HTML

CSSTEXT = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm;
        @bottom-center { content: counter(page); font: 8.5pt Georgia, serif;
                         color: #7a7873; } }
body { font: 10.2pt/1.48 Georgia, "Times New Roman", serif; color: #16150f;
       hyphens: auto; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 2mm 0; color: #0b0b0b; }
h2 { font-size: 13.5pt; margin: 7mm 0 2mm 0; padding-bottom: 1mm;
     border-bottom: 1px solid #d8d7d2; color: #0b0b0b;
     break-after: avoid; }
h3 { font-size: 11.3pt; margin: 5mm 0 1.5mm 0; color: #26251d;
     break-after: avoid; }
h4 { font-size: 10.4pt; font-style: italic; margin: 4mm 0 1mm 0;
     color: #3a382e; break-after: avoid; }
p { margin: 0 0 2.2mm 0; }
ul, ol { margin: 0 0 2.4mm 0; padding-left: 5.5mm; }
li { margin: 0 0 1.1mm 0; }
code { font: 8.8pt "DejaVu Sans Mono", monospace; background: #f2f1ec;
       padding: 0 0.6mm; border-radius: 1.5px; }
pre { background: #f6f5f0; border-left: 2px solid #cfcec7; padding: 2mm 3mm;
      font: 8.6pt/1.35 "DejaVu Sans Mono", monospace; overflow-wrap: break-word;
      white-space: pre-wrap; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 2.5mm 0 3.5mm 0;
        font-size: 8.9pt; break-inside: avoid; }
th { text-align: left; border-bottom: 1.1pt solid #4a4840; padding: 1.3mm 2mm;
     font-weight: bold; }
td { border-bottom: 0.5pt solid #ddddd6; padding: 1.2mm 2mm;
     vertical-align: top; }
tr:last-child td { border-bottom: 1.1pt solid #4a4840; }
strong { color: #000; }
hr { border: none; border-top: 1px solid #d8d7d2; margin: 5mm 0; }
blockquote { margin: 2mm 0 2mm 4mm; padding-left: 3mm;
             border-left: 2px solid #cfcec7; color: #3a382e; }
a { color: #1a4f8a; text-decoration: none; }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()
    out = args.out or os.path.splitext(args.src)[0] + ".pdf"

    text = open(args.src).read()
    title = args.title or (re.search(r"^#\s+(.+)$", text, re.M)
                           or re.match("", "")).group(1)
    html = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    doc = (f'<html><head><meta charset="utf-8"><title>{title}</title></head>'
           f"<body>{html}</body></html>")
    HTML(string=doc, base_url=os.path.dirname(os.path.abspath(args.src))).write_pdf(
        out, stylesheets=[CSS(string=CSSTEXT)])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
