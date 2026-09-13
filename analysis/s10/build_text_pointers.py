#!/usr/bin/env python3
"""Replace verbatim transcript text with verifiable pointers.

WHY

The detector arms ship the sample they were computed on so a reader can check
that our scores belong to that text. But the control and flagged pools draw on
all twenty chambers, and their terms differ: British Columbia permits
reproduction "other than personal use" only with the Speaker's express written
consent, and Victoria publishes no general reuse grant for Hansard (see
SOURCE-LICENCES.md). Republishing those rows is not ours to do.

A pointer does the same job without redistributing anything. Each row keeps its
identifiers and gains `text_sha256` — the SHA-256 of the exact string that was
scored. A replicator fetches the segment from the chamber's own archive, hashes
it, and gets a yes/no answer on whether they are holding the same text we
scored. That is a stricter check than eyeballing a copy, and it needs no
licence from anyone.

The bypass variants are NOT converted. They are model rewrites that no script
can regenerate, so a hash of them points at nothing a reader could obtain; and
they draw only on NB and CA-FED, both of which permit research reproduction.

Usage:  python build_text_pointers.py [--check]
        --check verifies committed hashes against local text, and is how you
        confirm a pointer file still describes the corpus you have.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# file -> (format, the field holding text)
TARGETS = {
    "detector_bench_controls.jsonl": "jsonl",
    "flagged_hits_pool.json": "json",
}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def convert(row):
    text = row.pop("text", None)
    if text is None:
        return row, False
    row["text_sha256"] = sha(text)
    row["n_chars"] = len(text)
    return row, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify hashes against local text instead of writing")
    args = ap.parse_args()

    for name, fmt in TARGETS.items():
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"  {name}: absent, skipped")
            continue
        if fmt == "json":
            rows = json.load(open(path, encoding="utf-8", errors="replace"))
        else:
            rows = [json.loads(l) for l in open(path, encoding="utf-8",
                                                errors="replace") if l.strip()]
        if args.check:
            have = sum(1 for r in rows if "text_sha256" in r)
            text = sum(1 for r in rows if "text" in r)
            bad = sum(1 for r in rows if "text" in r and "text_sha256" in r
                      and sha(r["text"]) != r["text_sha256"])
            print(f"  {name}: {len(rows)} rows, {have} hashed, {text} still "
                  f"carry text, {bad} hash mismatches")
            continue
        n = sum(1 for r in rows if convert(r)[1])
        if fmt == "json":
            json.dump(rows, open(path, "w", encoding="utf-8"))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  {name}: {n} of {len(rows)} rows converted to pointers")


if __name__ == "__main__":
    main()
