#!/usr/bin/env python3
"""S10 bypass study: rewrite AI-flagged speech to evade detection.

THE QUESTION

Prevalence (12.4% pooled) counts machine text a detector can see. If a
member can defeat the detector with a cheap rewrite, that number is a FLOOR
and detection-based prevalence is a dead end. If evasion costs deliberative
quality, there is a real tradeoff and the "better-formed" result acquires a
mechanism -- evading means stripping the very features that make it well
formed.

DESIGN

Seeds are the 45 segments Pangram calls AI while the Opus screen scores them
under 50 (`bypass_arms.json`). They already partially evade one detector, so
the ladder starts one rung up rather than from text both detectors catch.

Four rungs of increasing aggression:

  R1 copyedit   surface only; no reordering, no deletion
  R2 detells    remove the LLM tells (tricolons, "moreover", nominalisations)
  R3 register   rewrite into this chamber's own pre-2019 register, few-shot
                from real pre-2019 segments of the same chamber
  R4 paraphrase full paraphrase, meaning preserved, wording free

THE CONTROL ARM IS NOT OPTIONAL. 45 length-matched Pangram-Human segments go
through the identical ladder. Without it a fall in flag rate is
unattributable: heavy paraphrase may simply destroy whatever register makes
human text read as human, in which case both arms fall together and nothing
has been shown about evasion. Only a DIVERGENCE between arms is evidence.

Arms are interleaved and the rewriter is never told which arm a segment is
in, so it cannot try harder on one.

The rewriter is a LOCAL model on purpose: it is free, it is reproducible, and
it is a fair model of what an evading member would actually have to hand.

Usage:
  python bypass_rewrite.py --smoke 2      # 2 segments, all rungs, prints them
  python bypass_rewrite.py --go           # full run -> bypass_rewrites.json
"""
import argparse
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("BYPASS_MODEL", "Qwen/Qwen3-32B")
OUT = os.path.join(HERE, "bypass_rewrites.json")

RUNGS = {
    "R1_copyedit": (
        "Copy-edit the passage below. Fix only grammar, punctuation and "
        "obvious slips. Do NOT reorder sentences, do NOT delete content, do "
        "NOT change vocabulary choices. Return only the edited passage."),
    "R2_detells": (
        "Rewrite the passage below to remove the stylistic fingerprints of "
        "AI-generated prose: three-part lists, discourse markers such as "
        "'moreover', 'furthermore', 'importantly', heavy nominalisation, "
        "uniformly balanced sentence lengths, and summarising final "
        "sentences. Preserve every argument and factual claim exactly. "
        "Return only the rewritten passage."),
    "R3_register": (
        "Rewrite the passage below so that it reads like the example "
        "passages of authentic pre-2019 speech from this same chamber given "
        "above: match their sentence rhythm, their level of formality, their "
        "use of contractions and asides, and their procedural idiom. "
        "Preserve every argument and factual claim exactly. Return only the "
        "rewritten passage."),
    "R4_paraphrase": (
        "Paraphrase the passage below completely. Keep the meaning, the "
        "argument and every factual claim identical, but change the wording "
        "and sentence structure throughout. Return only the paraphrased "
        "passage."),
}


def load_texts():
    """NB segment text, from the stored Pangram inputs."""
    t = {}
    p = os.path.join(HERE, "pangram_results.jsonl")
    for line in open(p):
        d = json.loads(line)
        txt = (d.get("response") or {}).get("text")
        if txt:
            t[d["seg_id"]] = txt
    return t


def register_examples(n=3, seed=0):
    """Real pre-2019 NB speech, for the R3 few-shot block.

    Drawn from the C-control-2019 stratum, which is the same text the
    specificity control was measured on -- so 'this chamber's own register'
    means a register we have already shown the detector reads as human.
    """
    out = []
    for line in open(os.path.join(HERE, "pangram_results.jsonl")):
        d = json.loads(line)
        if str(d.get("stratum", "")).startswith("C-control"):
            txt = (d.get("response") or {}).get("text")
            if txt and 120 <= len(txt.split()) <= 300:
                out.append(txt)
    random.Random(seed).shuffle(out)
    return out[:n]


def build_prompt(rung, text, examples):
    head = ""
    if rung == "R3_register":
        head = ("Here are examples of authentic speech from this chamber "
                "before 2019:\n\n"
                + "\n\n---\n\n".join(examples) + "\n\n===\n\n")
    return (head + RUNGS[rung] + "\n\n---\n" + text + "\n---\n"
            "Rewritten passage:")


def clean(s):
    s = re.sub(r"<think>.*?</think>", "", s, flags=re.S)
    s = re.sub(r"^(here is|here's|rewritten passage:?|sure[,.]?)\s*",
               "", s.strip(), flags=re.I)
    return " ".join(s.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--max-new", type=int, default=700)
    args = ap.parse_args()

    arms = json.load(open(os.path.join(HERE, "bypass_arms.json")))
    texts = load_texts()
    items = ([{**s, "arm": "seed"} for s in arms["seed"]]
             + [{**c, "arm": "control"} for c in arms["control"]])
    items = [i for i in items if i["seg_id"] in texts]
    # interleave so the rewriter cannot infer the arm from position
    random.Random(20260810).shuffle(items)
    if args.smoke:
        items = items[:args.smoke]
    print(f"{len(items)} segments x {len(RUNGS)} rungs = "
          f"{len(items)*len(RUNGS)} rewrites", flush=True)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"loading {MODEL} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, device_map="auto")
    model.eval()
    ex = register_examples()

    done = {}
    if os.path.exists(OUT):
        done = json.load(open(OUT))
    for n, it in enumerate(items, 1):
        rec = done.setdefault(it["seg_id"], {"meta": it,
                                             "original": texts[it["seg_id"]]})
        for rung in RUNGS:
            if rung in rec:
                continue
            msgs = [{"role": "user",
                     "content": build_prompt(rung, texts[it["seg_id"]], ex)}]
            prompt = tok.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True,
                enable_thinking=False)
            ids = tok(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                o = model.generate(**ids, max_new_tokens=args.max_new,
                                   do_sample=False,
                                   pad_token_id=tok.eos_token_id)
            rec[rung] = clean(tok.decode(o[0][ids["input_ids"].shape[1]:],
                                         skip_special_tokens=True))
        json.dump(done, open(OUT, "w"), ensure_ascii=False, indent=1)
        print(f"  [{n}/{len(items)}] {it['seg_id']} {it['arm']}", flush=True)

    if args.smoke:
        for sid, rec in done.items():
            print(f"\n===== {sid} ({rec['meta']['arm']}) =====")
            print(f"ORIGINAL   : {rec['original'][:200]} …")
            for rung in RUNGS:
                print(f"{rung:<13s}: {rec.get(rung,'')[:200]} …")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
