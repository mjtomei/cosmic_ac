#!/usr/bin/env python3
"""S10: per-speech likelihood-ratio scorer (lexicon-based, in-domain P/Q).

For each speech (turn), a naive-Bayes log-likelihood ratio over the
Tier-1.5 pattern set, with per-pattern Poisson rates measured in-domain:
  P (human)  = 2019 control corpus rates
  Q (AI-ish) = synthetic corpus rates (Mistral-7B-Instruct legislative
               speech; small and single-generator -- pilot instrument)
  LLR(speech) = sum_j [ k_j * log(lam_Qj / lam_Pj) - n * (lam_Qj - lam_Pj) ]
with add-alpha smoothing on both rate estimates. Thresholds are calibrated
on the 2019 control turns themselves (95th/99th percentile -> 5%/1% FPR by
construction); Se is reported on the synthetic set.

HONESTY NOTE (also in PILOT.md): this scorer reuses the trend's patterns,
so it is NOT independent evidence of the corpus-level shift -- it is the
localization tool: which speeches, which speakers, which years carry the
signal, at a known FPR. Liang et al.'s document-level machinery adapted to
our in-domain reference corpora.

Usage: python lr_speech_scorer.py       (writes lr_scores.csv, appends
                                         top new candidates to the batch)
"""
import csv
import json
import math
import re
from collections import defaultdict

from tier15_wiki_signs import PATTERNS
from tier15_quarters_speakers import UP

RX = {n: re.compile(p, 0 if n == "additionally-start" else re.I)
      for n, p in PATTERNS.items() if n in UP}
ALPHA = 0.5          # pseudo-hits added to each corpus per pattern
MIN_WORDS = 80       # speeches shorter than this are unscoreable
TOP_APPEND = 15      # new Pangram candidates from the top of the list


def main():
    turns = defaultdict(lambda: {"texts": [], "date": "", "speaker": "",
                                 "n_words": 0})
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "se_segments.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if not s.get("scoreable"):
                continue
            t = turns[s["turn_id"]]
            t["texts"].append(s["text"])
            t["date"] = s["date"]
            t["speaker"] = s["speaker"]
            t["n_words"] += s["n_words"]

    ctl_w = syn_w = 0
    ctl_k, syn_k = defaultdict(int), defaultdict(int)
    for t in turns.values():
        text = " ".join(t["texts"])
        if t["date"].startswith("2019"):
            ctl_w += t["n_words"]
            for n, rx in RX.items():
                ctl_k[n] += len(rx.findall(text))
        elif t["date"].startswith("synthetic"):
            syn_w += t["n_words"]
            for n, rx in RX.items():
                syn_k[n] += len(rx.findall(text))

    lam_p, lam_q, w_j = {}, {}, {}
    for n in RX:
        lam_p[n] = (ctl_k[n] + ALPHA) / ctl_w
        lam_q[n] = (syn_k[n] + ALPHA) / syn_w
        w_j[n] = math.log(lam_q[n] / lam_p[n])
    informative = sorted(RX, key=lambda n: -abs(w_j[n]))
    print(f"P from {ctl_w:,} control words, Q from {syn_w:,} synthetic words")
    print("most informative patterns (log rate ratio):")
    for n in informative[:8]:
        print(f"  {n:20s} lamP={lam_p[n]*1e5:6.2f} lamQ={lam_q[n]*1e5:7.1f} "
              f"logw={w_j[n]:+.2f}")

    sum_dl = sum(lam_q[n] - lam_p[n] for n in RX)
    rows = []
    for tid, t in turns.items():
        if t["n_words"] < MIN_WORDS:
            continue
        text = " ".join(t["texts"])
        n_tok = t["n_words"]
        llr = -n_tok * sum_dl
        hits = 0
        for n, rx in RX.items():
            k = len(rx.findall(text))
            hits += k
            if k:
                llr += k * w_j[n]
        rows.append({"turn_id": tid, "date": t["date"],
                     "speaker": t["speaker"], "n_words": n_tok,
                     "lex_hits": hits, "llr": round(llr, 3)})

    ctl_scores = sorted(r["llr"] for r in rows if r["date"].startswith("2019"))
    syn_scores = [r["llr"] for r in rows if r["date"].startswith("synthetic")]
    thr05 = ctl_scores[int(0.95 * len(ctl_scores))]
    thr01 = ctl_scores[int(0.99 * len(ctl_scores))]
    se05 = sum(s > thr05 for s in syn_scores) / max(1, len(syn_scores))
    se01 = sum(s > thr01 for s in syn_scores) / max(1, len(syn_scores))
    print(f"\ncalibration: thr@5%FPR={thr05:.2f} thr@1%FPR={thr01:.2f} "
          f"(on {len(ctl_scores)} control speeches)")
    print(f"Se on synthetic: {se05:.2f} @5%  {se01:.2f} @1%  "
          f"(n={len(syn_scores)})")

    print("\nper-year speech flag rates (LLR > thr):")
    by_year = defaultdict(list)
    for r in rows:
        if r["date"][:4].isdigit():
            by_year[r["date"][:4]].append(r["llr"])
    for y in sorted(by_year):
        v = by_year[y]
        print(f"  {y}: n={len(v):5d}  @5%thr {sum(s > thr05 for s in v)/len(v):6.2%}"
              f"  @1%thr {sum(s > thr01 for s in v)/len(v):6.2%}")

    for r in rows:
        r["flag05"] = r["llr"] > thr05
        r["flag01"] = r["llr"] > thr01
    with open("lr_scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -r["llr"]))
        f.write(f"# P=2019 control, Q=synthetic (alpha={ALPHA}); thr05={thr05:.3f} "
                f"thr01={thr01:.3f}; Se {se05:.2f}/{se01:.2f}; localization "
                f"tool, not independent evidence (shares patterns with the "
                f"trend analysis)\n")

    # top real speeches -> Pangram batch stratum A7
    real = [r for r in rows if r["date"][:4] >= "2023" and r["date"][:4].isdigit()]
    real.sort(key=lambda r: -r["llr"])
    seg_by_turn = defaultdict(list)
    for path in ("segments_all.jsonl", "segments_60th.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if s.get("scoreable"):
                seg_by_turn[s["turn_id"]].append(s)
    batch_ids = {json.loads(l)["seg_id"] for l in open("pangram_batch.jsonl")}
    added = 0
    with open("pangram_batch.jsonl", "a") as f:
        for r in real:
            if added >= TOP_APPEND:
                break
            for s in seg_by_turn.get(r["turn_id"], []):
                if s["seg_id"] not in batch_ids:
                    f.write(json.dumps({"seg_id": s["seg_id"],
                                        "stratum": "A7-speech-llr",
                                        "date": s["date"],
                                        "speaker": s["speaker"],
                                        "n_words": s["n_words"],
                                        "text": s["text"]},
                                       ensure_ascii=False) + "\n")
                    batch_ids.add(s["seg_id"])
                    added += 1
    n = sum(1 for _ in open("pangram_batch.jsonl"))
    w_tot = sum(json.loads(l)["n_words"] for l in open("pangram_batch.jsonl"))
    print(f"\ntop speeches (LLR, 2023+):")
    for r in real[:6]:
        print(f"  {r['llr']:8.2f} | {r['date']} | {r['speaker'][:24]:24s} | "
              f"{r['n_words']}w, {r['lex_hits']} hits")
    print(f"appended {added} segments as A7-speech-llr -> batch {n} segs, "
          f"{w_tot:,} words")


if __name__ == "__main__":
    main()
