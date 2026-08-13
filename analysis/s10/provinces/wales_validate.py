#!/usr/bin/env python3
"""Validate wales_pdf_manifest.json without downloading the corpus.

(1) re-fetch 6 doc-list pages spread across 2006/2008/2010/2015 and confirm the
    page title says "Plenary" and the date matches the manifest row;
(2) range-GET 8 PDF URLs spread across both windows, confirming HTTP 200,
    content-type application/pdf and size > 100 KB.
"""
import json
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
rows = json.load(open(os.path.join(HERE, "wales_pdf_manifest.json")))
random.seed(20260807)


def curl(args):
    return subprocess.run(["curl", "-sL", "-m", "60", "-A", UA] + args,
                          capture_output=True, text=True).stdout


print("=" * 70)
print("VALIDATION 1 - doc-list page title/date (6 meetings)")
print("=" * 70)
pool = {}
for r in rows:
    pool.setdefault(r["date"][:4], []).append(r)
sample1 = []
for y, n in [("2006", 2), ("2008", 2), ("2010", 1), ("2015", 1)]:
    sample1 += random.sample(pool[y], n)
ok1 = 0
for r in sample1:
    h = curl([f"https://business.senedd.wales/ieListDocuments.aspx?CId={r['body']}&MId={r['meeting']}"])
    t = re.search(r"<title>([^<]*)</title>", h)
    t = t.group(1) if t else "(no title)"
    plen = "Plenary" in t
    dm = re.search(r"(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", t)
    MON = {m: i + 1 for i, m in enumerate("January February March April May June July "
                                          "August September October November December".split())}
    tdate = f"{dm.group(3)}-{MON[dm.group(2)]:02d}-{int(dm.group(1)):02d}" if dm and dm.group(2) in MON else None
    good = plen and tdate == r["date"]
    ok1 += good
    print(f"  [{'OK ' if good else 'FAIL'}] {r['date']} MId={r['meeting']} CId={r['body']} :: {t}")
print(f"  => {ok1}/{len(sample1)} passed\n")

print("=" * 70)
print("VALIDATION 2 - PDF URLs reachable (8, range GET)")
print("=" * 70)
sample2 = []
for y, n in [("2006", 2), ("2007", 1), ("2008", 1), ("2009", 1), ("2010", 1), ("2015", 2)]:
    sample2 += random.sample(pool[y], n)
ok2 = 0
for r in sample2:
    out = curl(["-D", "-", "-o", "/dev/null", "-r", "0-0", r["url"]])
    # CeConvert2PDF 302-redirects to a static /Data/... file, so -L yields TWO
    # header blocks. Only the LAST one describes the object we actually get.
    codes = re.findall(r"HTTP/[\d.]+ (\d{3})", out)
    ctypes = re.findall(r"(?im)^content-type:\s*(\S+)", out)
    cranges = re.findall(r"(?im)^content-range:\s*bytes \d+-\d+/(\d+)", out)
    clens = re.findall(r"(?im)^content-length:\s*(\d+)", out)
    size = int(cranges[-1]) if cranges else (int(clens[-1]) if clens else 0)
    code = codes[-1] if codes else "?"
    ctype = (ctypes[-1] if ctypes else "?").split(";")[0]
    good = code in ("200", "206") and ctype == "application/pdf" and size > 100_000
    ok2 += good
    print(f"  [{'OK ' if good else 'FAIL'}] {r['date']} {code} {ctype} {size/1024:8.0f} KB  {r['url'][:88]}")
print(f"  => {ok2}/{len(sample2)} passed")
sys.exit(0 if ok1 == len(sample1) and ok2 == len(sample2) else 1)
