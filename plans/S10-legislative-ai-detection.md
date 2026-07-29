# S10 — AI-generated text in legislative transcripts: session plan

**Self-contained starting point for a fresh session.** Everything needed to
execute is here; background context is in `../studies-and-work-log.md` (S10) and
`../outline-cosmic-ac.md` (V.3, "the office is a socket").

## Why

Measure what share of legislative speech is machine-generated, and how it has
moved since late 2022. For the paper this converts an anecdote — a member
reading a model's framing sentence aloud in the New Brunswick assembly — into a
measured trend, and it is the strongest candidate for an original empirical
figure. It is also cheap enough to stand alone as a short paper.

## Where things stand

- **Corpus on hand:** 38 sittings of NB's 61st Legislature, 2nd Session
  (Oct 2025 – May 2026). Index at `../analysis/hansard-nb/nb-hansard-index.json`
  as `[date, PDF URL]` pairs; ~39 MB; re-download with any HTTP client.
  Measured: **1,604,993 words bilingual, ≈802k English-only** (English and
  French run in parallel — split them before scoring).
- **Not yet public:** the sitting containing the Bill Oliver speech. NB's
  published Hansard stops at 2026-05-14; Bills 46/47 (Energy Sector Consumer
  Advocate Act) were introduced 2026-05-26. Unlisted transcripts come from the
  Hansard Office (leghaninfo@legnb.ca, 506-453-2531) — **worth requesting early,
  it is the study's origin document.**
- **Estimator settled** (details in S10): sample-and-correct, not corpus
  modelling. Liang et al. is dropped from the plan and kept as a reference.

## The design in one paragraph

Score segments with a detector; treat the flag rate `π̂ = k/n` as a binomial
proportion; correct for the detector's own error with Rogan–Gladen,
`τ̂ = (π̂ + Sp − 1)/(Se + Sp − 1)`. Measure both nuisance parameters **in-domain**
rather than trusting published accuracy: pre-2022 sittings give `1 − Sp`
directly, and known-AI legislative speech (prompt a model with the real bill text
and speaking role) gives `Se`. Free local detectors run over the *whole* corpus
and serve as the stratifier for a small paid Pangram sample — two-phase sampling,
where the free detector need only be *correlated* with truth, not accurate, to
cut the paid estimate's variance. Cluster by speech, not by segment.

---

## Task 1 — Survey current detectors, then pick one

Do this first and with fresh eyes: **the field moves fast and our shortlist is
from 2024.** Verify what is current before building on it.

Known-good baseline (all verified to exist, 2026-07-28):
- **Binoculars** — Hans, Schwarzschild, Cherepanova et al., arXiv:2401.12070.
  Zero-shot; contrasts two closely related models (an "observer" and a
  "performer"); no training. Default choice unless something better has landed.
- **Fast-DetectGPT** — Bao, Zhao, Teng et al., arXiv:2310.05130. Conditional
  probability curvature; cheap successor to DetectGPT.
- **Ghostbuster** — Verma, Fleisig, Tomlin et al., arXiv:2305.15047. Features
  from weaker models; no token-probability access to the target model needed.

Search for anything newer (2025–26), and specifically for **detector evaluations
on non-essay registers** — every one of the above was validated on essays and
news, mostly against 2023–24 models. Legislative oratory is a different register
and 2026 models are harder to detect, so treat published accuracy as
uncalibrated for our domain. That is exactly why we measure `Se`/`Sp` ourselves.

## Task 2 — Pilot on the NB corpus

1. Extract text per sitting; **split English from French** (parallel columns —
   confirm the split is clean, it is the most likely silent error).
2. Segment by speech, retaining: date, chamber, speaker, party, and whether the
   passage reads as prepared remarks or spontaneous debate. Keep speech IDs —
   they are the clustering unit later.
3. Score with the chosen detector. **Measure throughput while doing it** (Task 4).
4. Report the raw flag-rate distribution and eyeball the extremes. At this stage
   the number is uncorrected and not yet meaningful — the point is to shake out
   the pipeline and get a real tokens/second figure.
