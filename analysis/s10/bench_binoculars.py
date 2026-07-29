#!/usr/bin/env python3
"""S10 pilot: batched Binoculars scoring + throughput measurement on GB10.

Faithful port of the reference math (github.com/ahans30/Binoculars,
binoculars/metrics.py), reorganized for throughput:
  score = logPPL_performer(text) / X-entropy(observer -> performer)
  - logPPL: token-shifted CE of true tokens under performer logits,
    attention-mask averaged (per segment).
  - X-entropy: CE(target=softmax(observer logits), input=performer logits)
    over ALL positions (unshifted, as in the reference), pad-masked.
Deviation from reference: score math in fp32 (reference runs CE on bf16
logits); differences are ~1e-3, far below domain-calibration uncertainty.
Score < ~0.85-0.90 reads as AI under the reference's Falcon thresholds;
thresholds are NOT calibrated for legislative register (we measure Se/Sp
in-domain later — see the session plan).

Batching: segments tokenized once, sorted by length, greedily packed into
batches capped by a padded-token budget. bf16, SDPA attention.

Usage:
  python bench_binoculars.py SEGMENTS_JSONL --pair falcon \
      --budgets 8192,16384,32768 --subset-tokens 60000        # sweep
  python bench_binoculars.py SEGMENTS_JSONL --pair falcon \
      --budget 16384 --full --scores-out scores_falcon.csv    # full run
"""
import argparse
import csv
import json
import sys
import time

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

PAIRS = {
    "falcon": ("tiiuae/falcon-7b", "tiiuae/falcon-7b-instruct"),
    "qwen1.7": ("Qwen/Qwen3-1.7B-Base", "Qwen/Qwen3-1.7B"),
    "qwen8": ("Qwen/Qwen3-8B-Base", "Qwen/Qwen3-8B"),
}
MAX_TOKENS = 512          # reference: max_token_observed
CHUNK_TOKENS = 4096       # fp32 score-math chunk: ~5 GB transient at 65k vocab


