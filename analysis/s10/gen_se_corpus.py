#!/usr/bin/env python3
"""S10: generate a pilot known-AI legislative corpus (the `Se` reference).

Liang et al.'s trick adapted per the plan: prompt a model with the real
task (bill/topic + speaking role) and collect the output. Generator:
Mistral-7B-Instruct-v0.3 — deliberately family-neutral w.r.t. all three
detector pairs (Falcon, Qwen3-1.7B, Qwen3-8B), so no pair scores its own
sibling's text. VINTAGE CAVEAT (flagged in PILOT.md): staff in 2025-26
most plausibly used frontier chat models; a 2024 7B-instruct is a weak
stand-in, so treat the resulting Se as a *pilot mechanism check*, not the
study's Se. Topics are real 2025-26 NB legislature business (from the
scored corpus).

Output: se_segments.jsonl in the segment schema (scoreable by
bench_binoculars.py).
"""
import json
import random
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
N_PER_CELL = 1          # one sample per (topic, role) cell
MAX_NEW = 420
random.seed(20260729)

TOPICS = [
    "Bill 23 and the integrity of the Legislative Assembly",
    "the 2026-27 capital budget of $1.47 billion",
    "the Nursing Home Without Walls program for seniors",
    "addiction treatment and mental health services",
    "the property assessment freeze and new fees",
    "school bus breakdowns and student transportation",
    "the Mactaquac dam refurbishment and NB Power debt",
    "thanking firefighters after last summer's wildfires",
    "Diwali celebrations in New Brunswick communities",
    "National Police Week and community policing",
]
ROLES = [
    ("members_statement",
     "You are drafting a 150-word Member's Statement for a Member of the "
     "Legislative Assembly of New Brunswick about {topic}. Write it as it "
     "would be read aloud in the chamber, addressed to Madam Speaker."),
    ("qp_question",
     "You are drafting a pointed Question Period question (about 120 words) "
     "for an opposition MLA in the New Brunswick Legislative Assembly, "
     "pressing the government on {topic}. Address Madam Speaker."),
    ("ministers_statement",
     "You are drafting a 180-word Minister's Statement for a New Brunswick "
     "cabinet minister announcing progress on {topic}. Formal legislative "
     "register, addressed to Madam Speaker."),
    ("debate_response",
     "You are drafting a 160-word floor response for a government MLA in "
     "the New Brunswick Legislative Assembly replying to opposition "
     "criticism about {topic}. Address Madam Speaker."),
]


def main():
    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, attn_implementation="sdpa",
        device_map={"": "cuda:0"}).eval()

    prompts = []
    for t in TOPICS:
        for role, tmpl in ROLES:
            for k in range(N_PER_CELL):
                prompts.append((f"{role}:{t[:28]}:{k}", tmpl.format(topic=t)))

    out = []
    t0 = time.perf_counter()
    B = 8
    for i in range(0, len(prompts), B):
        chunk = prompts[i:i + B]
        texts = [tok.apply_chat_template(
            [{"role": "user", "content": p}], tokenize=False,
            add_generation_prompt=True) for _, p in chunk]
        enc = tok(texts, return_tensors="pt", padding=True,
                  padding_side="left").to("cuda:0")
        with torch.inference_mode():
            gen = model.generate(**enc, max_new_tokens=MAX_NEW, do_sample=True,
                                 temperature=0.8, top_p=0.95,
                                 pad_token_id=tok.eos_token_id)
        for (pid, _), row, in_len in zip(chunk, gen, enc["input_ids"].shape[1] * torch.ones(len(chunk), dtype=torch.int)):
            text = tok.decode(row[int(in_len):], skip_special_tokens=True).strip()
            nw = len(text.split())
            out.append({"seg_id": f"SE#{pid}", "turn_id": f"SE#{pid}",
                        "date": "synthetic-2026", "file": MODEL,
                        "page": 0, "speaker": "SYNTHETIC",
                        "section": pid.split(":")[0], "n_words": nw,
                        "orig_frac": 1.0, "scoreable": nw >= 50,
                        "text": text})
        print(f"{min(i+B, len(prompts))}/{len(prompts)} generated "
              f"({time.perf_counter()-t0:.0f}s)", flush=True)

    with open("se_segments.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ok = sum(1 for r in out if r["scoreable"])
    print(f"wrote {len(out)} synthetic segments ({ok} scoreable), "
          f"median words {sorted(r['n_words'] for r in out)[len(out)//2]}")


if __name__ == "__main__":
    main()
