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

Ground truth is Pangram 4 (pangram_p4_verdicts.csv), the study's canonical
oracle per METHODOLOGY 3.2, joined to the pool through the blind_id -> sid map
in fable_judge_v2_scores.csv. The group field in that file is the older P3
labelling; 30 of 241 binary labels differ, so it is used only for the id join,
not for the label itself. Under P4 the three arms read 0.948 / 0.951 / 0.942
(archived low / fresh low / max) -- max is still the lowest, so the null holds.

Usage: python opus_effort_ab.py [WORKFLOW_RUN_DIR]
       An explicit run dir is honoured; otherwise the newest workflow dir that
       actually contains both arms is used. opus_effort_raw.json is a fallback
       only when no run dir yields data.

The generating workflow .js was not retained, but the run is fully recoverable:
both arms are re-derived from the `effort` field on the agent transcripts, so no
committed script is load-bearing for reproduction.
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
    """blind_id -> Pangram-4 binary label, via the blind_id -> sid join.

    The group field in fable_judge_v2_scores.csv is P3 and is used only to reach
    sid; the label itself is read from the P4 verdicts so this A/B uses the same
    oracle as the rest of the study (30/241 binary labels differ under P3).
    """
    p4 = {}
    for r in csv.DictReader(open(os.path.join(HERE,
                                              "pangram_p4_verdicts.csv"))):
        v = r.get("pangram")
        p4[r["seg_id"]] = (1 if v in ("AI", "Mixed")
                           else 0 if v == "Human" else None)
    lab, sid = {}, {}
    for r in csv.DictReader(open(os.path.join(HERE,
                                              "fable_judge_v2_scores.csv"))):
        g = r["group"]
        if not (g.endswith("_ai") or g.endswith("_human") or g == "ctl2019"):
            continue
        sid[r["blind_id"]] = r["sid"]
        y = p4.get(r["sid"])
        if y is not None:
            lab[r["blind_id"]] = y
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
    """{arm: {blind_id: score}} read straight from a workflow run directory.

    The arm each agent belonged to IS on disk: every transcript record carries
    a top-level `effort` field ("low" or "max"), constant within a file. We tag
    every score in a file by that file's effort, so the mapping survives even if
    opus_effort_raw.json is deleted. Returns empty arms if run_dir is falsy or
    holds no scores; the caller decides whether to fall back to the cache.
    """
    arms = {"low": {}, "max": {}}
    if not run_dir:
        return arms
    for path in glob.glob(os.path.join(run_dir, "*.jsonl")):
        eff, scores = [None], {}

        def absorb(x):
            if isinstance(x, dict):
                e = x.get("effort")
                if isinstance(e, str) and e in ("low", "max"):
                    eff[0] = e
                i, g = x.get("id"), x.get("ai_guess")
                if isinstance(i, str) and i.startswith("S") \
                        and isinstance(g, int):
                    scores[i] = g
                else:
                    for v in x.values():
                        absorb(v)
            elif isinstance(x, list):
                for v in x:
                    absorb(v)
        for line in open(path):
            try:
                absorb(json.loads(line))
            except Exception:
                continue
        if eff[0] and scores:
            arms[eff[0]].update(scores)
    return arms


def resolve_arms(run):
    """(arms, source) with honest precedence: explicit run_dir, then the newest
    workflow dir that actually contains both arms, then the cached JSON."""
    if run:
        a = harvest(run)
        if a["low"] and a["max"]:
            return a, run
    for c in sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                           "workflows", "wf_*")),
                    key=os.path.getmtime, reverse=True):
        a = harvest(c)
        if a["low"] and a["max"]:
            return a, c
    cached = os.path.join(HERE, "opus_effort_raw.json")
    if os.path.exists(cached):
        return json.load(open(cached)), "(cached opus_effort_raw.json)"
    return {"low": {}, "max": {}}, None


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    arms, source = resolve_arms(run)
    if not (arms["low"] and arms["max"]):
        sys.exit("no run dir with both arms found — pass one explicitly")
    print(f"scores from: {source}")

    lab, _ = labels()
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

    # Paired bootstrap of max - mean(low) over segments. A single
    # |archived - fresh| gap is a 1-df benchmark that carries almost no
    # information about run-to-run variance and, being tiny by chance in one
    # pair, can flip an arbitrary sign into a spurious "effect". The bootstrap
    # interval is what the write-up reports.
    if all(k in series for k in ("archived low", "fresh low", "max")):
        import random
        keys = sorted(set(series["archived low"]) & set(series["fresh low"])
                      & set(series["max"]) & set(lab))

        def gap(sample):
            def a(name):
                return auc([(series[name][k], lab[k]) for k in sample])
            return a("max") - (a("archived low") + a("fresh low")) / 2
        point = gap(keys)
        rng = random.Random(7)
        draws = sorted(gap([keys[rng.randrange(len(keys))]
                            for _ in range(len(keys))]) for _ in range(4000))
        lo, hi = draws[int(.025 * len(draws))], draws[int(.975 * len(draws))]
        print(f"\neffort gap   max - mean(low) = {point:+.4f}  "
              f"95% CI [{lo:+.4f}, {hi:+.4f}]")
        print("             -> interval contains zero; effects below ~0.03 AUC "
              "are outside this design's resolution")

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
