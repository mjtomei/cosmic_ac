#!/usr/bin/env python3
"""Dual-purpose smoke test for the Pangram Bulk API.

IT ANSWERS TWO QUESTIONS AT ONCE

1. BILLING. Does API usage draw on the API's dollar balance ($167.10 "plan
   balance") or on the same 15,000/month text-credit pool the web dashboard
   uses? If they are the same pool, routing the overhang through the API buys
   nothing. Read /plan and /apikey before and after this run and compare.

2. ROUTE AGREEMENT. Do the web dashboard and the API return the same verdict
   on the same text? We are about to split one arm across two routes, so a
   systematic difference between them would land in whichever chambers got the
   API and quietly shift their prevalence. That is the same reason each chamber
   buys its own specificity control instead of borrowing one.

SAMPLING IS DELIBERATELY NOT RANDOM. The web-scored pool is 607 Human / 30 AI
/ 23 Mixed, so a random 20 would come back ~19 Human and agreement would look
perfect no matter how the routes differ. This is a validation sample, not a
prevalence estimate, so it oversamples AI and Mixed, where disagreement can
actually show up. Do NOT reuse these verdicts as prevalence data.

TEXT FIDELITY. Segment text is recovered by reversing the exact RTF encoding
that was uploaded to the web, so both routes see the same characters. The one
irreducible difference is the container: the web got RTF, the API gets a JSON
string. That is part of what is being measured.

Usage: python api_route_check.py [--n 20] [--go]
       Without --go it prints the sample and the cost and submits nothing.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "https://text.external-api.pangram.com"
DIRS = {"pangram_ch_manifest.json": "pangram_ch",
        "pangram_ch2_manifest.json": "pangram_ch2",
        "pangram_x_manifest.json": "pangram_x",
        "pangram_genre_manifest.json": "pangram_genre"}
OUT = HERE / "api_route_check.json"


def api_key():
    k = os.environ.get("PANGRAM_API_KEY")
    if k:
        return k.strip()
    p = Path.home() / ".pangram_key"
    if p.exists():
        return p.read_text().strip()
    sys.exit("no API key: ~/.pangram_key or PANGRAM_API_KEY")


# Destination groups whose contents are metadata, not text. Left in, the
# font table leaks "Times New Roman;" into the payload.
SKIP = ("fonttbl", "colortbl", "stylesheet", "info", "pict", "header",
        "footer", "generator")


def unrtf(s):
    """Extract plain text from RTF.

    Written generically rather than as the inverse of one writer: the
    2026-07 batches (pangram_ch/ch2) carry a bare \\rtf1\\ansi\\deff0 header
    while build_pangram_expansion.py emits a fonttbl and \\fs24, so a
    header-specific regex silently no-ops on half the corpus and ships the
    control words to the detector as if they were speech.
    """
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == "{":
            m = re.match(r"\{\\\*?\\?([a-zA-Z]+)", s[i:])
            if m and m.group(1) in SKIP:      # skip the balanced group whole
                depth, j = 0, i
                while j < n:
                    if s[j] == "{":
                        depth += 1
                    elif s[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                i = j + 1
                continue
            i += 1
            continue
        if c == "}":
            i += 1
            continue
        if c == "\\":
            if i + 1 < n and s[i + 1] in "\\{}":
                out.append(s[i + 1])
                i += 2
                continue
            m = re.match(r"\\u(-?\d+)\s?\??", s[i:])
            if m:
                cp = int(m.group(1))
                out.append(chr(cp + 65536 if cp < 0 else cp))
                i += m.end()
                continue
            m = re.match(r"\\'([0-9a-fA-F]{2})", s[i:])
            if m:
                out.append(chr(int(m.group(1), 16)))
                i += m.end()
                continue
            m = re.match(r"\\([a-zA-Z]+)(-?\d+)?[ ]?", s[i:])
            if m:
                if m.group(1) in ("par", "line", "tab"):
                    out.append(" ")
                i += m.end()
                continue
            i += 1
            continue
        out.append(c)
        i += 1
    return " ".join("".join(out).split())


def post(path, payload, key):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def get(path, key):
    req = urllib.request.Request(BASE + path, headers={"x-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--resume", default="", help="poll an existing bulk_id")
    ap.add_argument("--model", default="pangram-4",
                    help="pangram-4 (matches the web) or default (=Pangram 3)")
    args = ap.parse_args()

    man, home = {}, {}
    for mf, d in DIRS.items():
        p = HERE / mf
        if p.exists():
            got = json.load(open(p))
            man.update(got)
            home.update({k: d for k in got})

    rows = [r for r in csv.DictReader(open(HERE / "pangram_ch_verdicts.csv"))
            if r.get("pangram") and r["file"] in man]

    # oversample the informative classes; deterministic, no RNG
    by_v = {"AI": [], "Mixed": [], "Human": []}
    for r in sorted(rows, key=lambda r: r["file"]):
        by_v.setdefault(r["pangram"], []).append(r)
    want = {"AI": 8, "Mixed": 6, "Human": 6}
    scale = args.n / 20.0
    pick = []
    for v, k in want.items():
        pool = by_v.get(v, [])
        k = min(round(k * scale), len(pool))
        # spread across chambers rather than taking a contiguous run
        step = max(len(pool) // k, 1) if k else 1
        pick += pool[::step][:k]

    items, meta = [], {}
    for r in pick:
        f = r["file"]
        rtf_path = HERE / home[f] / (f + ".rtf")
        if not rtf_path.exists():
            continue
        text = unrtf(rtf_path.read_text())
        items.append({"id": f, "text": text})
        meta[f] = {"web": r["pangram"], "chamber": r["chamber"],
                   "stratum": r["stratum"], "n_words": r["n_words"],
                   "chars": len(text)}

    words = sum(int(meta[i["id"]]["n_words"]) for i in items)
    print(f"validation sample: {len(items)} segments, {words:,} words")
    print(f"  web verdicts: {dict(Counter(meta[i['id']]['web'] for i in items))}")
    print(f"  chambers    : {dict(Counter(meta[i['id']]['chamber'] for i in items))}")
    print(f"  cost @ bulk $0.04/100w ~= ${words * 0.0004:.2f}")
    if not args.go:
        print("\ndry run — pass --go to submit")
        return

    key = api_key()
    if args.resume:
        bulk_id = args.resume
        print(f"resuming bulk_id={bulk_id}", flush=True)
    else:
        print("\nsubmitting bulk job...", flush=True)
        # MUST be explicit. The API default is "default" = Pangram 3
        # (version 3.3.2); the web dashboard runs Pangram 4. Omitting this
        # silently scores on a different model from every web verdict we
        # hold, and the 2026-07 New Brunswick run did exactly that.
        sub = post("/bulk", {"items": items, "model": args.model}, key)
        bulk_id = sub.get("bulk_id") or sub.get("id")
        # persist FIRST. A previous run lost a paid job because the id only
        # ever existed in stdout, which was buffered through a pipe and
        # discarded when the poll loop hit its timeout.
        (HERE / "api_bulk_id.txt").write_text(str(bulk_id) + "\n")
        print(f"  bulk_id={bulk_id} (saved)  raw={json.dumps(sub)[:300]}",
              flush=True)

    recs = []
    for attempt in range(120):
        st = get(f"/bulk/{bulk_id}", key)
        if attempt == 0:
            # print the whole thing once: guessing at field names is what
            # made the last run poll a finished job until it was killed
            print(f"  raw status: {json.dumps(st)[:500]}", flush=True)
        status = str(st.get("status") or st.get("stage") or "").upper()
        print(f"  [{attempt * 5:>4}s] status={status} "
              f"{ {k: v for k, v in st.items() if k != 'status'} }"[:160],
              flush=True)
        if "FAIL" in status or "ERROR" in status:
            sys.exit(f"bulk job failed: {json.dumps(st)[:400]}")
        # Gate on succeeded==total, NOT on row count: /results returns all
        # rows immediately in a pending state, so "len(rows)==len(items)"
        # fires while every verdict is still empty.
        if st.get("succeeded", 0) + st.get("failed", 0) >= st.get(
                "total_items", len(items)):
            res = get(f"/bulk/{bulk_id}/results?offset=0&limit=500", key)
            recs = res.get("items") or res.get("results") or []
            break
        time.sleep(5)
    print(f"\ngot {len(recs)} results")
    if not recs:
        sys.exit("no results — bulk_id saved to api_bulk_id.txt, "
                 "re-poll with --resume $(cat api_bulk_id.txt)")

    out, agree, dis = [], 0, []
    for rec in recs:
        rid = rec.get("id") or rec.get("item_id")
        m = meta.get(rid, {})
        r = rec.get("result") or {}          # verdict is nested, not top-level
        api_v = (r.get("prediction_short") or r.get("prediction") or "?")
        api_v = {"ai": "AI", "human": "Human", "mixed": "Mixed"}.get(
            str(api_v).strip().lower(), str(api_v))
        row = {"file": rid, **m, "api": api_v,
               "version": r.get("version"),
               "fraction_ai": r.get("fraction_ai"),
               "fraction_ai_assisted": r.get("fraction_ai_assisted")}
        out.append(row)
        if m.get("web") == api_v:
            agree += 1
        else:
            dis.append(row)

    json.dump(out, open(OUT, "w"), indent=1)
    n = len(out)
    print(f"\n=== ROUTE AGREEMENT ===")
    print(f"  exact verdict match: {agree}/{n}"
          f"{'' if not n else f' ({agree / n:.0%})'}")
    print(f"  cross-tab (web -> api):")
    ct = Counter((r["web"], r["api"]) for r in out)
    for k in sorted(ct):
        print(f"    {k[0]:<6s} -> {k[1]:<6s} {ct[k]}")
    if dis:
        print(f"  disagreements:")
        for r in dis:
            print(f"    {r['file']} {r['chamber'][:22]:<22s} "
                  f"web={r['web']:<6s} api={r['api']:<6s} "
                  f"frac_ai={r.get('fraction_ai')}")
    print(f"\nwrote {OUT}")
    print("NOW: re-read /plan and /apikey. If text credits are still 11,123 "
          "and the dollar balance fell, the pools are separate.")


if __name__ == "__main__":
    main()
