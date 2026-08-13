#!/usr/bin/env python3
"""Alberta Hansard PDF -> shared segment schema.

pdftotext WITHOUT -layout yields correct reading order for the two-column
layout (verified: columns interleave badly WITH -layout). Structure in the
text stream:
  - running headers: "Alberta Hansard", "Month D, YYYY", bare page numbers
  - "head:" marker lines with the section title on an adjacent line
  - speaker turns start at line-anchored "Honorific Name: " labels
  - [bracketed stage directions], possibly multi-line
  - timestamps like "3:00 p.m." on their own line

Turns end at the next speaker label or a head: marker. Units for window
packing are sentences (PDF text has no reliable paragraph boundaries).

Usage: python3 ab_extract.py RAW_DIR OUT_JSONL
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prov_common import is_chair, pack_turn, sentences, dehyphenate

NAMEWORD = r"(?:[A-Z][A-Za-z'’\-.]*|van|von|de[rn]?)"
SPEAKER = re.compile(
    r"^(The (?:Acting |Deputy |Assistant )?"
    r"(?:Speaker|Chair(?:man)?|Clerk(?: Assistant)?|Sergeant-at-Arms"
    r"|Premier|Lieutenant Governor)"
    r"|His Honour[^:]{0,50}|Her Honour[^:]{0,50}"
    r"|An Hon\. Member|Some Hon\. Members|Hon\. Members(?: and Guests)?|Members"
    r"|(?:Hon\. )?(?:Mr\.|Mrs\.|Ms\.?|Miss|Dr\.|Rev\.|Member) ?"
    + NAMEWORD + r"(?: " + NAMEWORD + r"){0,2}"
    r"(?: \(on behalf of [^)]{0,60}\))?"
    r"):\s+(.*)$")
HEADER = re.compile(
    r"^(Alberta Hansard|\d{1,4}|"
    r"(?:January|February|March|April|May|June|July|August|September|October"
    r"|November|December) \d{1,2}, \d{4})$")
TIMESTAMP = re.compile(r"^\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.)?$")
META = re.compile(r"^(Title:|Date:|head:)")
INLINE_BRACKET = re.compile(r"\[[^\]\[]{0,200}\]")


def heading_like(line):
    """Short title line adjacent to a head: marker."""
    return (0 < len(line) <= 70 and len(line.split()) <= 10
            and not line.endswith((".", "?", "!", ",", ";"))
            and not SPEAKER.match(line))


def extract_file(pdf, prov="AB"):
    name = Path(pdf).name
    m = re.match(r"(\d{4})(\d{2})(\d{2})_", name)
    date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    txt = subprocess.run(["pdftotext", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    txt = dehyphenate(txt)
    lines = txt.split("\n")

    # mark heading lines adjacent to "head:" markers for removal
    drop = set()
    for i, ln in enumerate(lines):
        if ln.strip() != "head:":
            continue
        for j in range(i + 1, min(i + 4, len(lines))):   # title usually after
            s = lines[j].strip()
            if s:
                if heading_like(s):
                    drop.add(j)
                break
        for j in range(i - 1, max(i - 4, -1), -1):        # sometimes before
            s = lines[j].strip()
            if s:
                if heading_like(s) and j not in drop:
                    drop.add(j)
                break

    out = []
    turn = 0
    speaker = None
    parts = []           # accumulated raw text lines of current turn
    in_bracket = False

    def close():
        nonlocal parts, speaker, turn
        if speaker and parts and not is_chair(speaker):
            body = INLINE_BRACKET.sub(" ", " ".join(parts))
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                pack_turn(prov, date, turn, speaker, sentences(body), out)
                turn += 1
        parts, speaker = [], None

    for i, ln in enumerate(lines):
        s = ln.strip()
        if i in drop or not s:
            continue
        if HEADER.match(s) or TIMESTAMP.match(s):
            continue
        if META.match(s):
            if s.startswith("head:"):
                close()
            continue
        if in_bracket:
            if "]" in s:
                in_bracket = False
            continue
        if s.startswith("[") and "]" not in s:
            in_bracket = True
            continue
        if s.startswith("[") and s.endswith("]"):
            continue
        sm = SPEAKER.match(s)
        if sm:
            close()
            speaker = sm.group(1).strip()
            rest = sm.group(2).strip()
            if rest:
                parts.append(rest)
            continue
        if speaker:
            parts.append(s)
    close()
    return out, len(txt.split())


def main():
    raw_dir, out_path = Path(sys.argv[1]), sys.argv[2]
    n = raw_words = kept_words = 0
    with open(out_path, "w") as fh:
        for pdf in sorted(raw_dir.glob("*.pdf")):
            try:
                recs, rw = extract_file(pdf)
            except Exception as e:
                print(f"FAIL {pdf.name}: {e}", file=sys.stderr)
                continue
            raw_words += rw
            for r in recs:
                kept_words += r["n_words"]
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} segments; kept {kept_words}/{raw_words} raw words "
          f"({kept_words/max(raw_words,1):.1%})", file=sys.stderr)


if __name__ == "__main__":
    main()
