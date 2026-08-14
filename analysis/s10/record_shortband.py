#!/usr/bin/env python3
"""Append a harvested short-band batch to pangram_shortband_verdicts.csv.

Reads a JSON map {id: verdict} on stdin (the output of the browser harvester),
joins it to pangram_shortband_manifest.json for chamber/era/seg_id, and writes
only ids not already recorded. Idempotent, so re-running a batch is safe.

Usage:  echo '{"sbca-p015":"Human", ...}' | python record_shortband.py
        python record_shortband.py --summary
"""
import csv, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.join(HERE, "pangram_shortband_manifest.json")
OUT = os.path.join(HERE, "pangram_shortband_verdicts.csv")
FIELDS = ["id","chamber","era","seg_id","date","n_words","band","pangram","version"]
FLAG = ("AI", "Mixed")


def summary(rows):
    man = json.load(open(MAN))
    plan = collections.Counter((v["chamber"], v["era"]) for v in man.values())
    print(f"{'chamber':<9s} {'era':<5s} {'scored':>7s} {'planned':>8s} {'flagged':>10s}")
    tot = fl_tot = 0
    for key in sorted(plan):
        s = [r for r in rows if (r["chamber"], r["era"]) == key]
        if not s:
            print(f"{key[0]:<9s} {key[1]:<5s} {'-':>7s} {plan[key]:>8d}")
            continue
        fl = sum(1 for r in s if r["pangram"] in FLAG)
        tot += len(s); fl_tot += fl
        print(f"{key[0]:<9s} {key[1]:<5s} {len(s):>7d} {plan[key]:>8d} "
              f"{fl:>3d} = {100*fl/len(s):>5.1f}%")
    print(f"\n{tot:,} of {sum(plan.values()):,} scored; {fl_tot} flagged "
          f"({100*fl_tot/tot:.2f}%)" if tot else "")


def main():
    rows = list(csv.DictReader(open(OUT))) if os.path.exists(OUT) else []
    if "--summary" in sys.argv:
        summary(rows); return
    res = json.load(sys.stdin)
    man = json.load(open(MAN))
    have = {r["id"] for r in rows}
    added = skipped = 0
    for k, v in res.items():
        if v not in ("Human", "AI", "Mixed"):
            skipped += 1; continue
        if k in have or k not in man:
            skipped += 1; continue
        m = man[k]
        rows.append({"id": k, "chamber": m["chamber"], "era": m["era"],
                     "seg_id": m["seg_id"], "date": m["date"],
                     # Take the band from the MANIFEST, never a literal. This read
                     # "short" until 2026-08-13, which was harmless while the
                     # short band was all there was -- then the 19 over-360
                     # segments were recorded and every one was filed as
                     # short, moving the short band's word-weighted rate from
                     # 0.82% to 2.03% and leaving "over" reading as unscored.
                     "n_words": m["n_words"], "band": m.get("band", "short"),
                     "pangram": v, "version": "4.0-web"})
        added += 1
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f"added {added}, skipped {skipped}, total {len(rows)}\n")
    summary(rows)


if __name__ == "__main__":
    main()
