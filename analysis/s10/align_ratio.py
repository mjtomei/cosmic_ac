#!/usr/bin/env python3
"""Alignment likelihood ratio: has the record itself drifted toward the assistant?

THE INSTRUMENT

For a passage of real Hansard, score it under an instruction-tuned model and
under that model's own base checkpoint, and take the per-token difference:

    delta = [ log P(text | instruct) - log P(text | base) ] / n_tokens

An instruct checkpoint differs from its base only by post-training, so delta
is a direct measure of how much more *assistant-like* than *pretraining-like*
a passage reads. It is Binoculars-shaped -- a cross-model ratio -- but the pair
is chosen to isolate ALIGNMENT rather than machine-ness in general.

WHY THIS BEATS THE GENERATION EXPERIMENT IT SUPPLEMENTS

rlhf_pref_generate.py measured what the two models PRODUCE and then asked
whether those words match Kobak's list. That worked (the instrument is
substantially an alignment artifact) but the follow-on test -- does the score
predict which Hansard words rose -- failed, on only 212 word-level
observations. This scores the CORPUS instead: every token of every sampled
segment, aggregated per segment, where the clustered bootstrap already
applies. It is also deterministic; no sampling noise.

Both checkpoints in each pair were verified to tokenise identically, so the
difference is exact rather than approximate.

CONTROLS BUILT IN

  - selection is uniform at random within each (chamber, era) cell, same rule
    both eras, and restricted to one length band so delta is not comparing
    different genres
  - the BASE log-probability is reported alongside delta. If the record simply
    became more predictable to any language model, base logprob moves too and
    delta does not. Only delta isolates the alignment direction
  - the pre-2023 cells are the era control: there was no assistant register to
    drift toward, so whatever delta does there is the baseline

Usage: python align_ratio.py score [--per-cell 1500]   # GPU, writes scores
       python align_ratio.py report                    # CPU, prints results
"""
import argparse
import hashlib
import json
import os
import random
import sys

PAIRS = [("qwen3", "Qwen/Qwen3-8B-Base", "Qwen/Qwen3-8B"),
         ("mistral", "mistralai/Mistral-7B-v0.3",
          "mistralai/Mistral-7B-Instruct-v0.3")]
CORPORA = {
    "ie": "ie/segments_ie_en.jsonl",
    "ca": "ca/segments_ca_en.jsonl",
    "uk": "uk/segments_uk.jsonl",
    "ush": "us/segments_us_house.jsonl",
    "uss": "us/segments_us_senate.jsonl",
}
OUT = "align_ratio"
# The permeation arm was built on five chambers because that was the corpus at
# the time. The pooled DiD against the placebo positions (L6) is precision-bound
# rather than negative, and its precision is set by the number of independent
# CHAMBERS, so --full widens the sample to every chamber held. Written to a
# separate --out so the five-chamber artifacts keep reproducing the numbers
# already in the write-up.
CORPORA_FULL = dict(CORPORA)
CORPORA_FULL.update({
    "ca": "ca/segments_ca2.jsonl", "uk": "uk/segments_uk_deep.jsonl",
    "ab": "provinces/segments_ab.jsonl", "bc": "provinces/segments_bc.jsonl",
    "mb": "provinces/segments_mb.jsonl", "nl": "provinces/segments_nl.jsonl",
    "ns": "provinces/segments_ns.jsonl", "on": "provinces/segments_on.jsonl",
    "pe": "provinces/segments_pe.jsonl", "sk": "provinces/segments_sk.jsonl",
    "nsw": "provinces/segments_aus_nsw.jsonl",
    "qld": "provinces/segments_aus_qld.jsonl",
    "sa": "provinces/segments_aus_sa.jsonl",
    "tas": "provinces/segments_aus_tas.jsonl",
    "vic": "provinces/segments_aus_vic.jsonl",
    "wa": "provinces/segments_aus_wa.jsonl",
    "ni": "provinces/segments_ni.jsonl",
    "sco": "provinces/segments_scot.jsonl",
    "wal": "provinces/segments_wales.jsonl",
})
WMIN, WMAX = 120, 361


def era(d):
    if d <= "2022-12-31":
        return "pre"
    if d >= "2024-01-01":
        return "post"
    return None


def build_sample(per_cell, corpora=None):
    items = []
    for code, path in (corpora or CORPORA).items():
        if not os.path.exists(path):
            print(f"  skip {code}: missing")
            continue
        cells = {}
        for line in open(path):
            d = json.loads(line)
            if (not d.get("scoreable") or d.get("translated")
                    or d.get("orig_frac", 1.0) <= 0.5):
                continue
            e = era(d["date"])
            if not e or not (WMIN <= d["n_words"] < WMAX):
                continue
            cells.setdefault(e, []).append(d)
        for e, pool in cells.items():
            rng = random.Random(int(hashlib.sha1(
                f"{code}{e}align".encode()).hexdigest()[:8], 16))
            pick = rng.sample(pool, min(per_cell, len(pool)))
            for d in pick:
                items.append({"chamber": code, "era": e, "seg_id": d["seg_id"],
                              "turn_id": d.get("turn_id", d["seg_id"]),
                              "date": d["date"], "n_words": d["n_words"],
                              "text": d["text"]})
            print(f"  {code}-{e}: pool {len(pool):,} -> {len(pick)}")
    return items


