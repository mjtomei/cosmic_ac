#!/usr/bin/env python3
"""Score the S10 expansion + the New Brunswick rescore on Pangram 4.

ROUTING

Two paid routes exist and they are INDEPENDENT pools (verified 2026-08-09:
44 API scans moved the API dollar balance and left the 15,000 monthly text
credits untouched):

  Bulk API   - $0.04 / 100 words at the 20% bulk discount, plan balance
  Dashboard  - 1 credit / 100 words, rounded UP per document

MODEL MUST BE NAMED. The API's default model is "default" = Pangram 3
(version 3.3.2); the web dashboard runs Pangram 4. On a 20-segment sample
enriched for AI and Mixed, the two agreed on 11/20 — the default called
Human on 3 of 8 web-AI segments and 5 of 6 web-Mixed, and never returned
Mixed at all. With model="pangram-4" agreement was 20/20 including all six
Mixed. So the routes are interchangeable ONLY when the model is explicit.
See api_route_check.py.

That same defect is why New Brunswick is being rescored: the 2026-07 run
passed no model and silently took Pangram 3, so its 658 verdicts are a
different instrument from every web-scored chamber.

WHAT GOES WHERE. New Brunswick goes to the API unconditionally: its text
survives only inside pangram_results.jsonl (the RTFs were built for a
different batch), and reusing the stored text guarantees the rescore sees
byte-identical input to the P3 run, which is what makes the two comparable.
The API budget is then filled with expansion files, controls and genre
first so an interruption leaves whole arms. Everything left is written to
a worklist for the dashboard.

RESUMABLE. Every bulk_id is persisted BEFORE polling and verdicts are
appended as they land, so a kill or a timeout costs nothing. An earlier
run lost a paid job by keeping the id only in piped stdout.

Usage: python pangram_run_p4.py [--budget 150] [--go]
       Without --go it prints the plan and submits nothing.
"""
import argparse
import csv
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from api_route_check import DIRS, api_key, get, post, unrtf

HERE = Path(__file__).resolve().parent
VERDICTS = HERE / "pangram_p4_verdicts.csv"
BULKS = HERE / "pangram_p4_bulks.jsonl"
WEB_WORKLIST = HERE / "pangram_p4_web_worklist.json"
RATE = 0.0004          # $/word, Pangram 4 bulk
CHUNK = 100
FIELDS = ["file", "source", "chamber", "stratum", "arm", "seg_id", "date",
          "speaker", "n_words", "genre", "regime_flag", "pangram",
          "fraction_ai", "version", "prior_p3"]


def load_items():
    """Every unit of work, with the text already resolved."""
    items = []

    # --- New Brunswick rescore: text straight from the P3 results ---
    p = HERE / "pangram_results.jsonl"
    if p.exists():
        for line in open(p):
            d = json.loads(line)
            t = (d.get("response") or {}).get("text")
            if not t:
                continue
            items.append({
                "id": "nb_" + str(d["seg_id"]), "text": t,
                "meta": {"source": "nb_rescore", "chamber": "NB",
                         "stratum": d.get("stratum", ""), "arm": "tier4",
                         "seg_id": d["seg_id"], "date": d.get("date", ""),
                         "speaker": d.get("speaker", ""),
                         "n_words": len(t.split()), "genre": "",
                         "regime_flag": "",
                         "prior_p3": d["response"].get("prediction_short", "")}})

    # --- expansion: text recovered from the RTFs that the dashboard eats ---
    for mf, sub in DIRS.items():
        f = HERE / mf
        if not f.exists() or sub in ("pangram_ch", "pangram_ch2"):
            continue          # already scored on the web route (Pangram 4)
        for name, m in json.load(open(f)).items():
            rtf = HERE / sub / (name + ".rtf")
            if not rtf.exists():
                continue
            items.append({
                "id": name, "text": unrtf(rtf.read_text()),
                "meta": {"source": "expansion", "chamber": m["chamber"],
                         "stratum": m["stratum"], "arm": m["arm"],
                         "seg_id": m["seg_id"], "date": m["date"],
                         "speaker": m.get("speaker", ""),
                         "n_words": m["n_words"], "genre": m.get("genre", ""),
                         "regime_flag": m.get("regime_flag", ""),
                         "prior_p3": ""}})
    return items


