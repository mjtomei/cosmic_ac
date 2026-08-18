# Pre-registration — does upward linguistic accountability explain the register better than class?

**Written 2026-08-17, before any O\*NET data has been joined to the corpus.**
Registered because the hypothesis and the composite were both formulated *after*
seeing the class inverted U (§4.6a), which makes the instrument unusually
flexible unless its definition is fixed in advance.

## The question

The register's class profile is an inverted U: it peaks at EGP class II (lower
service — teachers, journalists, social workers, nurses), sits lower at class I
(higher service — lawyers, physicians, accountants), and is lowest of all at
IVc (farmers) and VIIab (semi- and unskilled manual). Two features of that shape
are not explained by status rank, which is what EGP orders on:

1. **The II-over-I crossover.** The highest-status class is not the heaviest
   user.
2. **Farmers at the floor.** EGP places IVc mid-table; the register places it
   last, below semi-skilled manual work.

**Hypothesis (Matthew, 2026-08-17).** The register tracks *upward linguistic
accountability* — how much an occupation consists of rendering one's own
judgment into prose for a superior who can overrule it — rather than status,
autonomy, or education.

Autonomy alone was rejected as the framing, for a reason that is itself part of
the hypothesis: **a farmer and a miner are about equally unfree, but their
requirements are imposed by the natural world rather than by a person.** Freedom
conflates constraint-by-nature with constraint-by-authority, and only the second
is predicted to generate the register. Autonomy is not discarded, though — the
claim is about reporting *and* discretion together, so both enter the composite,
autonomy reverse-scored. What is rejected is autonomy *on its own*, which is why
the direction split in (C) and the two-half decomposition both exist.

## The instrument

O\*NET **30.3** (US Department of Labor), CC-BY 4.0, distributed as CSV at
`onetcenter.org/dl_files/database/db_30_3_csv/`. Element IDs below were verified
against `content_model_reference.csv` on 2026-08-17, which corrected three
errors in the first draft of this file: the item is **Written** Letters and
Memos; Documenting/Recording sits under technical activities rather than the
communication block; and "Structured versus Unstructured Work" no longer exists
in the taxonomy.

### The confirmatory composite (FIXED — no item may be added, dropped or reweighted)

The construct is **subordinate account-giving**: rendering your judgment into
prose for someone above you *and* not holding the final say over it. Reporting
and autonomy are two faces of one thing rather than two things (Matthew), so
both enter the composite, with the autonomy items **reverse-scored**.

Equally weighted mean of these six, each standardised across occupations:

| element ID | name | sign | block |
|---|---|---|---|
| `4.C.1.a.2.j` | Written Letters and Memos | + | Work Context |
| `4.A.3.b.6` | Documenting / Recording Information | + | Work Activities |
| `4.A.4.a.2` | Communicating with Supervisors, Peers, or Subordinates | + | Work Activities |
| `4.A.4.c.1` | Performing Administrative Activities | + | Work Activities |
| `4.C.3.a.4` | Freedom to Make Decisions | **−** | Work Context |
| `4.C.3.b.8` | Determine Tasks, Priorities and Goals | **−** | Work Context |

Including autonomy negatively is not a free parameter — it is a prediction, and
it sharpens the case the hypothesis has to explain. Class I documents heavily
(lawyers, physicians, senior administrators) but holds high discretion, so the
reverse-scored terms pull it down; that is precisely the II-over-I crossover the
composite must reproduce. It also keeps the farmer where the theory wants him:
low reporting *and* high freedom, low on both halves.

**Only one separate covariate.** Required education (Job Zone, or Education
Level Required) is not part of the construct — it is the *supply* side of the
two-factor account, the resources needed to produce the register at all, as
against the demand the composite measures. It therefore gets its own
coefficient rather than being averaged in.

**Autonomy is predicted SUFFICIENT but NOT NECESSARY (Matthew), and the
composite's linear form does not capture that.** High autonomy should reliably
suppress the register; low *measured* autonomy should predict little, because
O\*NET rates **nominal** autonomy — discretion recognised in the hierarchy —
while a miner or farm labourer holds substantial **effective** autonomy
moment-to-moment that never registers as recognised discretion. Nobody dictates
how you swing a pick. This is why the manual classes sit at the floor despite
scoring low on measured freedom: the measure misses autonomy that is really
there, not the theory.

