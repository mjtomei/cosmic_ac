#!/usr/bin/env python3
"""S10: Fast-DetectGPT + log-rank ratio (LRR) from the Falcon pair's passes.

Fast-DetectGPT (Bao et al., ICLR 2024, arXiv:2310.05130): conditional
probability curvature d = (ll - mu) / sigma, where ll is the text's
log-likelihood under the scoring model and mu/sigma are the analytic
mean/std of that log-likelihood under the sampling model's conditional
distribution. Their recommended black-box combo is sampling=falcon-7b,
scoring=falcon-7b-instruct — the same two models as our Binoculars runs,
so the marginal cost of this detector is one shared forward pass.
Higher d => more machine-like.

LRR (DetectLLM, Su et al. 2023): -sum(log p) / sum(log rank) under the
scoring model. Higher => more machine-like.

Output CSV: seg_id, date, speaker, n_tok, logppl, fastdetect_d, lrr.
Usage: python score_multistat.py OUT_CSV SEGMENTS_JSONL [SEGMENTS_JSONL...]
"""
import csv
import json
import sys
import time

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

SAMPLING = "tiiuae/falcon-7b"            # q
SCORING = "tiiuae/falcon-7b-instruct"    # p
MAX_TOKENS = 512
BUDGET = 16384
CHUNK_TOKENS = 4096


@torch.inference_mode()
def batch_stats(q_model, p_model, ids_list, pad_id):
    B = len(ids_list)
    L = max(len(x) for x in ids_list)
    input_ids = torch.full((B, L), pad_id, dtype=torch.long)
    attn = torch.zeros((B, L), dtype=torch.long)
    for r, ids in enumerate(ids_list):
        input_ids[r, :len(ids)] = torch.tensor(ids, dtype=torch.long)
        attn[r, :len(ids)] = 1
    input_ids, attn = input_ids.to("cuda:0"), attn.to("cuda:0")
    q_logits = q_model(input_ids=input_ids, attention_mask=attn).logits
    p_logits = p_model(input_ids=input_ids, attention_mask=attn).logits

    rows_per_chunk = max(1, CHUNK_TOKENS // L)
    out = torch.empty((B, 4), dtype=torch.float64)
    for r0 in range(0, B, rows_per_chunk):
        r1 = min(B, r0 + rows_per_chunk)
        # Binoculars x-entropy (unshifted, pad-masked, as the reference)
        xe = -(F.softmax(q_logits[r0:r1].float(), -1) *
               F.log_softmax(p_logits[r0:r1].float(), -1)).sum(-1)
        pm = (input_ids[r0:r1] != pad_id).float()
        xppl = (xe * pm).sum(1) / pm.sum(1).clamp(min=1)
        lp = F.log_softmax(p_logits[r0:r1, :-1].float(), -1)
        q = F.softmax(q_logits[r0:r1, :-1].float(), -1)
        labels = input_ids[r0:r1, 1:]
        m = attn[r0:r1, 1:].float()
        lp_true = lp.gather(-1, labels.unsqueeze(-1)).squeeze(-1)      # B,L-1
        ll = (lp_true * m).sum(1)
        mu_t = (q * lp).sum(-1)
        var_t = (q * lp.pow(2)).sum(-1) - mu_t.pow(2)
        mu = (mu_t * m).sum(1)
        var = (var_t * m).sum(1)
        d = (ll - mu) / var.clamp(min=1e-9).sqrt()
        # LRR: rank of true token under scoring model
        logit_true = p_logits[r0:r1, :-1].float().gather(
            -1, labels.unsqueeze(-1))
        rank = 1 + (p_logits[r0:r1, :-1].float() > logit_true).sum(-1)
        lrr = -(lp_true * m).sum(1) / \
            (torch.log(rank.float()) * m).sum(1).clamp(min=1e-9)
        logppl = -(lp_true * m).sum(1) / m.sum(1).clamp(min=1)
        out[r0:r1, 0] = logppl.double().cpu()
        out[r0:r1, 1] = d.double().cpu()
        out[r0:r1, 2] = lrr.double().cpu()
        out[r0:r1, 3] = (logppl / xppl).double().cpu()   # binoculars score
    ntok = attn.sum().item()
    return out, ntok


def main():
    out_csv, seg_files = sys.argv[1], sys.argv[2:]
    segs = []
    for pth in seg_files:
        segs += [json.loads(l) for l in open(pth)]
    segs = [s for s in segs if s.get("scoreable")]
    print(f"{len(segs)} segments", file=sys.stderr)

    kw = dict(dtype=torch.bfloat16, attn_implementation="sdpa",
              device_map={"": "cuda:0"})
    q_model = AutoModelForCausalLM.from_pretrained(SAMPLING, **kw).eval()
    p_model = AutoModelForCausalLM.from_pretrained(SCORING, **kw).eval()
    tok = AutoTokenizer.from_pretrained(SAMPLING)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    enc = tok([s["text"] for s in segs], truncation=True,
              max_length=MAX_TOKENS)["input_ids"]
    order = sorted(range(len(enc)), key=lambda i: len(enc[i]))
    batches, cur, cur_max = [], [], 0
    for i in order:
        Lx = len(enc[i])
        if cur and max(cur_max, Lx) * (len(cur) + 1) > BUDGET:
            batches.append(cur); cur, cur_max = [], 0
        cur.append(i); cur_max = max(cur_max, Lx)
    if cur:
        batches.append(cur)

    t0 = time.perf_counter()
    results = {}
    done_tok = 0
    for bi, b in enumerate(batches):
        stats, ntok = batch_stats(q_model, p_model, [enc[i] for i in b],
                                  tok.pad_token_id)
        for j, i in enumerate(b):
            results[i] = stats[j].tolist()
        done_tok += ntok
        if bi % 10 == 0:
            rate = done_tok / (time.perf_counter() - t0)
            print(f"batch {bi+1}/{len(batches)} {rate:.0f} tok/s", flush=True)

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seg_id", "date", "speaker", "n_words", "orig_frac",
                    "n_tok", "logppl", "fastdetect_d", "lrr", "binoc"])
        for i, s in enumerate(segs):
            lp, d, lrr, binoc = results[i]
            w.writerow([s["seg_id"], s["date"], s["speaker"], s["n_words"],
                        s["orig_frac"], len(enc[i]), round(lp, 5),
                        round(d, 5), round(lrr, 5), round(binoc, 5)])
    print(f"wrote {out_csv} in {time.perf_counter()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
