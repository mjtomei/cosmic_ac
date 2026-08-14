#!/usr/bin/env python3
"""Paired base-vs-instruct generation: is the leaked register the ALIGNMENT register?

THE HYPOTHESIS

"AI-preferred vocabulary" is usually treated as one thing. But an instruct
model differs from its own base model only by post-training -- SFT plus
preference optimisation (RLHF/DPO). If the vocabulary drifting into Hansard is
specifically the vocabulary that post-training ADDS, then what has leaked is
not "machine text" in general but the assistant register: the hedged,
affirming, relentlessly constructive voice that preference tuning selects for.
That is a much more specific and more interesting claim, and it is testable
because base and instruct checkpoints of the same pretraining run are public.

THE DESIGN, AND WHY IT IS PAIRED

Both models get the SAME prompts -- openings of real pre-2023 Hansard segments,
so the domain is right and the task (continue this speech) is one a base model
can actually do. Identical prompts, identical decoding, identical seeds. The
only difference is the weights.

That pairing matters for a second reason. The study's earlier word-level
mechanism test (ai_pref_prediction.py) compared model output against a HUMAN
corpus, so each word's own rarity sat inside both the predictor and the
outcome; adversarial review showed the predictor was 92% a rarity index and
the correlation vanished when frequency was partialled out. Comparing instruct
against ITS OWN BASE cancels corpus frequency exactly, in the manner of Geng &
Trotta and Yakura et al. This is the replacement for that dead test.

NO CHAT TEMPLATE is applied. Feeding the instruct model a chat template would
confound format with tuning; raw continuation isolates the weight change.

Three families, so a result cannot be one lab's house style:
  meta-llama/Meta-Llama-3-8B      vs  Meta-Llama-3-8B-Instruct
  Qwen/Qwen3-8B-Base              vs  Qwen/Qwen3-8B
  mistralai/Mistral-7B-v0.3       vs  Mistral-7B-Instruct-v0.3

Usage: python rlhf_pref_generate.py [--prompts 1000] [--new-tokens 180]
"""
import argparse
import glob
import hashlib
import json
import os
import random
import re

os.environ.setdefault("CUDA_CACHE_MAXSIZE", "17179869184")
os.environ.setdefault("CUDA_CACHE_PATH", "/home/matt/.nv_cache_s10")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PAIRS = [
    ("llama3", "meta-llama/Meta-Llama-3-8B", "meta-llama/Meta-Llama-3-8B-Instruct"),
    ("qwen3", "Qwen/Qwen3-8B-Base", "Qwen/Qwen3-8B"),
    ("mistral", "mistralai/Mistral-7B-v0.3", "mistralai/Mistral-7B-Instruct-v0.3"),
]
SRC = ["ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl", "ca/segments_ca_en.jsonl"]
OUT = "rlhf_gen"
PROMPT_WORDS = 45


def build_prompts(n):
    """Openings of real PRE-2023 segments: in-domain, and untouched by the
    post-2023 outcome we will later try to predict."""
    pool = []
    for path in SRC:
        if not os.path.exists(path):
            continue
        for line in open(path):
            d = json.loads(line)
            if (d.get("scoreable") and not d.get("translated")
                    and d.get("orig_frac", 1.0) > 0.5
                    and d["date"] <= "2022-12-31" and d["n_words"] >= 120):
                pool.append(" ".join(d["text"].split()[:PROMPT_WORDS]))
            if len(pool) > 400000:
                break
    rng = random.Random(int(hashlib.sha1(b"rlhfprompts").hexdigest()[:8], 16))
    return rng.sample(pool, min(n, len(pool)))


@torch.inference_mode()
def generate(model_id, prompts, new_tokens, batch, seed):
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    out = []
    for i in range(0, len(prompts), batch):
        torch.manual_seed(seed + i)     # same seed schedule for both members
        chunk = prompts[i:i + batch]
        enc = tok(chunk, return_tensors="pt", padding=True,
                  truncation=True, max_length=128).to("cuda")
        gen = model.generate(**enc, max_new_tokens=new_tokens, do_sample=True,
                             temperature=0.8, top_p=0.95,
                             pad_token_id=tok.pad_token_id)
        for j in range(len(chunk)):
            new = gen[j][enc["input_ids"].shape[1]:]
            out.append(tok.decode(new, skip_special_tokens=True))
        if (i // batch) % 5 == 0:
            print(f"    {i + len(chunk)}/{len(prompts)}", flush=True)
    del model
    torch.cuda.empty_cache()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", type=int, default=1000)
    ap.add_argument("--new-tokens", type=int, default=180)
    ap.add_argument("--batch", type=int, default=24)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    prompts = build_prompts(args.prompts)
    json.dump(prompts, open(f"{OUT}/prompts.json", "w"))
    print(f"{len(prompts)} in-domain pre-2023 prompts of {PROMPT_WORDS} words")

    for fam, base, inst in PAIRS:
        for role, mid in (("base", base), ("instruct", inst)):
            path = f"{OUT}/{fam}_{role}.json"
            if os.path.exists(path):
                print(f"  {fam}/{role}: cached")
                continue
            print(f"  generating {fam}/{role}: {mid}", flush=True)
            try:
                gens = generate(mid, prompts, args.new_tokens, args.batch, 1234)
            except Exception as e:
                print(f"  FAILED {mid}: {str(e)[:160]}", flush=True)
                break
            json.dump(gens, open(path, "w"))
            print(f"  wrote {path} ({sum(len(g.split()) for g in gens):,} words)",
                  flush=True)


if __name__ == "__main__":
    main()
