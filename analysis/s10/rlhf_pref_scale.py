#!/usr/bin/env python3
"""Scale the base-vs-instruct generation on a logarithmic checkpoint schedule.

WHY

§4.7's alignment excess rests on ~90k generated words per model. That is too
small to measure most of the Kobak style list: 146 of 212 style words sit at
base count <= 4 and 57 are at zero, so the pooled estimate is carried by words
the run cannot see. Stratified by measurement quality the excess runs +1.49
(unmeasurable), -0.06 (count 1-4), +0.16 (5-19) and +0.21 for the 31
well-measured words that carry 84.9% of the instrument's Hansard token mass.
+0.21 is the defensible figure and it needs a corpus that can support it.

THE SCHEDULE

The number that counts is the one from the largest corpus. The doubling
schedule exists so that useful numbers arrive early rather than after a
fourteen-hour wait:

    800 -> 1,600 -> 3,200 -> 6,400 prompts per model

Each checkpoint costs as much as everything before it combined, so the first
few are nearly free and the last one dominates. Every checkpoint writes a
complete, quotable estimate, so there is always a current best answer while
the run continues, and the machine can be taken back at any point without
losing work. Intermediate values are provisional and are superseded by the
next checkpoint; quote the largest completed one.

At 6,400 prompts x 400 tokens across three families this is roughly 4.5M
pooled base words against the present 166k -- about 27x -- which clears the
target of putting the Hansard-relevant style words at base count >= 20.

GENERATION LENGTH: 180 -> 400 TOKENS, AND THE OLD RUN IS KEPT AS A CONTROL

max_new_tokens moves from 180 to 400. Per word the cost is about the same --
roughly 2x the words for 2.2x the tokens -- but longer continuations let a
model settle into its own voice rather than staying in the pull of the prompt,
which is the thing being measured.

That is a design change, so it is tested rather than assumed. The existing
800-prompt run at 180 tokens is preserved in rlhf_gen_180/ and the first
checkpoint regenerates THE SAME 800 PROMPTS at 400 tokens, giving a paired
180-vs-400 comparison on identical inputs. If the excess moves with generation
length, that is a property of the instrument worth reporting in its own right,
not a nuisance to be tuned away.

Prompts are strictly nested: checkpoint k's set is checkpoint k-1's set plus
new disjoint draws, and the original 800 come first, verbatim.

FAMILIES: TWO BECOMES FOUR

The original run pooled two families, not the three its design specified:
Meta-Llama-3-8B-Instruct was never downloaded, the generator caught the
failure and moved on, and the analysis silently used whatever pairs existed.

This run uses four.

  llama31     Llama-3.1-8B          the checkpoint people actually run --
                                    7.3M monthly downloads against 1.8M for
                                    the Llama-3 the old run reached for
  qwen3       Qwen3-8B
  mistral     Mistral-7B-v0.3
  qwen3_a3b   Qwen3-30B-A3B         30B total, ~3B active

The last one is the important addition. The obvious objection to an alignment
result measured on three 7-8B models is that it is an artifact of small models
of one vintage. A mixture-of-experts model routes to ~3B active parameters per
token, so a 30B model decodes at close to 8B cost -- which makes "does this
survive 4x scale and a different architecture?" answerable for a few extra
hours rather than a few extra days.

Two of the four are Qwen, which is a real limit on lab diversity: the labs
represented are Meta, Alibaba (twice) and Mistral. Google's Gemma-3-12B was
the alternative and would have bought a fourth lab instead of scale. Scale won
because the small-model objection is the one a referee reaches for first.
gpt-oss cannot be used at any size: OpenAI released post-trained weights only,
with no base checkpoint to difference against.

Usage:
  python rlhf_pref_scale.py --plan            # show the schedule and exit
  python rlhf_pref_scale.py --run             # generate + analyse each step
  python rlhf_pref_scale.py --stop-after 3200 # cap the schedule
"""
import argparse
import glob
import hashlib
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "rlhf_gen")
LEGACY = os.path.join(HERE, "rlhf_gen_180")
OUT = os.path.join(HERE, "rlhf_scale_convergence.json")
CHECKPOINTS = [800, 1600, 3200, 6400]
# Per-family cap. Qwen3-30B-A3B runs ~6x slower per prompt than the dense 8B
# models -- 15s against 2-3s -- so carrying it to 6,400 would cost ~40 hours
# against ~24 for the three 8B families combined. The mixture-of-experts
# argument for including it (30B total, ~3B active, so near-8B decode cost)
# holds at batch size 1 and fails at batch 48: different sequences route to
# different experts, so the union touched per step approaches the full 30B and
# the advantage disappears. Capped at 800, which still answers "does the effect
# survive past 8B and a different architecture" at reduced precision.
# excess_at() drops any family short of the current checkpoint, so a capped
# family simply stops contributing rather than blocking anything.
FAMILY_CAP = {"qwen3_a3b": 800}
PROMPT_WORDS = 45
NEW_TOKENS = 400
SRC = ["ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl", "ca/segments_ca_en.jsonl"]
PAIRS = [
    # Llama-3.1 rather than Llama-3: 7.3M monthly downloads against 1.8M, so
    # it is the checkpoint people actually run. Costs a 64GB download.
    ("llama31", "meta-llama/Llama-3.1-8B", "meta-llama/Llama-3.1-8B-Instruct"),
    ("qwen3", "Qwen/Qwen3-8B-Base", "Qwen/Qwen3-8B"),
    ("mistral", "mistralai/Mistral-7B-v0.3", "mistralai/Mistral-7B-Instruct-v0.3"),
    # 30B at ~3B active: tests whether the effect survives 4x scale and a
    # mixture-of-experts architecture, at close to 8B decode cost. The
    # cheapest available answer to "is this a small-model artifact?"
    ("qwen3_a3b", "Qwen/Qwen3-30B-A3B-Base", "Qwen/Qwen3-30B-A3B"),
]
# Families present in the 180-token legacy run, for the length comparison.
# The others did not exist then, so the paired 180-vs-400 contrast is run on
# these two alone rather than on a changing family set.
LEGACY_FAMS = {"qwen3", "mistral"}


