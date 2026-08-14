#!/usr/bin/env python3
"""Fetch UK Commons 2023, the one year the download design skipped.

Every year from 2000 to 2026 is present in uk/xml_deep/ except 2023. That is
not a source gap -- TheyWorkForYou lists 369 files for it -- but the same
washout-year exclusion the US downloader applied (fetch_us.py keeps PRE_YEARS
2018-2022 and POST_YEARS 2024-2026, dropping the ChatGPT transition year).

Sound for a pre/post contrast, wrong for a trend: 2023 is the single most
interesting year in a series about when machine drafting arrived, and its
absence puts a hole at exactly the point a reader looks first.

Usage: python fetch_uk_2023.py [--out xml_deep]
"""
import argparse, os, re, time, urllib.request

BASE = "https://www.theyworkforyou.com/pwdata/scrapedxml/debates/"
UA = {"User-Agent": "performance-commons-research/1.0 "
                    "(academic corpus build; matthewtomei@gmail.com)"}


def get(url, tries=4):
    for a in range(tries):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=90) as f:
                return f.read()
        except Exception:
            if a == tries - 1:
                return None
            time.sleep(5 * (a + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="xml_deep")
    ap.add_argument("--year", default="2023")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    idx = get(BASE)
    names = sorted(set(re.findall(
        rf'href="(debates{a.year}-\d{{2}}-\d{{2}}[a-z]?\.xml)"',
        idx.decode("utf-8", "replace"))))
    print(f"{len(names)} files for {a.year}", flush=True)
    ok = skip = fail = 0
    for i, n in enumerate(names, 1):
        p = os.path.join(a.out, n)
        if os.path.exists(p) and os.path.getsize(p) > 200:
            skip += 1
            continue
        b = get(BASE + n)
        # A truncated or error body must not be stored as if it were a sitting
        # NOT every valid file carries an <?xml prolog: many open straight
        # into <publicwhip scraperversion=...>. Requiring the prolog threw
        # away 18 of the first 50 good sitting days -- the same silent-loss
        # shape found in three other extractors today, here caused by a
        # validity check that was too tight rather than too loose.
        head = b.lstrip()[:40] if b else b""
        if b and len(b) > 200 and (head[:5] == b"<?xml"
                                   or head[:11] == b"<publicwhip"):
            open(p, "wb").write(b)
            ok += 1
        else:
            fail += 1
            print(f"  FAIL {n}", flush=True)
        if i % 50 == 0:
            print(f"  {i}/{len(names)} ok={ok} skip={skip} fail={fail}",
                  flush=True)
        time.sleep(1.0)
    print(f"done: ok={ok} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
