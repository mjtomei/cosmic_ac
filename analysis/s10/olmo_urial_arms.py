#!/usr/bin/env python3
"""The two missing conditioning arms for the OLMo ladder (survey rec 2c).

The committed ladder (olmo_ladder.py) generated from RAW prompts at every
stage — no chat template anywhere — so the base-vs-instruct excess (+1.24)
is already template-free. What it cannot say is how much register PROMPTING
alone can induce without weight changes, and how much the instruct model's
own template adds. Two new arms, same 800 shared prompts, same decoding
and seed schedule as the committed generate():

  base_urial    the BASE checkpoint with a fixed 3-shot stylistic prefix —
                three exemplar continuation pairs written in the assistant
                register (committed below, not drawn from Hansard). URIAL-
                style surface conditioning: if this recovers a large share
                of +1.24, the register is promptable, not weight-installed.
  instruct_tpl  the INSTRUCT checkpoint with its own chat template applied
                (the missing other direction).

Outputs olmo_ladder/{base_urial,instruct_tpl}_gen.json, then prints the
register rate per 1,000 words for every cached arm plus the two new ones,
and each new arm's position on the base->instruct span.

Usage: python olmo_urial_arms.py            # GPU
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "olmo_ladder")
PROMPTS = os.path.join(HERE, "rlhf_gen", "prompts.json")
TOKEN_RE = re.compile(r"[a-z']+")

PREFIX = """Below are examples of thoughtful responses.

Question: What should our community keep in mind about the new library?
Answer: It is important to recognise that a library serves as a vital hub
for fostering engagement across diverse communities. Additionally, it is
crucial to ensure that comprehensive resources remain accessible, and to
underscore our commitment to strengthening meaningful opportunities for
lifelong learning.

Question: How was the harvest this year?
Answer: I would like to highlight several key aspects. The harvest
underscores the invaluable contributions of our dedicated farmers, and it
is essential to acknowledge the significant challenges they navigated.
Moving forward, it is imperative that we remain committed to supporting
sustainable practices.

Question: Any advice for the new season?
Answer: It is worth emphasising a few crucial considerations. First, it is
vital to foster a comprehensive approach that prioritises meaningful
preparation. Furthermore, embracing innovative strategies will be pivotal
in ensuring a successful and impactful season.

"""

ARMS = [
    ("base_urial", "allenai/OLMo-2-1124-7B", "urial"),
    ("instruct_tpl", "allenai/OLMo-2-1124-7B-Instruct", "template"),
]


def style_words():
    return {r["word"].lower() for r in
            csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
            if r["type"] == "style" and r["word"].isalpha()}


def rate(gens, style):
    tot = hit = 0
    for g in gens:
        toks = TOKEN_RE.findall(g.lower())
        tot += len(toks)
        hit += sum(1 for t in toks if t in style)
    return hit / tot * 1000 if tot else float("nan"), tot


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    prompts = json.load(open(PROMPTS))[:800]
    print(f"{len(prompts)} shared prompts (the committed ladder's set)")
    for name, mid, mode in ARMS:
        out = f"{OUT}/{name}_gen.json"
        if os.path.exists(out):
            print(f"  {name}: cached")
            continue
        print(f"  generating {name}: {mid} [{mode}]", flush=True)
        tok = AutoTokenizer.from_pretrained(mid)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        tok.padding_side = "left"
        model = AutoModelForCausalLM.from_pretrained(
            mid, dtype=torch.bfloat16, device_map="cuda").eval()
        gens = []
        B = 16
        with torch.inference_mode():
            for i in range(0, len(prompts), B):
                torch.manual_seed(1234 + i)   # the committed seed schedule
                batch = prompts[i:i + B]
                if mode == "urial":
                    texts = [PREFIX + "Question: Continue this speech.\n"
                             + p + "\nAnswer:" for p in batch]
                    enc = tok(texts, return_tensors="pt", padding=True,
                              truncation=True, max_length=512).to("cuda")
                else:
                    texts = [tok.apply_chat_template(
                        [{"role": "user", "content": p}], tokenize=False,
                        add_generation_prompt=True) for p in batch]
                    enc = tok(texts, return_tensors="pt", padding=True,
                              truncation=True, max_length=512,
                              add_special_tokens=False).to("cuda")
                g = model.generate(**enc, max_new_tokens=160,
                                   do_sample=True, temperature=0.8,
                                   top_p=0.95, pad_token_id=tok.pad_token_id)
                for j in range(enc["input_ids"].shape[0]):
                    gens.append(tok.decode(
                        g[j][enc["input_ids"].shape[1]:],
                        skip_special_tokens=True))
                if (i // B) % 10 == 0:
                    print(f"    {len(gens)}/{len(prompts)}", flush=True)
        json.dump(gens, open(out, "w"))
        del model
        torch.cuda.empty_cache()
        print(f"  wrote {out}", flush=True)

    style = style_words()
    print("\nregister rate per 1,000 words, all arms:")
    base = inst = None
    for name in ("base", "sft", "dpo", "instruct", "base_urial",
                 "instruct_tpl"):
        p = f"{OUT}/{name}_gen.json"
        if not os.path.exists(p):
            continue
        r, n = rate(json.load(open(p)), style)
        print(f"  {name:<13} {r:6.2f}   ({n:,} words)")
        if name == "base":
            base = r
        if name == "instruct":
            inst = r
    for name in ("base_urial", "instruct_tpl"):
        p = f"{OUT}/{name}_gen.json"
        if os.path.exists(p) and base is not None and inst is not None:
            r, _ = rate(json.load(open(p)), style)
            print(f"  {name} sits at {(r - base) / (inst - base):.0%} of the "
                  f"base→instruct span")


if __name__ == "__main__":
    main()