def build_prompt_pool(target):
    """Nested prompt list: the original 800 first, then disjoint draws."""
    existing = []
    p = os.path.join(GEN, "prompts.json")
    if os.path.exists(p):
        existing = json.load(open(p))
    have = set(existing)
    pool = []
    for path in SRC:
        fp = os.path.join(HERE, path)
        if not os.path.exists(fp):
            continue
        for line in open(fp):
            d = json.loads(line)
            if (d.get("scoreable") and not d.get("translated")
                    and d.get("orig_frac", 1.0) > 0.5
                    and d["date"] <= "2022-12-31" and d["n_words"] >= 120):
                s = " ".join(d["text"].split()[:PROMPT_WORDS])
                if s not in have:
                    pool.append(s)
            if len(pool) > 600000:
                break
    rng = random.Random(int(hashlib.sha1(b"rlhfscale").hexdigest()[:8], 16))
    rng.shuffle(pool)
    need = max(0, target - len(existing))
    if need > len(pool):
        raise SystemExit(f"only {len(existing)+len(pool)} distinct prompts "
                         f"available, need {target}")
    return existing + pool[:need]


# ---------------------------------------------------------------- analysis
def load_style():
    sys.path.insert(0, HERE)
    import rlhf_pref_analyze as A
    return A.load_style(), A


def counts_for(gens, A):
    return A.counts(gens)


