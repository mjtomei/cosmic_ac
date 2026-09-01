# Review round 2 — design spec

The next review round, incorporating the model panel and a writing-quality
pass. Prose-first (Matthew wants the automated quality work done before his
own read), whole paper. This file is the spec; the workflow script and the
per-model agent definitions are built from it.

## The panel — frontier model per lab (7)

| lab | routed model token | notes |
|---|---|---|
| Anthropic | `work/claude-fable-5` | Fable 5.1 on the **work** account, so its calls do not contend with the primary account the orchestrator runs on |
| OpenAI | `chatgpt/gpt-5.6-sol-high` | high-effort variant |
| Google | `google/gemini-3.1-pro-preview` | |
| xAI | `x-ai/grok-4.6` | |
| Moonshot | `moonshotai/kimi-k3` | |
| Alibaba | `qwen/qwen3.8-max` | max tier (not the flash variants) |
| DeepSeek | `deepseek/deepseek-v4-pro` | pro tier |

Excluded per "frontier only": GLM (only `glm-5.3-flash` is routed), the
local vLLM Qwen 3.6 / 3.8-27B (below `qwen3.8-max`), and the low/mid GPT
and Qwen-flash variants. The orchestrator (Fable 5, primary account) runs
the harness and does no proposing or voting.

## Orchestration

Native **Workflow tool, driven from a `claude-mixed` session** — NOT a
Python harness shelling `claude-mixed -p` (that was only feasibility
probing). Each panel member is a **custom agent definition**
(`.claude/agents/panel-<lab>.md`) whose `model:` frontmatter is the routed
token above; under a claude-mixed session the local router dispatches each
to its backend. (The router's work-token is documented as existing "for
workflow workers only" — this is its intended use.) The workflow script
holds the provenance map and enforces blinding and self-exclusion; agents
never see authorship.

## Track B — writing quality (runs first)

### Generation members — reference-primed Fable 5.1 (propose-only)

In addition to the 7 review-panel members, two **generation members**:
both Fable 5.1, each primed with a specific craft reference, contributing
proposals only (they do not vote).

- **Prose generator** — Fable 5.1 + `writing_refs/gopen_swan_principles.md`
  (distilled from the fetched Gopen & Swan article) + the house voice memory
  (`writing-voice-challenge-not-apology`) + Williams/Pinker clarity
  principles from weights. Proposes prose and flow changes.
- **Data-presentation generator** — Fable 5.1 +
  `dataviz_refs/data_presentation_principles.md` + the loadable `dataviz`
  skill. Proposes table/figure/number-presentation changes.

**On the canonical texts (the honest state):** we do NOT have the primary
books on disk (Tufte, Cleveland, Williams, Few, Pinker). The workaround,
built here: (a) Gopen & Swan fetched and distilled (`writing_refs/`);
(b) the free downstream canon — Wilke's *Fundamentals of Data
Visualization* (fetched/distilled) and Healy's *Data Visualization* (both
full books, free online), plus Cleveland–McGill's graphical-perception
ranking via the open Heer–Bostock replication — distilled into
`dataviz_refs/`; (c) the models' in-weights knowledge of the full canon;
(d) the bundled `dataviz` skill. The generators are primed with the briefs,
not with reproduced copyrighted text.

**Self-exclusion (accepted, Matthew 2026-09-01):** the generators are
Fable 5.1 and the Anthropic *voting* seat is also Fable 5.1, so — per "no
model votes on its own proposal" — **every Fable instance is excluded from
voting on any Fable-authored candidate.** Consequence, accepted: candidates
that originate from the Fable generators (or the Anthropic seat) are judged
by the 6 non-Anthropic labs. The provenance map enforces this at dispatch;
the Anthropic Fable seat still votes on all non-Fable candidates.

### Stage 1 — Propose (one holistic ask per panel member)
Not per subsection. Each of the 7 models sees the **whole paper** + the
voice guide (confident and plain; no defensive hedging or self-
congratulation; keep substantive caveats; build on published work;
preserve Matthew's verbatim wording) + the **faithfulness constraint** (a
change may not alter any number, add any claim, or soften any hedge).
Each returns a structured changelist; every entry:

    { id, type: structural|prose, locus (section/anchor),
      action: reorder|merge|split|move|rewrite,
      proposed_text_or_move, rationale }

7 review-member calls + 2 generation-member calls, all into the same pool. (Fallback if a whole-paper ask overflows a model's context: one
ask per top-level section or group of related sections — ~8, not 40.)

### Stage 2 — Aggregate & mix (blind, de-authored)
The proposals are pooled and **stripped of authorship**. Deterministic
clustering by (locus, action) groups near-duplicate proposals, so
"5 of 7 want to merge §X into §Y" becomes one candidate with a support
count. Where several models rewrote the same locus, an **aggregator**
(the orchestrator, neutral) **mixes** them into 1–3 de-authored candidate
variants per locus. A **provenance map** (candidate → contributing models)
is kept out of band — used only to exclude authors from voting and for
later analysis, never shown to voters. Output: one anonymized ballot of
distinct candidate changes.

### Stage 3 — Vote (blind, no self-vote, multi-factor)
Each candidate is scored only by the panel members who did **not** propose
or co-author it (self-exclusion via the provenance map), blind to
authorship. Each voter returns a **multi-factor** ballot, not just a
keep/discard:

- `faithfulness` — hard gate: does it change a claim/number/hedge? (fail = discard regardless of the rest)
- `clarity` — reader comprehension improvement
- `voice` — match to the house voice; blandification penalized
- `concision`
- `structural_soundness` (for structural candidates)
- `keep` — the final keep/discard call

The multi-factor scores let ties (split keep vote) break on the composite,
and preserve the full record for later analysis of the panel process
(which factors drove decisions, per-factor agreement, per-model tendencies).

### Stage 4 — Synthesize & gate
A candidate is accepted if it clears the faithfulness gate AND wins its
keep vote among eligible voters; ties break on the factor composite.
Accepted changes are synthesized into (a) a proposed **reorganization
plan** (structural) and (b) per-locus **diffs** (prose), each carrying its
vote and factor record. **Nothing is auto-applied** — Matthew gates every
change; structural reorg is gated before any prose diff that depends on it.

### Captured artifacts (for later panel analysis)
`panel_proposals.json` (all raw proposals), `panel_ballot.json` (the
de-authored candidate set + provenance map), `panel_votes.json` (every
voter's multi-factor ballot), and the human-facing `REWRITES-round2/`
(diffs + tallies).

## Track A — correctness & gaps (runs after the prose gate)
The blind review descendant, same 13 dimensions, now multi-model: each
dimension reviewed by every panel member independently; a finding raised
by ≥2 is corroborated, singletons go to adversarial refutation by a
different member; seeded with the current 104 open findings to
confirm/close/supersede against the (possibly reorganized) draft. Same
multi-factor, no-self-vote machinery where it applies. Deferred here so
prose/structure settle first.

## Cost & rollout
Track B propose is 7 calls; vote is bounded by (distinct candidates ×
eligible voters). Far cheaper than the per-subsection design. Still
metered (OpenRouter credits, ChatGPT sub), so: build the agents + script,
**run a pilot first** — a single holistic round on one section-group to
verify (a) external routing through the workflow agents actually works
[the one unverified linchpin], (b) proposal quality, (c) the blind
self-excluded multi-factor vote — then green-light the full paper run.
