#!/usr/bin/env python3
"""S10: project measured detector throughput to candidate corpus scales.

Reads throughput_runs.jsonl (entries written by bench_binoculars.py), takes
the best end-to-end tok/s per pair, and writes projections.csv with
assumptions inline. Scales are the plan's Task-4 anchors (words -> tokens at
1.35 tok/word, English text, Falcon tokenizer ballpark; the NB row uses the
actually-measured token count when available).

CLOCK CAP: the GB10 ran at 513/3003 MHz for every measurement (see PILOT.md);
'unlocked_est' rows scale by 5.85 and are estimates, not measurements.

Usage: python make_projections.py [BEST_LABEL_SUBSTR ...]
"""
import csv
import json

TOK_PER_WORD = 1.35
CLOCK_HEADROOM = 3003 / 513  # 5.85x, measured cap ratio

SCALES = [
    ("NB 61st/2 EN corpus (this pilot)", None),        # use measured tokens
    ("NB full legislature, ~4 sessions", 3.2e6 * TOK_PER_WORD),
    ("Large province, 1 yr (~8M words)", 8e6 * TOK_PER_WORD),
    ("Canadian Parliament, 1 yr (~40M words)", 40e6 * TOK_PER_WORD),
    ("10 legislatures x 5 yrs (~200M words)", 200e6 * TOK_PER_WORD),
]


def main():
    runs = [json.loads(l) for l in open("throughput_runs.jsonl")]
    best = {}
    measured_tokens = {}
    for r in runs:
        pair = r["label"].split("-")[0]
        if r["label"].endswith("-full") and r["real_tokens"] > 100_000:
            measured_tokens[pair] = r["real_tokens"]   # ignore tiny Se runs
        cur = best.get(pair)
        if cur is None or r["tok_per_s_end2end"] > cur["tok_per_s_end2end"]:
            best[pair] = r

    rows = []
    for pair, r in sorted(best.items()):
        rate = r["tok_per_s_end2end"]
        for label, tokens in SCALES:
            t = tokens if tokens else measured_tokens.get(pair, 1.16e6)
            hours = t / rate / 3600
            rows.append({
                "pair": pair, "corpus": label, "tokens_millions": round(t / 1e6, 2),
                "measured_tok_per_s_capped": rate,
                "hours_at_capped_clocks": round(hours, 2),
                "hours_at_unlocked_est": round(hours / CLOCK_HEADROOM, 2),
                "source_label": r["label"], "budget": r["budget"],
            })

    with open("projections.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        f.write(f"# assumptions: {TOK_PER_WORD} tok/word (English, Falcon-scale vocab); "
                f"end-to-end rate incl. tokenize+batch+score-math; "
                f"unlocked_est = capped / {CLOCK_HEADROOM:.2f} (clock ratio 3003/513), "
                f"estimate NOT a measurement; model-load overhead (~4 min/job) excluded\n")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
