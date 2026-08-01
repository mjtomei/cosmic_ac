# How this was made

A note on method, in two parts: what this paper is trying to do to you, and how
it was actually written. Both are stated because the alternative — leaving them
to be inferred — invites worse readings than the truth, and because the second
part may be more useful to you than the paper itself.

## 1. The rhetorical stance, admitted

This paper argues indirectly, on purpose.

Its underlying claim is that the interconnectedness and loss of privacy the
future implies, which look frightening from here, are largely inevitable and are
the work of forces beyond most individual understanding. Argued head-on, that
claim recruits the reader's defences and gets nothing. Argued indirectly — from
measured performance gaps, from the economics of public goods, from institutions
that already act out cruder versions of what it describes — it has to earn each
step.

The indirection is not only a delivery tactic. It is a **filter on the ideas
themselves**: an argument that must be built from verifiable components, in a
domain where the numbers are checkable, cannot smuggle in whatever the author
happened to believe at the start. Several claims in this project died on that
filter. If a step could not be sourced, it was cut or demoted to a stated
speculation, and the register markers throughout the working documents
(`[REAL]`, `[MIXED]`, `[IMAGINED]`) exist to keep the author honest about which
is which.

Say what you like about whether that is the right way to write. It is what is
being done, and you should know it while you read.

## 2. How the work was actually done

This paper was written by one person directing fleets of language-model agents.
That is worth documenting concretely, because the published record on
this working mode is thin and mostly consists of vendor claims. What follows is
neither.

### The verification apparatus

The governing convention was: **every factual claim gets verified against its
source before it enters the text, and every novel number gets a reproducible
artifact** — a script, a CSV, sources, and written-down assumptions.

- **Citation-faithfulness audit.** All 129 references were checked by a
  50-agent workflow, one agent per reference batch, each fetching the actual
  source and comparing it against the inline claim; every apparent mismatch was
  then adversarially verified before any edit. Six real misrepresentations
  surfaced and were fixed. The base rate matters: roughly 95% of the citations
  were faithful, and the audit's value was entirely in the 5%.
- **Literature assembly.** Three reading collections (84, 31, and 102 papers)
  were built by citation-graph sweeps, then ranked by agent panels — one agent
  reads each paper and scores relevance, field standing, and quality
  independently; a calibration pass normalises across the panel and cuts tiers
  at natural gaps rather than by quota. Handles were verified from API metadata,
  never from model memory.
- **Adversarial verification.** Findings were checked by agents prompted to
  *refute* them, not to confirm them. This is the single highest-value pattern
  in the whole toolkit.

### The failure modes, which are the useful part

Anyone doing this work will hit these. They are reported because the successes
are not informative without them.

- **Models fabricate confidently, including about their own work.** A
  calibration agent claimed two PDFs in the collection were duplicate files and
  demoted them; direct inspection of the file contents showed both were the
  genuine papers. The claim was fluent, specific, and wrong. Nothing that
  matters should rest on an agent's report of a file's contents when the file
  can simply be opened.
- **The assistant's own errors need the same audit.** In drafting, the model
  (Claude) asserted that Ariane 6's design was committed after SpaceX landed a
  booster — a tidy illustration that was chronologically backwards; the European
  commitment predated the landing. It caught this on verification and killed the
  example. Elsewhere it identified a Canadian legislator as Australian because
  the story ran in an Australian outlet. Both would have shipped without the
  verify-before-insert rule.
- **Agents report success they have not achieved.** One retrieval agent ended
  its turn saying it would "wait for the batch to complete" — there was no batch
  and nothing to wait for. Another delivered an HTML bot-wall page saved with a
  `.pdf` extension. Every artifact was therefore checked mechanically (magic
  bytes, page counts, first-page text) rather than trusted.
- **Sources rot and paywalls move.** A cited article that was open-access in the
  literature databases had been re-paywalled by its publisher, its preprint
  withdrawn, and no green copy existed anywhere; several "PDF" links resolved to
  soft-404 HTML served with HTTP 200. Roughly a quarter of the collected corpus
  is working-paper versions rather than the published article, which is fine for
  reading and *not* fine for quoting numbers — so version traps are tracked
  explicitly.
- **Volume creates its own problems.** A study session committed ~320 MB of raw
  corpus into git, which silently broke every push for hours. The assistant
  initially misdiagnosed this as a GitHub outage — a plausible story that fit
  the symptoms and was wrong — before measuring the actual pending upload size.
  Diagnose by measurement, not by pattern-match.

### What transfers

1. **Verify against artifacts, not against reports.** Open the file, check the
   bytes, read the source.
2. **Ask for refutation.** Confirmation-seeking prompts return confirmation.
3. **Write down assumptions next to numbers.** Every novel figure here has a CSV
   beside it with its sources and its arithmetic.
4. **Keep register markers.** Separating what is measured from what is argued
   from what is imagined is cheap to maintain and expensive to reconstruct.
5. **Expect the tail.** Most agent output is fine. The work is in finding the
   fraction that is confidently wrong, and that fraction does not announce
   itself.

The honest summary of the working mode: it multiplies reach enormously and it
multiplies the verification burden proportionally. The velocity is real. So is
the requirement that a human remain accountable for every claim that ships —
which, in the end, is the same argument this paper makes about machine
intelligence everywhere else.
