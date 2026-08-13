#!/usr/bin/env python3
"""Tasmanian House of Assembly Hansard (.docx) -> shared segment schema.

SOURCE MARKUP
The Tasmanian Parliament publishes Hansard as Word files, one or two per sitting
day ("Part 1 - Pages 1 - 24" / "Part 2 - Pages 25 - 50"), and the ISYS search host
serves the original .docx. There is no semantic markup: paragraph styles are
auto-generated names (Style1..Style4, ListParagraph) whose meaning is not stable
across files, so this extractor works from the run-level formatting and the
Hansard house conventions instead.

  * A speech turn opens with a BOLD leading run holding the speaker label, with
    the surname in CAPITALS, immediately followed by an optional parenthetical
    and a dash:
        **Ms WHITE** (Lyons - Leader of the Opposition) - Madam Speaker, ...
        **Mr HODGMAN** - Madam Speaker, I move -
    The all-caps surname is what separates a speech from narration about a
    member, which uses ordinary case in the same bold position:
        **Mr Shelton** tabled the Report of Government Business Scrutiny ...
  * Later paragraphs of the same turn are plain (non-bold) body paragraphs.
  * ALL-CAPS paragraphs are section headings; the line under them is the subject.
  * [11.16 a.m.] timestamps sit on their own paragraph.
  * Procedural narration ("Motion agreed to.", "Sitting suspended from ...",
    "The House met at ...", "Members interjecting.") ends the turn.
  * Quoted matter -- motions, bills, correspondence read into the record -- is set
    as an indented block (w:ind w:left >= 340 twips). It is not the member's own
    speech, so it is dropped rather than packed.

ERA SPLITS
2006-2010 files use short generated names (h7june1.docx, h31october2.docx) and
2015-2019 files use descriptive ones (HA Tuesday 19 March 2019.docx), but the
internal conventions above are the same across both windows; the date comes from
the manifest, not the filename. Some 2006-2010 files are .doc (OLE2) rather than
.docx -- those are converted with LibreOffice on the fly if it is installed, and
skipped with a warning otherwise.

Estimates Committee / Government Businesses Scrutiny / Joint Sitting transcripts
share the same folders and are excluded upstream in aus_tas_manifest.py.

Units for packing are the original paragraphs.

Usage: python3 aus_tas_extract.py RAW_DIR OUT_JSONL [MANIFEST_JSON]
"""
import html as htmllib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn

PROV = "TAS"

W_T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)
W_P = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
W_R = re.compile(r"<w:r(?:\s[^>]*)?>.*?</w:r>", re.S)
W_RPR = re.compile(r"<w:rPr>.*?</w:rPr>", re.S)
W_BOLD = re.compile(r"<w:b\s*/>|<w:b\s[^>]*/>")
W_IND = re.compile(r'<w:ind[^>]*\sw:(?:left|start)="(-?\d+)"')

# "Mr HODGMAN", "Ms O'BYRNE", "Mr MICHAEL HODGMAN (Denison)", "Mr McKIM",
# "Madam SPEAKER", "The PRESIDENT": title + label + optional parentheticals + dash.
# The label is accepted as a SPEECH opener only when it is capitalised in the
# Hansard way (is_caps_label): a bold ordinary-case label in the same position is
# an interjection ("Mr Hidding - Not for mozzarella;"), which must not be folded
# into the speech it interrupts.
SPEAKER = re.compile(
    r"^((?:Mr|Mrs|Ms|Miss|Dr|Hon\.?|Madam|Sir|The)\s+[^-–—()\[\]:;,]{1,45}?)"
    r"\s*((?:\([^)]{0,140}\)\s*)*)[-–—‐]\s+")


def is_caps_label(name):
    """Hansard capitalises the speaker of a turn: HODGMAN, O'BYRNE, McKIM."""
    letters = [c for c in name if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) >= 0.6


