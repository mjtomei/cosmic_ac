#!/usr/bin/env python3
"""Does reasoning effort buy detection ability at the frontier?

THE QUESTION AND WHY IT WAS OPEN

The Opus screen's headline figure -- AUC 0.951 against Pangram, used in the
write-up as evidence that a cheap LLM screen tracks a commercial detector --
was produced at effort=low, and low was never compared against anything. We
had assumed low was the weaker setting. That assumption had no support:
measured on this same pool, effort moved gpt-oss-120b by +0.015 AUC and
Qwen3-32B by +0.172. A 10x spread across two open models means the frontier
case cannot be inferred either way.

THE NOISE FLOOR IS THE POINT

Comparing one max run against one low run cannot separate an effort effect
from run-to-run variation, so low is replicated. Three numbers result:

    archived low   opus_lean_scores.csv, the published 0.951
    fresh low      same prompt, same batching, new run
    max            same prompt, same batching, effort=max

|archived - fresh| is the noise floor. A max-vs-low gap smaller than that
floor is not evidence of anything, however tidy it looks.

Ground truth is the Pangram-derived group label carried in
fable_judge_v2_scores.csv: *_ai = AI, *_human and ctl2019 = human.

Usage: python opus_effort_ab.py [WORKFLOW_RUN_DIR]
"""
import csv
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.expanduser("~/.claude/projects")


def labels():
    lab, sid = {}, {}
    for r in csv.DictReader(open(os.path.join(HERE,
                                              "fable_judge_v2_scores.csv"))):
        g = r["group"]
        if g.endswith("_ai"):
            lab[r["blind_id"]] = 1
        elif g.endswith("_human") or g == "ctl2019":
            lab[r["blind_id"]] = 0
        sid[r["blind_id"]] = r["sid"]
    return lab, sid


def auc(pairs):
    pos = [s for s, y in pairs if y]
    neg = [s for s, y in pairs if not y]
    if not pos or not neg:
        return None
    w = sum(1.0 if p > n else 0.5 if p == n else 0.0
            for p in pos for n in neg)
    return w / (len(pos) * len(neg))


def boot_ci(pairs, n=2000, seed=7):
    """Percentile bootstrap on the AUC, resampling segments."""
    import random
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        s = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        a = auc(s)
        if a is not None:
            vals.append(a)
    vals.sort()
    return vals[int(.025 * len(vals))], vals[int(.975 * len(vals))]


def harvest(run_dir):
    """{arm: {blind_id: score}}.

    Prefers opus_effort_raw.json, extracted from the workflow's own return
    value. The per-agent journal cannot be used: its `key` is a content hash
    and the meta files carry only agentType/model, so nothing on disk records
    which arm an agent belonged to. Split by return value, not by transcript.
    """
    cached = os.path.join(HERE, "opus_effort_raw.json")
    if os.path.exists(cached):
        return json.load(open(cached))
    arms = {"low": {}, "max": {}}
    for p in glob.glob(os.path.join(run_dir, "*.jsonl")):
        arm = ("low" if os.path.basename(p).startswith("agent-low")
               else "max" if os.path.basename(p).startswith("agent-max")
               else None)
        for line in open(p):
            try:
                o = json.loads(line)
            except Exception:
                continue

            def absorb(x, arm=arm):
                if isinstance(x, dict):
                    i, g = x.get("id"), x.get("ai_guess")
                    if isinstance(i, str) and i.startswith("S") \
                            and isinstance(g, int):
                        if arm:
                            arms[arm][i] = g
                    else:
                        for v in x.values():
                            absorb(v, arm)
                elif isinstance(x, list):
                    for v in x:
                        absorb(v, arm)
            absorb(o)
    return arms


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    if not run:
        cands = sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                              "workflows", "wf_*")),
                       key=os.path.getmtime, reverse=True)
        for c in cands:
            a = harvest(c)
            if a["low"] and a["max"]:
                run = c
                break
    if not run:
        sys.exit("no run dir with both arms found — pass one explicitly")
    print(f"run dir: {run}")

    lab, _ = labels()
    arms = harvest(run)
    arch = {r["blind_id"]: int(r["opus_ai_guess"])
            for r in csv.DictReader(open(os.path.join(
                HERE, "opus_lean_scores.csv")))
            if r.get("opus_ai_guess")}
    series = {"archived low": arch, "fresh low": arms["low"],
              "max": arms["max"]}

    print(f"\nlabels: {sum(lab.values())} AI / {len(lab)-sum(lab.values())} human")
    print(f"\n{'run':<15s} {'n':>5s} {'AUC':>7s} {'95% CI':>18s} {'mean score':>11s}")
    aucs = {}
    for nm, s in series.items():
        pairs = [(v, lab[k]) for k, v in s.items() if k in lab]
        if not pairs:
            print(f"{nm:<15s} {'--- no data ---':>25s}")
            continue
        a = auc(pairs)
        aucs[nm] = a
        lo, hi = boot_ci(pairs)
        print(f"{nm:<15s} {len(pairs):>5d} {a:>7.3f} "
              f"{f'[{lo:.3f}, {hi:.3f}]':>18s} "
              f"{statistics.mean(v for v,_ in pairs):>11.1f}")

    if "archived low" in aucs and "fresh low" in aucs:
        floor = abs(aucs["archived low"] - aucs["fresh low"])
        print(f"\nnoise floor  |archived low - fresh low| = {floor:.3f}")
        if "max" in aucs:
            gap = aucs["max"] - statistics.mean(
                [aucs["archived low"], aucs["fresh low"]])
            print(f"effort gap   max - mean(low)            = {gap:+.3f}")
            verdict = ("EXCEEDS the noise floor — effort buys detection"
                       if abs(gap) > floor else
                       "WITHIN the noise floor — no evidence effort helps")
            print(f"             -> {verdict}")

    # per-segment stability: do the two low runs agree with each other as
    # closely as low agrees with max? If not, the arms differ in kind.
    def corr(a, b):
        k = sorted(set(a) & set(b))
        if len(k) < 10:
            return None
        x = [a[i] for i in k]
        y = [b[i] for i in k]
        mx, my = statistics.mean(x), statistics.mean(y)
        num = sum((p-mx)*(q-my) for p, q in zip(x, y))
        den = math.sqrt(sum((p-mx)**2 for p in x)*sum((q-my)**2 for q in y))
        return num/den if den else None
    print("\nper-segment score correlation:")
    for a, b in (("archived low", "fresh low"), ("archived low", "max"),
                 ("fresh low", "max")):
        c = corr(series[a], series[b])
        if c is not None:
            print(f"  {a:<14s} vs {b:<14s} r = {c:+.3f}")

    out = os.path.join(HERE, "opus_effort_ab.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["blind_id", "label", "archived_low", "fresh_low", "max"])
        for k in sorted(lab):
            w.writerow([k, lab[k], arch.get(k, ""),
                        arms["low"].get(k, ""), arms["max"].get(k, "")])
    print(f"\nwrote {os.path.basename(out)}")


if __name__ == "__main__":
    main()
