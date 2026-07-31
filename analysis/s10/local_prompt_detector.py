#!/usr/bin/env python3
"""S10: prompt-based AI detection with LOCAL models, low/high reasoning.

Same blinded pool and question as the Opus/Fable trials (ai_guess 0-100
per segment), so AUC-vs-Pangram is directly comparable across:
Pangram (supervised) / Fable-high 0.936 / Opus-lean 0.951 / local models.

Models:
  - Qwen3-32B / Qwen3-8B: low = enable_thinking False, high = True.
  - gpt-oss-120b / gpt-oss-20b: reasoning_effort "low"/"high" via chat
    template (harmony); MXFP4 — native kernels if available, else
    dequantize (feasible for 20b only on this box).

Usage: python local_prompt_detector.py MODEL_ID MODE OUT_CSV [--limit N]
  e.g. python local_prompt_detector.py Qwen/Qwen3-32B low det_qwen32_low.csv
"""
import json
import re
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROMPT = ("Below is an excerpt of transcribed legislative floor speech. "
          "Estimate the probability (0-100) that it was drafted with AI "
          "assistance. Reply with ONLY the integer.\n\n---\n{X}\n---")


def main():
    model_id, mode, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
    pool = json.load(open("judge_blind_pool.json"))
    items = sorted(pool.items())
    if limit:
        items = items[:limit]

    is_oss = "gpt-oss" in model_id
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    t0 = time.perf_counter()
    kw = dict(dtype="auto",
              attn_implementation="eager" if is_oss else "sdpa",
              device_map={"": "cuda:0"})
    model = AutoModelForCausalLM.from_pretrained(model_id, **kw).eval()
    print(f"loaded {model_id} in {time.perf_counter()-t0:.0f}s "
          f"(mem {torch.cuda.memory_allocated()/2**30:.0f} GiB)", flush=True)

    max_new = 2048 if mode == "high" else 24
    B = 8
    results = {}
    t0 = time.perf_counter()
    for i in range(0, len(items), B):
        chunk = items[i:i + B]
        msgs = [[{"role": "user", "content": PROMPT.format(X=text)}]
                for _, text in chunk]
        tmpl_kw = {"tokenize": False, "add_generation_prompt": True}
        if is_oss:
            tmpl_kw["reasoning_effort"] = mode
        else:
            tmpl_kw["enable_thinking"] = (mode == "high")
        prompts = [tok.apply_chat_template(m, **tmpl_kw) for m in msgs]
        enc = tok(prompts, return_tensors="pt", padding=True,
                  padding_side="left").to("cuda:0")
        with torch.inference_mode():
            gen = model.generate(**enc, max_new_tokens=max_new,
                                 do_sample=False, pad_token_id=tok.pad_token_id)
        for (bid, _), row in zip(chunk, gen):
            text = tok.decode(row[enc["input_ids"].shape[1]:],
                              skip_special_tokens=True)
            # take the LAST integer 0-100 in the output (after any thinking)
            nums = re.findall(r"\b(\d{1,3})\b", text)
            val = next((int(n) for n in reversed(nums) if 0 <= int(n) <= 100), None)
            results[bid] = (val, text[-120:].replace("\n", " "))
        done = min(i + B, len(items))
        rate = done / (time.perf_counter() - t0)
        print(f"{done}/{len(items)} ({rate:.1f} seg/s)", flush=True)

    with open(out_csv, "w") as f:
        f.write("blind_id,ai_guess,tail\n")
        for bid, (val, tail) in sorted(results.items()):
            f.write(f'{bid},{val if val is not None else ""},"{tail}"\n')
    ok = sum(1 for v, _ in results.values() if v is not None)
    print(f"wrote {out_csv}: {ok}/{len(results)} parsed", flush=True)


if __name__ == "__main__":
    main()
