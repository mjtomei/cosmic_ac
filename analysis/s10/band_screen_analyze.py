#!/usr/bin/env python3
"""Harvest the Opus band screen and run the permeation dose-response test.

THE TEST

Drafting and permeation make opposite predictions about how the vocabulary
shift should be distributed across speech formats:

  DRAFTING: machine text enters where drafting is easy and worthwhile --
  long prepared statements. The AI-vocabulary shift should track detected
  AI, so it should be concentrated in the long band.

  PERMEATION: the ambient register has changed, so it shows up wherever
  people produce language, including short spontaneous interventions that
  nobody drafts with a model. The shift should be present -- and can be
  larger -- in the short band, while detected AI there stays near zero.

WHY THE PRE-2023 CELLS MATTER

An obvious objection to any short/long comparison is that the detector is
itself length-biased: maybe short text just scores lower. The pre-2023 cells
settle it. There was no AI to find in 2018-2022, so whatever short/long gap
appears there is pure instrument bias, and it can be subtracted from the
post-period gap. That makes the comparison valid even if the screen IS
length-biased.

Usage: python band_screen_analyze.py [RUN_DIR]
"""
import glob
import json
import math
import os
import sys
from collections import defaultdict

KEY = "band_screen_key.json"
BASE = ("/home/matt/.claude/projects/-home-matt-performance-commons/"
        "90221613-745b-4ed1-89b6-bc432df3d564/subagents/workflows")
THRESH = 50


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def harvest(run_dir):
    """Pull {id: score} out of the workflow journal and agent transcripts."""
    scores = {}

    def absorb(obj):
        if isinstance(obj, dict):
            if ("id" in obj and "ai_guess" in obj
                    and isinstance(obj.get("id"), str)
                    and obj["id"].startswith("B")):
                scores[obj["id"]] = obj["ai_guess"]
            else:
                for v in obj.values():
                    absorb(v)
        elif isinstance(obj, list):
            for v in obj:
                absorb(v)

    for path in glob.glob(os.path.join(run_dir, "*.jsonl")):
        for line in open(path):
            try:
                absorb(json.loads(line))
            except Exception:
                continue
    return scores


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir:
        cands = sorted(glob.glob(os.path.join(BASE, "wf_*")),
                       key=os.path.getmtime, reverse=True)
        for c in cands:
            if harvest(c):
                run_dir = c
                break
    if not run_dir:
        sys.exit("no workflow run directory with band scores found")
    print(f"run dir: {run_dir}")

    key = json.load(open(KEY))
    scores = harvest(run_dir)
    print(f"harvested {len(scores)} scores of {len(key)} segments\n")

    cell = defaultdict(list)
    for sid, s in scores.items():
        k = key.get(sid)
        if k:
            cell[(k["chamber"], k["band"], k["era"])].append(s)

    print(f"{'cell':<22s} {'n':>5s} {'mean':>7s} {'flag>=' + str(THRESH):>9s} "
          f"{'95% CI':>16s}")
    rates = {}
    for c in sorted(cell):
        v = cell[c]
        k = sum(x >= THRESH for x in v)
        lo, hi = wilson(k, len(v))
        rates[c] = (k, len(v), k / len(v))
        print(f"{'-'.join(c):<22s} {len(v):>5d} {sum(v)/len(v):>7.1f} "
              f"{k/len(v):>8.1%}  [{lo:>5.1%},{hi:>5.1%}]")

    print("\n=== dose-response, length-bias corrected ===")
    print("post-era flag rate minus that chamber-band's own pre-era rate,")
    print("so any length bias in the screen cancels within each band.\n")
    print(f"{'chamber':<10s} {'short signal':>14s} {'long signal':>13s} "
          f"{'long - short':>13s}")
    for ch in ("ie", "ca", "uk"):
        out = {}
        for band in ("short", "long"):
            pre = rates.get((ch, band, "pre"))
            post = rates.get((ch, band, "post"))
            if not (pre and post):
                out[band] = None
                continue
            out[band] = post[2] - pre[2]
        if out.get("short") is None or out.get("long") is None:
            print(f"{ch:<10s} incomplete")
            continue
        print(f"{ch:<10s} {out['short']:>13.1%} {out['long']:>12.1%} "
              f"{out['long'] - out['short']:>+12.1%}")

    print("\nReading: a POSITIVE 'long - short' means detected AI is")
    print("concentrated in prepared speech, as drafting predicts. Compare")
    print("against the lexicon excess, which runs the other way (short band")
    print("larger). Detected drafting up in long, vocabulary shift up in")
    print("short = the two are not the same phenomenon.")

    json.dump({"-".join(k): {"n": len(v), "mean": sum(v) / len(v),
                             "flag_rate": sum(x >= THRESH for x in v) / len(v)}
               for k, v in cell.items()},
              open("band_screen_results.json", "w"), indent=1)
    print("\nwrote band_screen_results.json")


if __name__ == "__main__":
    main()
