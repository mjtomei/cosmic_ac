#!/usr/bin/env python3
"""Link the fill-year NL raw files into nl_raw_fill/ for the extractor.

`download.py nl` writes every manifest row into the shared nl_raw/, which
already holds the 2006-2010 and 2015-2019 sampled years. The extractor takes a
directory, not a file list, so the fill years need their own directory. These
are symlinks: the raw transcripts are publisher-licensed, never committed, and
there is no reason to hold a second copy of 415 files.

TWO WAYS THIS STEP FAILS SILENTLY, BOTH GUARDED

Name mismatch. download.py's local_name() prefixes NL files with their session
directory, because Hansard basenames repeat across General Assemblies
(06-02-23.htm is a real filename in more than one session). Names are computed
here by calling that same function rather than reconstructed, and the run
asserts that every manifest row found its file. An earlier Queensland attempt
matched "20110215" against files named "2011_02_15_WEEKLY.PDF", linked nothing,
and the extractor produced a clean empty output that read as a parliament that
never sat.

Soft 404s. assembly.nl.ca answers a missing Hansard page with HTTP 200 and a
~4.7 KB "Sorry, this page could not be found!" document. download.py's check
only asks whether the bytes are HTML, so those land in nl_raw/ looking like
sitting days. They are detected here by content and excluded, with the dates
printed -- an error page contributes no turns, so the cost of missing one is a
sitting day that quietly reads as silence.

Usage: python nl_link_fill.py [--raw nl_raw] [--dest nl_raw_fill]
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from download import local_name          # the exact naming used to write them

ERROR_MARK = re.compile(r"this page could not be found|NL - Error Page", re.I)
# A real page the publisher posts in a sitting day's slot to say the day was
# lost, usually to weather. Kept and linked -- it yields no turns, which is the
# right answer -- but counted separately, because a reader checking these
# per-year totals against the sitting record needs to know which days are
# transcripts and which are notices that there is nothing to transcribe.
DID_NOT_SIT = re.compile(r"House of Assembly did not si", re.I)


def head_text(path):
    with open(path, "rb") as fh:
        return fh.read(6000).decode("utf-8", errors="replace")


def is_error_page(path):
    return bool(ERROR_MARK.search(head_text(path)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="nl_manifest_fill.json")
    ap.add_argument("--raw", default="nl_raw")
    ap.add_argument("--dest", default="nl_raw_fill")
    a = ap.parse_args()

    rows = json.load(open(os.path.join(HERE, a.manifest)))
    raw, dest = os.path.join(HERE, a.raw), os.path.join(HERE, a.dest)
    os.makedirs(dest, exist_ok=True)
    for f in os.listdir(dest):                   # idempotent re-runs
        p = os.path.join(dest, f)
        if os.path.islink(p):
            os.unlink(p)

    linked, missing, errors, notices = 0, [], [], []
    per_year = collections.Counter()
    notice_year = collections.Counter()
    for r in rows:
        name = local_name("nl", r["url"])
        src = os.path.join(raw, name)
        if not os.path.exists(src):
            missing.append((r["date"], name))
            continue
        if is_error_page(src):
            errors.append((r["date"], name))
            continue
        os.symlink(os.path.relpath(src, dest), os.path.join(dest, name))
        linked += 1
        per_year[r["date"][:4]] += 1
        if DID_NOT_SIT.search(head_text(src)):
            notices.append(r["date"])
            notice_year[r["date"][:4]] += 1

    print(f"{len(rows)} manifest rows -> {linked} linked into {a.dest}")
    for y in sorted(per_year):
        n = notice_year[y]
        extra = f"  ({n} of them a did-not-sit notice)" if n else ""
        print(f"  {y}: {per_year[y]:>3d} files{extra}")
    if notices:
        print(f"{len(notices)} did-not-sit notices (no turns to extract): "
              f"{notices}")
    if errors:
        print(f"{len(errors)} error pages excluded: {[d for d, _ in errors]}")
    if missing:
        print(f"{len(missing)} NOT DOWNLOADED: {missing}")
    # the Queensland failure mode: a directory the extractor happily reads as
    # a parliament that never met
    assert linked > 0, "linked zero files -- check local_name() against nl_raw/"
    assert not missing, f"{len(missing)} manifest rows have no file in {a.raw}"


if __name__ == "__main__":
    main()
