#!/usr/bin/env python3
"""Download the NI 2011-12/2012-09 gap day pages listed in ni_manifest_gap.json.

Why not the shared download.py: its local_name() takes the last path segment of
the URL, and these URLs end in a directory slash, so every day would land on
the same local name.  The manifest rows carry an explicit "file" key and this
script honours it.

The type check is stricter than download.py's generic "looks like HTML".  The
whole point of this route is that the day page carries the Official Report
inline; a page that is served but carries no speaker paragraphs is a landing
page, not a transcript, and must be recorded as a failure rather than pass
through and become a sitting day with no turns.  Two markup generations
qualify: up to 2012-03-27 the pages keep the Word export's class names
(B1SpeakersName et al.), and from 2012-04-16 the CMS emits the same document
with the classes stripped, a speaker turn being a bare
<p><strong>Name</strong>: ... .  Both are demanded at >= 50 speaker paragraphs,
which no landing page has and no real sitting day falls below.

Same politeness contract as download.py: >= 1 s between requests, 3 tries,
resumable (an already-good file is skipped).

Usage: python3 ni_download_gap.py [manifest.json] [raw_dir]
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"


# the colon sits either inside the <strong> or just after it, and both forms
# occur inside a single day page
SPEAKER_P = re.compile(rb'<p[^>]*>\s*<strong>[^<]{2,140}</strong>\s*:'
                       rb'|<p[^>]*>\s*<strong>[^<]{2,140}:\s*</strong>')


def ok(path):
    try:
        blob = path.read_bytes()
    except OSError:
        return False
    return len(blob) > 20000 and len(SPEAKER_P.findall(blob)) >= 50


def main():
    man = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "ni_manifest_gap.json")
    raw = Path(sys.argv[2] if len(sys.argv) > 2 else HERE / "ni_raw_gap")
    rows = json.load(open(man))
    raw.mkdir(exist_ok=True)
    log = open(HERE / "ni_download_gap.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url, dest = r["url"], raw / r["file"]
        if dest.exists() and ok(dest):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    dest.write_bytes(resp.read())
                if ok(dest):
                    got = True
                    break
                print(f"NOMARKUP attempt{attempt} {dest.name} {url}",
                      file=log, flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"ERR attempt{attempt} {dest.name} {url} {e}",
                      file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            if dest.exists():
                dest.unlink()
            print(f"FAIL {dest.name} {url}", file=log, flush=True)
        if (i + 1) % 20 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    msg = f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}"
    print(msg, file=log, flush=True)
    print(msg)


if __name__ == "__main__":
    main()
