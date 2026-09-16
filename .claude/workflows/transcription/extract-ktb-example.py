#!/usr/bin/env python3
"""Extract KTB (2016 Princeton Classics scan) ABBYY text layer to markdown.
Font-size classification: body >=12, footnotes ==11, running heads <=10 at top.
Emits [*N*] printed-page anchors, chapter headings from the PDF outline, and a
per-page footnote block collected into a ## Notes section at the end.

KEPT AS THE WORKED EXAMPLE for stage 1 of the transcription flow
(reading/00-TRANSCRIPTION-METHODOLOGY.md). The font sizes, page-number offset,
and body/plates/index ranges are PER-BOOK: recalibrate each (survey a few pages
with `pdftohtml -xml -f N -l N -stdout`) before reusing on a new scan.
Bug fixed 2026-09-04 and baked in below: pdftohtml declares fontspecs
CUMULATIVELY across a page range, so the font table must be collected from the
whole batch, not per page."""
import re, subprocess, html, sys
from collections import defaultdict

PDF = "/home/matt/reading/artificial-persons/kantorowicz-1957-kings-two-bodies-2016-princeton-classics-full.pdf"
OUT = "/home/matt/reading/artificial-persons/kantorowicz-1957-kings-two-bodies.md"
LAST_BODY = 552   # plates 553-576, bibliography+index 577-631 skipped
ADDENDA = 632
PRINT_OFFSET = 40  # pdf page - 40 = printed page (calibrated: Dante ch. pdf491 = print451)

def get_xml(f, l):
    r = subprocess.run(["pdftohtml","-xml","-i","-f",str(f),"-l",str(l),"-stdout",PDF],
                       capture_output=True, text=True)
    return r.stdout

def parse_page(xml_page, inherited_fonts=None):
    fonts = dict(inherited_fonts or {})
    fonts.update({m.group(1): int(m.group(2)) for m in
             re.finditer(r'<fontspec id="(\d+)" size="(-?\d+)"', xml_page)})
    els = []
    for m in re.finditer(r'<text top="(\d+)" left="(\d+)" width="(\d+)" height="(\d+)" font="(\d+)">(.*?)</text>', xml_page, re.S):
        top, left, w, h, f, content = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5), m.group(6)
        italic = '<i>' in content
        txt = html.unescape(re.sub(r'<[^>]+>', '', content))
        if not txt.strip(): continue
        els.append(dict(top=top, left=left, w=w, h=h, size=fonts.get(f, 12), italic=italic, txt=txt))
    return els

def lines_from(els):
    """group elements into lines by top coordinate"""
    lines = defaultdict(list)
    for e in els:
        key = min((k for k in lines if abs(k - e['top']) <= 3), default=e['top'])
        lines[key].append(e)
    out = []
    for top in sorted(lines):
        parts = sorted(lines[top], key=lambda e: e['left'])
        seg = ""
        for e in parts:
            t = re.sub(r'\s+', ' ', e['txt']).strip()
            if e['italic'] and len(t) > 1:
                t = f"*{t}*"
            seg += (" " if seg else "") + t
        out.append(dict(top=top, left=min(p['left'] for p in parts), txt=seg))
    return out

def classify(els):
    body, notes, pageno = [], [], None
    for e in els:
        if e['top'] < 90 and e['size'] <= 10:
            n = re.fullmatch(r'\s*(\d{1,3})\s*', e['txt'])
            if n: pageno = int(n.group(1))
            continue  # running head / page number
        if re.fullmatch(r'\s*\d{1,3}\s*', e['txt']) and (e['top'] < 90 or e['top'] > 860):
            pageno = int(e['txt'].strip()); continue
        if e['size'] >= 12:
            body.append(e)
        elif e['size'] == 11:
            notes.append(e)
        else:
            body.append(e)  # small inline (superscripts etc.) stay with body
    return body, notes, pageno

def paragraphs(lines, indent_threshold=12):
    if not lines: return []
    base_left = min(l['left'] for l in lines)
    paras, cur = [], ""
    for l in lines:
        newpara = l['left'] > base_left + indent_threshold and cur
        if newpara:
            paras.append(cur); cur = l['txt']
        else:
            if cur.endswith('-') and not cur.endswith('--'):
                cur = cur[:-1] + l['txt']
            else:
                cur += (" " if cur else "") + l['txt']
    if cur: paras.append(cur)
    return [re.sub(r'\s+', ' ', p).strip() for p in paras if p.strip()]

# outline -> {pdfpage: title}
ol_xml = subprocess.run(["pdftohtml","-xml","-i","-f","1","-l","1","-stdout",PDF],
                        capture_output=True, text=True).stdout
outline = {}
for m in re.finditer(r'<item page="(\d+)">([^<]+)</item>', ol_xml):
    outline.setdefault(int(m.group(1)), []).append(html.unescape(m.group(2)).strip())

body_out, notes_out = [], []
pages = list(range(1, LAST_BODY + 1)) + [ADDENDA]
# batch pdftohtml calls 50 pages at a time
for start in range(0, len(pages), 50):
    chunk = pages[start:start+50]
    xml = get_xml(chunk[0], chunk[-1])
    batch_fonts = {m.group(1): int(m.group(2)) for m in
                   re.finditer(r'<fontspec id="(\d+)" size="(-?\d+)"', xml)}
    for pm in re.finditer(r'<page number="(\d+)".*?</page>', xml, re.S):
        pno = int(pm.group(1))
        if pno not in chunk: continue
        els = parse_page(pm.group(0), batch_fonts)
        b, n, printed = classify(els)
        printed = printed if printed else (pno - PRINT_OFFSET if pno > PRINT_OFFSET else None)
        if pno in outline:
            for title in outline[pno]:
                level = "##" if re.match(r'^[IVX]+\.', title) or title.isupper() else "###"
                body_out.append(f"\n{level} {title}\n")
        anchor = f"[*{printed}*]" if printed else f"[pdf {pno}]"
        bl = paragraphs(lines_from(b))
        if bl:
            bl[0] = anchor + " " + bl[0]
            body_out.extend(bl)
        elif n:
            body_out.append(anchor)
        nl = paragraphs(lines_from(n), indent_threshold=8)
        if nl:
            notes_out.append(f"**[p. {printed if printed else pno}]** " + " ".join(nl))
    print(f"pages {chunk[0]}-{chunk[-1]} done", file=sys.stderr)

md = "\n\n".join(body_out)
md = re.sub(r"\n{3,}", "\n\n", md)
md += "\n\n---\n\n## Notes (the printed footnotes, collected per printed page)\n\n" + "\n\n".join(notes_out) + "\n"

header = """# The King's Two Bodies: A Study in Mediaeval Political Theology

(Provenance header — see the generated file for the version actually shipped.)

---

"""
open(OUT, "w").write(header + md)
print(f"wrote {OUT}: {len(header+md)} chars, {len(notes_out)} note-pages")
