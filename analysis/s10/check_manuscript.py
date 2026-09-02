#!/usr/bin/env python3
"""Mechanical integrity checks for the S10 manuscript and its LaTeX label map.

Run after any change application. Exits non-zero if issues are found, so an
apply loop can iterate — fix, re-check — until it comes back clean.

Checks:
  refs      every §N / §N.M reference resolves to a heading that exists
  assets    every referenced image file actually exists on disk
  appendix  every "Appendix X" reference resolves to an appendix that exists
  footnotes every [^tag] use has a definition (unused definitions: informational)
  headings  no duplicate heading text; numbering has no duplicate prefixes
  labels    every numbered heading has a LaTeX label in reformat.py's map, and
            every appendix letter is mapped (the transform must never hard-code
            a number; it strips them and uses \\cref/\\ref)
  ranges    reformat.py's appendix regexes cover every appendix letter in use
  forward   forward references, reported as a count only (convention, not error)

Usage: check_manuscript.py [--draft PATH] [--quiet]
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT = os.path.join(HERE, "S10-WRITEUP-DRAFT.md")
REFORMAT = os.path.join(HERE, "latex", "reformat.py")
EXTERNAL = ("METHODOLOGY", "analyze.py", "README", ".md ")   # cross-document refs


def maps_from_reformat():
    src = open(REFORMAT, encoding="utf-8").read()
    ns = {}
    for name in ("PREFIX_LABELS", "APPENDIX_LABELS"):
        m = re.search(r'^%s\s*=\s*\{.*?\n\}' % name, src, re.M | re.S)
        if m:
            exec(m.group(0), ns)
    letters = set()
    for m in re.finditer(r'\[A-([A-Z])\]', src):
        letters.add(m.group(1))
    return ns.get("PREFIX_LABELS", {}), ns.get("APPENDIX_LABELS", {}), letters


def main():
    draft = DRAFT
    if "--draft" in sys.argv:
        draft = sys.argv[sys.argv.index("--draft") + 1]
    text = open(draft, encoding="utf-8").read()
    issues, notes = [], []

    heads = re.findall(r'^(#{2,4})\s+(.+)$', text, re.M)
    titles = [h[1].strip() for h in heads]
    numbered = {}
    appendices = {}
    for t in titles:
        m = re.match(r'(\d+(?:\.\d+[a-z]?)?)\.?\s+(.*)', t)
        if m:
            numbered.setdefault(m.group(1), []).append(m.group(2))
        a = re.match(r'Appendix\s+([A-Z])\b\s*[—-]*\s*(.*)', t)
        if a:
            appendices.setdefault(a.group(1), []).append(a.group(2))

    # headings
    dupes = [t for t in set(titles) if titles.count(t) > 1]
    for d in dupes:
        issues.append(f"headings: duplicate heading {d!r}")
    for k, v in numbered.items():
        if len(v) > 1:
            issues.append(f"headings: section number {k} used {len(v)} times: {v}")

    # refs
    body = re.sub(r'^\[\^[^\]]+\]:.*$', '', text, flags=re.M)
    for ref in sorted(set(re.findall(r'§(\d+(?:\.\d+[a-z]?)?)', body))):
        if ref not in numbered:
            ctx = re.search(r'.{0,60}§' + re.escape(ref) + r'.{0,40}', body, re.S)
            snippet = " ".join(ctx.group(0).split())[:100] if ctx else ""
            if any(e in snippet for e in EXTERNAL):
                notes.append(f"refs: §{ref} looks like a cross-document ref ({snippet[:60]})")
            else:
                issues.append(f"refs: §{ref} does not resolve to any heading — {snippet}")
    for letter in sorted(set(re.findall(r'Appendix~?\s*([A-Z])\b', body))):
        if letter not in appendices:
            issues.append(f"appendix: 'Appendix {letter}' referenced but no such appendix")

    # footnotes
    defs = set(re.findall(r'^\[\^([^\]]+)\]:', text, re.M))
    uses = set(re.findall(r'\[\^([^\]]+)\](?!:)', text))
    for u in sorted(uses - defs):
        issues.append(f"footnotes: [^{u}] used but never defined")
    if defs - uses:
        notes.append(f"footnotes: defined but never referenced: {sorted(defs - uses)}")

    # assets: a proposal can add a figure reference for a figure that does not
    # exist — the data-faithfulness gate passes it (no datum changes) and voters
    # judge the described figure as if it were real. Verify the file.
    for path in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
        if path.startswith(("http://", "https://", "data:")):
            continue
        cand = path if os.path.isabs(path) else os.path.join(os.path.dirname(os.path.abspath(draft)), path)
        if not os.path.exists(cand):
            issues.append(f"assets: image {path!r} is referenced but no such file exists")

    # figures must be wired into the LaTeX transform, or they render as bare
    # images with no float, caption, label, or cross-reference.
    try:
        rsrc = open(REFORMAT, encoding="utf-8").read()
        figmap = dict(re.findall(r'"([^"]+\.png)"\s*:\s*"(fig:[^"]+)"', rsrc))
        for path in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
            base = os.path.basename(path)
            if base.endswith(".png") and base not in figmap:
                issues.append(f"labels: figure {base!r} has no FIGLABEL entry in reformat.py "
                              f"— it will render without a float, caption or label")
    except OSError:
        pass

    # latex label map
    P, A, letters = maps_from_reformat()
    if P:
        for num in sorted(numbered):
            if num.replace(".", "") not in P:
                issues.append(f"labels: §{num} ({numbered[num][0][:40]}) has no entry in PREFIX_LABELS "
                              f"— the LaTeX transform will not be able to label it")
    if A:
        for letter in sorted(appendices):
            if f"appendix-{letter.lower()}" not in A:
                issues.append(f"labels: Appendix {letter} ({appendices[letter][0][:34]}) missing from APPENDIX_LABELS")
    if letters and appendices:
        top = max(letters)
        want = max(appendices)
        if want > top:
            issues.append(f"ranges: reformat.py regexes cover appendices up to [A-{top}] "
                          f"but the draft now goes to {want}")

    # hard-coded numbers that should be references (informational)
    fwd = len(re.findall(r'§\d', body))
    notes.append(f"forward/section references in draft: {fwd} (LaTeX resolves these via \\cref)")

    if "--quiet" not in sys.argv:
        for n in notes:
            print(f"  note: {n}")
    if issues:
        print(f"\n{len(issues)} ISSUE(S):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("\nclean: no issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
