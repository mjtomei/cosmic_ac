#!/usr/bin/env python3
"""Historical CREC (2006-2017), sampled, for the state-gradient experiment.

WHY THESE YEARS

The exposure-gradient design regresses each member's register drift on their
state's computer/internet adoption timing. The drift window must be entirely
pre-LLM so nothing about ChatGPT contaminates it -- the UK long series shows
the register climb starts around 2006, so the informative span is
2006-2019: early window 2006-2010, late window 2015-2019. We hold the
complete record from 2018 on; this fetches the missing 2006-2017.

SAMPLED, NOT COMPLETE: 60 sitting days per year. Per-speaker drift uses
per-word rates over five-year pooled windows, so uniform within-year sampling
costs precision but not validity. ~60 days/yr x 12 yr ~= 720 zips ~= 18 GB.

The sitting-day oracle is the corrected one: a 2-byte range request checked
for the zip magic "PK". Status codes lie -- GovInfo 302s missing packages to
an HTML page and urllib follows redirects; that bug cost 40 fake days once
already (see repair_us.py).

Usage: python fetch_us_hist.py [--per-year 60] [--workers 8]
"""
import argparse
import datetime as dt
import hashlib
import os
import random
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch_us import PKG, UA, download

YEARS = list(range(2006, 2018))


def weekdays(year):
    d = dt.date(year, 1, 1)
    end = dt.date(year, 12, 31)
    out = []
    while d <= end:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def probe(day, tries=3):
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
    ap.add_argument("--per-year", type=int, default=60)
    ap.add_argument("--out", default="zips")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    picked = []
    for year in YEARS:
        cands = weekdays(year)
        rng = random.Random(int(hashlib.sha1(
            f"CREChist{year}".encode()).hexdigest()[:8], 16))
        rng.shuffle(cands)
        got, tried = [], 0
        for day in cands:
            if len(got) >= args.per_year:
                break
            p = os.path.join(args.out, f"CREC-{day}.zip")
            if os.path.exists(p) and good(p):
                got.append(day)
                continue
            tried += 1
            if probe(day):
                got.append(day)
            time.sleep(0.2)
        print(f"{year}: {len(got)} sitting days ({tried} probed)", flush=True)
        picked += sorted(got)

    todo = [d for d in picked
            if not good(os.path.join(args.out, f"CREC-{d}.zip"))]
    print(f"\n{len(picked)} days selected, {len(todo)} to download", flush=True)
    ok = done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(download, d, args.out): d for d in todo}
        for fut in as_completed(futs):
            done += 1
            ok += bool(fut.result())
            if done % 25 == 0:
                print(f"  {done}/{len(todo)} ok={ok}", flush=True)
    print(f"done: {ok}/{len(todo)}", flush=True)
    open("../US_HIST_DONE", "w").write(f"{ok}\n")


if __name__ == "__main__":
    main()
