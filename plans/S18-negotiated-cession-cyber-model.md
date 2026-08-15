# S18 (candidate) — The negotiated-cession regime: extending the Fable–Carson cyber-cost model

**Status:** candidate, not committed. Written 2026-08-15 so a fresh session can
execute without this session's context. Matthew decides whether it runs.

## Handoff — start here (for the fresh session)

You are executing this plan in `/home/matt/performance_commons`. CLAUDE.md
loads automatically and its conventions bind; this file is the study brief.
Everything below "The question" is the brief; this section is logistics.

**Set up (15 minutes):**
1. Clone the model fresh — the prior session's copy was in a session-scratch
   dir that no longer exists:
   `git clone --depth 1 https://github.com/bradrcarson/cowen-cyber` into your
   own scratchpad (NOT into this repo). Fallback: Zenodo archive
   `https://zenodo.org/api/records/21879325/files/cowen-cyber-archive.zip/content`.
2. The paper PDF is at
   `~/reading/security-economics/fable-carson-2026-cyber-costs.pdf` (35 pp;
   text extracts cleanly). Read §4 (model) and DECISIONS.md before touching
   code.
3. `sim/run.py` has a `python3.12` shebang — check the interpreter exists;
   full sealed run is "minutes, not weeks" (10⁴ outer × 10⁴ inner);
   `--n-outer 500 --n-inner 500` for iteration; `--skip-tornado` to skip
   sensitivity reruns.
4. S16's artifacts (the rent side) are tracked in
   `analysis/enterprise-idle-fleet/` — read its README first;
   `profit_per_machine.py` and `actuarial_model.py` are the two you will join
   against.

**Findings already verified by the prior session — reuse, do not re-derive:**
- Defense in their model is a per-regime severity-truncation haircut only;
  the config notes state "the placeholder detection/patch/containment
  machinery is removed." (Quote it from `config/params.json` notes directly.)
- Offense-side autonomy IS modeled: S3b "fresh agentic event tree"
  (8 params, `parameter_sheet.md` §S3b), autonomous campaigns/yr, agentic
  self-propagation as common-shock factors.
- Their own prior-sensitivity output ships in `out/tornado.csv`; the paper
  states median ≈ insensitive to regime weights, mean/P99/exceedance ∝
  offense-dominant weight (sealed weights 30/45/25).
- Parameters are sealed for 2026–2028 only; 2028 rate "held at 2027 level
  (no sealed growth)". Any horizon extension is OUR construction — label it.
- Headline to reproduce as sanity check: median AI-added ≈ $116B/yr by 2028,
  mean ≈ $262B, P(>$200B) ≈ 39%, caps $250B/event and $3.5T/yr.

**Where the results go:**
- Code + CSVs + README → `analysis/negotiated-cession/` (every novel number
  with sources and assumptions, per convention).
- Proposed paper text → `plans/S18-proposed-text.md`, STAGED ONLY — do not
  edit `outline-cosmic-ac.md` or the paper; Matthew decides (S17 precedent).
  The outline anchor points you are feeding: III.3's Fable & Carson block
  (committed 2d07b76) and III.2's federation/Omerta material; read both
  before writing so the staged text lands in their vocabulary.
- Add a dated entry to `studies-and-work-log.md` only if Matthew commits S18.

**Boundaries:**
- Commit locally with the repo's commit style; **do not push** — the repo is
  public and publishing batches is Matthew's call.
- A parallel S10 session may have uncommitted files in `analysis/s10/` and
  the worktree generally — never `git add -A` from the repo root blindly;
  add your own paths explicitly. Do not rewrite history.
- Do not touch the reading directories' pending download list — that thread
  stays with Matthew in the prior session.
- Do not contact the paper's authors or file issues on their repo.
- Subagents: default session model; use `model: 'opus'` for ranking/judgment
  stages of any workflow (see memory note `subagents-on-opus-not-fable`).
- Honest-limits section is mandatory in the writeup; the weakest link is
  named in the brief (our cession-lowers-losses channel enters through a
  severity-truncation parameter we choose ourselves — say so plainly).

## The question (Matthew, 2026-08-10/15)

What would have to happen in the Fable–Carson model for something like III.3's
prediction to come true? Specifically: **what has to be true for it to be
economically and personally beneficial for a human or company to cede control
of their own compute in certain negotiated cases — to where the meaning of
malware, compromise, and ownership changes? And how does that change the
model?**

## What is already in hand (do not redo)

- **The model + code**: github.com/bradrcarson/cowen-cyber (public; also
  Zenodo archive 10.5281/zenodo.21879325, PDF at
  `~/reading/security-economics/fable-carson-2026-cyber-costs.pdf`). Cloned
  once already; structure: `sim/{run,engine,counterfactual,outputs}.py`,
  `config/params.json` (sealed), `DECISIONS.md` (D-01–D-15),
  `parameter_sheet.md`, `out/results.json` + `out/tornado.csv` (their own
  prior-sensitivity output), full working transcripts.
