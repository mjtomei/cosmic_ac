#!/usr/bin/env python3
"""Download EVERY Congressional Record sitting day in both protocol windows.

WHY REPLACE THE SAMPLE

The 330-day stratified sample gave the US ~3M pre-window words per chamber
against the UK's 47M. Both US chambers came out statistically null under
protocol v1.1, but at that corpus size a null is uninformative -- the effect
sizes seen elsewhere (+0.03 to +0.12) are simply not detectable. Taking the
complete record turns a shrug into a real test, and gives two more
adequately-powered chambers rather than two more question marks.

It also removes the sampling artifact that inflated the US v1.0 numbers:
sampling days thins per-word counts, raises the zero-count rate, and drags
the placebo baseline down (US -0.37/-0.44 versus -0.13/-0.31 in the complete
corpora), which inflates every excess. A complete corpus is directly
comparable to the other chambers; a sample is not.

THE PROBE IS THE CORRECTED ONE. fetch_us.py accepted HTTP 200/206, but
GovInfo 302-redirects missing packages to an HTML error page and urllib
follows redirects, so 40 of 330 "sitting days" were 44 KB of HTML. Here the
oracle checks the response BODY for the zip magic number, which an error page
cannot fake.

Scale: ~1,980 weekdays across the two windows, of which roughly two thirds
have a Record; about 25 MB each, so on the order of 35 GB.

Usage: python fetch_us_all.py [--workers 8] [--probe-workers 16]
"""
import argparse
import datetime as dt
import os
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch_us import PKG, UA, download

WINDOWS = [(dt.date(2018, 1, 1), dt.date(2022, 12, 31)),
           (dt.date(2024, 1, 1), dt.date.today() - dt.timedelta(days=2))]


def all_weekdays():
    out = []
    for start, end in WINDOWS:
        d = start
        while d <= end:
            if d.weekday() < 5:
                out.append(d.isoformat())
            d += dt.timedelta(days=1)
    return out


def probe(day, tries=3):
    """True only if the body starts with the zip magic. Status codes lie:
    a missing package 302s to an HTML page and urllib follows it."""
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
                time.sleep(15 * (a + 1))
                continue
            return False
        except Exception:
            time.sleep(4 * (a + 1))
    return False


def good(path):
    try:
        with zipfile.ZipFile(path) as zf:
            return any(n.endswith("mods.xml") for n in zf.namelist())
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="zips")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--probe-workers", type=int, default=16)
    args = ap.parse_args()
    os.makedirs(args.dir, exist_ok=True)

    days = all_weekdays()
    have = set()
    for f in os.listdir(args.dir):
        if f.endswith(".zip") and good(os.path.join(args.dir, f)):
            have.add(f.replace("CREC-", "").replace(".zip", ""))
    todo = [d for d in days if d not in have]
    print(f"{len(days):,} weekdays in the protocol windows; "
          f"{len(have)} already downloaded; probing {len(todo):,}", flush=True)

    hits = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.probe_workers) as ex:
        futs = {ex.submit(probe, d): d for d in todo}
        for fut in as_completed(futs):
            done += 1
            if fut.result():
                hits.append(futs[fut])
            if done % 200 == 0:
                print(f"  probed {done:,}/{len(todo):,}, {len(hits)} with a Record",
                      flush=True)
    hits.sort()
    print(f"{len(hits):,} sitting days to fetch "
          f"(~{len(hits) * 26 / 1024:.0f} GB)", flush=True)
    with open("us_days_all.txt", "w") as fh:
        fh.write("\n".join(sorted(have | set(hits))) + "\n")

    ok = 0
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(download, d, args.dir): d for d in hits}
        for fut in as_completed(futs):
            done += 1
            ok += bool(fut.result())
            if done % 25 == 0:
                mb = sum(os.path.getsize(os.path.join(args.dir, f))
                         for f in os.listdir(args.dir)
                         if f.endswith(".zip")) / 1e3
                print(f"  {done:,}/{len(hits):,} ok={ok} {mb:.1f} GB", flush=True)
    print(f"done: {ok}/{len(hits)}", flush=True)
    open("../US_FULL_DONE", "w").write(f"{ok}\n")


if __name__ == "__main__":
    main()
