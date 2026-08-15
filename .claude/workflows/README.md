# Preserved reading-pipeline workflows

Rescued 2026-08-15 from ephemeral session directories (sessions `aaa6ff40`
main + `-reading`, 2026-07-28/29) — these built the reading collections'
citation sweeps, PDF acquisitions, and `00-RANKINGS.json` files, and the
method decisions they encode existed nowhere version-controlled.

**These are TEMPLATES, not turnkey.** Each hardcodes its collection's
directory, file list or seed list, and PROJECT context block. To reuse:
copy, swap those three things, keep the structure. (Invoking one by name
unedited would re-run a stale list.)

The three-stage pipeline, as used per collection:

1. **Search** — two shapes:
   - `citation-graph-reading-list.js` (from governance-citation-graph):
     per-seed forward/backward sweep to BUILD a reading list.
   - `citation-graph-novelty-check.js` (from citation-graph-knowledge-problem):
     sweep → adversarial per-candidate verify, to FALSIFY a novelty claim
     ("try hard to refute; a clean negative is a valuable answer").
   Both carry an API_HELP block: Semantic Scholar + OpenAlex via curl,
   pagination, DOI resolution — and the rule that Google Scholar is
   bot-walled and must not be scraped. All agents opus/medium.
2. **Acquire** — `citgraph-acquire.js`: batched fetch agents with hard
   verification rules (%PDF magic, >50KB, page-1 text matches
   title/author, version reported), known techniques (aeaweb needs
   Playwright expect_download; NBER path pattern; JSTOR blocked — use
   repositories/author pages/Wayback), never-fabricate, per-file
   ok|failed|no_oa status JSON.
3. **Rank** — `reading-list-ranking.js` (canonical: one opus/medium agent
   per PDF reads it and scores relevance/standing/quality 1-10, then one
   opus/high calibrator computes composite = 0.5*rel + 0.3*standing +
   0.2*quality, corrects reviewer self-inflation, cuts tiers at natural
   gaps not quotas). `governance-ranking.js` and
   `artificial-persons-ranking.js` are the batched-read variants (opus
   readers in batches, opus/high synthesis).

Model policy (Matthew, standing): subagent fan-outs on opus — readers at
effort medium, the single judge/calibrator at effort high. Keep this when
adapting unless told otherwise.

Products these built: `~/reading/*/00-CITATION-SWEEP.json`,
`00-RANKINGS.json`, and the collections' PDF sets. The security-economics
collection (2026-08-15) ran its sweep with plain parallel agents (before
the templates were rescued), then its acquire + ranking stages from these
templates — those two instances are preserved here as
`security-economics-acquire.js` (10 fetch agents, 92/99 ok, honest no_oa
reporting) and `security-economics-ranking.js` (92 opus/medium readers +
opus/high calibrator; its calibration notes in
`~/reading/security-economics/00-RANKINGS.json` are the model for what the
calibrate stage should return).
