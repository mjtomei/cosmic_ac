#!/usr/bin/env python3
"""Mechanically apply an already-selected list of prose rewrites to the draft.

Selection — the unanimity gate and the contention resolution that decides WHICH
change lands — now lives in the workflow script (workflows/round2_iter_all.js),
where it is deterministic and inspectable alongside the votes that produced it.
This file does only the part that must not be a model's freehand job: locating
each change's verbatim `current` text and replacing it with `proposed`.

A change is applied ONLY if its `current` matches exactly once (after a
whitespace-tolerant fallback for line-rewrap differences). Anything ambiguous is
skipped and reported --- never guessed at.

Input is a JSON list of {id, current, proposed}. Exits non-zero if any change
could not be applied, so the caller can react rather than assume success.

Usage: apply_prose.py <selected.json> [--draft PATH] [--dry-run]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT = os.path.join(HERE, "S10-WRITEUP-DRAFT.md")


def find_span(text, needle):
    """Return (start, end) of the unique occurrence of needle, or None/'multi'."""
    n = text.count(needle)
    if n == 1:
        i = text.index(needle)
        return (i, i + len(needle))
    if n > 1:
        return "multi"
    # whitespace-tolerant: the draft may wrap lines differently
    pat = re.compile(r"\s+".join(re.escape(t) for t in needle.split()), re.S)
    hits = list(pat.finditer(text))
    if len(hits) == 1:
        return (hits[0].start(), hits[0].end())
    return "multi" if len(hits) > 1 else None


def main():
    changes = json.load(open(sys.argv[1]))
    draft = DRAFT
    if "--draft" in sys.argv:
        draft = sys.argv[sys.argv.index("--draft") + 1]
    dry = "--dry-run" in sys.argv
    text = open(draft, encoding="utf-8").read()
    before = len(text)

    applied, skipped = [], []
    for c in changes:
        cur, prop = (c.get("current") or "").strip(), (c.get("proposed") or "").strip()
        if not cur or not prop:
            skipped.append((c.get("id"), "empty current/proposed")); continue
        span = find_span(text, cur)
        if span is None:
            skipped.append((c.get("id"), "current text not found (superseded by an earlier change?)")); continue
        if span == "multi":
            skipped.append((c.get("id"), "current text is ambiguous (matches more than once)")); continue
        s, e = span
        text = text[:s] + prop + text[e:]
        applied.append(c.get("id"))

    print("applied: {}  skipped: {}".format(len(applied), len(skipped)))
    for i, why in skipped:
        print("  - {}: {}".format(i, why))
    print("  draft {:,} -> {:,} bytes ({:+,})".format(before, len(text), len(text) - before))

    if dry:
        print("  (dry run --- nothing written)")
        return 1 if skipped else 0
    open(draft, "w", encoding="utf-8").write(text)
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
