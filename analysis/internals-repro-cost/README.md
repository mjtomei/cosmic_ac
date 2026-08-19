# What the internals cluster cost, and what a frontier-open reproduction costs

Prompted by Matthew (2026-08-19) after the user-modeling ranking pass flagged
that every "the model knows and does not say" internals result runs on
small-to-mid open-weight models. Question: what did those experiments cost,
and what would reproducing them on a frontier open-source model cost?

`cost_model.py` — every knob a named constant; `results.txt` — output.

## Grounding (extracted from the PDFs on disk, not assumed)

Actual model ranges per paper: Burns CCS (DeBERTa/T5/RoBERTa/GPT-J ≤6B);
Azaria-Mitchell (OPT-6.7B, LLaMA2-7B); Zhu (Mistral-7B); Mirtaheri
(Llama-3.1-8B, Gemma-3); Genadi (Gemma-3-27B + one Qwen3-235B run);
Pacchiardi (LLaMA-7/30B, Vicuna-7B); **Marks-Tegmark and Parrack reach 70B**
(LLaMA-2-70B; Llama-3.3-70B) — so the ranking pass's "3B–27B" caution
slightly overstated; the accurate statement is *nothing above 70B, and
nothing frontier*. Dataset scales: hundreds to ~20k examples, tokens per
example 15–2,000.

## Method and assumptions

These papers train no models: cost = hooked forward passes (activation
collection + intervention sweeps) + negligible probe training. We estimate
final-run tokens from the papers' own dataset sizes, convert via
tokens/sec ranges for HOOKED research serving (memory-bandwidth-bound;
peak-FLOP math would overstate speed several-fold), price at mid-2026
on-demand rates (A100 $1.20/hr, H100 $2.20/hr, 8×H200 node $30/hr,
2×8×H100 $40/hr), and apply a ×5 dev multiplier (debug/iteration/abandoned
runs). Frontier targets: a DeepSeek-class 671B MoE (~37B active — cheap per
token, expensive to house) and a dense 405B. Intervention-heavy papers get
×1.7 tokens at frontier (more layers to sweep).

## Results (orders of magnitude, not quotes)

- **The original suite was nearly free.** All eight papers together:
  **~$150–$2,700 of GPU time including the ×5 dev multiplier.** Six of the
  eight land under ~$220 each even with dev; only the two 70B papers
  plausibly reached ~$0.1–1.6k. These are laptop-budget results.
- **Frontier open reproduction is cheap in compute:** the full 8-paper suite
  on a 671B-MoE ≈ **$1.5k–$25k** (single paper typically $0.2–3k); on a
  dense 405B ≈ **$4k–$68k**. The MoE's 37B active parameters make per-token
  cost comparable to a 70B dense model; what you pay for is *housing* it —
  a ≥8×H200 node ($30/hr) must be up whether you saturate it or not.

## The honest conclusion the numbers force

**Compute is not why these experiments stop at 70B.** The barriers are:
(1) *engineering* — white-box hooked serving of a 671B MoE is not supported
by the standard interpretability stacks (TransformerLens tops out far below;
you need custom vLLM/SGLang/nnsight instrumentation, i.e. weeks of skilled
labour worth far more than the GPU bill); (2) *memory floor* — the minimum
viable cluster to even load the model; (3) *access* — the actually-frontier
closed models cannot be reproduced at any price. Which is the paper's own
thesis in miniature: the gap between what is run and what could be run is
effort and access, not physics — and only OPEN frontier models make the
reproduction possible at all.

## Limits

Token counts are reconstructed from dataset descriptions, not authors'
logs (could be off ×3 either way); throughput ranges are for research-grade
hooked code, not optimized serving; the ×5 dev multiplier is a convention,
not a measurement; API-model costs (Pacchiardi's GPT-3.5 arm, Genadi's
Qwen3-235B run) excluded as negligible; researcher time — the true dominant
cost — is deliberately not priced.