5. Run the **Tier-1 prompt-leakage regex** over the full corpus in parallel:
   assistant framing ("Here's a…", "Certainly, here is…", "I hope this helps"),
   instruction echoes ("in a professional tone", "as requested", "a more natural
   flowing version"), self-identification, unfilled placeholders ("[Your Name]"),
   markdown surviving into the record. Every hit is individually verifiable and
   quotable — this is the hard floor, and it costs nothing.

## Task 3 — Find every usable corpus

Goal: a table of sources with coverage dates, format, size, and access method.
**Requirement: must span pre- and post-2022**, or it cannot support the control.

Leads to verify (from memory — search budget was exhausted when this was
written, so confirm each exists and check licensing):
- **ParlaMint** (CLARIN) — standardised multilingual parliamentary corpora in
  TEI XML across many European parliaments, built for exactly this kind of
  analysis. If it is what I recall, this is the single highest-value find.
- **LiPaD** — Linked Parliamentary Data, Canadian federal Hansard, digitised and
  structured.
- **UK**: hansard.parliament.uk; mySociety's parlparse / TheyWorkForYou XML.
- **Australia**: aph.gov.au Hansard; OpenAustralia.
- **US**: GovInfo bulk data (Congressional Record); Open States API for state
  legislatures.
- **Ireland**: Oireachtas API. **New Zealand**: parliament.nz Hansard.
- **Canadian provinces**: each publishes separately, mostly PDF (NB is the
  pattern we have).
- **EU Parliament** verbatim reports.

Note per source: machine-readable (XML/JSON) vs PDF-only, since PDF extraction
and speaker attribution is most of the work. Prefer structured sources.

## Task 4 — Throughput and batching

The deliverable is an estimate of wall-clock time to score everything found in
Task 3. **Measure, do not guess.**

Environment: **NVIDIA GB10**, 119 GB RAM, Ubuntu 24.04, Python 3.12.
`torch` is **not installed**. A Playwright venv exists at `~/.venvs/pw` (for
JS-rendered pages); `yt-dlp` is at `~/.local/bin/yt-dlp`.

Throughput notes:
- Detection is **forward-pass only** — no generation, no KV-cache growth — so it
  is far cheaper per token than inference and batches well.
- Sort segments by token length before batching to minimise padding waste; this
  alone is often a large win.
- Use `torch.inference_mode()`, bf16, and flash/SDPA attention if available.
- Binoculars needs **two** models resident; budget memory for both, and consider
  scoring in two passes (all segments through the observer, then the performer)
  to avoid thrashing if memory is tight.
- Sweep batch size and sequence length to find the throughput knee; record
  tokens/second and extrapolate to the Task-3 corpus sizes.
- Scale check: one NB session ≈ 2M tokens bilingual. A 200M-word multi-legislature
  corpus is ~260M tokens — at 5k tok/s that is ~14 hours, at 50k tok/s ~1.5
  hours. The pilot's job is to find which end of that range we are on.

---

## Deliverables

1. `analysis/s10/` with the extraction and scoring pipeline, and a CSV of scored
   segments (speech ID, date, chamber, speaker, detector score, regex hits).
2. A corpus table from Task 3: source, coverage, format, size, access.
3. A measured throughput figure and a projected wall-clock for the full sweep.
4. A short memo: does the pilot justify the full study, and at what sample size
   for the paid tier?

## Open decisions for that session

- Which detector, after the survey.
- Segment unit: whole speech, paragraph, or fixed window. Affects both clustering
  and the detectors, several of which have length sensitivities.
- Which model generates the `Se` reference corpus. It should plausibly be one
  legislative staff were using in the period studied — a 2026 frontier model's
  fingerprint is not a 2023 model's, and choosing wrong biases `Se` in a
  direction that is awkward to argue about afterwards.
- Whether to request the Bill Oliver sitting from the Hansard Office now.

## Do not

- Do not report a raw flag rate as an AI rate. The correction is the study.
- Do not skip the pre-2022 control. It is not a sanity check; it is the estimate
  of `1 − Sp` that the whole result depends on.
- Do not pick a segment vocabulary, threshold, or detector by which one gives the
  largest number. Select on stability against the control.
- Do not conflate "AI-generated" with "not written by the speaker". Prepared
  speeches have always been staff-drafted; only the machine-drafting claim is
  being measured, and the paper's argument (V.3) actually depends on that
  distinction rather than being damaged by it.