The composite keeps a plain reverse-scored linear term regardless, because a
hinge would introduce a knot location as a free parameter and defeat the point
of fixing the instrument in advance. The asymmetry is therefore registered as a
prediction about **how to read the result**, and as two fixed secondary tests:

- **Asymmetry test.** Split the autonomy score at its median and fit the two
  sides separately. The prediction is that the **high-autonomy** side carries a
  clear negative association with register and the **low-autonomy** side is
  near-flat. A weak *linear* autonomy coefficient is therefore NOT
  disconfirmation — under this hypothesis it is what a symmetric fit to a
  one-sided relationship should produce.
- **Nominal versus effective.** The two are separable in O\*NET and are fixed
  here as two scores. Nominal: `4.C.3.a.4` Freedom to Make Decisions,
  `4.C.3.a.2.a` Impact of Decisions on Co-workers, `4.C.3.a.2.b` Frequency of
  Decision Making, `4.C.3.a.1` Consequence of Error. Effective: `4.C.3.b.8`
  Determine Tasks, Priorities and Goals, and reverse-scored `4.C.3.d.3` Pace
  Determined by Speed of Equipment, `4.C.3.b.7` Importance of Repeating Same
  Tasks, `4.C.3.b.2` Degree of Automation. The prediction is that **effective**
  autonomy tracks the register's floor better than nominal does, and
  specifically that it places miners and labourers near farmers rather than near
  teachers. If nominal does the better job, the effective/nominal distinction is
  wrong and should be dropped rather than rescued.

**Pre-specified decomposition (secondary, not a re-definition).** The composite
is reported first and is what the hypothesis stands or falls on. Alongside it,
and fixed here, the two halves are also reported separately — the four
accountability items as one score, the two autonomy items as another — so it is
visible which half carries the result. This is a decomposition of a fixed
composite, not licence to re-weight it: if the autonomy half does all the work,
that is reported as such and the hypothesis is revised in a later study, not
here.

### The full element set

There is **no subset**. Coding maps each occupation string to one O\*NET-SOC
code; every rated element then joins for free from the public CSVs, so the
marginal cost of an extra element is zero and the free model receives all of
them:

| block | element ID prefix | rated elements |
|---|---|---|
| Work Context | `4.C` | 59 |
| Abilities | `1.A` | 52 |
| Generalized Work Activities | `4.A` | 41 |
| Basic Interests | `1.B.3` | 41 |
| Knowledge | `2.C` | 33 |
| Cross-functional Skills | `2.B` | 25 |
| Basic Skills | `2.A` | 10 |
| Interests (RIASEC) | `1.B.1` | 9 |
| Job Zone | — | 1 |
| **total** | | **~271** |

(The content model lists 3,006 rows, but 2,419 of those are detailed work-activity
*task statements* under `4.A` with no per-occupation ratings.)

**Elements with a prior claim** — named because theory points at them, not
because the pool is limited to them: *Interpreting the Meaning of Information
for Others* `4.A.4.a.1`, *Communicating with People Outside the Organization*
`4.A.4.a.3`, *Assisting and Caring for Others* `4.A.4.a.5`, *Selling or
Influencing Others* `4.A.4.a.6`, *Performing for or Working Directly with the
Public* `4.A.4.a.8`, *Training and Teaching Others* `4.A.4.b.3`, *Providing
Consultation and Advice to Others* `4.A.4.b.6`, *Evaluating Information to
Determine Compliance with Standards* `4.A.2.a.3`; *Writing* `2.A.1.c`,
*Speaking* `2.A.1.d`, *Persuasion* `2.B.1.c`, *Instructing* `2.B.1.e`, *Social
Perceptiveness* `2.B.1.a`; *English Language* `2.C.7.a`, *Communications and
Media* `2.C.9.b`, *Sociology and Anthropology* `2.C.4.f`, *Therapy and
Counseling* `2.C.5.b`, *Law and Government* `2.C.8.b`.

**Deliberate negative controls**, already in the pool and flagged so their
selection is interpretable: *Spend Time Sitting* `4.C.2.d.1.a`, *Indoors,
Environmentally Controlled* `4.C.2.a.1.a`, *Physical Proximity* `4.C.2.a.3`. If
these predict as well as the composite, the model has found "office job" rather
than anything about language.

### Coverage check, to be reported before any model is fitted