ALLCAPS = re.compile(r"^[A-Z][A-Z0-9 ,.'’\-()&/]{3,}$")
TIMESTAMP = re.compile(r"^\[?\s*\d{1,2}[.:]\d{2}\s*(?:a\.?m\.?|p\.?m\.?)?\s*\]?$", re.I)
PAGE = re.compile(r"^(?:Pages?\s+\d+.*|\d{1,4}|[ivxlc]+)$", re.I)
PROC = re.compile(
    r"^(?:Motion|Amendment|Question|Bill|Clause|Clauses|Preamble|Title|Schedule"
    r"|Resolution|Petition|Report)\b.{0,160}"
    r"(?:agreed to|negatived|carried|lost|put and passed|read (?:a )?(?:first|second"
    r"|third)|resolved|adopted|withdrawn|tabled|laid on the table)\.?$"
    r"|^The (?:House|Committee|Council|Chamber)\s+(?:met|adjourned|divided|rose"
    r"|resumed|suspended|proceeded to divide)\b.{0,200}$"
    r"|^Sittings?\s+(?:suspended|resumed|adjourned)\b.{0,120}$"
    r"|^Members?\s+interjecting\.?$|^.{0,60}interjecting\.?$"
    r"|^(?:Laughter|Applause|Prayers|Interjections?)\b.{0,60}$"
    r"|^In (?:Committee|the Chair)\b.{0,120}$"
    r"|^\[.{0,200}\]$"
    r"|^(?:Ayes|Noes|AYES|NOES)\b.{0,200}$"
    r"|^Time expired\.?$|^Debate adjourned\.?$|^Leave granted\.?$"
    r"|^Business (?:interrupted|resumed)\b.{0,120}$"
    # narration ABOUT a member: "Mr Shelton tabled the Report ..." -- the verb has
    # to follow the name directly, so a member's own "Mr Speaker, I have moved ..."
    # is not caught
    r"|^(?:Mr|Mrs|Ms|Miss|Dr|Hon\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+"
    r"(?:tabled|presented|moved|took|resumed|read|was sworn|were sworn"
    r"|delivered|withdrew|retired)\b.{0,200}$",
    re.S)
# Tasmanian chair / procedural voices beyond prov_common's list: the Council's
# President and Deputy President, the Chairman of Committees, Serjeant/Usher.
TAS_CHAIR = re.compile(
    r"president|chairman|chairperson|serjeant|usher|black rod|governor"
    r"|leave granted|honourable member|^madam\b.*\b(speaker|president|chair)"
    r"|^(?:an?|some)\s+member", re.I)


W_STYLE = re.compile(r'<w:style\s[^>]*w:styleId="([^"]+)".*?</w:style>', re.S)
W_PSTYLE = re.compile(r'<w:pStyle w:val="([^"]+)"')
W_JC = re.compile(r'<w:jc w:val="([^"]+)"')


def style_map(z):
    """{styleId: (left_indent_twips, justification)} from word/styles.xml.

    The files carry no semantic style names, but the generated styles do encode
    layout: the quoted-matter style is the one with a left indent (typically 864
    twips = 0.6"), and headings are the centred style.
    """
    try:
        s = z.read("word/styles.xml").decode("utf-8", "replace")
    except KeyError:
        return {}
    out = {}
    for m in W_STYLE.finditer(s):
        blk = m.group(0)
        ind = W_IND.search(blk)
        jc = W_JC.search(blk)
        out[m.group(1)] = (int(ind.group(1)) if ind else 0,
                           jc.group(1) if jc else "")
    return out


def paragraphs(docx_path):
    """[(text, bold_lead, indented, centred)] in document order."""
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
        styles = style_map(z)
    # Word encodes non-breaking hyphens as their own element; without this
    # "Auditor-General" comes out as "AuditorGeneral"
    xml = xml.replace("<w:noBreakHyphen/>", "<w:t>-</w:t>")
    xml = re.sub(r"<w:(?:tab|br)\s*/>", "<w:t> </w:t>", xml)
    out = []
    for p in W_P.findall(xml):
        ppr = p.split("</w:pPr>")[0] if "</w:pPr>" in p else ""
        sm = W_PSTYLE.search(ppr)
        s_ind, s_jc = styles.get(sm.group(1), (0, "")) if sm else (0, "")
        m = W_IND.search(ppr)
        indent = int(m.group(1)) if m else s_ind
        jm = W_JC.search(ppr)
        centred = (jm.group(1) if jm else s_jc) == "center"
        bold_lead = False
        first = True
        for r in W_R.findall(p):
            rpr = W_RPR.search(r)
            txt = "".join(W_T.findall(r))
            if not txt.strip():
                continue
            if first:
                bold_lead = bool(rpr and W_BOLD.search(rpr.group(0)))
                first = False
        text = htmllib.unescape("".join(W_T.findall(p)))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            out.append((text, bold_lead, indent >= 340, centred))
    return out


