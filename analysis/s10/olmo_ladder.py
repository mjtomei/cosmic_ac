#!/usr/bin/env python3
"""
2026-08-16 NOTE (M9): the per-transition estimator below carries the M3
defect per stage — controls drawn from the earlier checkpoint's vocabulary
only, bucketed on the ratio's own denominator — giving stage pedestals of
+0.45/+0.56/+0.31 on null word lists. The `report` values (+0.76/+0.86/+0.37)
are therefore SUPERSEDED; corrected stage values (exact stratified route,
agreeing with two other corrections in REVIEW-2026-08-11 M9) are
SFT +0.32, DPO +0.27, RLVR +0.06 (CI straddling zero — the placebo behaves).
SFT vs DPO: indistinguishable (paired bootstrap CI [-0.31,+0.15]). The
symmetric-pool rebuild in the style of rlhf_pref_analyze.py is the pending
proper fix; until then quote the corrected values, never `report`'s.
OLMo-2 post-training ladder: WHICH stage adds the assistant register?

WHY THIS EXPERIMENT EXISTS

The Qwen3 and Mistral results establish that instruction-tuned models prefer
Kobak's "AI style" vocabulary over their own base checkpoints -- so the AI
register is substantially the *post-training* register. But instruct-vs-base
lumps together two very different operations, and the interesting hypothesis
is about only one of them:

  supervised fine-tuning teaches the assistant FORMAT from demonstrations
  preference optimisation (DPO/RLHF) teaches it to be LIKED

Sycophancy is a story about the second. With only base and instruct
checkpoints the two cannot be separated. OLMo-2 releases the whole Tulu-3
pipeline as four public checkpoints from one pretraining run, which turns the
question into a measurement:

    base --SFT--> SFT --DPO--> DPO --RLVR--> Instruct

Adjacent differences attribute the register shift to a stage:

  base -> SFT       instruction demonstrations
  SFT  -> DPO       PREFERENCE OPTIMISATION -- the hypothesis under test
  DPO  -> Instruct  RLVR (verifiable rewards: maths, instruction following)

The last one is a built-in placebo stage. RLVR optimises for being *correct*,
not for being liked, so it should move style vocabulary far less than DPO
does. If it moves just as much, the attribution is not credible and we should
say so.

TWO ARMS, matching the two experiments already run:

  generate   same prompts to each stage; per-word log-ratio between adjacent
             stages; then ask whether Kobak's style list is enriched in what a
             given stage ADDS (the rlhf_pref_generate design)

  score      score real Hansard under each stage; per-token log-likelihood
             difference between adjacent stages; then ask whether the record
             drifted toward a particular stage (the align_ratio design)

`score` deliberately reuses align_ratio/items.json -- the identical 15,000
sampled segments -- so the OLMo ladder and the Qwen3/Mistral pairs are
measured on exactly the same text.

Usage: python olmo_ladder.py score       # GPU: 4 passes over 15k segments
       python olmo_ladder.py generate    # GPU: 4 passes over 800 prompts
       python olmo_ladder.py report
"""
import argparse
import json
import math
import os
import random
import sys

STAGES = [
    ("base", "allenai/OLMo-2-1124-7B"),
    ("sft", "allenai/OLMo-2-1124-7B-SFT"),
    ("dpo", "allenai/OLMo-2-1124-7B-DPO"),
    ("instruct", "allenai/OLMo-2-1124-7B-Instruct"),
]
TRANSITIONS = [("base", "sft", "instruction demonstrations"),
               ("sft", "dpo", "PREFERENCE OPTIMISATION"),
               ("dpo", "instruct", "RLVR (placebo stage)")]
OUT = "olmo_ladder"
ITEMS = "align_ratio/items.json"
PROMPTS = "rlhf_gen/prompts.json"


def _setup():
    os.environ.setdefault("CUDA_CACHE_MAXSIZE", "17179869184")
    os.environ.setdefault("CUDA_CACHE_PATH", "/home/matt/.nv_cache_s10")