O\*NET rates roughly 900 O\*NET-SOC occupations, and many of our 7,421 strings
will map to the same code, so **distinct SOC codes — not member count — is what
bounds the occupational variety available**. Report, before fitting: the number
of distinct SOC codes matched, the share of members mapped, the ten most common
codes with their member counts, and the share of members sitting in the top ten.
If the panel collapses onto a few dozen codes, the study is underpowered for
occupational structure regardless of how many members it has, and that should be
visible in advance rather than discovered in the results.

### A second registered hypothesis: sociality, and the direction of interaction

RIASEC **Social** `1.B.1.d` may reproduce the class U on its own — the peak
(teachers, nurses, social workers, journalists) is the Social cluster nearly by
definition, the floor (farmers, miners, labourers) is **Realistic** `1.B.1.a`,
class I is Investigative/Enterprising, class III is Conventional. The
**Social-minus-Realistic contrast** is therefore registered here as a second
hypothesis in its own right, on equal footing with the accountability composite.

It is a **sibling of the accountability hypothesis, not a rival** (Matthew): any
job that requires interacting with an individual involves reporting to them in
some sense, so the two constructs overlap by construction. What separates them
is not whether interaction happens but **which way it points**, and O\*NET rates
that separately:

| direction | elements |
|---|---|
| **upward** — to someone who can overrule you | `4.A.4.a.2` Communicating with Supervisors, Peers, or Subordinates; the accountability composite above |
| **lateral / public** — to people you serve rather than answer to | `4.A.4.a.4` Establishing and Maintaining Interpersonal Relationships; `4.A.4.a.5` Assisting and Caring for Others; `4.A.4.a.8` Performing for or Working Directly with the Public; `1.B.1.d` Social |
| **downward** — to people who answer to you | `4.A.4.b.1` Coordinating the Work and Activities of Others; `4.A.4.b.4` Guiding, Directing, and Motivating Subordinates; `4.A.4.b.5` Coaching and Developing Others |

**The three-way contrast is the discriminating test**, and each outcome names a
different finding:

- **upward alone predicts** — reporting in a social *hierarchy*; the
  accountability hypothesis.
- **all three predict about equally** — general social *role*; sociality, and
  direction is irrelevant.
- **downward predicts too** — a managerial register, which is a third account
  neither hypothesis proposed and would need its own explanation.
- **lateral predicts but upward does not** — service-facing speech rather than
  deference, which would invert the reading of the U.

This distinction is the reason to run the test at all: both hypotheses predict
the same cross-sectional U, and only the direction split tells them apart.

## Specification

Member-level, matching the canonical spec in `member_level_estimation.py`: one
observation per legislator, equal weight, register z-scored within chamber
against the chamber's full member population, HC1 errors.

    (A) z ~ account_giving + required_education              (+ birth decade)
    (B) z ~ social − realistic + required_education          (+ birth decade)
    (C) z ~ upward + lateral + downward + required_education (+ birth decade)
    (D) z ~ EGP class dummies                                (+ birth decade)

(A) is the accountability hypothesis, (B) sociality, (C) the direction split
that discriminates them, (D) the incumbent. All four fitted on the **same
members** and compared by adjusted R², by held-out performance on withheld
occupations, and by whether each block survives the others' inclusion. (C) is
what decides between (A) and (B); (A) and (B) are both reported whatever (C)
says, because a sibling hypothesis that also predicts is a result, not a
nuisance.

## Pre-specified predictions

1. **The account-giving composite is positive and survives** required
   education. Its two halves are also reported separately (see the composite
   section); the hypothesis predicts the reporting half positive and the
   autonomy half negative, i.e. both pointing the same way once reverse-scored.
2. **Sociality also predicts**, because the two constructs overlap by
   construction — a job requiring interaction with an individual involves
   reporting to them in some sense. A positive result for (B) is expected and is
   **not** evidence against (A). The informative quantity is (C).
3. **Upward outscores downward.** If the register is deference, the upward block
   carries (C) and the downward block does not. Roughly equal loadings across
   all three directions would favour sociality; a downward loading would
   indicate a managerial register, which neither hypothesis predicts and which
   would need its own account.
4. **Farmers are the diagnostic case.** EGP ranks IVc mid-table; both composites
   and the observed value place it at the floor. If either beats EGP anywhere,
   it should be here.
