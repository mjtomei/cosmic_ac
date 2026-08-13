#!/usr/bin/env python3
"""US Congressional Record (GovInfo CREC) -> stratified day sample of zips.

The govinfo *API* needs a key (DEMO_KEY is capped at ~40 req/hr and 429s
almost immediately, which killed the first attempt). The *content* endpoint
needs no credential at all:

    https://www.govinfo.gov/content/pkg/CREC-YYYY-MM-DD.zip
      HTTP 200/206 -> that day has a Record (Congress sat)
      HTTP 302     -> no package (recess/weekend)

So enumeration is dropped entirely: probe candidate weekdays with a 1-byte
range request and treat the status code as the sitting-day oracle.

Sampling is stratified by year so no single Congress dominates, and the
candidate order is seeded deterministically (sha1 of the year label) so the
sample is reproducible.

Windows follow replication_protocol.md: pre <= 2022-12-31, post >= 2024-01-01,
2023 excluded as the transition year.

Usage: python fetch_us.py [--per-year N] [--out DIR]
"""
import argparse
import datetime as dt
import hashlib
import os
import random
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = {"User-Agent": "s10-research/1.0 (academic corpus study)"}
PKG = "https://www.govinfo.gov/content/pkg/CREC-{d}.zip"
PRE_YEARS = [2018, 2019, 2020, 2021, 2022]
POST_YEARS = [2024, 2025, 2026]


def weekdays(year):
    d = dt.date(year, 1, 1)
    end = min(dt.date(year, 12, 31), dt.date.today() - dt.timedelta(days=2))
    out = []
    while d <= end:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def probe(day, tries=3):
    """True if CREC has a package for this day. Cheap 1-byte range GET."""
    req = urllib.request.Request(PKG.format(d=day),
                                 headers={**UA, "Range": "bytes=0-0"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status in (200, 206)
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


def download(day, out_dir, tries=3):
    path = os.path.join(out_dir, f"CREC-{day}.zip")
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return True
    req = urllib.request.Request(PKG.format(d=day), headers=UA)
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r, \
                    open(path + ".part", "wb") as fh:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    fh.write(b)
            os.replace(path + ".part", path)
            return True
        except Exception as e:
            print(f"    retry {day}: {str(e)[:70]}", flush=True)
            time.sleep(15 * (a + 1))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-year", type=int, default=30)
    ap.add_argument("--out", default="zips")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    picked = []
    for year in PRE_YEARS + POST_YEARS:
        cands = weekdays(year)
        rng = random.Random(int(hashlib.sha1(f"CREC{year}".encode()).hexdigest()[:8], 16))
        rng.shuffle(cands)
        # post-window years get a larger share: fewer years, and the
        # prevalence estimate needs the precision more than the baseline does
        want = args.per_year * (2 if year in POST_YEARS else 1)
        got, probes = [], 0
        for day in cands:
            if len(got) >= want:
                break
            probes += 1
            if probe(day):
                got.append(day)
            time.sleep(0.25)
        print(f"{year}: {len(got)} sitting days from {probes} probes", flush=True)
        picked += sorted(got)

    with open("us_days.txt", "w") as fh:
        fh.write("\n".join(picked) + "\n")
    print(f"\ntotal {len(picked)} days to download", flush=True)

    # Sequential fetching of ~21 MB packages runs about five hours; the
    # bottleneck is per-connection throughput, not the origin, so a small
    # thread pool is both much faster and still polite to the CDN.
    ok = 0
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(download, d, args.out): d for d in picked}
        for fut in as_completed(futs):
            ok += bool(fut.result())
            done += 1
            if done % 10 == 0:
                mb = sum(os.path.getsize(os.path.join(args.out, f))
                         for f in os.listdir(args.out) if f.endswith(".zip")) / 1e6
                print(f"  {done}/{len(picked)} ok={ok} {mb:.0f} MB", flush=True)

    print(f"done: {ok}/{len(picked)}", flush=True)
    open("../US_DOWNLOAD_DONE", "w").write(f"{ok}\n")


if __name__ == "__main__":
    main()
