#!/usr/bin/env python3
"""S10 Tier-4: analyze Pangram results by stratum.

- C-control-2019  -> Pangram's in-domain FPR (1-Sp), the parameter the
                     whole design turns on.
- D-synthetic     -> Pangram's in-domain Se (Mistral-class generator).
- A* strata       -> adjudication of the local detectors' candidates;
                     prints every segment Pangram calls AI or Mixed.
- B-decile        -> design-based prevalence: equal-probability deciles of
                     the falcon score, 12 sampled per decile, so the mean
                     of decile flag-rates estimates the corpus rate;
                     Rogan-Gladen corrected with the measured Se/Sp.

A segment counts as "flagged" if prediction_short is AI or Mixed
(sensitivity to Mixed is reported separately too).

Usage: python pangram_analyze.py
"""
import json
from collections import defaultdict


def flag(resp, include_mixed=True):
    p = (resp.get("prediction_short") or "").lower()
    if p == "ai":
        return True
    if include_mixed and p == "mixed":
        return True
    return False


def main():
    rows = [json.loads(l) for l in open("pangram_results.jsonl")]
    by_str = defaultdict(list)
    for r in rows:
        by_str[r["stratum"]].append(r)

    print(f"{len(rows)} results across {len(by_str)} strata\n")

    ctl = [r for s, v in by_str.items() if s.startswith("C") for r in v]
    syn = [r for s, v in by_str.items() if s.startswith("D") for r in v]
    for name, pool in (("C control 2019", ctl), ("D synthetic", syn)):
        if not pool:
            print(f"{name}: none scored yet")
            continue
        f_ai = sum(flag(r["response"], False) for r in pool)
        f_mix = sum(flag(r["response"], True) for r in pool)
        mean_fai = sum(r["response"].get("fraction_ai", 0) for r in pool) / len(pool)
        print(f"{name}: n={len(pool)}  AI-only {f_ai} ({f_ai/len(pool):.1%})  "
              f"AI+Mixed {f_mix} ({f_mix/len(pool):.1%})  "
              f"mean fraction_ai {mean_fai:.3f}")
    print()

    adj = [r for s, v in by_str.items() if s.startswith("A") for r in v]
    hits = [r for r in adj if flag(r["response"], True)]
    print(f"A* adjudication: {len(adj)} candidates scored, "
          f"{len(hits)} called AI/Mixed by Pangram:")
    for r in sorted(hits, key=lambda r: -r["response"].get("fraction_ai", 0)):
        resp = r["response"]
        print(f"  {resp.get('prediction_short','?'):5s} "
              f"fai={resp.get('fraction_ai', 0):.2f} "
              f"| {r['stratum']:16s} | {r['date']} | {r['speaker'][:24]}")
    print()

    b = [r for s, v in by_str.items() if s.startswith("B") for r in v]
    if b:
        dec = defaultdict(list)
        for r in b:
            dec[r["stratum"]].append(flag(r["response"], True))
        rates = [sum(v) / len(v) for v in dec.values()]
        pi = sum(rates) / len(rates)
        print(f"B decile sample: n={len(b)} across {len(dec)} deciles; "
              f"design-based raw flag rate = {pi:.3%}")
        if ctl and syn:
            sp = 1 - sum(flag(r["response"], True) for r in ctl) / len(ctl)
            se = sum(flag(r["response"], True) for r in syn) / len(syn)
            denom = se + sp - 1
            if denom > 0.1:
                tau = (pi + sp - 1) / denom
                print(f"Rogan-Gladen with measured Se={se:.3f} Sp={sp:.3f}: "
                      f"tau-hat = {max(0.0, tau):.3%}"
                      + ("  (truncated at 0)" if tau < 0 else ""))


if __name__ == "__main__":
    main()
