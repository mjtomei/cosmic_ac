# Transcription methodology — scans/OCR → readable, citable markdown

Canonical rules for turning a scanned primary source (a book, a case report)
into a markdown edition that reads cleanly and cites safely. Proven on
*Dartmouth v. Woodward* (199 pp, 2026-08-24 → 09-04) and *The King's Two
Bodies* (632 pp, 2026-09-04 → 09-06). Sibling of `00-FETCH-METHODOLOGY.md`;
workflow scripts live in `.claude/workflows/transcription/`.

## The flow, in order

**0. Substrate choice.** Prefer an existing digitization over fresh OCR when a
legitimate one exists (Dartmouth: Caselaw Access Project's `static.case.law`
— structured HTML with page labels and tagged footnotes, public domain).
Otherwise use the scan's own embedded text layer (KTB: ABBYY). Do NOT plan on
wholesale vision-model transcription through the API: **bulk verbatim
reproduction of scanned book pages trips the output content filter** even on
public-domain text (all 8 agents blocked, 2026-08-24). Small surgical diffs
never trip it — the whole flow below is built on that fact.

**1. Script extraction (deterministic, no model).** Build the markdown by
script:
- **Page anchors:** printed page breaks inline as `[*N*]`, complete and
  gap-checked. This is what makes the edition citable; the scan stays the
  quotation authority.
- **Body/footnote/running-head separation by font size** via
  `pdftohtml -xml` (KTB: body 12pt, notes 11pt, heads ≤10pt at top). GOTCHA:
  pdftohtml declares fontspecs **cumulatively across a page range** — collect
  the font table from the whole batch, not per page, or most pages classify
  everything as body.
- **Headings from the PDF outline** when present (KTB's carried every
  chapter/section with its page — check before hand-building structure).
- **Footnotes collected in a `## Notes` section at the end**, keyed by
  printed page (`fn<page><letter>` for lettered notes; `**[p. N]**` blocks
  for numbered). NEVER inline definitions mid-text — that was v1's mistake
  and the main readability complaint. Pair marks to notes by
  (printed page, letter/number), not by the source's own link structure
  (CAP's hrefs sent 124 marks at 8 targets).
- **Deterministic cleanup before any model runs:** soft-hyphen line breaks,
  hyphenation rejoins, spacing collapse (2,136 fixes in KTB for free).
- One paragraph per line; newlines only at paragraph breaks.

**2. In-place LLM smoothing (the Opus workflow).** Chunk by printed-page
ranges (~14–27 pp/agent; give the Notes section its own agents on a
footnote-heavy book). Each agent edits **in place with small
old_string/new_string Edit calls — never rewrites paragraphs, never Writes
the file**. That discipline is what makes the pass filter-safe, concurrent
(agents share the file; stale-Edit → re-read, retry once, else skip), and
**idempotently resumable** (after an interruption, resume the same run ID:
finished agents return cached, restarted ones' applied fixes no longer match
and are skipped — proven on KTB).

Fix: garbles whose intended reading is unambiguous from context; intra-word
spacing/letterspacing; running-head and marginal debris; broken quote marks;
split/fused words. **Image consult allowed but discouraged**: only when
context cannot decide, rasterize the ONE page (`pdftoppm -png -r 200`), and
count every consult. If even the image cannot decide, leave as-printed and
report it. Measured consult rates: 14/360 edits (Dartmouth), 46/1,995 (KTB)
— context decides ~97% of the time.

Fidelity rules (verbatim into every agent brief):
- **Period orthography is untouchable** — "shew", "chuse", "farther",
  "expence", archaic capitalization and punctuation. Modernizing is
  corruption. The printing's own errors stay too (Dartmouth's "Trusteees"
  and "tyranical", both image-verified and kept).
- **Latin/Greek are edit-forbidden** unless the garble is provable from
  within the passage or the image; every such edit individually ledgered.
  Medieval orthography ("michi", "nichil", e for ae) LOOKS wrong and is
  right. Same caution for German/French.
- No paraphrase, no reordering, no added/dropped content — which means
  marginal-note fragments the OCR injected mid-sentence stay put (repairing
  them needs reordering); they go in the unresolved ledger instead.
- Page anchors, footnote markers, headings untouched.

**3. Translation glosses (optional pass, same mechanics).** English for
non-English content, inserted after the span as **`(tr.: …)`** — the marker
is mandatory so additions are never mistakable for printed text;
**`(tr. uncert.: …)`** where the reading/sense is doubtful (each listed).
Skip when the author translates or paraphrases adjacently — his rendering
outranks ours (Kantorowicz does this constantly: ~395 skips vs 2,194
glosses). Recurring termini glossed at first occurrence per chunk only;
citation-only titles never; absorbed legal Latin (*viz.*, *per se*) never.
The non-English text itself is untouched in this pass.

**4. Verification + provenance (every pass, non-negotiable).**
- Invariants after every pass: page-anchor completeness (no gaps), footnote
  ref==def reconciliation, no hard-wrapped lines, orthography-guard spot
  checks (grep the protected words — they must survive).
- Structured reports from every agent (edits made, image consults, per-item
  Latin edits, unresolved list) → saved as a JSON ledger **beside the
  edition** (`*-corrections.json`, `*-smoothing-ledger.json`,
  `translation-pass-ledger.json`).
- The edition's header narrates its whole provenance chain: substrate,
  extraction method, each pass with its numbers, and the standing rule —
  **the markdown is for reading; the scan is the authority for any
  load-bearing quotation.**

## What we learned the hard way (do not re-derive)

- Wholesale vision transcription → content filter (see 0). Flag-then-verify
  (LLM plausibility nominates, page image adjudicates — 983 flags → 949
  confirmed, 96.5% precision on Dartmouth) works but only repairs what gets
  nominated; the smoothing pass (step 2) supersedes it as the default.
- An LLM's English prior is the *wrong* instrument for Latin/Greek — hence
  the hard rule and per-item ledger. It is also exactly the *right*
  instrument for garbled English: Matthew's hypothesis, confirmed at 97%
  context-only resolution.
- Footnote placement is a determinism problem, not an intelligence problem.
  Solve it in the extraction script.
- ~130 unresolved spans per book is the honest residue (mid-sentence
  marginalia, text absent from the OCR layer). A local VLM re-read
  (GB10; ollama+VLM, or white-box SGLang serving for true logprob flagging)
  is the escalation path if it ever matters — designed, not built.

## Worked artifacts

| Piece | Where |
|---|---|
| Smoothing workflow (case report, 14 agents) | `.claude/workflows/transcription/dartmouth-smoothing.js` |
| Smoothing workflow (book, 24 agents, Latin rule, notes agents) | `.claude/workflows/transcription/ktb-smoothing.js` |
| Translation-gloss workflow (25 agents, both files) | `.claude/workflows/transcription/ktb-translations.js` |
| Flag-then-verify (superseded default; kept for reference) | `.claude/workflows/transcription/dartmouth-ocr-correction.js` |
| Extraction worked example (font-size classify + outline) | `.claude/workflows/transcription/extract-ktb-example.py` — per-book constants MUST be recalibrated |
| Finished editions + ledgers | `~/reading/artificial-persons/dartmouth-v-woodward-1819.md`, `kantorowicz-1957-kings-two-bodies.md`, `*-ledger.json` beside them |

All workflow agents run **Opus, medium effort** (standing instruction).
