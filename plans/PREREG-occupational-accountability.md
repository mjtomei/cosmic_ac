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

An earlier framing used autonomy ("freedom to make decisions") and was rejected
before testing, for a reason that is itself part of the hypothesis: **a farmer
and a miner are about equally unfree, but their requirements are imposed by the
natural world rather than by a person.** Freedom conflates constraint-by-nature
with constraint-by-authority; only the second is predicted to generate the
register.

## The instrument

O\*NET **30.3** (US Department of Labor), CC-BY 4.0, distributed as CSV at
`onetcenter.org/dl_files/database/db_30_3_csv/`. Element IDs below were verified
against `content_model_reference.csv` on 2026-08-17, which corrected three
errors in the first draft of this file: the item is **Written** Letters and
Memos; Documenting/Recording sits under technical activities rather than the
communication block; and "Structured versus Unstructured Work" no longer exists
in the taxonomy.

### The confirmatory composite (FIXED — no item may be added, dropped or reweighted)

Equally weighted mean of these four, each standardised across occupations:

| element ID | name | block |
|---|---|---|
| `4.C.1.a.2.j` | Written Letters and Memos | Work Context |
| `4.A.3.b.6` | Documenting / Recording Information | Work Activities |
| `4.A.4.a.2` | Communicating with Supervisors, Peers, or Subordinates | Work Activities |
| `4.A.4.c.1` | Performing Administrative Activities | Work Activities |

Entered as **separate covariates**, not folded into the composite, so autonomy
and literacy stay distinguishable from accountability:

| element ID | name | why separate |
|---|---|---|
| `4.C.3.a.4` | Freedom to Make Decisions | the autonomy axis this hypothesis rejects as insufficient |
| `4.C.3.b.8` | Determine Tasks, Priorities and Goals | second autonomy item, replaces the retired structured/unstructured scale |
| Job Zone / education | required education | literacy resources, the supply side of the two-factor account |

### The exploratory pool (for the free model only)

About 215 rated elements, none of which may inform the composite:

- **Work Context** `4.C.*` — 59 leaves, including the deliberate negative
  controls *Spend Time Sitting* `4.C.2.d.1.a`, *Indoors, Environmentally
  Controlled* `4.C.2.a.1.a`, *Physical Proximity* `4.C.2.a.3`. If those predict
  as well as the composite, the model has found "office job", not language.
- **Work Activities** `4.A.*` at the rated level — notably *Interpreting the
  Meaning of Information for Others* `4.A.4.a.1`, *Communicating with People
  Outside the Organization* `4.A.4.a.3`, *Assisting and Caring for Others*
  `4.A.4.a.5`, *Selling or Influencing Others* `4.A.4.a.6`, *Performing for or
  Working Directly with the Public* `4.A.4.a.8`, *Training and Teaching Others*
  `4.A.4.b.3`, *Providing Consultation and Advice to Others* `4.A.4.b.6`,
  *Evaluating Information to Determine Compliance with Standards* `4.A.2.a.3`.
- **Skills** `2.A.*`, `2.B.*` — *Writing* `2.A.1.c`, *Speaking* `2.A.1.d`,
  *Reading Comprehension* `2.A.1.a`, *Active Listening* `2.A.1.b`, *Persuasion*
  `2.B.1.c`, *Instructing* `2.B.1.e`, *Social Perceptiveness* `2.B.1.a`,
  *Service Orientation* `2.B.1.f`.
- **Knowledge** `2.C.*` — *English Language* `2.C.7.a`, *Communications and
  Media* `2.C.9.b`, *Education and Training* (2.C.6 branch), *Sociology and
  Anthropology* `2.C.4.f`, *Psychology* `2.C.4.e`, *Therapy and Counseling*
  `2.C.5.b`, *Law and Government* `2.C.8.b`.
- **Interests** — RIASEC `1.B.1.a`–`1.B.1.f` (Realistic, Investigative,
  Artistic, **Social**, Enterprising, Conventional) and the 41 basic-interest
  scales `1.B.3.*`.

**A rival hypothesis worth naming in advance.** The RIASEC **Social** scale
`1.B.1.d` may reproduce the whole class U on its own: the peak (teachers,
nurses, social workers, journalists) is the Social cluster nearly by
definition, the floor (farmers, miners, labourers) is **Realistic** `1.B.1.a`,
class I is Investigative/Enterprising and class III is Conventional. A
Social-minus-Realistic contrast is two numbers, defined by other people decades
ago for unrelated purposes, and if it beats both the accountability composite
and EGP then the finding is about working-with-people rather than about
answering-to-people. That is a different claim and should not be reported as a
confirmation of this one.

## Specification

Member-level, matching the canonical spec in `member_level_estimation.py`: one
observation per legislator, equal weight, register z-scored within chamber
against the chamber's full member population, HC1 errors.

    z  ~  accountability + freedom + required_education   (+ birth decade)

against the incumbent model

    z  ~  EGP class dummies                               (+ birth decade)

Model comparison on the **same members**, by adjusted R² and by whether each
block survives the other's inclusion.

## Pre-specified predictions

1. **Accountability is positive and survives** freedom and required education.
2. **Farmers are the diagnostic case.** EGP ranks IVc mid-table; both the
   composite and the observed value place it at the floor. If the composite
   beats EGP anywhere, it should be here.
3. **Police are predicted to be MISSED.** Police other-ranks write heavily
   (incident reports, statements, court files), so they will score high on
   Documenting and Letters-and-Memos, but they are observed at −0.200. This is
   recorded as an expected failure **in advance**, and the composite will NOT be
   modified to accommodate it. A simple combination of existing scales that
   misses one occupation is a more informative result than a bespoke rule that
   misses none.
4. **Two-factor outcome is the most likely.** Accountability negative-at-the-top
   and required-education positive-at-the-bottom would produce the observed U as
   the product of two crossed gradients, and would explain why education showed
   the same shape while being statistically inseparable from class.

## The free model (Matthew, 2026-08-17) — exploratory by construction

The composite above is a model built by hand. The complement is to let a model
choose its own elements from the whole pool and report which ones it wants. Two
rules keep the two from contaminating each other: the free model runs **only
after** the confirmatory comparison above is computed and recorded, and **it can
never revise the composite**. If the free model finds something the composite
missed, that is a new hypothesis for a later study, not a correction to this one.

### The trap this design has to avoid

Register is measured per member; every O\*NET element is constant within an
occupation. Roughly 5,000 members will map to perhaps 600–900 distinct SOC
codes, so for learning occupation-level structure the effective sample is the
number of **occupations**, not members. Three hundred lawyers are one
observation of "lawyer". Fitting ~215 heavily collinear elements against ~700
effective observations will select confidently and replicate nothing.

### Consequently

1. **Aggregate to SOC**, or cluster all errors on SOC. Never let member count
   stand in for occupational variety.
2. **Regularise** — elastic net over the standardised pool, alpha and lambda by
   cross-validation *at the SOC level* so no occupation appears in both folds.
3. **Stability selection.** Bootstrap the fit and report selection *frequency*
   per element, not a single chosen set. Lasso picks one member of a correlated
   cluster arbitrarily, and which one it picks is not a finding. Report clusters,
   not winners.
4. **Held-out evaluation**, with the accountability composite, the RIASEC
   Social-minus-Realistic contrast, and EGP class all scored on the **same**
   held-out occupations. The deliverable is a three- or four-way out-of-sample
   comparison, not a coefficient table.
5. **Report what it costs.** If the free model beats the composite by a trivial
   margin while selecting fifty elements, say so; a hand-built two-term model
   that nearly matches a fifty-term one is the more useful result.

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
