# Reproducing a verdict: from a recorded `seg_id` back to the text

Every Pangram verdict this study reports is keyed to a `seg_id`, and every
`seg_id` is tracked in this repository. The transcripts themselves are not —
they are licensed by their publishers and are never redistributed here. This
document is the bridge: what a `seg_id` means, and how to rebuild the exact
text it names.

## What a seg_id is

```
CA2025-06-16#t91w0        federal Canada, 16 June 2025, turn 91, window 0
2026-05-07#t2871w4        New Brunswick, 7 May 2026, turn 2871, window 4
US2025-03-11-Pg S1729#t4  US Senate, page S1729, turn 4
```

`date#t<turn>w<window>`. The turn index counts speaker turns within a sitting
in document order; the window index counts the packer's output within that
turn. Both are deterministic functions of the source file and the extraction
code, so the same inputs reproduce the same ids.

**This means a `seg_id` is only meaningful together with the extractor that
produced it.** All of them are tracked — see below. An earlier version of the
`.gitignore` blanket-ignored `analysis/s10/provinces/` and `analysis/s10/us/`
to keep transcripts out of the repo, and swallowed the extraction scripts with
them; 17 of the 21 chambers were unreproducible as a result. Fixed 2026-08-12.

## The chain

1. **Fetch.** Per-chamber downloaders, named `*_download.py`, `fetch_*.py` or
   `*_harvest*.py`. Each records its source URLs; several write a `download.log`
   with what was retrieved and when.
2. **Extract.** Per-chamber `*_extract.py` converts the publisher's format —
   PDF, DOCX, HTML, XML, GovInfo zips — into the shared paragraph schema. The
   formats differ enough that each chamber needs its own; the schema does not.
3. **Segment.** `segment.py` assembles paragraphs into speaker turns and packs
   each turn into windows of at most 360 words, flagging anything under 50 as
   unscoreable. This is where `seg_id` is assigned. `us_extract.py` performs
   its own segmentation with the same constants and the same packer.
4. **Sample.** `build_pangram_expansion.py` (long band) and
   `build_shortband.py` (short and over bands) draw the samples. Both are
   seeded per chamber-era, so they redraw identically.
5. **Score.** Upload CSVs to the Pangram dashboard with `id` as the tag column,
   or use the Bulk API with `model: "pangram-4"` named explicitly — the API
   defaults to Pangram 3, which is a materially different instrument (§3.2).

## Verdict files, and which is which

| file | what it holds |
|---|---|
| `pangram_p4_verdicts.csv` | 4,258 long-band verdicts, all Pangram 4, with `fraction_ai` |
| `pangram_shortband_verdicts.csv` | short and over band verdicts as they land |
| `pangram_shortband_manifest.json` | the sample: id, chamber, era, `seg_id`, date, speaker, length, band |
| `pangram_ch_verdicts.csv` | the earlier four-chamber arm (**Pangram 3 era — see below**) |
| `pangram_verdicts.csv` | the New Brunswick pilot |

**A note about `pangram_ch_verdicts.csv`.** It carries no `version` column,
so its model tier is inferred rather than recorded. Earlier text here called
its 120 short-band rows (119 Human, 1 AI, no Mixed) "the Pangram 3 signature"
and told you not to pool them. **That inference was wrong on both halves.**
Pangram 3 does return Mixed — the `prior_p3` column of
`pangram_p4_verdicts.csv` holds 8 of them — so absence of Mixed identifies
nothing. And zero Mixed among 120 *short* segments is what Pangram 4 predicts
anyway: the matched-rate P4 short band flagged 9 of 1,648.

What the tier actually rests on: the arm was scored by uploading RTFs to the
web dashboard (`pangram_ch/` holds 540 files, `pangram_ch2/` the short band),
and the dashboard runs Pangram 4 — the P3 default afflicts the *API* route
(§3.2). That is strong but indirect. Before pooling these rows with Pangram 4
results, rescore a sample and check agreement.

## To find the exact segments that came back AI

```bash
# every flagged long-band segment, with its chamber and date
python3 -c "
import csv
for r in csv.DictReader(open('pangram_p4_verdicts.csv')):
    if r['pangram'] in ('AI','Mixed'):
        print(r['chamber'], r['date'], r['seg_id'], r['pangram'], r['fraction_ai'])"
```

Then run the chain above for that chamber and look the `seg_id` up in the
resulting `segments_*.jsonl`. The text is in the `text` field.

## What cannot be reproduced

- **Rewritten bypass variants.** Close paraphrases of Hansard, held locally in
  `bypass_text/` and gitignored. Ids, scores and hypotheses are tracked.
- **Text under 50 words.** Pangram refuses it, so 3.5% of the record is
  unmeasurable by any sampling design rather than merely unmeasured
  (`corpus_audit.py`).
- **The four-chamber short bands**, until they are rescored on Pangram 4.

## Manitoba: the live files understate the record (found 2026-08-13)

`provinces_extract.py` matched a speaker prefix in a single `<b>` run. From
mid-2018 Manitoba's Word export splits a name across several runs around
inserted TOC anchors — `<b>Ms. Malaya </b><b><a name=_Toc..>Marcelino</a></b><b>
 (Notre Dame):</b>` — so the prefix did not match, the speech accreted to the
previous turn (usually the Speaker's) and was then dropped as chair voice.
Chair share of page text runs 4% in 2011–13 against 37–40% in 2020–24.

The extractor is fixed. The **live files are not regenerated**, because
re-extraction shifts turn indices and 135 of the 278 Manitoba segments carrying
a Pangram verdict would lose their `seg_id` anchor.

| file | status |
|---|---|
| `segments_mb.jsonl`, `segments_mb_2025.jsonl` | live; understate 2018+ |
| `segments_mb_FIXED.jsonl` | corrected, complete 2006–2026, **not yet canonical** |

Measured shortfall in the live files: 2018 −4.9%, 2019 −41.0%, 2025 −78.1%,
2026 −65.1%; 2006–2017 unaffected (≤0.5%).

**What this does and does not invalidate.** The instrument rate barely moves —
Manitoba 2025–26 goes 3,556 to 3,627 per 100k, **+2.0%** — because the lost
text is ordinary member speech of much the same register, so the trend series
is sound. What is compromised is the *sampling frame*: Manitoba's prevalence
sample was drawn from 58% of its record. The verdicts themselves remain valid
measurements of the text that was scored.

Before any Manitoba prevalence claim is relied on, redraw the sample from
`segments_mb_FIXED.jsonl` and rescore (~500 credits). Before any Manitoba trend
claim, the +2.0% is within the noise of the series and no action is needed.
