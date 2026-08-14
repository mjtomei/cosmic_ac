#!/usr/bin/env python3
"""Polite resumable downloader for the WA backfill years, off the Archive.

Same contract as download.py -- >= 1 s between requests, resumable, %PDF and
soft-404 checks (imported from it, not re-implemented) -- reading
aus_wa_manifest_fill.json and writing into the existing aus_wa_raw/.

WHY NOT JUST download.py.  Three differences, all about the Archive rather
than about WA.

1. RETRY DEPTH.  web.archive.org answers a sustained series of requests
   unevenly: a run of fetches will collect 503s and outright connection
   refusals for a minute and then serve the same URLs perfectly. download.py
   gives each URL three attempts over ten seconds, which is the right budget
   for a parliament's own web server and far too short here -- the first pass
   through this manifest failed 11 of the first 13 files, every one of which
   downloaded fine on a later attempt. This makes several passes over the
   whole manifest with a long wait between them, so a transient outage costs
   a retry rather than a sitting day. That matters more than usual for this
   province: a dropped file is a missing chamber-day in a backfill that is
   already thin in 2011-2014, and it would look like a parliament in recess.

2. USER AGENT.  download.py sends a browser UA for aus_wa because
   parliament.wa.gov.au's WAF 403s anything else. We are not talking to the
   parliament here, so the honest research UA is used instead -- the Archive
   asks for identifiable clients, and there is nothing to get past.

3. TRUNCATION, AND WHY THE NEWEST CAPTURE IS NOT ALWAYS THE ONE TO TAKE.
   download.py's ok() reads the first 2 KB, which a half-stored PDF passes.
   Six of these files arrived at exactly 1 MiB, starting "%PDF" and ending
   mid-stream: the crawler that made those captures stopped at a megabyte, so
   the truncation is in the Archive's copy and re-fetching returns the same
   bytes. pdftotext refuses them ("Couldn't find trailer dictionary") and the
   extractor logs a FAIL, which is six sitting days quietly absent from the
   output. So a file must also carry %%EOF near its end, and when the capture
   named in the manifest fails that test this asks CDX for every capture of
   the same URL and tries them newest first -- for 2022-09-21 Assembly the
   manifest's newest capture is the truncated one and an earlier crawl holds
   the whole document. The check is local rather than in download.py's ok()
   because the other provinces fetch from origin servers that either complete
   a response or fail it; this is the Archive's failure mode.

Local names come from download.py's local_name(), which URL-unquotes the
basename: the Wayback URLs end in the original attachment path, so
".../$File/A38%20S1%2020110216%20All.pdf" lands as "A38 S1 20110216 All.pdf",
matching the 2006-2019 files already in aus_wa_raw/. Checked before the first
run: 546 rows, 546 distinct local names, no collisions with what is there.

Usage: python3 aus_wa_download_fill.py [--passes N]
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from download import local_name, ok as head_ok

HERE = Path(__file__).parent
CDX = "http://web.archive.org/cdx/search/cdx"
UA = ("performance-commons-research/1.0 "
      "(academic corpus build; matthewtomei@gmail.com)")


def ok(path, url):
    """download.py's checks, plus a whole-file one: PDFs end in %%EOF."""
    if not head_ok(path, url):
        return False
    try:
        with path.open("rb") as fh:
            fh.seek(max(0, path.stat().st_size - 4096))
            return b"%%EOF" in fh.read()
    except OSError:
        return False


def captures(url, log):
    """Every timestamp the Archive holds for a wrapped URL, newest first."""
    orig = urllib.parse.unquote(url.split("id_/", 1)[1])
    q = urllib.parse.urlencode({"url": orig, "output": "json",
                                "filter": "statuscode:200", "fl": "timestamp"})
    try:
        with urllib.request.urlopen(CDX + "?" + q, timeout=180) as r:
            rows = json.loads(r.read().decode() or "[]")
        return sorted((t for t, in rows[1:]), reverse=True)
    except Exception as e:
        print(f"CDXERR {url} {e}", file=log, flush=True)
        return []


def try_url(url, dest, log, attempts=4):
    """One URL, N attempts, backing off 1/6/16/31 s. True if stored intact."""
    for attempt in range(attempts):
        time.sleep(1.0 + attempt * 5 + (attempt == 3) * 10)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read()
            dest.write_bytes(data)
            if ok(dest, url):
                return True
            print(f"BADTYPE a{attempt} {len(data)}B {url}", file=log, flush=True)
        except Exception as e:
            print(f"ERR a{attempt} {url} {e}", file=log, flush=True)
    return False


def fetch(url, dest, log):
    """The manifest's capture; failing that, the URL's other captures."""
    if try_url(url, dest, log):
        return True
    stamp = url.split("/web/", 1)[1].split("id_/", 1)[0]
    for ts in captures(url, log):
        if ts == stamp:
            continue
        alt = url.replace(f"/web/{stamp}id_/", f"/web/{ts}id_/", 1)
        print(f"ALT trying {ts} for {dest.name}", file=log, flush=True)
        if try_url(alt, dest, log, attempts=2):
            print(f"ALT ok {ts} {dest.name}", file=log, flush=True)
            return True
    if dest.exists():
        dest.unlink()
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--manifest", default="aus_wa_manifest_fill.json")
    a = ap.parse_args()

    rows = json.load(open(HERE / a.manifest))
    raw = HERE / "aus_wa_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "aus_wa_download_fill.log", "a")

    for p in range(a.passes):
        todo = [r for r in rows
                if not ok(raw / local_name("aus_wa", r["url"]), r["url"])]
        print(f"pass {p}: {len(todo)} of {len(rows)} still missing",
              file=log, flush=True)
        print(f"pass {p}: {len(todo)} of {len(rows)} still missing", flush=True)
        if not todo:
            break
        got = 0
        for i, r in enumerate(todo):
            if fetch(r["url"], raw / local_name("aus_wa", r["url"]), log):
                got += 1
            if (i + 1) % 25 == 0:
                print(f"  pass {p} {i+1}/{len(todo)} dl={got}",
                      file=log, flush=True)
        print(f"pass {p} done: {got}/{len(todo)}", file=log, flush=True)
        if got < len(todo) and p + 1 < a.passes:
            time.sleep(120)                        # let the Archive recover

    have = sum(1 for r in rows
               if ok(raw / local_name("aus_wa", r["url"]), r["url"]))
    print(f"DONE have={have}/{len(rows)} missing={len(rows)-have}",
          file=log, flush=True)
    print(f"DONE have={have}/{len(rows)} missing={len(rows)-have}", flush=True)
    for r in rows:
        if not ok(raw / local_name("aus_wa", r["url"]), r["url"]):
            print(f"MISSING {r['date']} {r['chamber']} {r['url']}",
                  file=log, flush=True)


if __name__ == "__main__":
    main()
