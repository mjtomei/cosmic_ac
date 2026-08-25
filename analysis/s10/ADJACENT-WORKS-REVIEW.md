# Adjacent-works review: how comparable papers write their sections, and a rewrite plan for S10

**Purpose.** Matthew's read of the reformatted draft: "still pretty far off" — an
extremely short §1 that doesn't read like an introduction, and many subsections
that still read like a *report of what was done* (e.g. "Limits, and they are
real"). This is the grounding pass before the writing-quality workflows: what do
the closest published papers actually do in each section, where does S10 fall
short, and what concretely changes. Sourced from three parallel studies
(2026-08-24) of (a) the Kobak excess-vocabulary paper, (b) Science Advances /
PNAS quantitative-text conventions, (c) the legislative / LLM-detection
comparables. Word-count figures are approximate.

---

## 1. The model paper: Kobak et al., *Science Advances* 2025

The single closest twin — same method family (an LLM "register" built from
overused vocabulary), a temporal headline, and our target venue. One fact about
it is the most useful signal we have: **on the way from preprint to Science
Advances, the authors *added* findings-first subsection headings** to Results.
The published version is the one to model.

- **Section order & balance.** Unlabeled Introduction · Results · Discussion ·
  Materials and Methods. **Results is the largest section; the Introduction is a
  full 6-paragraph funnel, not a few lines; Methods is full-length and
  quarantined at the very end** with "(see Methods)" pointers from the narrative.
  Rough target proportions across the genre: Intro ~15–25%, Results ~30–40%
  (largest), Discussion ~20–25%, Methods ~15–25%.
- **Introduction = a five-move funnel** (this is the fix for our §1):
  1. **Hook on the phenomenon, end ¶1 on the question.** Kobak: "When the world
     changes, human-written text changes… *Do technological advances leave a
     similar footprint on our writing?*"
  2. **The specific event and the stakes** (why it matters now).
  3. **Prior work, organized** — Kobak taxonomizes it into three named groups,
     not a name-dump.
  4. **The gap, with a "most importantly" pivot** — stated once, load-bearing.
  5. **"Here, we…"** — names the method, the corpus, and closes on the
     qualitative headline (the precise number is held for the abstract/Results).
- **Results headings are complete claims**, subject–verb–object: "Excess words
  indicate widespread LLM usage" · "Combining excess words puts a lower bound on
  LLM usage" · "Lower bounds differed between subcorpora." A reader who scans
  only the headings gets the argument. Figures are cited **inline and
  parenthetically** ("… (Fig. 2)"), never "Figure 2 shows…".
- **Discussion** opens by restating the contribution ("Here, we leveraged…to
  show…"), uses run-in headings **Summary · Interpretation and limitations ·
  Related work · Implications and policies**, and ends on future work.
  Limitations live *inside* "Interpretation and limitations," bundled with
  interpretation — never a standalone confession.
- **The rhetorical masterstroke: the headline is a *lower bound*.** Every
  undercounting worry is pre-absorbed ("this is only a lower bound because…"),
  so undetected usage becomes evidence the true figure is *higher*, not a
  weakness. And the strongest robustness beat is **two non-overlapping word sets
  independently returning the same bound** ("independent confirmation").

## 2. Section conventions (Science Advances / PNAS), from three exemplars

Confirmed against Kobak (SciAdv 2025), Card et al. (PNAS 2022, 140 years of US
immigration speeches — our domain), and Wei et al. (PNAS 2025, semantic change
in congressional speech — a surprising-temporal-claim twin).

- **Intro is a 6–8 paragraph funnel** every time. ¶1 hook ending on the
  question; specific phenomenon + stakes; prior work organized and credited (not
  novelty-argued); the gap once and quietly; an explicit "Here, we…"; corpus and
  scope with numbers. For a *surprising* result, **previewing the headline in the
  intro is a strength** (Card and Wei both do; their titles state the finding).
- **Findings-first Results, two legal styles, one rule.** Either assertion
  headings (Kobak) or neutral noun-phrase topic labels (Card, Wei) — but in both,
  **the first sentence of each subsection states the result**, and figures are
  cited parenthetically. None uses wry/essayistic/report-style headings.
- **Discussion** restates contribution in sentence 1; a plainly-labeled
  limitations home; caveats **specific and corpus-anchored** (genre, coverage,
  who's excluded — Wei: "political speech… does not fully represent the wider
  language community"); ends on significance/future work, not a recap.
- **Methods** full and at the end (15–25%). *(PNAS also wants a ~120-word
  Significance statement; Science Advances does not.)*

## 3. The comparables landscape, and where S10 stands

Six works measure LLM text in institutional corpora. Positioning matters more
than novelty here — we land where the literature predicts, then add what nobody
else has.

| Work | Scope | Text | Instrument | Headline | Baseline |
|---|---|---|---|---|---|
| Suvanto et al. 2026 (arXiv:2606.14209) | 2 chambers / 2 countries / EN+SV | written motions | 1 glass-box classifier | 15% (UK) / 9% (SE) paragraph-level | 2014–20 |
| Liang "Monitoring" 2024 (ICML) | 4 review venues | peer reviews | population-level MLE | 6.5–16.9% | post-2023 |
| Liang "Quantifying" 2025 (*Nat. Hum. Behav.*) | ~951k papers | papers | population-level MLE | CS 17.5% / math 6.3% | 2020–24 |
| Gray 2025 (arXiv:2512.01560) | multi-field | papers | lexical marker words | >10% of 2024 papers | notes pre-LLM levels |
| Rice 2026 (Substack) | Australian federal | speeches | 5 commercial detectors | flat 2018=2026 (null) | 8-yr detector series |
| Pimlico 2025 (blog) | UK Commons | speeches | phrase z-scores | phrase spikes | 2007–25 |
| **S10** | **22 / 4 / EN** | **speeches** | **calibrated detector + independent register** | **~9%; 11× spread; register from 1994–96** | **~30 yr** |

**We own three axes:** *scale* (22 chambers vs. the next parliamentary study's
2), *triangulation* (nobody else pairs a calibrated commercial detector with a
detector-independent lexical instrument), and *time-depth* (a ~30-year baseline
vs. everyone's 2020+ window). Our ~9% sitting inside the field's 6.5–17% range is
a **credibility asset**, not a novelty deficit.

**Three positioning lessons:**
- **Don't claim "first to detect."** Suvanto banks that. Claim scale,
  triangulation, and the historical result. State any "first" quietly, once.
- **Make the two instruments the answer to the field's central anxiety** —
  detector unreliability. Every serious comparable is organized around distrust
  of instance-level detection (Liang builds a whole distributional method to
  avoid it; Rice's and Pimlico's naive detectors flatline or return 0%). Our
  lever is the *lexical register* (population-level, detector-independent) plus
  *Pangram calibrated per-chamber against pre-2022 speech* (measured false-
  positive rate). **Their agreement is the reliability argument — lead with it.**
- **Pre-empt "you're just penalizing valid words."** Suvanto §7.1 aims this
  straight at lexical instruments. Neutralize it by framing the register as a
  **corpus-level measure, never an accusation of any individual speaker**
  (Liang's "population-level, not instance-level" language), and by using its
  **decades-long pre-model rise as proof it measures real drift, not a detector
  artifact** — the history turns the weakness into the headline.

## 4. Gap analysis — S10 as it stands

1. **§1 is not an introduction.** It's short and jumps to the two-instrument
   setup without the funnel: no phenomenon hook, no organized prior work, no
   explicit "Here, we…", no scope paragraph. → Rebuild as the 6-paragraph funnel.
2. **Report-style headings.** "Limits, and they are real," and topic-label
   subsections throughout Results, read like lab notes. → Convert to findings-
   first claims; rename the limitations material to "Interpretation and
   limitations."
3. **The 9% is not framed as a lower bound.** We already argue it's conservative
   (Se=1; evadable) but don't brand it. → Adopt the lower-bound frame explicitly.
4. **The two-instrument agreement is not foregrounded as the reliability
   argument.** It's the paper's strongest credibility asset and the field's
   central concern. → Lead the Results (and the abstract) with the convergence.
5. **The historical result is buried mid-Results (§4.5).** It's our most
   differentiated finding. → Give it a claim-heading and make it the Discussion's
   opening interpretation; the intro should preview it.
6. **Related work is defensive/rebuttal-shaped** (much of §7 argues with Rice).
   → Reframe as positioning (scale/triangulation/depth), credit precedents
   (Gray's pre-LLM elevation; Rice's "already machine-like" null) and build on
   them rather than litigating.

## 5. Section-by-section rewrite plan (the brief for the writing workflows)

**Matthew's emphasis (2026-08-24, plan approved).** Foreground three findings
throughout — they are the paper's intellectual payload and should drive the
Results ordering and the Discussion's opening:
1. **The joint occupation model** — the four-component instrument (U/L/D/N) and
   the altitude ladder peaking at the insulated middle (the apex delta); §4.6b.
2. **The discovery that class and its correlates link to the register** — the
   class inverted-U and the generation/occupation/prominence gradients are a
   *found* structure, not a control; §4.6a–4.6b.
3. **The evidence that the register is a post-training artifact** — the causal
   pinpoint to post-training; §4.7. This is what turns "a register exists" into
   "the machines inherited and amplified it," and should anchor the Discussion.
4. **The substitution-worry quantification (Matthew, 2026-08-24).** The
   occupational result — weak as the effect is — may be the first quantitative
   demonstration of the worry that LLMs are being developed primarily to
   replace workers for the owners of capital: post-training installed the
   register of the insulated organisational middle, exactly the stratum the
   systems are positioned to substitute for. It raises the oversight question —
   what measurements could attach there (whose register, whose work, a model
   is tuned to reproduce) — which we may be the first to quantify. In the
   intro's meta ¶ (softened phrasing, weakness flagged); expand in Discussion/
   future work during pass 3.


- **Abstract.** Already close (Matthew approved the beats). One addition: brand
  the 9% as a floor and name the two-instrument convergence.
- **Introduction — rebuild to a 6-paragraph funnel.** ¶1 institutions write in
  recognizable registers → end on "did a machine-like register exist before the
  machines?" ¶2 LLMs enter public/legislative drafting + stakes (legitimacy,
  representation, authorship of law). ¶3 prior work as a 3-bucket taxonomy
  (commercial detectors; population/word-frequency estimates; marker-word lists),
  credited. ¶4 the gap + "most importantly" pivot: all prior work needs ground-
  truth training data and treats the register as a *recent* discontinuity — none
  asks whether it predates the machines. ¶5 "Here, we…" — two instruments, 22
  chambers / 4 countries, ~30-year span. ¶6 preview the headlines (9% floor;
  register from 1994–96).
- **Results — findings-first headings, convergence first.** Reorder so the
  two-instrument agreement leads, then prevalence + spread, genre, the historical
  rise (claim-heading: "The register predates the models by three decades"),
  generation/occupation (the U/apex), quality, evasion. Example rewrites:
  "Calibration: 1,260/1,260" → "A per-chamber-calibrated detector puts a floor
  under machine-drafted speech"; "Limits, and they are real" → move to Discussion.
- **Discussion — the standard arc, flowing prose.** (Matthew, 2026-08-24: the
  labeled Kobak skeleton is not required — and it is not the field norm: both
  PNAS exemplars run flowing Discussions with no subsection labels.) Arc:
  restate the contribution → interpret → limitations candid and corpus-anchored
  → relate to prior work (positioning, not rebuttal) → implications/policy →
  close on significance. Open on the historical inversion: the machines
  inherited and accelerated a pre-existing human register. Trim the current
  pile of subsections toward this arc.
- **Intro tells the honest discovery story** (Matthew, 2026-08-24): began from
  the prevalence question after a news instance (the NB clip with prompt traces
  visible); the register — borrowed as a lighter, edit-robust cross-check —
  turned out to predate the machines and correlate with post-training; the
  class/occupation correlations came from seeking an explanation and are
  weaker than the simple birth-cohort correlate; they open three fields
  (machine speech impacts/biases; class markers in legislatures; large-scale
  register study on open data). The intro also carries the meta point: the
  study itself demonstrates machine-executed measurement at near-zero cost,
  nulls and replications included. APPLIED in writing pass 1.
- **Materials and Methods.** Already at the end; keep tightening narrative→
  "(see Methods)" pointers.
- **New moves worth adding** (from the broad-science template): a hero
  cross-chamber figure; an explicit **negative control** (the flat pre-1994
  baseline already serves); a **correlates** framing (which chambers, seniority,
  procedure drive the spread) — a proven broad-science crowd-pleaser.

---

## Sources
- Kobak et al., *Science Advances* 11(27):eadt3813 (2025); arXiv:2406.07016.
- Card et al., *PNAS* 119 (2022), 10.1073/pnas.2120510119.
- Wei et al., *PNAS* 122 (2025), 10.1073/pnas.2426815122.
- Suvanto, McGlinchey, Barclay & Wahde, arXiv:2606.14209 (2026).
- Koniaris et al. (ParliaBench), arXiv:2511.08247 (2026).
- Liang et al., "Monitoring AI-Modified Content at Scale," ICML 2024, arXiv:2403.07183.
- Liang et al., "Quantifying LLM usage in scientific papers," *Nat. Hum. Behav.* (2025); arXiv:2404.01268.
- Gray, arXiv:2512.01560 (2025).
- Rice, "Hunting for ChatGPT in Parliament," *Rice On Paper* (Substack), 2026.
- "Apple Tokamak," *Pimlico Journal* (2025).


## 6. Last-pass takeaways (2026-08-24, mined before the Results edits; all applied in pass 2 unless noted)

1. **Results as an escalation ladder** (Kobak): signal → historical control →
   characterise → lower bound → independent confirmation → subgroups. Our
   existing order already climbs it; the claim headings now make it legible.
2. **Conceptual scaffold at the top of Results** (Wei's move): with Methods now
   trailing the Discussion, Results opens with one paragraph defining both
   instruments operationally and pointing at Materials and Methods — fixes the
   forward dependency the reorder created. APPLIED.
3. **Population-level, not instance-level** (Liang's language; pre-empts
   Suvanto §7.1's "penalizing valid words"): one explicit sentence in §4.2 —
   the estimate describes the corpus, a segment verdict is an instrument
   reading, not an attribution. APPLIED.
4. **Name negative controls as negative controls** (Liang's Nature-reviews
   move): RLVR now introduced as "registered as the arm's negative control
   before the run." APPLIED (trend placebos already carry the word).
5. **Gray as published precedent for marker decay**: our obvious-tells
   peak-and-fall now cites Gray's observation that publicised marker words
   dropped in scholarly text. APPLIED.
6. **Parenthetical figure citations** ("… (Fig. 2)"), never narrative
   "Figure 2 shows". Altitude anchor converted. APPLIED.
7. **"(see Methods)" pointers** to slim inline method detail from Results —
   partially applied (scaffold ¶); fuller sweep belongs to pass 4 (flow).
8. **Question-as-opener** is a legitimate device (Kobak) — available for
   pass 4, use sparingly.
9. **Discussion: flowing arc** (restate → interpret → limitations → prior work
   → implications → significance/future work), no labeled skeleton — for pass 3.
10. **The worry citation**: Brynjolfsson's Turing trap (Daedalus 2022) is the
    academic origin of the substitution worry; attributing it distances us —
    "We do not advance that reading; we note that it now has a measurable
    form." APPLIED in intro ¶7.