def priority(it):
    """API budget goes to whole arms first, so a stop leaves them complete."""
    m = it["meta"]
    if m["source"] == "nb_rescore":
        return 0                       # must be API: text lives only in JSON
    if m["arm"] == "genre":
        return 1
    if m["stratum"] == "ctl":
        return 2
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=150.0,
                    help="max $ of API balance to spend")
    ap.add_argument("--go", action="store_true")
    args = ap.parse_args()

    done = set()
    if VERDICTS.exists():
        for r in csv.DictReader(open(VERDICTS)):
            if r.get("pangram"):
                done.add(r["file"])

    items = [i for i in load_items() if i["id"] not in done]
    items.sort(key=lambda i: (priority(i), i["id"]))

    # conservative costing: assume per-document round-up to 100 words even
    # though the measured bulk charge was word-proportional ($1.92 for
    # 4,812 words). Erring high cannot overspend; erring low can.
    api, web, spend = [], [], 0.0
    for it in items:
        c = math.ceil(len(it["text"].split()) / 100) * 0.04
        if spend + c <= args.budget:
            api.append(it)
            spend += c
        else:
            web.append(it)

    def summarise(rows, label):
        by = Counter(f"{r['meta']['source']}/{r['meta']['stratum'] or r['meta']['arm']}"
                     for r in rows)
        w = sum(len(r["text"].split()) for r in rows)
        print(f"{label:<10s} {len(rows):>5,} files  {w:>9,} words")
        for k, v in sorted(by.items()):
            print(f"             {k:<28s} {v:>5,}")
        return w

    print(f"already scored on P4: {len(done):,}\n")
    wa = summarise(api, "API")
    print(f"             est. cost ${spend:.2f} (conservative) / "
          f"${wa * RATE:.2f} (word-proportional)\n")
    ww = summarise(web, "DASHBOARD")
    wc = sum(math.ceil(len(r["text"].split()) / 100) for r in web)
    print(f"             {wc:,} credits of 11,123 available\n")

    json.dump([{"file": r["id"], **r["meta"]} for r in web],
              open(WEB_WORKLIST, "w"), indent=1)
    print(f"wrote {WEB_WORKLIST.name} ({len(web):,} files for the browser)")

    if not args.go:
        print("\ndry run — pass --go to submit the API portion")
        return

    key = api_key()
    if not VERDICTS.exists():
        with open(VERDICTS, "w", newline="") as fh:
            csv.DictWriter(fh, fieldnames=FIELDS).writeheader()

    tally = Counter()
    for start in range(0, len(api), CHUNK):
        chunk = api[start:start + CHUNK]
        payload = {"items": [{"id": c["id"], "text": c["text"]} for c in chunk],
                   "model": "pangram-4"}
        try:
            sub = post("/bulk", payload, key)
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            print(f"  submit failed ({e.code}): {body}", flush=True)
            if e.code in (402, 403):
                print("  stopping — looks like balance exhausted")
                break
            continue
        bid = sub.get("bulk_id")
        with open(BULKS, "a") as fh:      # persist BEFORE polling
            fh.write(json.dumps({"bulk_id": bid,
                                 "ids": [c["id"] for c in chunk]}) + "\n")
        recs = []
        for _ in range(240):
            st = get(f"/bulk/{bid}", key)
            if st.get("succeeded", 0) + st.get("failed", 0) >= st.get(
                    "total_items", len(chunk)):
                recs = (get(f"/bulk/{bid}/results?offset=0&limit=500",
                            key).get("items") or [])
                break
            time.sleep(5)
        meta = {c["id"]: c["meta"] for c in chunk}
        with open(VERDICTS, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            for rec in recs:
                rid = rec.get("id")
                r = rec.get("result") or {}
                v = r.get("prediction_short") or "?"
                tally[v] += 1
                w.writerow({"file": rid, **meta.get(rid, {}), "pangram": v,
                            "fraction_ai": r.get("fraction_ai"),
                            "version": r.get("version")})
        print(f"  [{start + len(chunk):>5,}/{len(api):,}] bulk={bid[:16]} "
              f"got {len(recs)}  running tally={dict(tally)}", flush=True)

    print(f"\ndone. {sum(tally.values()):,} verdicts -> {VERDICTS.name}")


if __name__ == "__main__":
    main()