5. **The manual classes are no longer a counter-case, and that must not be
   claimed as a success.** V/VI and VIIab score low on measured autonomy yet sit
   at the register's floor. Under the sufficient-not-necessary reading this is
   expected — they hold effective autonomy the nominal scales miss — but that
   reading was adopted *after* seeing them there, so it earns no credit unless
   the effective-autonomy score above independently places them near farmers.
   That is the test; the narrative is not.
6. **Police are predicted to be MISSED.** Police other-ranks write heavily
   (incident reports, statements, court files), so they will score high on
   Documenting and Written Letters and Memos, but they are observed at −0.200.
   Recorded as an expected failure **in advance**; neither composite will be
   modified to accommodate it. A simple combination of existing scales that
   misses one occupation is more informative than a bespoke rule that misses
   none.
7. **Two-factor outcome is the most likely.** An accountability or sociality
   term negative-at-the-top with required education positive-at-the-bottom would
   produce the observed U as the product of two crossed gradients, and would
   explain why education showed the same shape while being statistically
   inseparable from class.

## The free model (Matthew, 2026-08-17) — exploratory by construction

The composite above is a model built by hand. The complement is to let a model
choose its own elements from the whole pool and report which ones it wants. Two
rules keep the two from contaminating each other: the free model runs **only
after** the confirmatory comparison above is computed and recorded, and **it can
never revise the composite**. If the free model finds something the composite
missed, that is a new hypothesis for a later study, not a correction to this one.

### Sampling and validation (Matthew, 2026-08-17)

**Keep every member-level row.** O\*NET elements are constant within an
occupation, but the model is not given occupation alone: member-level features
(birth decade, chamber, education level, prominence) vary within occupation, so
two teachers of different cohorts in different chambers are genuinely two
observations and the model should be free to learn probabilistic structure from
them. Aggregating to one row per SOC code would discard that.

**Validation is repeated random holdout over members.** The question this study
asks is descriptive — *which occupational properties travel with the register* —
not predictive of occupations never seen. A model that predicts partly through
an occupation's mean still answers the descriptive question, because the
features are what describe the occupation. So the primary design holds out
random subsets of members, repeatedly.

**Fixed training process, repeated, findings must survive.** The procedure is
specified once and not tuned per run: standardise on the training split, elastic
net over the pool, hyperparameters by inner cross-validation. It is then
repeated over many random holdout splits, and **only findings that survive
across runs are reported**. The deliverable per element is a selection
*frequency* across repetitions, not its presence in any one fit — regularised
regression picks one member of a correlated cluster arbitrarily, and which one
it picks is not a finding. Report clusters and frequencies; never a single
winning set.

**One secondary check, on one sub-question.** Random member holdout is neutral
for feature importance but mildly favours the free model in the *model
comparison*, because ~271 features can fingerprint an occupation and recall its
mean in a way a four-term composite cannot. So the comparison of (A)–(D) and the
free model is **additionally** run with whole occupations held out, and both
numbers are reported. If they agree, the point is moot; if they disagree, the
grouped number is the conservative one for that comparison only, and neither is
used to revise feature selection.

**Report what the free model costs.** If it beats a hand-built two-term model by
a trivial margin while selecting fifty elements, say so; the near-match by the
small model is then the more useful result.

### What would count as each outcome

- **Free model ≫ composite and ≫ class** — our hand-built theory is leaving
  signal on the table; the selected clusters name what we missed.
- **Free model ≈ composite** — the four hand-picked items captured what is
  there, which is the strongest possible support for the hypothesis.
- **Free model ≈ class, composite worse** — occupational structure predicts, but
  not through accountability; the hypothesis is wrong and EGP was adequate.
- **Nothing predicts out of sample** — the class U is chamber composition or
  noise, and §4.6a should be weakened accordingly. This outcome is live and
  should not be argued away.

## Exploratory follow-up, labelled as such

Matthew's reading of the police case is that they "nominally report to the
people," which is closer in kind to reporting to a rock face or a farm than to
reporting to an individual — an **abstract principal** rather than a person who
demands justification. O\*NET counts the writing but cannot see who the
principal is, so if the distinction is real the composite should systematically
over-predict abstract-principal occupations.

After the pre-registered comparison is run, examine which occupations the
composite most **over-predicts**, and ask whether they share that character
(police, military other-ranks, elected and public-facing roles) against
occupations answering to a named superior. This is exploratory, is not part of
the model comparison, and cannot be used to revise the composite.

## Known limitations, stated in advance

- **Prior occupation, not current.** Every member's present job is identical, so
  the claim is that formative occupational experience shapes register.
