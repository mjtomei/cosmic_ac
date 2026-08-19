#!/usr/bin/env python3
"""Stage 6: never-human-reviewed machine continuations vs their human twins.

Design and pre-stated contrasts: plans/S10-stage6-unreviewed-continuations.md.
Pool: 60 pre-2023 prompts x 4 arms (human continuation, mistral-instruct,
qwen3-instruct, mistral-base), length-matched within prompt, graded blind on
the frozen v2b DQI rubric, two passes, judge pinned to Opus (on arch-home,
2026-08-19). PRIMARY: instruct minus human on justification, common_good,
respect_groups, and on P(applicable) for the two sentinel dimensions (the Q1
quantity). SECONDARY: base vs instruct; ai_guess by arm.

Paired by prompt; per-text scores are the mean of the two passes; sentinel
value -1 = inapplicable (excluded from level means, counted for
applicability). Paired t across the 60 prompts.

Usage: python analyze_stage6.py
"""
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENT = {"respect_demands", "respect_counterargs"}
FORM = ["justification", "common_good", "respect_groups"]
ARMS = ["human", "mistral_instruct", "qwen3_instruct", "mistral_base"]


def main():
    rows = json.load(open(os.path.join(HERE, "results_stage6.json")))
    key = json.load(open(os.path.join(HERE, "key6.json")))
    per = defaultdict(list)
    for r in rows:
        per[r["id"]].append(r)
    # per-text: mean over passes; sentinels averaged only over applicable passes
    text = {}
    for tid, rs in per.items():
        k = key[tid]
        rec = {"arm": k["arm"], "prompt": k["prompt_idx"]}
        for d in DIMS:
            vals = [r[d] for r in rs if not (d in SENT and r[d] == -1)]
            rec[d] = sum(vals) / len(vals) if vals else None
            if d in SENT:
                rec[d + "_app"] = sum(1 for r in rs if r[d] != -1) / len(rs)
        rec["ai_guess"] = sum(r["ai_guess"] for r in rs) / len(rs)
        text[tid] = rec
    byarm = defaultdict(dict)
    for rec in text.values():
        byarm[rec["arm"]][rec["prompt"]] = rec

    def paired(a, b, kk):
        ds = []
        for p in byarm[a]:
            x, y = byarm[a][p].get(kk), byarm[b].get(p, {}).get(kk)
            if x is not None and y is not None:
                ds.append(x - y)
        n = len(ds)
        m = sum(ds) / n
        sd = math.sqrt(sum((d - m) ** 2 for d in ds) / max(n - 1, 1))
        return m, m / (sd / math.sqrt(n)) if sd else 0.0, n

    print("arm means (per-text, two-pass mean):")
    hdr = f"{'arm':<18s}" + "".join(f"{d[:9]:>10s}" for d in DIMS) + f"{'ai_guess':>10s}"
    print(" " + hdr)
    for a in ARMS:
        v = byarm[a].values()
        cells = ""
        for d in DIMS:
            xs = [r[d] for r in v if r[d] is not None]
            cells += f"{sum(xs)/len(xs):>10.2f}"
        ag = sum(r["ai_guess"] for r in v) / len(v)
        print(f" {a:<18s}{cells}{ag:>10.1f}")

    print("\nPRIMARY — instruct minus human, paired across prompts:")
    for a in ("mistral_instruct", "qwen3_instruct"):
        line = f" {a:<18s}"
        for d in FORM:
            m, t, n = paired(a, "human", d)
            line += f"  {d[:12]} {m:+.2f} (t {t:+.1f})"
        print(line)
    print("\n applicability, P(sentinel applicable), arm vs human:")
    for d in SENT:
        line = f" {d:<22s}"
        for a in ARMS:
            v = byarm[a].values()
            line += f" {a.split('_')[0][:7]}{'_i' if 'instruct' in a else '_b' if 'base' in a else ''} " \
                    f"{sum(r[d+'_app'] for r in v)/len(v):.2f} "
        print(line)

    print("\nSECONDARY — instruct minus base (mistral), paired:")
    line = " "
    for d in FORM + ["evidence"]:
        m, t, n = paired("mistral_instruct", "mistral_base", d)
        line += f" {d[:12]} {m:+.2f} (t {t:+.1f})"
    print(line)
    print("\n ai_guess by arm (did the blind judge smell the machine):")
    for a in ARMS:
        v = byarm[a].values()
        print(f"   {a:<18s}{sum(r['ai_guess'] for r in v)/len(v):>6.1f}")


if __name__ == "__main__":
    main()
