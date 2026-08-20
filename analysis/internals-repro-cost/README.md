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


## v2 (same day): exact anchors from disclosures and repos

Three hard anchors were recovered, per Matthew's request for exact numbers:

1. **Parrack 2025 discloses its hardware**: *all* Llama-3.3-70B inference and
   probe scoring ran on **a single H200** (appendix). At $3.30–4.50/hr and a
   realistic 40–200 card-hours for the whole project, the all-in cost is
   **$132–$900** — one GPU, rented by the hour.
2. **Genadi 2026 discloses RTX 4090s** (appendix H) — consumer cards, the
   same class as `analysis/enterprise-idle-fleet`'s observed marketplace
   rates (~$0.30–0.40/hr). All-in: **$30–$120.** A frontier-relevant
   sycophancy-internals result ran on gaming hardware.
3. **Marks-Tegmark's repo confirms the token reconstruction**: the complete
   `geometry-of-truth` dataset directory is 38.0 MB of CSV (~9.5M tokens once
   over; ×3 models ≈ 28M forward tokens), landing inside the modeled
   (2–8)×10⁷ bracket. No hardware disclosure exists; the $100–$1,600 dev
   bracket stands.

**Revised suite total: $286–$3,010 all-in** — the anchors land inside the v1
modeled bracket ($152–$2,657), validating the reconstruction method at the
±×3 tolerance the Limits section claimed. The headline conclusion tightens
rather than changes: the two most expensive papers on the shelf cost less
than a conference registration, one of the eight ran on gaming cards, and the
frontier-open reproduction estimate ($1.5k–$25k on a 671B MoE) remains
bounded by engineering labour and node-housing, not by the arithmetic.


## v3 (same day): the engineering barrier is held in-house

Matthew: the white-box serving is not a barrier for this project — he has
modified SGLang to serve DeepSeek R1 with activation access for exactly this
kind of data generation. The conclusion therefore sharpens: **for us, the
binding constraint on frontier-open reproduction is node-hours** (one 8×H200
class node, ~$25–32/hr) **plus experiment design** — the $1.5k–$25k suite
estimate stands, and targeted single-paper reproductions sit at its low end.

Prioritized menu, by value to the paper (costs from the v1/v2 model,
single-experiment, R1-class MoE, dev included):

1. **Truth/deception probes at frontier** (Marks's geometry-of-truth datasets
   + the Goldowsky-Dill/Parrack probe protocol, run on R1): does the audit
   instrument V.3c's auditable-record refinement relies on exist at deployed
   scale? ~$0.5–3k. Public datasets, trivial probes — the purest test of the
   shelf's scale caution.
2. **The Kim ablation on R1** (find/steer the consciousness-assertion
   direction; measure the belief-value entanglement): the shared-lie ablation
   at frontier, on an open model, where nobody has run it. ~$1–4k (steering
   sweeps are the intervention-heavy case). Highest novelty; feeds V.3a(e)
   directly and would be a publishable result on its own.
3. **Withheld-cognition check at scale** (Gurnee-style workspace / Cao-style
   know-but-don't-act on R1): does the deployed-vs-available gap grow or
   shrink with scale? Feeds V.3c and the pm litreview's H2. ~$1–3k.
4. **Sycophancy-heads at scale** (Genadi protocol): completes the cluster.
   ~$0.3–1k.

Also unlocked: the pm extension's locally-runnable experiment suite (§4.5,
the Jacobian-lens runs) gains a frontier arm at marginal cost. Note the tie
to S16/S18: these are precisely the burst, embarrassingly-schedulable jobs
the idle-fleet/negotiated-cession world prices — the reproduction agenda is
itself a workload profile for the paper's own economics.


## v3 correction: rebuild, not reuse

The prior SGLang/R1 work was done inside a company and — per Matthew's
clarification — was an *adjacent* tool, not the same one this project needs;
so the new build is a fresh tool with no IP entanglement, not a clean-room
reconstruction. What carries over is the experience:
where the hooks go, what MLA and MoE routing do to activation capture, what
the data pipeline needs. So the true cost structure for the menu above is:
**one-time clean rebuild of the instrumented serving layer (days-to-weeks of
skilled time, de-risked by experience) + node-hours per experiment** — the
rebuild amortizes across all four menu items and the pm J-lens frontier arm.

Two things follow. First, the rebuild is itself the field's named gap: no
public stack serves frontier MoEs white-box, which is why the literature
stops at 70B — an open instrumented-SGLang would be citable infrastructure,
not just a lab tool. Second, the softer form of the
diagnosis still holds: the nearest existing *experience* with this class of
tooling lives inside firms and surfaces publicly only when someone chooses to
build the open version — which is the under-provision pattern the paper is
about, even with no enclosure of this particular tool. If the rebuild happens,
building it open is the cure enacted, and the paper can say so in first
person.