- **O\*NET is US-coded**, applied here to Australian, Canadian, Irish and UK
  occupational titles. Standard practice in comparative work, but a mapping
  assumption.
- **The mapping is a coding pass.** 7,421 occupation strings → SOC codes, via
  the same double-blind-with-adjudication harness used for the EGP coding
  (95.96% raw agreement), keyed off the coders' cleaned `coded_occupation`
  field rather than the raw Hansard strings.
- **Accountability will correlate with class.** That is the point of the model
  comparison; a composite that merely reproduces EGP is a null result.

---

## Coverage check, run 2026-08-17 BEFORE any model was fitted

As required above. SOC mapping completed by double-blind coding with
adjudication (`workflows/soccode.js` on arch-home for the two votes,
`workflows/socfinish.js` here for the remaining second votes and every
adjudication), then validated against O\*NET 30.3's published occupation list.

| quantity | value |
|---|---|
| occupations in pool | 4,402 |
| with a valid SOC code | 4,263 (96.8%) |
| member-occupation slots | 7,034 |
| slots with a code | 6,829 (97.1%) |
| **distinct SOC codes matched** | **470** of 1,016 in O\*NET 30.3 |
| top-10 codes cover | 45.0% of coded slots |
| top-50 / top-200 | 73% / 93% |

**The study is not collapsed onto a few dozen occupations**, which was the
failure mode this check existed to detect: 470 distinct occupations, with the
top 200 needed to reach 93% of slots. Occupational variety is adequate for
fitting occupation-level structure.

**Correction, 2026-08-18 — the check as written asked the wrong question.** It
tested whether a code is *valid*, not whether O\*NET *rates* it. O\*NET
publishes ratings for 894 of its 1,016 occupations; the remainder are mostly
"All Other" residual categories and the whole military block (`55-xxxx`). Of our
470 codes, **55 are unrated and cover 680 member slots**, so:

| coverage | value |
|---|---|
| slots with a valid code | 6,829 (97.1%) |
| slots with a **rated** code | **6,170 (87.7%)** |
| distinct codes, rated | 416 of 470 |

**87.7% is the number any model must report**, and the unrated 10% is not
missing at random — it is concentrated in residual categories and the military,
so members whose occupation resisted specific coding are exactly the ones who
drop out. Largest unrated: Military Officers, All Other (115 members),
Postsecondary Teachers, All Other (101), Public Relations Managers (49),
Community and Social Service Specialists, All Other (39).

Ten most common: Lawyers (1,051 members), Secondary School Teachers (458),
General and Operations Managers (324), Chief Executives (286), Farmers/Ranchers
(251), News Analysts and Reporters (226), Labor Relations Specialists (137),
Military Officers (115), Public Relations Specialists (115), Accountants (109).
Lawyers alone are 15% of coded slots, which is worth remembering when reading
any class-I result — the higher service class is heavily one profession.

### Coding quality, and one defect the design could not catch

Raw double-blind agreement **90.41%** (3,980 of 4,402 before adjudication), 421
adjudicated, 139 occupations honestly coded unknown. The two votes came from
Fable (arch-home's session model, inherited because the workflow names no
model); the second votes for the 727 singletons and **every adjudication** were
Opus at high effort, per Matthew's call. Worth recording that the instrument is
therefore not model-homogeneous.

Validating all 4,402 codes against the published taxonomy found **18 records
carrying codes that do not exist** — and **all 18 were in the AGREED set**.
Double-blind coding catches independent error; it cannot catch *correlated*
error, where both coders make the same mistake and the record never reaches
adjudication. (The adjudicator separately caught 26 invalid codes among the
disagreements, which is the same defect surfacing where the design could see
it.) All were near-misses with unambiguous intent — a real occupation's code
mistyped, or a retired 2010 SOC code — and were repaired by
`repair_soc_coding.py`, which documents each mapping. Zero invalid codes remain.

**The general lesson, which applies to the EGP coding too:** an external
validity check against the source taxonomy is not redundant with double-blind
agreement. It catches a different class of error, and it should be run on any
coded instrument this study relies on.

One inconsistency is recorded and deliberately NOT repaired: eight coal-mining
records split between `47-5041.00` (Continuous Mining Machine Operators) and
`47-5049.00` (Underground Mining Machine Operators, All Other). Both codes
exist and both are defensible for a bare "coal miner", so merging them would be
a re-coding rather than a repair.
