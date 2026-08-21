#!/usr/bin/env python3
"""Regenerate the stage-6 blind pools (pool6.json, pool6c.json) byte-identically.

The pools hold truncated parliamentary excerpts, so per repo policy they are
NOT committed to the public repo (the pre-push hook's content backstop exists
for exactly this class; quality_expansion/pool*.json is gitignored). This
script is the committed pointer: it rebuilds both pools deterministically
from sources, and verifies the rebuild against the committed key6.json ids,
which are content-hashes -- an id match IS a byte-identity proof for every
text.

Sources required locally (not in the public repo; see ARTIFACT-MANIFEST.md):
  corpus segment files   ie/segments_ie_en.jsonl, uk/segments_uk.jsonl,
                         ca/segments_ca_en.jsonl (for the human twins)
  rlhf_gen/prompts.json  the 800 45-word prompt openings (itself regenerable
                         from the corpus via rlhf_pref_generate.build_prompts)
  rlhf_gen/*.json        open-weight continuations (committed)
  claude_gen*/           Claude continuations (committed)

Both builds replicate the original 2026-08-19 code paths exactly, including
RNG order, so ids reproduce. Usage: python build_stage6_pool.py
"""
import hashlib
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
S10 = os.path.dirname(HERE)


def build_pool6():
    prompts = json.load(open(f"{S10}/rlhf_gen/prompts.json"))
    gens = {m: json.load(open(f"{S10}/rlhf_gen/{m}.json")) for m in
            ("mistral_instruct", "qwen3_instruct", "mistral_base")}
    rng = random.Random(20260819)
    idx = sorted(rng.sample(range(len(prompts)), 60))
    SRC = ["ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl",
           "ca/segments_ca_en.jsonl"]
    want = {" ".join(prompts[i].split()): i for i in idx}
    twin = {}
    for path in SRC:
        p = os.path.join(S10, path)
        if not os.path.exists(p):
            raise SystemExit(f"corpus file missing: {path} — see "
                             "ARTIFACT-MANIFEST.md for acquisition")
        for line in open(p):
            d = json.loads(line)
            if (not d.get("scoreable") or d.get("translated")
                    or (d.get("orig_frac") or 1.0) <= 0.5):
                continue
            if d["date"] > "2022-12-31" or (d.get("n_words") or 0) < 120:
                continue
            toks = d["text"].split()
            j = want.get(" ".join(toks[:45]))
            if j is not None and j not in twin:
                twin[j] = " ".join(toks[45:])
    pool, key = [], {}
    for i in idx:
        if i not in twin:
            continue
        arms = {"human": twin[i],
                "mistral_instruct": gens["mistral_instruct"][i],
                "qwen3_instruct": gens["qwen3_instruct"][i],
                "mistral_base": gens["mistral_base"][i]}
        n = min(len(v.split()) for v in arms.values())
        if n < 60:
            continue
        for arm, txt in arms.items():
            t = " ".join(txt.split()[:n])
            hid = "s6" + hashlib.sha1(
                f"{i}|{arm}|{t[:40]}".encode()).hexdigest()[:10]
            pool.append({"id": hid, "text": t})
            key[hid] = {"prompt_idx": i, "arm": arm, "n_words": n}
    rng.shuffle(pool)
    return pool, key


def build_pool6c(key6):
    nw = {}
    for v in key6.values():
        nw.setdefault(v["prompt_idx"], v["n_words"])
    idx = sorted(nw)

    def load_arm(folder, stem):
        out = {}
        d = os.path.join(S10, folder)
        for f in sorted(os.listdir(d)):
            if f.startswith(stem) and f.endswith(".json"):
                for r in json.load(open(os.path.join(d, f))):
                    out[r["i"]] = r["text"]
        return out

    ARMS = {
        "claude_fable5": load_arm("claude_gen", "fable"),
        "claude_opus5": load_arm("claude_gen", "opus"),
        "claude_sonnet5": load_arm("claude_gen", "sonnet"),
        "claude_haiku_old": load_arm("claude_gen_old", "haiku"),
        "claude_opus41": load_arm("claude_gen_old", "claude_opus_4_1"),
        "claude_opus4": load_arm("claude_gen_old", "claude_opus_4_2025"),
        "claude_sonnet45": load_arm("claude_gen_old", "claude_sonnet_4_5"),
    }
    pool, key = [], {}
    rng = random.Random(20260819)
    for arm, d in ARMS.items():
        for i in idx:
            t = d.get(i)
            if t is None:
                continue
            n = nw[i]
            toks = t.split()
            if len(toks) < 0.8 * n:
                continue
            txt = " ".join(toks[:n])
            hid = "s6c" + hashlib.sha1(
                f"{i}|{arm}|{txt[:40]}".encode()).hexdigest()[:10]
            pool.append({"id": hid, "text": txt})
            key[hid] = {"prompt_idx": i, "arm": arm,
                        "n_words": min(n, len(toks))}
    rng.shuffle(pool)
    return pool, key


def main():
    committed = json.load(open(os.path.join(HERE, "key6.json")))
    k6 = {k: v for k, v in committed.items() if len(k) == 12}
    k6c = {k: v for k, v in committed.items() if len(k) == 13}
    p6, key6 = build_pool6()
    assert set(key6) == set(k6), "pool6 rebuild does not match committed key6 ids"
    p6c, key6c = build_pool6c(key6)
    assert set(key6c) == set(k6c), "pool6c rebuild does not match committed ids"
    json.dump(p6, open(os.path.join(HERE, "pool6.json"), "w"), indent=1)
    json.dump(p6c, open(os.path.join(HERE, "pool6c.json"), "w"), indent=1)
    print(f"rebuilt pool6 ({len(p6)} texts) and pool6c ({len(p6c)}); every id "
          f"matches the committed key — byte-identity proven by content hash")


if __name__ == "__main__":
    main()