def to_docx(path):
    """.doc/.rtf -> a temporary .docx via LibreOffice; returns None if impossible."""
    tmp = Path(tempfile.mkdtemp(prefix="tas_"))
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "docx",
                        "--outdir", str(tmp), str(path)],
                       capture_output=True, timeout=300, check=True)
    except Exception:
        return None
    hits = list(tmp.glob("*.docx"))
    return hits[0] if hits else None


def extract_file(path, date, chamber="HA"):
    p = Path(path)
    src = p
    if p.suffix.lower() != ".docx":
        src = to_docx(p)
        if src is None:
            raise RuntimeError("no .docx and no LibreOffice to convert")
    paras = paragraphs(src)
    raw_words = sum(len(t.split()) for t, _, _, _ in paras)

    out = []
    turn = 0
    speaker = None
    body = []

    def close():
        nonlocal body, speaker, turn
        if speaker and body and not is_chair(speaker) \
                and not TAS_CHAIR.search(speaker):
            start = len(out)
            # chamber-qualified prov keeps seg_ids unique if the Council is ever
            # added on the same sitting dates; the schema field stays "TAS"
            pack_turn(PROV + chamber, date, turn, speaker, body, out)
            for r in out[start:]:
                r["prov"] = PROV
                r["chamber"] = chamber
            turn += 1
        body, speaker = [], None

    for text, bold_lead, indented, centred in paras:
        if TIMESTAMP.match(text) or PAGE.match(text):
            continue
        if ALLCAPS.match(text) or centred:      # section heading / title page
            close()
            continue
        m = SPEAKER.match(text) if bold_lead else None
        if m:
            label = re.sub(r"\s+", " ", m.group(1)).strip(" .-")
            if is_caps_label(re.sub(r"^(?:Mr|Mrs|Ms|Miss|Dr|Hon\.?|Madam|Sir|The)\s+",
                                    "", label)):
                close()
                speaker = label
                rest = text[m.end():].strip()
                if rest:
                    body.append(rest)
            # else: an interjection by another member -- drop the paragraph but
            # keep the interrupted turn open (Hansard resumes it below)
            continue
        if PROC.match(text):                    # procedural narration
            close()
            continue
        if indented:                            # quoted motion / bill / letter
            continue
        if speaker:
            body.append(text)
    close()
    return out, raw_words


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    man_path = Path(sys.argv[3]) if len(sys.argv) > 3 else \
        Path(__file__).parent / "aus_tas_manifest.json"
    rows = json.load(open(man_path))
    # part 1 and part 2 of a day are separate files but one continuous sitting;
    # sort by (date, filename) so turn numbering is deterministic and give each
    # file a distinct turn offset via its part index
    rows.sort(key=lambda r: (r["date"], r["local"]))
    n = raw_words = kept_words = 0
    seen_ids = set()
    dupes = 0
    part_of_day = {}
    with open(out_path, "w") as fh:
        for r in rows:
            f = raw_dir / r["local"]
            if not f.exists():
                continue
            k = (r["prov_chamber"], r["date"])
            part_of_day[k] = part_of_day.get(k, 0) + 1
            try:
                recs, rw = extract_file(f, r["date"], r["prov_chamber"])
            except Exception as e:
                print(f"FAIL {r['local']}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            if not recs and rw > 200:
                print(f"EMPTY {r['local']} ({rw} raw words, no speaker matched)",
                      file=sys.stderr)
            tag = f"p{part_of_day[k]}"
            for rec in recs:
                rec["seg_id"] = rec["seg_id"].replace("#t", f"#{tag}t")
                rec["turn_id"] = rec["turn_id"].replace("#t", f"#{tag}t")
                if rec["seg_id"] in seen_ids:
                    dupes += 1
                    continue
                seen_ids.add(rec["seg_id"])
                kept_words += rec["n_words"]
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments ({dupes} duplicate seg_ids dropped); kept "
          f"{kept_words}/{raw_words} docx words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
