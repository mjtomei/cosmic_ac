# S20 — The search for the register itself

*Planned 2026-08-18 (Matthew + Claude). Self-contained: a fresh session can
execute from this file. Status: PLANNED, not yet started. Prerequisite
artifacts all exist and are named below.*

## The question

S10 measured everything against ONE register: the Kobak-style excess-word
list, built from the machine-adoption time contrast. The occupational study
then showed that identifiers explain that index — cohort, class II, the
insulation delta — and its §5 calibration notes the consequence of a thin
probe: every correlation is a floor, attenuated by whatever the single index
misses.

S20 inverts the direction of search. **The register is the object, not the
instrument.** For each identifier, find the word set that carries its effect
— searched over the full vocabulary, not decomposed from the existing list
(Matthew: "it doesn't just have to be a decomposition of the existing
register, but could be a search over all possible subsets of words"). Then
measure the overlap structure: how much of the class register is the
insulation register; how much of each is the register of LLM-generated
speech, derived by the same methodology.

## Identifiers, fixed in advance

    period       words spoken 2023+ vs before (the adoption wave; the
                 original Kobak contrast, re-run inside this framework as
                 the anchor and positive control)
    cohort       birth decade, on the ERA-RESTRICTED outcome (2025-26),
                 because the career outcome mixes period into cohort
    class        EGP II vs the rest (the spiking category), with the full
                 block as a secondary coding
    insulation   the apex delta (registered, covariate-robust)
    machine      LLM-generated vs matched human text (see below)

Education is excluded (spent once class is present — S10 stage 2); adding
identifiers post hoc is not allowed.

## Data object

Member × word sparse matrix from the segment files (the 2.9 GB corpus;
two-pass build in the style of `long_trend_bootstrap.py`). Word inclusion
floors, fixed: alphabetic, lowercased; appears in ≥ 8 of 22 chambers and
≥ 200 members; per-member rates per 1,000 words; **each word's member-rate
z-scored within chamber** (the chamber confound — procedural vocabulary
differs by chamber exactly as covariates do — dies here or nowhere).
Expected vocabulary after floors: tens of thousands. No GPU needed for the
matrix or the searches; CPU-hours, not days.

## Three method tiers, each with its guard

**Tier 1 — per-word screen (the Kobak method, generalized).** For each word,
the member-level association with each identifier; Benjamini-Hochberg across
the vocabulary; R_screen(g) = signed survivors. Guard: chambers are split
once into discovery and validation halves (stratified by tier/size, split
fixed by seed before any pass); survivor lists are FROZEN on discovery
chambers and their replication rate reported on validation chambers.

**Tier 2 — stability selection.** Elastic-net predicting the identifier from
word rates, re-fit over many member resamples and grouped chamber holdouts;
report per-word SELECTION FREQUENCIES, never one fit's chosen set (S10 item
25's constraint: regularized regression picks one member of a correlated
cluster arbitrarily, and which one is not a finding).

**Tier 3 — subset optimization, which is what "all possible subsets"
honestly becomes.** 2^V is unsearchable and a raw optimum is a guaranteed
overfit, so: greedy-plus-annealing search maximizing the cross-validated
association between the identifier and the subset's rate index, run ONLY on
discovery chambers; the found subset frozen and validated once on the held
half. The search's own null: shuffle the identifier across members within
chamber and RE-RUN THE ENTIRE SEARCH, ~200 times — the null distribution of
the *optimized* statistic, which is the only fair comparison for an
optimized statistic. Report observed-minus-null, not observed.

## The overlap structure (the finding)

- **Effect-vector correlations** between identifiers over the full
  vocabulary (threshold-free; the primary overlap statistic), plus Jaccard
  on the frozen tier-1 lists (interpretable; threshold-dependent, labelled).
- **A shared core**: the first principal component of the per-word effect
  vectors — is there ONE register with identifier-specific weights, or
  several? — with each identifier's residual register after removing it.
- **Topic vs style**: occupations talk about different things, so content
  words will load topically. Report every register split into
  function/style words vs content words; a register that survives on its
  style half is a register, one that lives on its content half is a topic.

## The machine register, same methodology

Generate a matched machine corpus: prompt a panel of models spanning
vintages (local open weights on the GB10 for the older ones, API for
frontier) with real debate contexts — same chambers, same topics from the
order papers, same length distribution. Per-word excess vs the matched human
baseline = R(machine), the Kobak construction with a same-domain contrast
instead of a time contrast. Then the punchline measurements: the overlap of
R(machine) with each covariate register — **how much of the class and
insulation registers IS the machine register, and what residue is purely
human-drone**. A mini pre-registration fixes the confirmatory overlap
predictions before this leg runs (candidate, to be argued then: insulation
overlaps machine more than class does).

## Hazards, named now

- **Circularity**: the S10 outcome z is BUILT from the Kobak list. No S20
  validation may target that index; the validation target is always the
  identifier. The period identifier re-derives the adoption register from
  scratch as the positive control — if tier 1 on `period` does not
  substantially recover the known list, the pipeline is broken, and that
  check runs first.
- **Forking paths**: all discovery/validation splits, floors, identifier
  codings and tier definitions are fixed in this plan; deviations get dated
  amendments, S10-style.
- **The delta is itself derived** (from O*NET, not from speech), so
  R(insulation) is clean of lexical circularity; class and cohort likewise.

## Deliverables

Per-identifier word lists + full effect vectors (committed artifacts);
the overlap matrix and shared-core decomposition; R(machine) and its
overlaps; and revised register indices per identifier — the better probes
that item 26 (signaling-drag) and item 27 (the monitor) need, and the
direct answer to attenuation in S10 §5's calibration.

## Order of execution

1. Matrix build + floors + within-chamber z (commit the builder).
2. Tier 1 on `period` — the positive control gate.
3. Tier 1 on the remaining identifiers; freeze lists; validation pass.
4. Tier 2 frequencies; tier 3 on discovery halves + permutation nulls.
5. Overlap structure + shared core.
6. Machine-corpus generation; R(machine); mini-prereg; overlap punchline.