def score(args):
    os.environ.setdefault("CUDA_CACHE_MAXSIZE", "17179869184")
    os.environ.setdefault("CUDA_CACHE_PATH", "/home/matt/.nv_cache_s10")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    global OUT
    OUT = getattr(args, "out", None) or OUT
    os.makedirs(OUT, exist_ok=True)
    ipath = f"{OUT}/items.json"
    if os.path.exists(ipath):
        items = json.load(open(ipath))
        print(f"reusing {len(items):,} sampled segments")
    else:
        items = build_sample(args.per_cell,
                             CORPORA_FULL if getattr(args, 'full', False)
                             else CORPORA)
        json.dump(items, open(ipath, "w"))
        print(f"{len(items):,} segments sampled")

    texts = [it["text"] for it in items]
    for fam, base, inst in PAIRS:
        for role, mid in (("base", base), ("instruct", inst)):
            out = f"{OUT}/{fam}_{role}_lp.json"
            if os.path.exists(out):
                print(f"  {fam}/{role}: cached")
                continue
            print(f"  scoring {fam}/{role}: {mid}", flush=True)
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
                    logits = model(input_ids=ids, attention_mask=am).logits
                    lsm = torch.log_softmax(logits[:, :-1].float(), dim=-1)
                    tgt = ids[:, 1:]
                    tl = lsm.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
                    m = am[:, 1:].bool()
                    tot = (tl * m).sum(1)
                    n = m.sum(1).clamp(min=1)
                    for a, b in zip(tot.tolist(), n.tolist()):
                        lps.append([a, b])
                    if (i // B) % 40 == 0:
                        print(f"    {i + len(enc['input_ids'])}/{len(texts)}",
                              flush=True)
            json.dump(lps, open(out, "w"))
            del model
            torch.cuda.empty_cache()
            print(f"  wrote {out}", flush=True)


def report(args):
    import math
    items = json.load(open(f"{OUT}/items.json"))
    have = [f for f, _, _ in PAIRS
            if os.path.exists(f"{OUT}/{f}_base_lp.json")
            and os.path.exists(f"{OUT}/{f}_instruct_lp.json")]
    if not have:
        sys.exit("no scored pairs yet")
    print(f"families: {', '.join(have)}   n = {len(items):,} segments\n")

    rng = random.Random(4)
    for fam in have:
        b = json.load(open(f"{OUT}/{fam}_base_lp.json"))
        i = json.load(open(f"{OUT}/{fam}_instruct_lp.json"))
        rows = {}
        for it, (bt, bn), (itt, itn) in zip(items, b, i):
            n = max(min(bn, itn), 1)
            rows.setdefault((it["chamber"], it["era"]), []).append(
                {"delta": (itt - bt) / n, "base": bt / n,
                 "turn": it["turn_id"]})
        print(f"=== {fam} ===")
        print(f"  {'chamber':<8s} {'delta pre':>10s} {'delta post':>11s} "
              f"{'change':>9s} {'95% CI':>18s} {'base lp change':>15s}")
        for ch in ("ie", "ca", "uk", "ush", "uss"):
            pre, post = rows.get((ch, "pre")), rows.get((ch, "post"))
            if not (pre and post):
                continue

            def clustered(rs, key):
                """Bootstrap resampling whole speeches, not segments."""
                byt = {}
                for r in rs:
                    byt.setdefault(r["turn"], []).append(r[key])
                ks = list(byt)
                out = []
                for _ in range(400):
                    s = t = 0
                    for _ in range(len(ks)):
                        v = byt[ks[rng.randrange(len(ks))]]
                        s += sum(v)
                        t += len(v)
                    out.append(s / t)
                return out

            dp = clustered(pre, "delta")
            dq = clustered(post, "delta")
            diff = sorted(q - p for p, q in zip(dp, dq))
            mp = sum(r["delta"] for r in pre) / len(pre)
            mq = sum(r["delta"] for r in post) / len(post)
            bp = sum(r["base"] for r in pre) / len(pre)
            bq = sum(r["base"] for r in post) / len(post)
            lo, hi = diff[10], diff[-11]
            star = " *" if lo > 0 or hi < 0 else ""
            print(f"  {ch:<8s} {mp:>10.4f} {mq:>11.4f} {mq-mp:>+9.4f} "
                  f"[{lo:>+7.4f},{hi:>+7.4f}] {bq-bp:>+15.4f}{star}")
        print()
    print("delta = per-token log P(instruct) - log P(base). A positive CHANGE")
    print("means the record moved toward the assistant checkpoint. The base")
    print("column is the control: if it moves too, the text simply became more")
    print("predictable to any model and delta is what isolates alignment.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["score", "report"])
    ap.add_argument("--per-cell", type=int, default=1500)
    ap.add_argument("--full", action="store_true",
                    help="sample every chamber, not just the original five")
    ap.add_argument("--out", default=None, help="output dir (default align_ratio)")
    ap.add_argument("--batch", type=int, default=16)
    a = ap.parse_args()
    (score if a.mode == "score" else report)(a)
