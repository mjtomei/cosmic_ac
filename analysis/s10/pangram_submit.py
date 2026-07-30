#!/usr/bin/env python3
"""S10 Tier-4: submit the adjudication batch to Pangram.

Reads pangram_batch.jsonl, scores each segment with the Pangram API
(pangram-sdk, model pangram-4), appends full responses to
pangram_results.jsonl. RESUMABLE: seg_ids already present in the results
file are skipped, so re-running after an interruption is safe and spends
no additional words.

API key: ~/.pangram_key (chmod 600) or PANGRAM_API_KEY env var.
Word spend: the batch is ~71k words vs the Professional plan's 1.5M/month.

Usage: python pangram_submit.py [--limit N] [--stratum PREFIX]
  --limit 5           smoke-test on 5 segments first
  --stratum C         only submit one stratum (e.g. C-control first)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from pangram import Pangram

BATCH = "pangram_batch.jsonl"
RESULTS = "pangram_results.jsonl"


def api_key():
    k = os.environ.get("PANGRAM_API_KEY")
    if k:
        return k.strip()
    p = Path.home() / ".pangram_key"
    if p.exists():
        return p.read_text().strip()
    sys.exit("No API key: put it in ~/.pangram_key (chmod 600) "
             "or export PANGRAM_API_KEY")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stratum", default="")
    args = ap.parse_args()

    done = set()
    if Path(RESULTS).exists():
        for line in open(RESULTS):
            try:
                done.add(json.loads(line)["seg_id"])
            except Exception:
                pass

    batch = [json.loads(l) for l in open(BATCH)]
    todo = [b for b in batch if b["seg_id"] not in done
            and b["stratum"].startswith(args.stratum)]
    if args.limit:
        todo = todo[:args.limit]
    words = sum(b["n_words"] for b in todo)
    print(f"{len(todo)} segments to submit ({words:,} words); "
          f"{len(done)} already done", flush=True)

    client = Pangram(api_key=api_key())
    tally = {}
    with open(RESULTS, "a") as out:
        for i, b in enumerate(todo, 1):
            for attempt in (1, 2):
                try:
                    r = client.predict(b["text"])
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"  FAILED {b['seg_id']}: {str(e)[:90]}",
                              flush=True)
                        r = None
                    else:
                        time.sleep(3)
            if r is None:
                continue
            rec = dict(r) if isinstance(r, dict) else r.__dict__
            rec = {"seg_id": b["seg_id"], "stratum": b["stratum"],
                   "date": b["date"], "speaker": b["speaker"],
                   "n_words": b["n_words"], "response": rec}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            resp = rec["response"]
            label = (resp.get("prediction_short")
                     or resp.get("prediction") or "?")
            key = (b["stratum"].split("-")[0], label)
            tally[key] = tally.get(key, 0) + 1
            if i % 20 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}  tally={dict(sorted(tally.items()))}",
                      flush=True)
            time.sleep(0.3)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
