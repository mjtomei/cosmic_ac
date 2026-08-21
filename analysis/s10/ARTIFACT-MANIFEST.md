# Private-artifact manifest

Files that are part of the study's evidence chain but stay out of the public
repo (parliamentary text, bulk transcripts, or third-party bulk data). Each
entry: sha256, size, where copies live, and how to regenerate from committed
code. Everything needed to recompute every published number IS committed —
these are the inputs the committed scripts rebuild or read.

| file | sha256 | bytes | regenerate / acquire |
|---|---|---|---|
| arch_more_wf.tgz | 37aea78c418d904a… | 1351638 |  |
| arch_quality_wf.tgz | 4585a87b19f39e87… | 3903356 |  |
| arch_stage2_wf.tgz | f63e49c7c0d55c68… | 3374958 |  |
| onet_occupation_data.csv | a09eae1d6609686e… | 268030 |  |
| pool6c.json | 77646a0aa5f66e1e… | 246889 |  |
| pool6.json | 7796898757548e14… | 275597 |  |

- **pool6.json / pool6c.json** — stage-6 blind grading pools (truncated
  parliamentary excerpts + model continuations). Regenerate byte-identically:
  `python quality_expansion/build_stage6_pool.py` (verifies against the
  committed content-hash ids in key6.json). Requires the local corpus +
  rlhf_gen/prompts.json (itself rebuilt by `rlhf_pref_generate.build_prompts`).
- **arch_*.tgz** — raw grading-workflow transcripts from the grading machine.
  Scientific content fully committed as stage{1,2,3,4}_grades_by_id.json,
  sset_grades_by_id.json, screen_by_id.json (scores only, no text). Copies:
  ~/s10_private_artifacts on this machine; originals under
  ~/.claude/projects/-home-mjtomei-quality-expansion on the grading machine
  (retention now set to keep indefinitely).
- **onet_occupation_data.csv** — full O*NET 30.3 Occupation Data (CC-BY 4.0)
  incl. descriptions. The committed `onet_occupations.csv` (code+title) is
  the slim variant the pipeline uses. Full file: download
  db_30_3_text.zip from onetcenter.org, file "Occupation Data.txt".

Copies of everything above: /home/matt/s10_private_artifacts/ (this machine).