def excess_at(n, A, style, rng, only=None):
    """Corrected symmetric-control excess over the first n prompts.

    `only` restricts to a set of family names, so a comparison across two
    runs can be made on the families both of them contain.
    """
    base_c, base_n = Counter(), 0
    inst_c, inst_n = Counter(), 0
    fams = 0
    for fam, _, _ in PAIRS:
        if only and fam not in only:
            continue
        bp = os.path.join(GEN, f"{fam}_base.json")
        ip = os.path.join(GEN, f"{fam}_instruct.json")
        if not (os.path.exists(bp) and os.path.exists(ip)):
            continue
        bg, ig = json.load(open(bp)), json.load(open(ip))
        if min(len(bg), len(ig)) < n:
            continue
        bg, ig = bg[:n], ig[:n]
        keep = [k for k in range(n)
                if not A.META.search(ig[k][:300])
                and not A.META.search(bg[k][:300])]
        bc, bn = A.counts([bg[k] for k in keep])
        ic, inn = A.counts([ig[k] for k in keep])
        base_c += bc; base_n += bn
        inst_c += ic; inst_n += inn
        fams += 1
    if not fams or not base_n:
        return None

    def pref(w):
        return math.log(((inst_c[w] + 0.5) / inst_n)
                        / ((base_c[w] + 0.5) / base_n))

    present = [w for w in style if base_c[w] + inst_c[w] > 0]
    allw = set(base_c) | set(inst_c)
    cand = [w for w in allw
            if len(w) >= 4 and w.isalpha() and w not in set(style)]
    byb = defaultdict(list)
    for w in cand:
        byb[int(math.log2(base_c[w] + inst_c[w] + 1))].append(w)

    def pool_for(b):
        for off in (0, 1, -1, 2, -2, 3, -3):
            if byb.get(b + off):
                return byb[b + off]
        return max(byb.values(), key=len)

    def exc(ws, reps=400):
        if len(ws) < 5:
            return None
        v = sum(pref(w) for w in ws) / len(ws)
        pl = [pool_for(int(math.log2(base_c[w] + inst_c[w] + 1))) for w in ws]
        dr = sorted(sum(pref(rng.choice(p)) for p in pl) / len(pl)
                    for _ in range(reps))
        return v - dr[reps // 2]

    strata = {}
    for lo, hi, lab in ((0, 0, "0"), (1, 4, "1-4"), (5, 19, "5-19"),
                        (20, 10 ** 9, "20+")):
        ws = [w for w in present if lo <= base_c[w] <= hi]
        strata[lab] = {"n_words": len(ws), "excess": exc(ws)}
    return {
        "prompts": n, "families": fams,
        "base_words": base_n, "instruct_words": inst_n,
        "style_words_present": len(present),
        "unmeasured": sum(1 for w in present if base_c[w] == 0),
        "well_measured": sum(1 for w in present if base_c[w] >= 20),
        "excess_pooled": exc(present),
        "excess_well_measured": strata["20+"]["excess"],
        "strata": strata,
    }


# -------------------------------------------------------------- generation
def ensure(fam, base_id, inst_id, prompts, n, batch, dry):
    """Generate so that fam_{base,instruct}.json cover the first n prompts."""
    todo = []
    for role, mid in (("base", base_id), ("instruct", inst_id)):
        path = os.path.join(GEN, f"{fam}_{role}.json")
        have = len(json.load(open(path))) if os.path.exists(path) else 0
        if have < n:
            todo.append((role, mid, path, have))
    if dry:
        for role, mid, _, have in todo:
            print(f"    {fam}/{role}: {have} -> {n}  (+{n-have})")
        return
    if not todo:
        return
    # A family whose weights are not on disk yet is skipped, not fatal. The
    # schedule is nested, so it can be backfilled later at exactly the cost it
    # would have had now -- which is what makes it safe to start a 20-hour run
    # while a licence approval or a download is still outstanding.
    from huggingface_hub import snapshot_download
    # Check for the SAME file set the download fetched. Asking for a complete
    # snapshot raises IncompleteSnapshotError on any repo that also ships
    # original/*.pth or consolidated weights we never wanted, and the family
    # then gets silently skipped with its usable weights sitting on disk.
    # That is exactly how llama3 was lost from the original run; this check
    # was written to prevent it and reproduced it.
    PATTERNS = ["*.json", "*.safetensors", "*.model", "*.txt"]
    for role, mid, _, _ in todo:
        try:
            snapshot_download(mid, token=os.environ.get("HF_TOKEN"),
                              local_files_only=True, allow_patterns=PATTERNS)
        except Exception as e:
            print(f"    {fam}: SKIPPED -- {mid} not usable locally "
                  f"({type(e).__name__})", flush=True)
            return
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    for role, mid, path, have in todo:
        print(f"    generating {fam}/{role}: {have} -> {n}", flush=True)
        tok = AutoTokenizer.from_pretrained(mid)
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        tok.padding_side = "left"
        model = AutoModelForCausalLM.from_pretrained(
            mid, dtype=torch.bfloat16, device_map="cuda")
        model.eval()
        out = json.load(open(path)) if os.path.exists(path) else []
        with torch.inference_mode():
            for i in range(have, n, batch):
                chunk = prompts[i:min(i + batch, n)]
                torch.manual_seed(1234 + i)
                enc = tok(chunk, return_tensors="pt", padding=True,
                          truncation=True, max_length=128).to("cuda")
                g = model.generate(**enc, max_new_tokens=NEW_TOKENS,
                                   do_sample=True, temperature=0.8,
                                   top_p=0.95, pad_token_id=tok.pad_token_id)
                for j in range(len(chunk)):
                    out.append(tok.decode(g[j][enc["input_ids"].shape[1]:],
                                          skip_special_tokens=True))
                if (i // batch) % 10 == 0:
                    json.dump(out, open(path, "w"))
                    print(f"      {len(out)}/{n}", flush=True)
        json.dump(out, open(path, "w"))
        print(f"      wrote {len(out)} ({sum(len(x.split()) for x in out):,} "
              f"words)", flush=True)
        del model
        torch.cuda.empty_cache()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--stop-after", type=int, default=CHECKPOINTS[-1])
    ap.add_argument("--rate", type=float, default=263.0,
                    help="measured tokens/sec, for the plan estimate")
    args = ap.parse_args()

    sched = [c for c in CHECKPOINTS if c <= args.stop_after]
    prompts = build_prompt_pool(sched[-1])
    n_orig = len(json.load(open(os.path.join(GEN, "prompts.json"))))
    print(f"prompt pool: {len(prompts)} nested prompts "
          f"(first {n_orig} are the originals, regenerated at "
          f"{NEW_TOKENS} tokens for the length comparison)\n")

    # The 180-token run is a different design, not a smaller one. Move it aside
    # so the 400-token files start clean, and keep it as the control arm.
    if not args.plan:
        os.makedirs(LEGACY, exist_ok=True)
        moved = []
        for f in glob.glob(os.path.join(GEN, "*_base.json")) + \
                glob.glob(os.path.join(GEN, "*_instruct.json")):
            base = os.path.basename(f)
            # Only the families that ACTUALLY RAN at 180 tokens may be
            # archived as the 180-token run. The original test was "does a
            # file of this name already exist in LEGACY", which is not the
            # same question: llama31 and qwen3_a3b did not exist in the 180
            # run, so on a restart their 400-token output failed the test and
            # was filed away as legacy -- deleting 4,800 prompts' worth of
            # completed generation from the live set and mislabelling it as
            # output from a different design. Recovered by hand 2026-08-13.
            if not any(base.startswith(f"{fam}_") for fam in LEGACY_FAMS):
                continue
            dst = os.path.join(LEGACY, base)
            if not os.path.exists(dst):
                os.rename(f, dst)
                moved.append(base)
        if moved:
            print(f"preserved the 180-token run in "
                  f"{os.path.basename(LEGACY)}/: {', '.join(sorted(moved))}\n")
        json.dump(prompts, open(os.path.join(GEN, "prompts_all.json"), "w"))

    if args.plan:
        # every model restarts from zero: the existing files are 180-token
        # output and move to LEGACY before the run begins
        n_models = 2 * len(PAIRS)
        print(f"all {n_models} model runs start from zero -- the existing "
              f"files are {180}-token output and move aside\n")
        print(f"{'checkpoint':>10s} {'new prompts':>12s} {'new tokens':>13s} "
              f"{'this step':>10s} {'cumulative':>11s}")
        # A3B reads 30B of weights per token even though only ~3B are
        # active, so it is priced at half the dense-8B rate rather than at
        # parity. That is a guess and the first checkpoint will replace it.
        SLOW = {"qwen3_a3b": 0.5}
        prev, cum = 0, 0.0
        for c in sched:
            newp = c - prev
            hrs = sum(2 * newp * NEW_TOKENS
                      / (args.rate * SLOW.get(f, 1.0)) / 3600
                      for f, _, _ in PAIRS)
            cum += hrs
            print(f"{c:>10d} {newp*n_models:>12,} "
                  f"{newp*n_models*NEW_TOKENS:>13,} "
                  f"{hrs:>9.1f}h {cum:>10.1f}h")
            prev = c
        print(f"\nat {args.rate} tok/s measured on Qwen3-8B-Base, batch "
              f"{args.batch}, {NEW_TOKENS} new tokens; A3B assumed 0.5x "
              f"pending measurement")
        print(f"plus {n_models} model loads and ~186GB of downloads "
              f"(Llama-3.1 pair 64GB, Qwen3-30B-A3B pair 122GB)")
        print("\nthroughput scaled with batch in testing (24 -> 183 tok/s, "
              "48 -> 263); larger")
        print("batches were not measured, so these are upper bounds on time, "
              "not lower.")
        return
    if not args.run:
        print("nothing to do; pass --plan or --run")
        return

    style, A = load_style()
    rng = random.Random(20260812)
    hist = json.load(open(OUT)) if os.path.exists(OUT) else []
    for c in sched:
        print(f"\n=== checkpoint {c} prompts ===", flush=True)
        for fam, b, i in PAIRS:
            target = min(c, FAMILY_CAP.get(fam, c))
            if target < c:
                print(f"    {fam}: capped at {target} (see FAMILY_CAP)",
                      flush=True)
            ensure(fam, b, i, prompts, target, args.batch, dry=False)
        r = excess_at(c, A, style, rng)
        if r:
            hist = [h for h in hist if h["prompts"] != c] + [r]
            hist.sort(key=lambda h: h["prompts"])
            json.dump(hist, open(OUT, "w"), indent=1)
            print(f"  -> {r['families']} families, "
                  f"{r['base_words']:,} base words; "
                  f"pooled excess {r['excess_pooled']:+.4f}; "
                  f"well-measured ({r['well_measured']} words) "
                  f"{r['excess_well_measured'] if r['excess_well_measured'] is None else format(r['excess_well_measured'],'+.4f')}; "
                  f"{r['unmeasured']} still unmeasured", flush=True)

    # 180 vs 400 on the same 800 prompts: does generation length move the
    # estimate? A shift here is a property of the instrument, not noise.
    if os.path.isdir(LEGACY) and sched and sched[0] == 800:
        globals()["GEN_SAVE"] = GEN
        try:
            globals()["GEN"] = LEGACY
            old = excess_at(800, A, style, rng, only=LEGACY_FAMS)
        finally:
            globals()["GEN"] = globals().pop("GEN_SAVE")
        new = excess_at(800, A, style, rng, only=LEGACY_FAMS)
        if old and new:
            print("\nGENERATION LENGTH, same 800 prompts:")
            print(f"  180 tokens: {old['families']} fam, "
                  f"{old['base_words']:,} base words, "
                  f"pooled {old['excess_pooled']:+.4f}, "
                  f"{old['unmeasured']} unmeasured")
            print(f"  400 tokens: {new['families']} fam, "
                  f"{new['base_words']:,} base words, "
                  f"pooled {new['excess_pooled']:+.4f}, "
                  f"{new['unmeasured']} unmeasured")
            print(f"  both restricted to {sorted(LEGACY_FAMS)} -- the only "
                  f"families the 180-token run contains")
            json.dump({"tokens_180": old, "tokens_400": new},
                      open(os.path.join(HERE, "rlhf_length_check.json"), "w"),
                      indent=1)

    print(f"\nconvergence written to {os.path.basename(OUT)}")
    print(f"{'prompts':>8s} {'fams':>5s} {'base words':>12s} "
          f"{'pooled':>9s} {'well-meas':>10s} {'unmeas':>7s}")
    for h in hist:
        wm = h["excess_well_measured"]
        print(f"{h['prompts']:>8d} {h['families']:>5d} "
              f"{h['base_words']:>12,} {h['excess_pooled']:>+9.4f} "
              f"{(format(wm,'+.4f') if wm is not None else 'n/a'):>10s} "
              f"{h['unmeasured']:>7d}")


if __name__ == "__main__":
    main()