- **Q2 (prior sensitivity) is ~answered**: tornado.csv ships in the repo; the
  paper states median ≈ insensitive to regime weights, mean/P99/exceedance ∝
  offense-dominant weight. Just read/plot their tornado output; a small
  regime-weight grid rerun (`run.py --n-outer 500 --n-inner 500`) if a figure
  is wanted.
- **Q3 (swarms/autonomy) is answered by inspection**: offense side modeled
  (S3b "fresh agentic event tree", 8 params, anchored to HF/Anthropic
  postmortems; autonomous campaigns/yr; agentic self-propagation as
  common-shock factors). **Defense side is a per-regime severity-truncation
  haircut ONLY** — config notes: "the placeholder detection/patch/containment
  machinery is removed." Continuous autonomous defense structurally cannot
  appear in this model except as a regime label. This is the sharp form of
  Matthew's objection and should open the study's writeup + go into III.3's
  citation caveats.
- **Q1 (extended horizon)**: parameters sealed for 2026–2028 only (2028 rate
  "held at 2027 level (no sealed growth)"). Any extension is OUR construction
  — label it so. Low value standalone; do it only as the baseline arm of the
  Q4 comparison (roll the sealed dynamics to ~2032 under stated assumptions).
- **The rent side of the inequality**: S16's
  `analysis/enterprise-idle-fleet/` — `profit_per_machine.py`,
  `actuarial_model.py` (freq×sev, Böhme-Kataria correlation, four isolation
  architectures Case 1–4), `insurance_sensitivity.py`, OBS_RATE = 0.00218
  $/TFLOPS-hr observed. Case-4 (purpose-built silicon) premium ≈ $0.11/machine-yr
  at severity $83k, P_M=1e-3, idx 9e-4.

## The study

**Claim to test/model:** ceding negotiated control of one's compute becomes
individually rational when
  E[rent from ceded compute] + Δ(defense cost avoided) + insurance transfer
  > E[residual loss under negotiated access],
and at that crossover the categories malware/compromise/ownership are
redefined (unauthorized→unnegotiated; compromise→breach-of-contract;
ownership→residual control rights over a negotiated bundle).

**Method sketch:**
1. Reproduce their headline (sanity: median ~$116B, mean ~$262B, 39% > $200B).
2. Add a fourth regime to the mixture — "negotiated cession" — expressed in
   their own parameter vocabulary: (a) attack-surface term falls as negotiated
   access replaces exploitation (their monoculture-surface and
   campaigns/yr knobs); (b) defense spend (Ch1) partially converts to rent
   income (S16's per-machine profit gives the rate); (c) severity truncation
   rises (isolation architectures bound blast radius — S16 Case 2–4);
   (d) a new transfer category: negotiated payments are NOT losses (their
   60/40 real-loss/transfer split shifts). Document every added parameter
   with source + assumption per the analysis/ convention.
3. Solve for the crossover: what rent rate, residual-risk level, and insurance
   price make cession beat defense for (i) an enterprise fleet (S16 mid/high
   config), (ii) a household. Compare against OBS_RATE and S16 premiums —
   the join of our two artifacts is the novel number.
4. Baseline arm: their sealed dynamics rolled to ~2032 (labeled ours);
   cession arm: same horizon with the regime phased in; report the wedge.
5. Writeup: `analysis/negotiated-cession/` (code + CSVs + README), proposed
   text staged for III.2/III.3 — outline untouched, Matthew decides (S17
   precedent).

**Literature to anchor (verify handles before citing; run as a small sweep):**
- Grossman & Hart 1986 / Hart & Moore 1990 — ownership as residual control
  rights: THE frame for "what ownership means when control is ceded."
- Coase 1960 — negotiated externalities; already in the paper's orbit
  (Dixit-Olson 2000 on disk for the failure case).
- Bug-bounty / vulnerability-market economics (e.g., Finifter-Akhawe-Wagner
  2013; HackerOne-era studies) — negotiated intrusion at small scale, priced.
- Coordinated vulnerability disclosure / safe-harbor (DOJ CFAA policy 2022) —
  the legal redefinition of "unauthorized" already underway.
- Botnet/underground economics (Anderson et al. "Measuring the Cost of
  Cybercrime" 2013/2019) — the unnegotiated market being displaced.
- Böhme & Kataria (already used in S16), cyber-insurance moral hazard.
- III.2's precedent set (BOINC/Lambda federation) and Omerta's economic
  anchors ($0.08 vs $0.50/hr) — internal.

**Conventions that bind:** every novel number gets analysis/ code+CSV with
sources and assumptions; extensions labeled ours, never theirs; build on
published work, no novelty claims; honest-limits section mandatory (their
model's defense-as-haircut means our "cession lowers losses" channel enters
through severity truncation we parameterize — the weakest link, say so).

**Not in scope:** re-litigating their sealed 2028 forecast; any claim about
their scoring; Q1 as a standalone product.
