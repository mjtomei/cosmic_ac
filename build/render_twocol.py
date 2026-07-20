#!/usr/bin/env python3
import markdown, pathlib, sys, re
from weasyprint import HTML

inp = sys.argv[1] if len(sys.argv) > 1 else "the-performance-commons.md"
out = sys.argv[2] if len(sys.argv) > 2 else "the-performance-commons-2col.pdf"

src = pathlib.Path(inp).read_text()

# ensure a blank line before lists that follow a non-blank, non-list line
_list_re = re.compile(r'^\s{0,3}([-*+]|\d+[.)])\s+\S')
_fixed = []
for _ln in src.split('\n'):
    if _list_re.match(_ln) and _fixed and _fixed[-1].strip() != '' and not _list_re.match(_fixed[-1]):
        _fixed.append('')
    _fixed.append(_ln)
src = '\n'.join(_fixed)

html_body = markdown.markdown(
    src, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "smarty"],
    extension_configs={"smarty": {"smart_dashes": False, "smart_quotes": False,
                                  "smart_angled_quotes": False, "smart_ellipses": False}})

# references list: compact hanging-indent style
html_body = re.sub(r'(<h2>References</h2>\s*)<ul>', r'\1<ul class="refs">', html_body)

# --- split front matter (title..abstract) from the two-column body (section 1 onward) ---
m = re.search(r'<h2>1\.', html_body)
front, body = (html_body[:m.start()], html_body[m.start():]) if m else ("", html_body)

# --- wrap figures: dense -> full width (span both columns); compact (figs 2,3,4) -> single column ---
def fig_class(src_):
    return 'onecol' if src_.endswith(('figure-2.png', 'figure-3.png', 'figure-4.png', 'figure-tapeout.png', 'figure-embargo.png')) else 'fullwidth'

def fig_repl(mm):
    s, cap = mm.group(1), mm.group(2)
    return (f'<figure class="fig {fig_class(s)}"><img src="{s}" />'
            f'<figcaption>{cap}</figcaption></figure>')

body = re.sub(r'<p>\s*<img\b[^>]*\bsrc="([^"]+)"[^>]*?/?>\s*</p>\s*<p>\s*<em>(.*?)</em>\s*</p>',
              fig_repl, body, flags=re.DOTALL)

# --- pair Figures 3+4 (files figure-2/figure-3) side by side in one full-width block ---
def twin_repl(mm):
    return ('<figure class="fig fullwidth twin">'
            f'<div class="half"><img src="{mm.group(1)}" /><figcaption>{mm.group(2)}</figcaption></div>'
            f'<div class="half"><img src="{mm.group(3)}" /><figcaption>{mm.group(4)}</figcaption></div>'
            '</figure>')
body = re.sub(r'<figure class="fig onecol"><img src="([^"]*figure-2\.png)" />'
              r'<figcaption>(.*?)</figcaption></figure>\s*'
              r'<figure class="fig onecol"><img src="([^"]*figure-3\.png)" />'
              r'<figcaption>(.*?)</figcaption></figure>',
              twin_repl, body, flags=re.DOTALL)

# --- wrap tables: table 1 -> single column; tables 2,3 -> full width ---
_tbl_n = [0]
def tbl_repl(mm):
    _tbl_n[0] += 1
    cls = 'onecol' if _tbl_n[0] == 1 else 'fullwidth'
    return (f'<div class="tbl {cls}"><table>{mm.group(1)}</table>'
            f'<div class="cap">{mm.group(2)}</div></div>')

body = re.sub(r'<table>(.*?)</table>\s*<p>\s*<em>(.*?)</em>\s*</p>',
              tbl_repl, body, flags=re.DOTALL)

