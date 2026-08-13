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

**A warning about `pangram_ch_verdicts.csv`.** Its 120 short-band rows are
119 Human, 1 AI and *no Mixed at all*, which is the Pangram 3 signature. They
were scored on 2026-08-02, a week before the model-tier defect was found, and
none has been rescored. Do not pool them with Pangram 4 results.

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
