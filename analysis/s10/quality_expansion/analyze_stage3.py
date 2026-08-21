#!/usr/bin/env python3
"""Stage 3: does detector-evading rewriting improve or degrade the speech?

THE QUESTION

The most effective evasion strategy found was "self-limiting first person" --
admitting what you do not know, conceding about yourself rather than about the
world. It flipped Pangram on 39% of attempts, against 11% for stripping
tricolons and nominalisations. Epistemic humility was absent from 0 of 40
AI-drafted seeds and present in 15% of matched human speech.

So the operation that defeats the detector may be the same operation that
improves the deliberation. If so, "humanizing" is not a synonym for "hiding":
a member editing an AI draft to sound like themselves and a member laundering
one past a detector perform the same edit, and the text cannot distinguish
their motives.

DESIGN

38 texts, each contributing its unmodified ORIGINAL and its best HUMANIZED
variant. Blinded, interleaved, graded on the v2b DQI rubric. Within-text
pairing means content, speaker and occasion are held fixed by construction --
the only thing varying is the rewrite.

LENGTH: REPORTED, NOT PARTIALLED OUT -- AND IT DOES NOT REPLICATE. Humanized
versions run longer in stage 4 (mean +29 words; stage 3's PAIRED shift is
~0: median +4, mean -1.3, 42% shorter -- the covariate is kept in stage 3
for precision, not bias: within-pair word-count sd ~38 words),
and within stage 4 justification tracks length at r = +0.33, the largest
correlation in either table. In stage 3 the same correlation is r = -0.24:
longer rewrites justify LESS. Neither is significant (p = 0.11, p = 0.15), and
stage 3 is the better-identified of the two, its deltas running both directions
with sd 38 against stage 4's one-sided 14. A sign that flips between two arms of
one design is not a finding, so the story that justification's stage-4 drift
"was length" fails on the data and not merely on the statistics.

It would not be a confound even if it held. On this rubric a longer passage
genuinely has room to justify more, and earning justification by adding words is
a strategy a member with a longer slot could use too -- partialling it out would
treat a real route to quality as a nuisance parameter. So length is
reported as a plain correlation, r(words), and the raw paired difference is the
quoted effect.

This file used to regress each pair's score change on its word change and
report the intercept -- the modelled effect at zero word delta -- with the
instruction "Quote that column." Two things were wrong with that and both are
now removed. It was never needed: the design is within-text paired, so content,
speaker and occasion are already fixed by construction and there is nothing for
a covariate to control. And it was not identified in stage 4, where 24 of 25
deltas are strictly positive, so a zero delta sat 2.1 sd outside the sample
(intercept VIF 5.43, standard error inflated 2.3x) and the column flipped
justification from +0.16 to -0.173 on extrapolation alone. The write-up quoted
that flip as evidence the gain "was length" before the error was caught.

-1 codes INAPPLICABLE (no other demand / no counterargument on the table) and
is excluded from means, matching the published v2 convention.

Usage: python analyze_stage3.py [WORKFLOW_RUN_DIR]
"""
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENTINEL = {"respect_demands", "respect_counterargs"}
BASE = os.path.expanduser("~/.claude/projects")


def harvest(run_dir):
    out = {}

    def absorb(o):
        if isinstance(o, dict):
            i = o.get("id")
            if isinstance(i, str) and i[:1] in ("H", "G") and len(i) == 4 \
                    and "justification" in o:
                out[i] = o
            else:
                for v in o.values():
                    absorb(v)
        elif isinstance(o, list):
            for v in o:
                absorb(v)

    for p in glob.glob(os.path.join(run_dir, "*.jsonl")):
        for line in open(p):
            try:
                absorb(json.loads(line))
            except Exception:
                pass
    return out


def paired_t(diffs):
    n = len(diffs)
    if n < 3:
        return None, None
    m = statistics.mean(diffs)
    s = statistics.stdev(diffs)
    if s == 0:
        return m, float("inf")
    return m, m / (s / math.sqrt(n))


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x)
                    * sum((b - my) ** 2 for b in y))
    return num / den if den else None


def main():
    args = [a for a in sys.argv[1:] if a != "--key4"]
    run = args[0] if args else None
    if not run:
        for c in sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                               "workflows", "wf_*")),
                        key=os.path.getmtime, reverse=True):
            if harvest(c):
                run = c
                break
    if not run:
        sys.exit("no run dir with H-ids found — pass one explicitly")
    print(f"run dir: {run}")
    kf = "key4.json" if "--key4" in sys.argv else "key3.json"
    pf = "G" if kf == "key4.json" else "H"
    key = json.load(open(os.path.join(HERE, kf)))
    g = harvest(run)
    print(f"graded {len(g)}/{len(key)}\n")
    if len(g) < 40:
        sys.exit("too few grades")

    pairs = {}
    for qid, rec in g.items():
        k = key.get(qid)
        if not k:
            continue
        pairs.setdefault(k["seg_id"], {})[k["condition"]] = (rec, k)
    full = {s: v for s, v in pairs.items() if "original" in v and "humanized" in v}
    print(f"complete pairs: {len(full)}/{len(pairs)}\n")

    print(f"{'dimension':<21s} {'original':>9s} {'humanized':>10s} "
          f"{'diff':>7s} {'t':>7s} {'r(words)':>9s}")
    for d in DIMS:
        raw, wd = [], []
        for s, v in full.items():
            o, h = v["original"][0].get(d), v["humanized"][0].get(d)
            if o is None or h is None:
                continue
            if d in SENTINEL and (o == -1 or h == -1):
                continue
            raw.append((o, h))
            wd.append(v["humanized"][1]["n_words"] - v["original"][1]["n_words"])
        if len(raw) < 5:
            print(f"{d:<21s} {'too few applicable pairs':>45s}")
            continue
        diffs = [h - o for o, h in raw]
        m, t = paired_t(diffs)
        r = pearson(wd, diffs)
        rs = f"{r:+.2f}" if r is not None else "n/a"
        print(f"{d:<21s} {statistics.mean(o for o,_ in raw):>9.2f} "
              f"{statistics.mean(h for _,h in raw):>10.2f} {m:>+7.2f} "
              f"{t:>+7.1f}{'*' if abs(t)>2.03 else ' '} {rs:>9s}  "
              f"n={len(raw)}")

    print("\n  diff = humanized - original, paired within text. This is the")
    print("  quoted quantity. The design is within-text paired -- same speech,")
    print("  same speaker, same occasion -- so content is held fixed by")
    print("  construction and no covariate is needed to get the effect.")

    allwd = [v["humanized"][1]["n_words"] - v["original"][1]["n_words"]
             for v in full.values()]
    if len(allwd) > 2:
        print(f"\n  word delta: mean {statistics.mean(allwd):+.1f}, "
              f"sd {statistics.stdev(allwd):.1f}, "
              f"{sum(1 for w in allwd if w > 0)}/{len(allwd)} longer")
    print("  r(words) is the correlation between how much longer a rewrite")
    print("  got and how much its score moved. Reported because it is")
    print("  interesting, NOT as a confound to be removed: on this rubric a")
    print("  longer passage genuinely has room to justify more, and earning")
    print("  justification by adding words is a strategy a member with a")
    print("  longer slot could use too. Partialling it out would treat a real")
    print("  route to quality as a nuisance parameter.")
    print("  * marks |t| > 2.03 (two-sided .05 at ~35 df).")


if __name__ == "__main__":
    main()