CSS = """
@page { size: Letter; margin: 13mm 13mm 15mm 13mm;
        @bottom-center { content: counter(page); font: 8pt 'Liberation Sans', sans-serif; color: #9aa7b4; } }
html { font-size: 9.4pt; }
body { font-family: 'Liberation Serif','DejaVu Serif',serif; line-height: 1.34; color: #1b1b1b; margin: 0;
       hyphens: auto; -weasy-hyphens: auto; }
h1,h2,h3 { font-family: 'Liberation Sans','DejaVu Sans',sans-serif; color: #15324f; }
.frontmatter { margin-bottom: 4mm; }
.frontmatter h1 { font-size: 20pt; margin: 0 0 1px 0; letter-spacing: -0.2px; }
.frontmatter h3 { font-weight: normal; font-size: 11.5pt; color: #5a6b7b; margin: 0 0 5px 0; }
.frontmatter > p { font-size: 8.4pt; color: #5f7081; font-style: italic; margin: 0 0 7px 0; }
.frontmatter h2 { font-size: 11pt; margin: 8px 0 4px 0; padding-bottom: 2px; border-bottom: 1.6px solid #15324f; }
.frontmatter > p:not(:first-of-type) { font-style: normal; font-size: 9.4pt; color: #1b1b1b; text-align: justify; }
hr { border: none; border-top: 0.6pt solid #d6dce2; margin: 7px 0; }
.paper { column-count: 2; column-gap: 6.5mm; column-fill: balance; }
.paper h2 { font-size: 11pt; margin: 11px 0 5px 0; padding-bottom: 2px; border-bottom: 1.6px solid #15324f;
            break-after: avoid; }
.paper h3 { font-size: 9.8pt; color: #294a6b; margin: 9px 0 4px 0; break-after: avoid; }
.paper h4 { font-size: 9.4pt; color: #3a5876; font-style: italic; margin: 8px 0 3px 0; break-after: avoid; }
p { margin: 0 0 6px 0; text-align: justify; orphans: 2; widows: 2; }
strong { color: #0e2334; font-weight: 700; }
ul,ol { margin: 0 0 6px 0; padding-left: 15px; }
li { margin: 0 0 3px 0; text-align: justify; }
em { font-style: italic; }
figure { margin: 6px 0 8px 0; break-inside: avoid; }
.fullblock { margin: 7px 0 9px 0; }
.fig.fullwidth, .tbl.fullwidth { margin: 0; }
.fig.onecol, .tbl.onecol { break-inside: avoid; margin: 6px 0 8px 0; }
.tbl { break-inside: avoid; }
.tbl table { break-inside: avoid; }
.fig { text-align: center; }
.fig img { height: auto; }
.fig.onecol img { width: 100%; max-height: 82mm; }
.fig.fullwidth img { display: inline-block; max-width: 146mm; max-height: 92mm; }
.fig.fullwidth figcaption { display: block; max-width: 146mm; margin: 3px auto 0 auto; }
.fig.twin { text-align: center; }
.fig.twin .half { display: inline-block; width: 48.6%; vertical-align: top; margin: 0 0.3%; }
.fig.twin .half img { width: 100%; max-width: none; max-height: 80mm; }
.fig.twin .half figcaption { max-width: none; margin: 2px 0 0 0; text-align: left; }
.appendixwrap { page-break-before: always; }
ul.refs { list-style: none; padding-left: 0; margin: 0; }
ul.refs li { font-size: 7.2pt; line-height: 1.18; margin: 0 0 2px 0; text-align: left;
             padding-left: 9px; text-indent: -9px; }
figcaption, .cap { font-size: 7.7pt; font-style: italic; color: #33424f; line-height: 1.24; margin-top: 3px;
                   text-align: left; }
table { width: 100%; border-collapse: collapse; font-family: 'DejaVu Sans','Liberation Sans',sans-serif;
        font-size: 7.0pt; line-height: 1.22; margin: 0; }
th,td { border: 0.5pt solid #c4ccd4; padding: 2.6px 4px; text-align: left; vertical-align: top; }
th { background: #15324f; color: #fff; font-weight: 700; }
tbody tr:nth-child(even) { background: #f1f4f7; }
tbody td:first-child { font-weight: 600; color: #15324f; }
.tbl.fullwidth table { font-size: 7.4pt; }
"""

front_html = f'<div class="frontmatter">{front}</div>' if front else ''

# Split the body at full-width elements: WeasyPrint's column-span is buggy (silently
# drops the rest of the document when a spanner lands on certain page geometries), so
# emit alternating two-column chunks and top-level full-width blocks instead.
def chunk(seg):
    parts = re.split(r'(<figure class="fig fullwidth[^"]*">.*?</figure>|<div class="tbl fullwidth">.*?</div>\s*</div>)',
                     seg, flags=re.DOTALL)
    out = []
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        if i % 2 == 1:  # a full-width element
            out.append(f'<div class="fullblock">{part}</div>')
        else:
            out.append(f'<div class="paper">{part}</div>')
    return ''.join(out)

# Appendix starts on a fresh page
_apx = re.search(r'<h2>Appendix', body)
if _apx:
    body_html = chunk(body[:_apx.start()]) + '<div class="appendixwrap">' + chunk(body[_apx.start():]) + '</div>'
else:
    body_html = chunk(body)

doc = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
       f'<style>{CSS}</style></head><body>{front_html}{body_html}</body></html>')

HTML(string=doc, base_url=str(pathlib.Path(inp).resolve().parent)).write_pdf(out)
print("wrote", out)
