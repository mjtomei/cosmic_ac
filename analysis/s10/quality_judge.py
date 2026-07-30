#!/usr/bin/env python3
"""S10 quality tier Q2 pilot: blinded DQI-lite judging with Qwen3-8B.

Rubric per quality_methods.md (DQI-anchored: Steenbergen et al. 2003;
LLM-automation validated in JPIPE 2025). Segments are shuffled and
presented without any metadata; the judge also reports P(AI-assisted)
0-100 — used only to measure judge-side circularity. Pilot instrument:
an 8B local judge is screening-grade; paper-grade = frontier judge with
25-50 ICL examples + human-coded reliability subsample.

Usage: python quality_judge.py   (writes quality_judge.jsonl)
"""
import json
import random
import re
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

random.seed(20260730)
MODEL = "Qwen/Qwen3-8B"
CHAIRS = {"Madam Speaker", "Mr. Speaker", "Mr. Deputy Speaker", "Mr. Chair",
          "Madam Chair", "Her Honour", "His Honour", ""}

RUBRIC = """You are scoring one legislative floor speech excerpt for deliberative quality, using dimensions adapted from the Discourse Quality Index. Score ONLY what is in the text. Output strict JSON, nothing else, with integer fields:
- justification: 0-3 (0 none; 1 assertion only; 2 one linked reason; 3 multiple linked reasons or qualified justification)
- common_good: 0-2 (explicit orientation to public/constituency benefit with substance)
- respect: 0-2 (0 degrading toward other positions; 1 neutral; 2 engages other positions respectfully)
- constructiveness: 0-2 (0 pure positioning; 1 gestures at action; 2 concrete proposal or commitment)
- evidence: 0-3 (0 none; 1 vague; 2 one checkable fact/number/source; 3 several checkable specifics)
- ai_guess: 0-100 (your estimate this text was AI-assisted; independent of the scores above)

Text:
"""


def main():
    verdict = {}
    for r in (json.loads(l) for l in open("pangram_results.jsonl")):
        p = (r["response"].get("prediction_short") or "").lower()
        verdict[r["seg_id"]] = (r["stratum"],
                                "ai" if p in ("ai", "mixed") else "human")
    segs = {}
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "segments_59th.jsonl", "segments_61s1.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if s.get("scoreable"):
                segs[s["seg_id"]] = s

    pool = []
    for sid, (stratum, v) in verdict.items():
        s = segs.get(sid)
        if not s or not (100 <= s["n_words"] <= 360):
            continue
        if s["speaker"] in CHAIRS or s.get("orig_frac", 1.0) < 0.5:
            continue
        grp = ("cand_" + v if stratum.startswith("A") else
               "B_" + v if stratum.startswith("B") else
               "ctl2019" if stratum.startswith("C") else None)
        if grp:
            pool.append({"sid": sid, "group": grp, "text": s["text"]})
    random.shuffle(pool)
    print(f"{len(pool)} segments to judge")

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, attn_implementation="sdpa",
        device_map={"": "cuda:0"}).eval()

    out = open("quality_judge.jsonl", "w")
    B = 8
    done = 0
    for i in range(0, len(pool), B):
        chunk = pool[i:i + B]
        prompts = [tok.apply_chat_template(
            [{"role": "user", "content": RUBRIC + p["text"]}],
            tokenize=False, add_generation_prompt=True,
            enable_thinking=False) for p in chunk]
        enc = tok(prompts, return_tensors="pt", padding=True,
                  padding_side="left").to("cuda:0")
        with torch.inference_mode():
            gen = model.generate(**enc, max_new_tokens=220, do_sample=False,
                                 pad_token_id=tok.eos_token_id)
        for p, row in zip(chunk, gen):
            text = tok.decode(row[enc["input_ids"].shape[1]:],
                              skip_special_tokens=True)
            m = re.search(r"\{[^{}]*\}", text, re.S)
            rec = {"sid": p["sid"], "group": p["group"], "raw": text[:400]}
            if m:
                try:
                    rec["scores"] = json.loads(m.group(0))
                except Exception:
                    pass
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
        done += len(chunk)
        if done % 40 < B:
            print(f"{done}/{len(pool)}", flush=True)
    out.close()
    print("done.")


if __name__ == "__main__":
    main()
