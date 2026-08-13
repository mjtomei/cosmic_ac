#!/usr/bin/env python3
"""Ontario / Manitoba / Nova Scotia Hansard HTML -> shared segment schema.

Per-province parsers feed a common turn-grouping + <=360-word window packer
(same conventions as ../ca/ca_extract.py). Chair/procedural voices excluded
by name; vote lists / prayers / orders-of-the-day excluded structurally
(headings reset the current speaker, so orphan paragraphs are dropped).

  ON: ola.org Drupal pages; transcript paragraphs all carry <span id="PARA..">
      anchors. class="td" = section headings, class="votetext" = division
      lists, <strong>NNNN</strong> = timestamps. French passages tagged by
      stopword ratio; French-majority segments scoreable:false.
  MB: Word-exported HTML, windows-1252 (Latin-1 superset). <div class=Section1>
      is the cover page (skipped); speech starts <b><span>Name:</span></b>.
      class=Subheading / align=center / all-bold paragraphs are headings.
  NS: two eras. 59th-60th assemblies: static .htm with <b>NAME:</b> speech
      prefixes (uppercase-name style). 61st+: Drupal pages, same field layout
      harvested from session tables; speech prefixes bold too.

Usage: python provinces_extract.py {on,mb,ns} RAW_DIR OUT_JSONL
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

MAX_WORDS = 360
MIN_WORDS = 50

CHAIR = re.compile(
    r"\b(speaker|clerk|chair|chairperson|president|sergeant[- ]at[- ]arms|"
    r"presiding officer)\b", re.I)
NONPERSON = re.compile(
    r"^(some hon|an hon|some honourable|an honourable|interjection|"
    r"a voice|voices|the house|hon\. members|hon\. member\b)", re.I)

EN = {"the","of","to","and","in","is","that","for","it","we","this","are",
      "have","be","will","with","on","as","has","was","our","not","by"}
FR = {"le","la","les","de","des","du","et","est","que","une","un","dans",
      "pour","nous","vous","avec","sur","qui","ce","cette","sont","pas","au"}

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
TIMESTAMP = re.compile(r"^[\d\s.:]+$")
MB_TIME = re.compile(r"\*\s*\(\s*\d{1,2}[.:]\d{2}\s*\)")


def strip_tags(s):
    return WS.sub(" ", htmllib.unescape(TAG.sub(" ", s))).strip()


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


def bad_speaker(sp):
    return (not sp) or CHAIR.search(sp) or NONPERSON.search(sp)


def emit_turns(turns, prov, date, fname, out):
    """turns: list of (speaker, section, [paragraph texts])"""
    tn = 0
    for speaker, section, paras in turns:
        if speaker:
            speaker = re.sub(r"^M\s+me\b", "Mme", speaker)   # M<sup>me</sup>
            speaker = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", speaker))
        if bad_speaker(speaker):
            continue
        paras = [p for p in paras if p]
        if not paras:
            continue
        turn_id = f"{prov}{date}#t{tn}"
        tn += 1
        buf, words, widx = [], 0, 0

        def flush():
            nonlocal buf, words, widx
            if not buf:
                return
            txt = " ".join(buf)
            lg = lang_of(txt)
            out.append({
                "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
                "date": date, "file": fname, "speaker": speaker,
                "section": section, "prov": prov, "lang": lg,
                "n_words": words,
                "scoreable": words >= MIN_WORDS and lg != "fr",
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


# ---------------------------------------------------------------- Ontario
P_TAG = re.compile(r"<p\b([^>]*)>(.*?)</p>", re.S)
STRONG0 = re.compile(r"^(?:\s|<a\b[^>]*>|</a>|<span\b[^>]*>|</span>|<!--.*?-->)*"
                     r"<strong>(.*?)</strong>", re.S)


ON_BLOCK = re.compile(r"<(p|h2|h3|h4)\b([^>]*)>(.*?)</\1>", re.S | re.I)


def parse_on(path):
    """Handles both eras: pre-2011 (class td/votetext, id=PARAnn) and
    2015+ (class speakerStart/procedure/timeStamp, id=parann, h2/h3 heads)."""
    h = path.read_text(encoding="utf-8", errors="replace")
    date = path.name[:10]
    has_ids = "id=\"para" in h.lower()
    if not has_ids:
        # rare export variant without paragraph anchors (e.g. 2015-05-07):
        # slice to the transcript region instead
        i = h.find('class="procedure"')
        j = h.find("</article")
        if i > 0:
            h = h[h.rfind("<", 0, i):(j if j > i else len(h))]
    turns = []
    section = ""
    cur = None       # (speaker, section, [paras])
    for m in ON_BLOCK.finditer(h):
        tag, attrs, body = m.group(1).lower(), m.group(2), m.group(3)
        if has_ids and 'id="para' not in body.lower():
            continue                    # transcript blocks carry para ids
        if 'href="#P' in body:
            continue                    # table-of-contents links
        if "votetext" in attrs or "timeStamp" in attrs:
            continue
        text = strip_tags(body)
        if not text:
            continue
        if tag in ("h2", "h3", "h4") or 'class="td"' in attrs:
            section = text[:120]        # section / topic heading
            cur = None
            continue
        if "procedure" in attrs:        # "Prayers." / "The House met at..."
            cur = None
            continue
        sm = STRONG0.match(body)
        if sm:
            st = strip_tags(sm.group(1))
            if TIMESTAMP.match(st):     # <strong>1350</strong> time marker
                continue
            if st.endswith(":"):
                sp = st.rstrip(":").strip()
                rest = strip_tags(body[sm.end():]).lstrip(":").strip()
                cur = (sp, section, [rest] if rest else [])
                turns.append(cur)
                continue
            # bold non-speaker line (inline heading) -> reset
            cur = None
            continue
        if cur is not None:
            cur[2].append(text)
    return date, turns


# ---------------------------------------------------------------- Manitoba
B_PREFIX = re.compile(r"^(?:\s|<a\b[^>]*>|</a>|<span\b[^>]*>|</span>|"
                      r"<st1:[^>]*>|</st1:[^>]*>|<o:p>|</o:p>|<!--.*?-->)*"
                      r"<b\b[^>]*>(.*?)</b>", re.S)


def parse_mb(path):
    h = path.read_text(encoding="latin-1", errors="replace")
    date = path.name[:10]
    # drop cover page (Section1); transcript starts at Section2
    i = h.find("<div class=Section2")
    if i > 0:
        h = h[i:]
    turns = []
    section = ""
    cur = None
    for m in P_TAG.finditer(h):
        attrs, body = m.group(1), m.group(2)
        body = MB_TIME.sub(" ", body)
        text = strip_tags(body)
        if not text:
            continue
        heading = ("Subheading" in attrs or "align=center" in attrs
                   or 'align="center"' in attrs or "DateStyle" in attrs)
        bm = B_PREFIX.match(body)
        if heading:
            section = text[:120]
            cur = None
            continue
        if bm:
            bt = strip_tags(bm.group(1))
            rest = strip_tags(body[bm.end():])
            if bt.endswith(":"):
                sp = bt.rstrip(":").strip()
                cur = (sp, section, [rest.lstrip(':').strip()] if rest else [])
                turns.append(cur)
                continue
            if rest.startswith(":"):
                cur = (bt.strip(), section, [rest.lstrip(":").strip()])
                turns.append(cur)
                continue
            if bt == text:              # fully-bold line = heading/marker
                section = text[:120]
                cur = None
                continue
        if cur is not None:
            cur[2].append(text)
    return date, turns


# ------------------------------------------------------------ Nova Scotia
NS_SPEAKER = re.compile(r"^([A-Z][A-Z0-9 .,'’&()À-Ü-]{2,70}?)\s*:\s+")
NS_PAGE = re.compile(r"^\[?Page \d+\]?$", re.I)


def ns_upper(s):
    # strip parenthetical role before uppercase test: HON. X (The Premier)
    core = re.sub(r"\([^)]*\)", "", s)
    letters = [c for c in core if c.isalpha()]
    return letters and all(c.isupper() for c in letters)


def parse_ns(path):
    h = path.read_text(encoding="utf-8", errors="replace")
    date = path.name[:10]
    # Drupal era: transcript sits in the main content region; old .htm era:
    # whole page is the transcript. Cut chrome by starting at the first
    # <P>/heading after the page H1 when a Drupal body wrapper exists.
    for marker in ('field--name-body', 'block-nslegislature-content'):
        i = h.find(marker)
        if i >= 0:
            h = h[i:]
            j = h.find('<footer')
            if j > 0:
                h = h[:j]
            break
    turns = []
    section = ""
    cur = None
    for m in re.finditer(r"<[pP]\b[^>]*>(.*?)</[pP]>", h, re.S):
        text = strip_tags(m.group(1))
        text = WS.sub(" ", text.replace("«", " ").replace("»", " ")).strip()
        if not text:
            continue
        if text.startswith("[") or NS_PAGE.match(text):
            continue                    # stage directions / page markers
        sm = NS_SPEAKER.match(text)
        if sm and ns_upper(sm.group(1)):
            sp = sm.group(1).strip()
            rest = text[sm.end():].strip()
            # QP topic headers look like "JUSTICE: PRISONER RELEASE - ..." --
            # all-caps remainder means heading, not speech
            if rest and ns_upper(rest) and len(rest.split()) < 20:
                section = text[:120]
                cur = None
                continue
            cur = (sp, section, [rest] if rest else [])
            turns.append(cur)
            continue
        if ns_upper(text) and len(text) < 120:
            section = text[:120]        # all-caps heading
            cur = None
            continue
        if cur is not None:
            cur[2].append(text)
    return date, turns


PARSERS = {"ON": parse_on, "MB": parse_mb, "NS": parse_ns}


def main():
    prov = sys.argv[1].upper()
    raw_dir = Path(sys.argv[2])
    out_path = sys.argv[3]
    parser = PARSERS[prov]
    n = 0
    files = sorted(raw_dir.iterdir())
    if prov == "NS":
        # A sitting can be listed on two session pages under different slugs
        # (e.g. 2010-03-25_61_1_house_10mar25 and 2010-03-25_house_10mar25).
        # Dedupe on date + the DDmonYY[a] token, keeping the larger file.
        best = {}
        for p in files:
            m = re.search(r"(\d{2}[a-z]{3}\d{2}[a-z]?)\.", p.name)
            key = (p.name[:10], m.group(1) if m else p.name)
            if key not in best or p.stat().st_size > best[key].stat().st_size:
                best[key] = p
        files = sorted(best.values())
    with open(out_path, "w") as fh:
        for p in files:
            if p.suffix not in (".html", ".htm"):
                continue
            try:
                date, turns = parser(p)
            except Exception as e:
                print(f"FAIL {p.name}: {e}", file=sys.stderr)
                continue
            out = []
            emit_turns(turns, prov, date, p.name, out)
            for r in out:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += len(out)
    print(f"{prov}: {len(files)} files -> {n} segments", file=sys.stderr)


if __name__ == "__main__":
    main()
