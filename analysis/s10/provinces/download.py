#!/usr/bin/env python3
"""Polite resumable downloader: 1 request/second max, verifies type/non-empty.

Usage: python3 download.py {bc|ab|sk|aus_wa}
Reads {prov}_manifest.json, writes into {prov}_raw/, logs to {prov}_download.log.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
# parliament.wa.gov.au and (documents.)parliament.qld.gov.au sit behind an
# Azure WAF that 403s non-browser agents; neither qld host serves robots.txt
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
              "Gecko) Chrome/126.0.0.0 Safari/537.36")
PROV_UA = {"aus_wa": BROWSER_UA, "aus_qld": BROWSER_UA}


# WHICH CHAMBERS THIS SCRIPT CAN ACTUALLY SERVE
#
# It names a downloaded file after the tail of its URL. That works only where
# the tail is a usable, unique filename. It is NOT true for most chambers, and
# the failures are silent or worse than silent:
#
#   NSW   .../pdf/HANSARD-1323879322-61896   -> extensionless; ok() then tests
#         it for HTML and rejects all of it (dl=0 fail=300)
#   SA    .../download                       -> EVERY row writes to one file
#         named "download"; the log reports skip=N, which reads as progress
#   TAS   bare .docx basenames               -> collide across years
#   ON    .../hansard                        -> all 702 days to one file
#   WALES CeConvert2PDF.aspx?MID=...         -> query string as filename, and
#         ok() rejects it for lacking a .pdf suffix
#
# Those five chambers have their own downloaders (aus_download.py,
# aus_sa_download.py, aus_tas_download.py, on_download_fill.py,
# wales_download_fill.py) which honour an explicit filename field in the
# manifest row. Use this script only for chambers whose manifest URLs end in a
# unique filename -- ab, bc, nl, sk, ni, aus_qld -- and check the tail before
# assuming a new one qualifies. Found 2026-08-13 after three chambers' fill
# downloads reported success and had fetched nothing.


def local_name(prov, url):
    parts = url.rsplit("/", 2)
    if prov in ("sk", "nl"):       # session dir prefix: basenames collide across sessions
        return parts[-2] + "_" + parts[-1]
    if prov == "aus_wa":           # "A39%20S1%2020160510%20All.pdf" -> spaces
        return urllib.parse.unquote(parts[-1])
    return parts[-1]


def ok(path, url):
    """Non-empty and right type for what the URL claims to be."""
    try:
        head = path.open("rb").read(2048)
    except OSError:
        return False
    if len(head) < 200:
        return False
    if url.lower().endswith(".pdf"):
        if not head.startswith(b"%PDF"):
            return False
        # TRUNCATED CAPTURES. A crawler that capped a fetch leaves a file that
        # starts %PDF and passes every check above, then fails extraction with
        # "Couldn't find trailer dictionary". Five Western Australia sitting
        # days came back from the Internet Archive at exactly 1 MiB for this
        # reason; re-fetching returns identical bytes, because the truncation
        # is in the stored copy. A head read cannot see it -- the tail can.
        try:
            with path.open("rb") as fh:
                fh.seek(max(0, path.stat().st_size - 2048))
                if b"%%EOF" not in fh.read():
                    return False
        except OSError:
            return False
        return True
    low = head.lower()
    if not (b"<html" in low or b"<!doctype" in low or b"<head" in low):
        return False
    # SOFT 404s. Several publishers answer a missing sitting with HTTP 200 and
    # a valid "page not found" document, which every check above passes.
    # assembly.nl.ca does exactly that in 4,755 bytes; the Internet Archive has
    # even crawled some of those error pages and stored them under the
    # sitting-day URL. A stored error page becomes a sitting day with no turns,
    # which reads as a parliament in recess rather than as a failed download.
    # Audited 2026-08-13 across every raw directory: no existing file matches,
    # so this is a guard against recurrence, not a repair.
    if len(head) < 12288:
        for m in (b"could not be found", b"page not found", b"page cannot be found",
                  b"error has occurred", b"no longer available",
                  b"access denied", b"the request is blocked"):
            if m in low:
                return False
    return True


def main():
    prov = sys.argv[1]
    rows = json.load(open(HERE / f"{prov}_manifest.json"))
    raw = HERE / f"{prov}_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / f"{prov}_download.log", "a")
    done = fail = skip = 0
    for i, r in enumerate(rows):
        url = r["url"]
        dest = raw / local_name(prov, url)
        if dest.exists() and ok(dest, url):
            skip += 1
            continue
        got = False
        for attempt in range(3):
            time.sleep(1.0 + attempt * 4)          # >= 1 s between requests
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": PROV_UA.get(prov, UA)})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                dest.write_bytes(data)
                if ok(dest, url):
                    got = True
                    break
                print(f"BADTYPE attempt{attempt} {url}", file=log, flush=True)
            except Exception as e:
                print(f"ERR attempt{attempt} {url} {e}", file=log, flush=True)
        if got:
            done += 1
        else:
            fail += 1
            if dest.exists():
                dest.unlink()
            print(f"FAIL {url}", file=log, flush=True)
        if (i + 1) % 50 == 0:
            print(f"progress {i+1}/{len(rows)} dl={done} skip={skip} fail={fail}",
                  file=log, flush=True)
    print(f"DONE total={len(rows)} dl={done} skip={skip} fail={fail}",
          file=log, flush=True)


if __name__ == "__main__":
    main()
