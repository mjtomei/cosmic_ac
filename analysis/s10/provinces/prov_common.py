"""Shared segmentation helpers for the provincial extractors (BC/AB/SK).

Schema matches ca/ca_extract.py's core fields:
  seg_id, turn_id, date, speaker, prov, n_words, scoreable, text
Packing rule: units (paragraphs, or sentences for PDF-derived text) packed
into windows of <=360 words, minimum 50 (smaller -> scoreable: false).
"""
import re

MAX_WORDS = 360
MIN_WORDS = 50

# Chair / procedural voices, per ca_extract.py's approach, extended for the
# western provinces (Sergeant-at-Arms, His/Her Honour = Lt. Gov., collective
# voices like "Some Hon. Members", "An Hon. Member").
CHAIR = re.compile(
    r"speaker|clerk|chair|presiding officer|sergeant|his honour|her honour"
    r"|lieutenant governor|acting|^members?$|hon\.? members|an hon\.? member"
    r"|some hon\.? members|both hon\. members|a voice|voices|interjection"
    r"|^the ",   # "The X" labels are all procedural voices in BC/AB/SK
    re.I)

SENT = re.compile(r"(?<=[.!?])[\"'’”)\]]?\s+(?=[A-Z“\"(\[])")


def is_chair(name):
    return bool(CHAIR.search(name))


def sentences(text):
    parts = []
    start = 0
    for m in SENT.finditer(text):
        end = m.start() + (1 if m.group(0)[0] in "\"'’”)]" else 0)
        parts.append(text[start:end].strip())
        start = m.end()
    parts.append(text[start:].strip())
    return [p for p in parts if p]


def pack_turn(prov, date, turn_idx, speaker, units, out):
    """Pack a list of text units into <=360-word windows; append dicts to out."""
    turn_id = f"{prov}{date}#t{turn_idx}"
    buf, words, widx = [], 0, 0

    def flush():
        nonlocal buf, words, widx
        if not buf:
            return
        txt = re.sub(r"\s+", " ", " ".join(buf)).strip()
        if not txt:
            buf, words = [], 0
            return
        n = len(txt.split())
        out.append({
            "seg_id": f"{turn_id}w{widx}", "turn_id": turn_id,
            "date": date, "speaker": speaker, "prov": prov,
            "n_words": n, "scoreable": n >= MIN_WORDS, "text": txt,
        })
        widx += 1
        buf, words = [], 0

    for u in units:
        w = len(u.split())
        if not w:
            continue
        if words + w > MAX_WORDS and words >= MIN_WORDS:
            flush()
        buf.append(u)
        words += w
    flush()


def dehyphenate(text):
    return re.sub(r"(\w)-\n(?=[a-z])", r"\1", text)
