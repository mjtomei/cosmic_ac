#!/usr/bin/env python3
"""Remove non-zip downloads and backfill the per-year quota.

THE BUG THIS FIXES

fetch_us.py's sitting-day oracle asked for one byte and accepted HTTP 200/206.
But when a package does not exist GovInfo 302-redirects to an HTML error page,
and urllib FOLLOWS redirects, so the probe saw 200 and called it a sitting day.
40 of 330 "sitting days" were 44 KB of HTML. They were caught only because the
zip failed to open at extraction time -- the same class of silent
server-side failure as the six truncated New Brunswick PDFs.

The corrected oracle checks the CONTENT, not the status: a real package starts
with the zip magic number "PK". That cannot be faked by an error page.

Because the bad days clustered in recess periods (August, late December), the
loss was NOT random with respect to date, so it is backfilled rather than
absorbed: each year is topped back up to its quota from the same deterministic
candidate order, skipping days already tried.

Usage: python repair_us.py [--dir zips] [--per-year 30]
"""
import argparse
import collections
import hashlib
import os
import random
import time
import urllib.error
import urllib.request
import zipfile

from fetch_us import PKG, POST_YEARS, PRE_YEARS, UA, download, weekdays


def is_zip(path):
    try:
        with zipfile.ZipFile(path) as zf:
            return any(n.endswith("mods.xml") for n in zf.namelist())
    except Exception:
        return False


def probe(day, tries=3):
    """True only if the response body actually begins with the zip magic."""
    req = urllib.request.Request(PKG.format(d=day),
                                 headers={**UA, "Range": "bytes=0-1"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read(2) == b"PK"
        except urllib.error.HTTPError as e:
            if e.code in (404, 302, 303):
                return False
            if e.code in (429, 503):
                time.sleep(20 * (a + 1))
                continue
            return False
        except Exception:
            time.sleep(5 * (a + 1))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="zips")
    ap.add_argument("--per-year", type=int, default=30)
    args = ap.parse_args()

    have = collections.Counter()
    removed = []
    for f in sorted(os.listdir(args.dir)):
        if not f.endswith(".zip"):
            continue
        p = os.path.join(args.dir, f)
        day = f.replace("CREC-", "").replace(".zip", "")
        if is_zip(p):
            have[day[:4]] += 1
        else:
            os.remove(p)
            removed.append(day)
    print(f"removed {len(removed)} non-zip files")
    for y in sorted(have):
        print(f"  {y}: {have[y]} good")

    tried = set(removed)
    for f in os.listdir(args.dir):
        tried.add(f.replace("CREC-", "").replace(".zip", ""))

    total = 0
    for year in PRE_YEARS + POST_YEARS:
        want = args.per_year * (2 if year in POST_YEARS else 1)
        need = want - have[str(year)]
        if need <= 0:
            continue
        cands = weekdays(year)
        rng = random.Random(int(hashlib.sha1(
            f"CREC{year}".encode()).hexdigest()[:8], 16))
        rng.shuffle(cands)
        got = 0
        for day in cands:
            if got >= need:
                break
            if day in tried:
                continue
            tried.add(day)
            if not probe(day):
                continue
            if download(day, args.dir) and is_zip(
                    os.path.join(args.dir, f"CREC-{day}.zip")):
                got += 1
            time.sleep(0.3)
        print(f"  {year}: backfilled {got}/{need}")
        total += got
    print(f"backfilled {total} days")


if __name__ == "__main__":
    main()