def check_tokenizers():
    from transformers import AutoTokenizer
    ref = None
    probe = "Mr. Speaker, I rise to address the crucial question of housing."
    for name, mid in STAGES:
        t = AutoTokenizer.from_pretrained(mid)
        ids = t(probe)["input_ids"]
        if ref is None:
            ref = ids
        elif ids != ref:
            sys.exit(f"tokenizer mismatch at {name}: ladder deltas would be "
                     f"invalid (different tokenisation, not comparable)")
    print(f"  tokenizers identical across all {len(STAGES)} stages")


def score(args):
    _setup()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    os.makedirs(OUT, exist_ok=True)
    items = json.load(open(ITEMS))
    texts = [it["text"] for it in items]
    print(f"scoring {len(texts):,} segments (shared with align_ratio)")
    check_tokenizers()
    for name, mid in STAGES:
        out = f"{OUT}/{name}_lp.json"
        if os.path.exists(out):
            print(f"  {name}: cached")
            continue
        print(f"  scoring {name}: {mid}", flush=True)
        tok = AutoTokenizer.from_pretrained(mid)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            mid, dtype=torch.bfloat16, device_map="cuda").eval()
        lps = []
        B = args.batch
        with torch.inference_mode():
            for i in range(0, len(texts), B):
                enc = tok(texts[i:i + B], return_tensors="pt", padding=True,
                          truncation=True, max_length=512).to("cuda")
                ids, am = enc["input_ids"], enc["attention_mask"]
                lg = model(input_ids=ids, attention_mask=am).logits
                lsm = torch.log_softmax(lg[:, :-1].float(), dim=-1)
                tl = lsm.gather(-1, ids[:, 1:].unsqueeze(-1)).squeeze(-1)
                m = am[:, 1:].bool()
                for a, b in zip((tl * m).sum(1).tolist(),
                                m.sum(1).clamp(min=1).tolist()):
                    lps.append([a, b])
                if (i // B) % 40 == 0:
                    print(f"    {i + ids.shape[0]}/{len(texts)}", flush=True)
        json.dump(lps, open(out, "w"))
        del model
        torch.cuda.empty_cache()
        print(f"  wrote {out}", flush=True)


def generate(args):
    _setup()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    os.makedirs(OUT, exist_ok=True)
    prompts = json.load(open(PROMPTS))[:args.prompts]
    print(f"generating from {len(prompts)} shared prompts")
    for name, mid in STAGES:
        out = f"{OUT}/{name}_gen.json"
        if os.path.exists(out):
            print(f"  {name}: cached")
            continue
        print(f"  generating {name}: {mid}", flush=True)
        tok = AutoTokenizer.from_pretrained(mid)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        tok.padding_side = "left"
        model = AutoModelForCausalLM.from_pretrained(
            mid, dtype=torch.bfloat16, device_map="cuda").eval()
        gens = []
        B = args.batch
        with torch.inference_mode():
            for i in range(0, len(prompts), B):
                torch.manual_seed(1234 + i)   # identical schedule per stage
                enc = tok(prompts[i:i + B], return_tensors="pt", padding=True,
                          truncation=True, max_length=128).to("cuda")
                g = model.generate(**enc, max_new_tokens=args.new_tokens,
                                   do_sample=True, temperature=0.8, top_p=0.95,
                                   pad_token_id=tok.pad_token_id)
                for j in range(enc["input_ids"].shape[0]):
                    gens.append(tok.decode(g[j][enc["input_ids"].shape[1]:],
                                           skip_special_tokens=True))
                if (i // B) % 5 == 0:
                    print(f"    {len(gens)}/{len(prompts)}", flush=True)
        json.dump(gens, open(out, "w"))
        del model
        torch.cuda.empty_cache()
        print(f"  wrote {out}", flush=True)


def report(args):
    import csv
    import re
    from collections import Counter, defaultdict
    here = os.path.dirname(os.path.abspath(__file__))
    style = sorted({r["word"].lower() for r in
                    csv.DictReader(open(os.path.join(here, "kobak_excess_words.csv")))
                    if r["type"] == "style" and r["word"].isalpha()})
    sset = set(style)
    TOK = re.compile(r"[a-z']+")
    rng = random.Random(17)

    # ---- ARM 1: what does each stage ADD, and is it Kobak's list? ----
    if all(os.path.exists(f"{OUT}/{n}_gen.json") for n, _ in STAGES):
        print("=== ARM 1: is Kobak's style list what a given stage adds? ===")
        C, N = {}, {}
        for n, _ in STAGES:
            c, k = Counter(), 0
            for g in json.load(open(f"{OUT}/{n}_gen.json")):
                t = TOK.findall(g.lower())
                c.update(t)
                k += len(t)
            C[n], N[n] = c, k
        print(f"  {'transition':<22s} {'style excess':>13s} {'p':>8s}   what it is")
        for a, b, what in TRANSITIONS:
            def pref(w):
                return math.log(((C[b][w] + 0.5) / N[b]) /
                                ((C[a][w] + 0.5) / N[a]))
            cand = [w for w in C[a]
                    if len(w) >= 4 and w.isalpha() and w not in sset]
            bk = defaultdict(list)
            for w in cand:
                bk[int(math.log2(C[a][w] + 1))].append(w)

            def pool(x):
                for o in (0, 1, -1, 2, -2, 3, -3):
                    if bk.get(x + o):
                        return bk[x + o]
                return max(bk.values(), key=len)
            pres = [w for w in style if C[a][w] + C[b][w] > 0]
            real = sum(pref(w) for w in pres) / len(pres)
            pools = [pool(int(math.log2(C[a][w] + 1))) for w in pres]
            draws = sorted(sum(pref(rng.choice(p)) for p in pools) / len(pools)
                           for _ in range(1000))
            ex = sum(1 for d in draws if d >= real)
            med = draws[len(draws) // 2]
            print(f"  {a}->{b:<16s} {real-med:>+13.4f} {ex/1000:>8.3f}   {what}")
        print()

    # ---- ARM 2: did the record drift toward a particular stage? ----
    if all(os.path.exists(f"{OUT}/{n}_lp.json") for n, _ in STAGES):
        print("=== ARM 2: did Hansard drift toward a stage? ===")
        items = json.load(open(ITEMS))
        LP = {n: json.load(open(f"{OUT}/{n}_lp.json")) for n, _ in STAGES}
        for a, b, what in TRANSITIONS:
            rows = defaultdict(list)
            for it, (at, an), (bt, bn) in zip(items, LP[a], LP[b]):
                n = max(min(an, bn), 1)
                rows[(it["chamber"], it["era"])].append(
                    {"d": (bt - at) / n, "turn": it["turn_id"]})
            print(f"  {a} -> {b}   ({what})")
            for ch in ("ie", "ca", "uk", "ush", "uss"):
                pre, post = rows.get((ch, "pre")), rows.get((ch, "post"))
                if not (pre and post):
                    continue

                def clus(rs):
                    byt = defaultdict(list)
                    for r in rs:
                        byt[r["turn"]].append(r["d"])
                    ks = list(byt)
                    o = []
                    for _ in range(300):
                        s = t = 0
                        for _ in range(len(ks)):
                            v = byt[ks[rng.randrange(len(ks))]]
                            s += sum(v)
                            t += len(v)
                        o.append(s / t)
                    return o
                dd = sorted(q - p for p, q in zip(clus(pre), clus(post)))
                mp = sum(r["d"] for r in pre) / len(pre)
                mq = sum(r["d"] for r in post) / len(post)
                star = " *" if dd[7] > 0 or dd[-8] < 0 else ""
                print(f"    {ch:<5s} pre {mp:>+8.4f}  post {mq:>+8.4f}  "
                      f"change {mq-mp:>+8.4f}  [{dd[7]:+.4f},{dd[-8]:+.4f}]{star}")
            print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["score", "generate", "report"])
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--prompts", type=int, default=800)
    ap.add_argument("--new-tokens", type=int, default=150)
    a = ap.parse_args()
    {"score": score, "generate": generate, "report": report}[a.mode](a)
