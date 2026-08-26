#!/usr/bin/env python3
"""Render EVIDENCE-STANDARDS-SURVEY.md from the workflow's structured output.

Input: evidence_survey_raw.json — nine per-claim surveys of adjacent
literatures (nearest works, the field's evidence checklist, what S10 meets,
gaps with severities) plus the cross-claim synthesis, produced by the
evidence-standards-survey workflow (2026-08-27, ten Opus agents, web-
verified works). Report structure is findings-first: synthesis up front,
per-claim detail after.

Usage: python build_evidence_survey_report.py [synthesis_override.md]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "evidence_survey_raw.json")))
synth = d.get("synthesis") or ""
if len(sys.argv) > 1:
    synth = open(sys.argv[1], encoding="utf-8").read()

TITLES = {
    "new-sociometric-measure": "The organisational-altitude measure",
    "prevalence": "Prevalence (9.03% machine-drafted)",
    "register-predates-models": "The register predates the models",
    "post-training-artifact": "Post-training artifact",
    "quality-null": "The quality null",
    "detector-evasion": "Detector evasion",
    "permeation": "Permeation into human speech",
    "chase-and-flight": "Chase-and-flight",
    "cohort-juniority": "Cohort / juniority gradient",
}
SEV = {"blocking": "**BLOCKING**", "expected-by-reviewers": "expected",
       "nice-to-have": "nice-to-have"}

L = []
L.append("# Evidence-standards survey — what the adjacent fields demand, "
         "and what S10 still owes\n")
L.append("Nine surveys of the literatures adjacent to S10's main claims, "
         "run 2026-08-27 (ten Opus agents, works web-verified before "
         "citation; structured outputs in `evidence_survey_raw.json`, "
         "regenerate this file with `build_evidence_survey_report.py`). "
         "Each survey extracted the de-facto evidence checklist from the "
         "3–7 published works nearest to the claim type, scored S10 "
         "against it, and returned gaps marked blocking / "
         "expected-by-reviewers / nice-to-have, with feasibility from "
         "held data.\n")
L.append("---\n\n## Synthesis\n")
L.append(synth.strip() + "\n")
L.append("\n---\n\n# Per-claim surveys\n")

for v in d["surveys"]:
    L.append(f"\n## {TITLES.get(v['claim_id'], v['claim_id'])}\n")
    L.append(f"**Verdict.** {v['verdict']}\n")
    L.append("\n**Nearest works and the evidence they marshalled:**\n")
    for w in v["nearest_works"]:
        L.append(f"- **{w['work']}** ({w['venue_year']}). "
                 f"{w['what_they_claimed']} *Evidence:* "
                 f"{w['evidence_they_marshalled']}")
    L.append("\n**The field's checklist:**\n")
    for x in v["field_standard"]:
        L.append(f"- {x}")
    L.append("\n**S10 already meets:**\n")
    for x in v["we_meet"]:
        L.append(f"- {x}")
    L.append("\n**Gaps:**\n")
    for g in sorted(v["gaps"], key=lambda g: ["blocking",
                    "expected-by-reviewers", "nice-to-have"].index(g["severity"])):
        L.append(f"- [{SEV[g['severity']]}] {g['gap']}\n"
                 f"  *Needed:* {g['data_or_analysis_needed']}\n"
                 f"  *Feasibility:* {g['feasibility']}")

out = os.path.join(HERE, "EVIDENCE-STANDARDS-SURVEY.md")
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
n_block = sum(1 for v in d["surveys"] for g in v["gaps"]
              if g["severity"] == "blocking")
n_exp = sum(1 for v in d["surveys"] for g in v["gaps"]
            if g["severity"] == "expected-by-reviewers")
print(f"wrote {out}: {len(d['surveys'])} claims, "
      f"{n_block} blocking + {n_exp} expected gaps")