def load_models(pair):
    obs_path, perf_path = PAIRS[pair]
    t0 = time.perf_counter()
    kw = dict(dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": "cuda:0"})
    observer = AutoModelForCausalLM.from_pretrained(obs_path, **kw).eval()
    performer = AutoModelForCausalLM.from_pretrained(perf_path, **kw).eval()
    tok = AutoTokenizer.from_pretrained(obs_path)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    load_s = time.perf_counter() - t0
    return observer, performer, tok, load_s


def build_batches(segs, tok, budget):
    texts = [s["text"] for s in segs]
    t0 = time.perf_counter()
    enc = tok(texts, truncation=True, max_length=MAX_TOKENS)["input_ids"]
    tok_s = time.perf_counter() - t0
    order = sorted(range(len(enc)), key=lambda i: len(enc[i]))
    batches, cur, cur_max = [], [], 0
    for i in order:
        L = len(enc[i])
        if cur and max(cur_max, L) * (len(cur) + 1) > budget:
            batches.append(cur)
            cur, cur_max = [], 0
        cur.append(i)
        cur_max = max(cur_max, L)
    if cur:
        batches.append(cur)
    return enc, batches, tok_s


@torch.inference_mode()
def score_batch(observer, performer, ids_list, pad_id, device="cuda:0"):
    """Returns (ppl, xppl, timings) for one padded batch."""
    B = len(ids_list)
    L = max(len(x) for x in ids_list)
    input_ids = torch.full((B, L), pad_id, dtype=torch.long)
    attn = torch.zeros((B, L), dtype=torch.long)
    for r, ids in enumerate(ids_list):
        input_ids[r, :len(ids)] = torch.tensor(ids, dtype=torch.long)
        attn[r, :len(ids)] = 1
    input_ids = input_ids.to(device)
    attn = attn.to(device)

    torch.cuda.synchronize()
    t0 = time.perf_counter()
    obs_logits = observer(input_ids=input_ids, attention_mask=attn).logits
    torch.cuda.synchronize()
    t1 = time.perf_counter()
    perf_logits = performer(input_ids=input_ids, attention_mask=attn).logits
    torch.cuda.synchronize()
    t2 = time.perf_counter()

    rows_per_chunk = max(1, CHUNK_TOKENS // L)
    ppl = torch.empty(B, dtype=torch.float32)
    xppl = torch.empty(B, dtype=torch.float32)
    for r0 in range(0, B, rows_per_chunk):
        r1 = min(B, r0 + rows_per_chunk)
        ol = obs_logits[r0:r1].float()
        pl = perf_logits[r0:r1].float()
        ids_c = input_ids[r0:r1]
        att_c = attn[r0:r1]
        # logPPL under performer (shifted)
        ce = F.cross_entropy(pl[:, :-1].transpose(1, 2), ids_c[:, 1:],
                             reduction="none")
        m = att_c[:, 1:].float()
        ppl[r0:r1] = ((ce * m).sum(1) / m.sum(1).clamp(min=1)).cpu()
        # X-entropy observer->performer (unshifted, pad-masked, as reference)
        xe = -(F.softmax(ol, -1) * F.log_softmax(pl, -1)).sum(-1)
        pm = (ids_c != pad_id).float()
        xppl[r0:r1] = ((xe * pm).sum(1) / pm.sum(1).clamp(min=1)).cpu()
    torch.cuda.synchronize()
    t3 = time.perf_counter()
    return ppl, xppl, (t1 - t0, t2 - t1, t3 - t2), int(attn.sum().item())


def run(segs, observer, performer, tok, budget, warmup=3, label=""):
    enc, batches, tok_s = build_batches(segs, tok, budget)
    pad_id = tok.pad_token_id
    # warmup on mid-sized batches (compile kernels, clock up)
    for b in (batches[len(batches) // 2:] + batches)[:warmup]:
        score_batch(observer, performer, [enc[i] for i in b], pad_id)
    torch.cuda.reset_peak_memory_stats()
    results = {}
    t_obs = t_perf = t_math = 0.0
    real_tokens = padded_tokens = 0
    t_all0 = time.perf_counter()
    for b in batches:
        ids = [enc[i] for i in b]
        ppl, xppl, (to, tp, tm), ntok = score_batch(observer, performer, ids, pad_id)
        for j, i in enumerate(b):
            results[i] = (float(ppl[j]), float(xppl[j]))
        t_obs += to; t_perf += tp; t_math += tm
        real_tokens += ntok
        padded_tokens += len(b) * max(len(x) for x in ids)
    wall = time.perf_counter() - t_all0
    peak = torch.cuda.max_memory_allocated() / 2**30
    stats = {
        "label": label, "budget": budget, "n_segments": len(segs),
        "n_batches": len(batches), "real_tokens": real_tokens,
        "padded_tokens": padded_tokens,
        "pad_efficiency": round(real_tokens / max(1, padded_tokens), 3),
        "tokenize_s": round(tok_s, 2), "wall_s": round(wall, 2),
        "obs_s": round(t_obs, 2), "perf_s": round(t_perf, 2),
        "math_s": round(t_math, 2),
        "tok_per_s_end2end": round(real_tokens / (wall + tok_s), 1),
        "tok_per_s_forward": round(real_tokens / max(1e-9, t_obs + t_perf), 1),
        "peak_mem_gib": round(peak, 1),
    }
    return results, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("segments")
    ap.add_argument("--pair", required=True, choices=PAIRS)
    ap.add_argument("--budgets", default="16384")
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--subset-tokens", type=int, default=0,
                    help="approx real-token size of the sweep subset")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--scores-out", default=None)
    ap.add_argument("--stats-out", default=None)
    args = ap.parse_args()

    segs = [json.loads(l) for l in open(args.segments)]
    segs = [s for s in segs if s.get("scoreable")]
    print(f"{len(segs)} scoreable segments", file=sys.stderr)

    observer, performer, tok, load_s = load_models(args.pair)
    print(f"models loaded in {load_s:.1f}s", file=sys.stderr)

    all_stats = []
    if args.full:
        budget = args.budget or int(args.budgets.split(",")[0])
        results, stats = run(segs, observer, performer, tok, budget,
                             label=f"{args.pair}-full")
        stats["load_s"] = round(load_s, 1)
        all_stats.append(stats)
        print(json.dumps(stats), flush=True)
        if args.scores_out:
            with open(args.scores_out, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["seg_id", "date", "speaker", "section", "n_words",
                            "orig_frac", "n_tok", "logppl", "xppl", "score"])
                enc = tok([s["text"] for s in segs], truncation=True,
                          max_length=MAX_TOKENS)["input_ids"]
                for i, s in enumerate(segs):
                    ppl, xppl = results[i]
                    w.writerow([s["seg_id"], s["date"], s["speaker"],
                                s["section"], s["n_words"], s["orig_frac"],
                                len(enc[i]), round(ppl, 5), round(xppl, 5),
                                round(ppl / xppl, 5)])
    else:
        # sweep: subset segments to ~subset-tokens by round-robin sampling
        sub = segs
        if args.subset_tokens:
            sub, acc = [], 0
            for s in segs[:: max(1, len(segs) // 2000)]:
                sub.append(s)
                acc += min(MAX_TOKENS, int(s["n_words"] * 1.4))
                if acc >= args.subset_tokens:
                    break
        print(f"sweep subset: {len(sub)} segments", file=sys.stderr)
        for budget in [int(x) for x in args.budgets.split(",")]:
            _, stats = run(sub, observer, performer, tok, budget,
                           label=f"{args.pair}-b{budget}")
            stats["load_s"] = round(load_s, 1)
            all_stats.append(stats)
            print(json.dumps(stats), flush=True)
            if args.stats_out:      # persist immediately, survive kills
                with open(args.stats_out, "a") as f:
                    f.write(json.dumps(stats) + "\n")
            torch.cuda.empty_cache()
        return

    if args.stats_out:
        with open(args.stats_out, "a") as f:
            for s in all_stats:
                f.write(json.dumps(s) + "\n")


if __name__ == "__main__":
    main()
