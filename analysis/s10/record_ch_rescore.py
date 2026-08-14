#!/usr/bin/env python3
"""Record the UK/Ireland Pangram 4 rescore and diff it against the old verdicts.

Takes the harvested {id: verdict} map on stdin, joins it to
pangram_ch_rescore/rescore_key.json, and writes pangram_ch_p4_verdicts.csv with
the same columns the rest of the study uses -- including a `version` column,
which is the thing the original arm lacked and the reason this rescore had to
happen at all.

THE DIFF IS THE POINT, NOT A BY-PRODUCT

Whatever the old tier was, the new verdicts are Pangram 4 and can be pooled. But
the old-vs-new comparison on 360 segments is also the largest P3-vs-P4 evidence
this study has: §3.2 currently rests on a 20-segment route check, and the New
Brunswick rescore flipped 55 of 658. If agreement here is near-total, the
four-chamber arm was already Pangram 4 and the tier worry was unfounded. If it
flips at a comparable rate to New Brunswick, the arm was Pangram 3 and every
figure that ever rested on it was wrong.

Read the flip DIRECTION too. P3 called Human on text P4 calls AI or Mixed, so a
P3 original should flip predominantly Human -> flagged. A symmetric scatter of
disagreements is not a tier difference; it is detector noise on borderline text,
and it would mean the two runs differ for reasons that have nothing to do with
the model version.

Usage:
  echo '{"ch000":"Human", ...}' | python record_ch_rescore.py
  python record_ch_rescore.py --summary
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "pangram_ch_rescore", "rescore_key.json")
OUT = os.path.join(HERE, "pangram_ch_p4_verdicts.csv")
FIELDS = ["id", "chamber", "stratum", "seg_id", "date", "n_words",
          "pangram", "prior", "version"]
FLAG = ("AI", "Mixed")


def load():
    return list(csv.DictReader(open(OUT))) if os.path.exists(OUT) else []


def summary(rows):
    if not rows:
        print("nothing recorded yet")
        return
    print(f"{len(rows)} of 360 rescored\n")
    print(f"  {'chamber':<22s} {'era':<5s} {'n':>4s} {'flagged w':>10s} "
          f"{'total w':>9s} {'rate':>7s}")
    for ch in sorted({r["chamber"] for r in rows}):
        for st in ("prev", "ctl"):
            sub = [r for r in rows if r["chamber"] == ch and r["stratum"] == st]
            if not sub:
                continue
            w = sum(int(r["n_words"]) for r in sub)
            kw = sum(int(r["n_words"]) for r in sub if r["pangram"] in FLAG)
            print(f"  {ch:<22s} {st:<5s} {len(sub):>4d} {kw:>10,} {w:>9,} "
                  f"{kw/w:>6.1%}")

    print("\n\nOLD vs NEW -- does the old arm behave like Pangram 4?\n")
    same = sum(1 for r in rows if r["pangram"] == r["prior"])
    print(f"  identical verdict: {same}/{len(rows)} = {same/len(rows):.1%}")
    diff = [r for r in rows if r["pangram"] != r["prior"]]
    if not diff:
        print("  no disagreements at all -- the arm was already Pangram 4")
        return
    print(f"  disagreements: {len(diff)}\n")
    print(f"  {'old -> new':<22s} {'n':>4s}")
    for (a, b), n in Counter((r["prior"], r["pangram"])
                             for r in diff).most_common():
        print(f"  {a + ' -> ' + b:<22s} {n:>4d}")
    up = sum(1 for r in diff if r["prior"] == "Human" and r["pangram"] in FLAG)
    dn = sum(1 for r in diff if r["prior"] in FLAG and r["pangram"] == "Human")
    print(f"\n  Human -> flagged: {up}    flagged -> Human: {dn}")
    if up > 3 * max(dn, 1):
        print("  Asymmetric toward flagged: the P3 signature. The old arm was "
              "Pangram 3.")
    elif abs(up - dn) <= max(2, 0.25 * len(diff)):
        print("  Roughly symmetric: this is borderline-text noise between two "
              "runs of the\n  SAME model, not a tier difference.")
    print(f"\n  For comparison, the New Brunswick P3->P4 rescore flipped 55 of "
          f"658 ({55/658:.1%}).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    rows = load()
    if a.summary:
        summary(rows)
        return

    key = json.load(open(KEY))
    got = json.load(sys.stdin)
    have = {r["id"] for r in rows}
    added = skipped = 0
    for cid, verdict in got.items():
        if cid in have:
            skipped += 1
            continue
        m = key.get(cid)
        if not m:
            print(f"  WARNING: {cid} is not in the key -- skipped")
            continue
        rows.append({"id": cid, "chamber": m["chamber"], "stratum": m["stratum"],
                     "seg_id": m["seg_id"], "date": m["date"],
                     "n_words": m["n_words"], "pangram": verdict,
                     "prior": m["prior"], "version": "4.0-web"})
        added += 1
    rows.sort(key=lambda r: r["id"])
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"added {added}, skipped {skipped}, total {len(rows)}/360")
    summary(rows)


if __name__ == "__main__":
    main()
