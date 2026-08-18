# Pre-registration — what occupational property explains the register better than class?

Two base measures (account-giving and sociality), each varied by direction of
interaction; a signed prediction across the resulting six cells; and an ordinal
prediction across three occupational profiles.

**Written 2026-08-17; revised 2026-08-18. No O\*NET element has been joined to
a member, and no relationship between any element and the register has been
examined.** Registered because the hypothesis and the measures were formulated
*after* seeing the class inverted U (§4.6a), which makes the instrument
unusually flexible unless fixed in advance.

**Exactly what has been looked at, so the claim above is precise.** During the
SOC coding (§6.1b of METHODOLOGY) three things touched O\*NET data: which codes
carry ratings at all, used for the coverage check below; the element values of
`47-5041.00`, `47-5049.00` and `47-5081.00`, used to decide a coal-mining coding
question; and the O\*NET occupation list, used to validate codes. None of it
involved the register outcome, and no element has been regressed on anything.
Every revision logged in this file was made before any such fit.

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
direction enters as a modifier of both base measures rather than as a
separate construct — see the six-cell grid in the Specification.

## The instrument

O\*NET **30.3** (US Department of Labor), CC-BY 4.0, distributed as CSV at
`onetcenter.org/dl_files/database/db_30_3_csv/`. Element IDs below were verified
against `content_model_reference.csv` on 2026-08-17, which corrected three
errors in the first draft of this file: the item is **Written** Letters and
Memos; Documenting/Recording sits under technical activities rather than the
communication block; and "Structured versus Unstructured Work" no longer exists
in the taxonomy.

### M1, the account-giving measure (FIXED — no item added, dropped or reweighted)

The construct is **subordinate account-giving**: rendering your judgment into
prose for someone above you *and* not holding the final say over it. Reporting
and autonomy are two faces of one thing rather than two things (Matthew), so
both enter the composite, with the autonomy items **reverse-scored**.

Equally weighted mean of these six, each standardised across occupations. In
the Specification's grid these are **M1a**, the upward cell — the direction
modifier splits the rest of M1 out into lateral and downward variants:

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

**O\*NET's occupation-level education requirement is out.** An earlier version
gave the models that term — Job Zone / Education Level Required — as the
*supply* side of the two-factor account, against the demand the composite
measures. It is out (Matthew, 2026-08-18): occupations demanding upward
account-giving also demand education, so conditioning on it is over-control on
the causal path.

Do not confuse it with the **member's own education level**, a different
variable from the §4.6a class arm. That one is absent from Stage 1 for the same
reason, but appears in Stage 2 as one toggle among the study's existing
covariates — where its job is not to adjust the occupational measure but to sit
beside it on equal terms in the lattice.

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

### Coverage check (specified here; results at the end of this file)

O\*NET rates roughly 900 O\*NET-SOC occupations, and many of our 7,421 strings
will map to the same code, so **distinct SOC codes — not member count — is what
bounds the occupational variety available**. Report, before fitting: the number
of distinct SOC codes matched, the share of members mapped, the ten most common
codes with their member counts, and the share of members sitting in the top ten.
If the panel collapses onto a few dozen codes, the study is underpowered for
occupational structure regardless of how many members it has, and that should be
visible in advance rather than discovered in the results.

### Why sociality (M2) is a base measure and not a rival

RIASEC **Social** `1.B.1.d` may reproduce the class U on its own — the peak
(teachers, nurses, social workers, journalists) is the Social cluster nearly by
definition, the floor (farmers, miners, labourers) is **Realistic** `1.B.1.a`,
class I is Investigative/Enterprising, class III is Conventional. That makes it
a serious account of the same shape, defined by other people decades ago for
unrelated purposes.

It is a **sibling of account-giving, not a rival** (Matthew): any job requiring
interaction with an individual involves reporting to them in some sense, so the
two overlap by construction. What separates them is not whether interaction
happens but **which way it points** — which is why direction enters as a
modifier of both measures rather than as a construct of its own, and why the
six-cell grid in the Specification is the shape of the test.

If the sign pattern holds on M2's row but not M1's, the finding is about working
with people; if it holds on M1's but not M2's, it is about answering to them; if
it holds on both, the register belongs to the occupation that does both while
directing nobody. Those are three different papers, and the grid is what tells
them apart.

## Specification

**Revised 2026-08-18, before any O\*NET data was joined**, and logged rather
than applied silently. The first version fitted four competing models and gave
one of them a covariate the incumbent lacked. The structure below is Matthew's:
two base measures, each **varied by direction of interaction**, giving six
predictors plus their combination — direction is a *modifier* of the proxies,
not a rival construct.

Member-level, canonical spec (`member_level_estimation.py`): one observation per
legislator, equal weight, register z-scored within chamber against the chamber's
full member population, HC1 errors.

**No education term in Stage 1**, on either the occupation or the member
(Matthew): occupations demanding account-giving also demand education, so
conditioning is over-control on the causal path. The member's own education
level returns in Stage 2 as one lattice toggle among the study's existing
covariates, not as a privileged control. And **nothing is a
privileged control** — not education, not cohort, not class. Every predictor is
reported as a distribution across all subsets of the others (see the lattice
below), because establishing an effect absent the other covariates matters
equally to establishing it net of them, and which control set to prefer is not a
choice this study should be making on the analyst's judgement.

### The two base measures

- **M1 — account-giving.** Proxy for the inverse of freedom from reporting to
  individuals: how much the job consists of rendering judgment into prose for
  someone else, and not holding the final say.
- **M2 — sociality.** Working with people rather than things (RIASEC Social
  against Realistic, and the people-serving activities).

### Varied by direction, giving six

| | upward (a) | lateral (b) | downward (c) |
|---|---|---|---|
| **M1** account-giving | `4.C.1.a.2.j` Written Letters and Memos · `4.A.3.b.6` Documenting/Recording · `4.A.4.a.2` Communicating with Supervisors · `4.A.4.c.1` Administrative Activities · **+ `4.C.3.a.4` Freedom to Make Decisions and `4.C.3.b.8` Determine Tasks reverse-scored** | `4.A.4.a.3` Communicating with People Outside the Organization · `4.A.4.a.4` Establishing and Maintaining Interpersonal Relationships | `4.A.4.b.1` Coordinating the Work of Others · `4.A.4.c.2` Staffing Organizational Units · `4.A.4.c.3` Monitoring and Controlling Resources |
| **M2** sociality | `4.A.4.a.6` Selling or Influencing Others *(thin — see below)* | `1.B.1.d` Social minus `1.B.1.a` Realistic · `4.A.4.a.5` Assisting and Caring for Others · `4.A.4.a.8` Working Directly with the Public | `4.A.4.b.3` Training and Teaching Others · `4.A.4.b.4` Guiding, Directing and Motivating Subordinates · `4.A.4.b.5` Coaching and Developing Others |

Each cell is the equally weighted mean of its standardised elements. The
autonomy items sit in **M1a** because not holding the final say is what makes
reporting *upward* rather than merely frequent.

**One cell is thin and is declared so in advance.** O\*NET has no clean
"sociality directed at a superior" element; `4.A.4.a.6` Selling or Influencing
Others is the closest and is not a good fit, since influencing is as often
lateral or downward. **M2a is therefore the weakest of the six and a null there
is uninformative** — it must not be read as evidence against the pattern.

### Models — two stages

The study runs in two stages, and conflating them was an error in an earlier
draft (Matthew). **Stage 1 selects a measure. Stage 2 evaluates it properly
against everything else the study already knows.**

#### Stage 1 — which occupational measure, if any

Small and focused. The question is whether any of the six cells carries signal,
and what the sign pattern across them looks like.

    each of the six cells, alone            z ~ M1a            (x6)
    the six jointly                         z ~ M1a+…+M2c
    the combination, alone                  z ~ combined
    the incumbent, for scale                z ~ EGP class dummies

`combined` is the equally weighted mean of the six standardised cells. **It is
reported in its own models and never alongside its components** — a composite
and the terms it is built from are collinear by construction, and entering both
is degenerate. Each of these is also fitted with `birthdec` added, giving the
unconditional and cohort-adjusted reading of each, since establishing an effect
absent the other covariates matters equally to establishing it net of them.

The six cells are collinear, so the joint fit is what says which *direction*
carries the result; the alone-fits are for interpretation and for reading
attenuation against each cell's own baseline.

#### Stage 2 — the proper evaluation, with everything the study holds

Whatever Stage 1 settles on enters the joint model **as one more covariate
beside the study's existing member-level predictors** — cohort, EGP class,
education and prominence (§4.6a) — and the whole set is run as a specification
lattice so that no covariate is privileged as a control:

    toggles:  <settled occupational measure>
              birthdec        cohort
              EGP             class dummies, as one block
              education       the level categories, as one block
              prominence      log article length

Five toggles is 2⁵ = 32 specifications, each predictor appearing in 16. If
Stage 1 settles on the six cells rather than a single summary, the toggle count
rises accordingly (ten toggles, 1,024 specifications) — still seconds of
compute, so the lattice is always enumerated rather than sampled.

**What is reported per predictor**, over the specifications containing it:

- median coefficient and 5th–95th percentile range
- **share of specifications in the predicted direction** — the sign-stability
  statistic, which is what matters for a signed prediction
- share reaching nominal significance, as a descriptive count and *not* as a
  p-value
- the extreme specifications named: which controls have to be in or out to move
  it most

**The pattern statistic is five signs, not six.** M2a is pre-declared thin
(below) and is excluded from the count: a cell whose null we have already agreed
is uninformative cannot be allowed to vote on whether the pattern held. It is
still reported, with its predicted sign, as an ordinary cell.

**It is counted over the specifications that can exhibit it.** A specification
omitting M1c has no sign for M1c, so the five-sign pattern is only checkable
where all five pattern cells are present. That count is stated explicitly
alongside the share, so a count like "holds in 8 of 8" is never mistaken for one
out of the full lattice. The permutation test uses this same five-sign
statistic, so the null distribution is the distribution of the statistic
actually reported.

**Inference is not taken from the curve.** Reporting many fits guarantees some
will look good by chance. The test is a **permutation**: shuffle the register
outcome across members within chamber, re-run the entire lattice, 2,000 times,
and record how often the sign pattern arises and how extreme the median
coefficients get under the null. That gives a p-value for the *pattern* rather
than for any single specification.

This is specification-curve / multiverse analysis — both verified 2026-08-18:
Uri Simonsohn, Joseph P. Simmons & Leif D. Nelson, "Specification curve
analysis," *Nature Human Behaviour* 4, no. 11 (2020): 1208–14,
doi:10.1038/s41562-020-0912-z; and Sara Steegen, Francis Tuerlinckx, Andrew
Gelman & Wolf Vanpaemel, "Increasing Transparency Through a Multiverse
Analysis," *Perspectives on Psychological Science* 11, no. 5 (2016): 702–12,
doi:10.1177/1745691616658637. Its three steps — enumerate, display, joint
inference — are what Stage 2 implements.

**Pre-specified subsets**, fixed here and read off Stage 1: M1a against M1c
(does reporting up beat commanding down?); M1a+M2b (the drone profile proper);
the six with the autonomy items removed from M1a.

## Pre-specified predictions

### The sign pattern (Matthew) — the drone profile

The register is predicted to belong to the occupation that **reports upward,
serves laterally, and commands nobody**. As signs on the six cells:

| | upward (a) | lateral (b) | downward (c) |
|---|---|---|---|
| **M1** account-giving | **+** | **+** | **−** |
| **M2** sociality | (+) *thin — excluded from the pattern test* | **+** | **−** |

**M2a carries a predicted sign but is not counted.** The cell is thin by
construction (no clean O\*NET element for sociality directed at a superior), so
it is reported like any other cell and excluded from the five-sign pattern
statistic. Including a cell we have already declared uninformative would let a
coin-flip decide the headline.

### The ordinal prediction: free < managerial < drone (Matthew)

The sign pattern says which direction of interaction goes with the register. A
second, stronger claim is registered here: the three occupational **profiles**
should order, on register use,

    completely free   <   managerial   <   drone

- **free** — answers to nobody: high autonomy, low on every reporting cell.
  Farmers, sole practitioners, own-account tradespeople.
- **managerial** — commands others: high on the downward cells, moderate
  upward. Executives, general managers, senior administrators.
- **drone** — reports up and serves sideways while directing nobody: high M1a
  and M2b, low M1c and M2c. Teachers, nurses, social workers, caseworkers.

**Why managerial is predicted intermediate rather than lowest**, on this study's
own prior findings rather than on intuition:

- **Farmers sit at the floor** of the class table (IVc, −0.44σ, the lowest of
  seven categories) — the free profile's anchor, and lower than the manual
  classes.
- **Office-holders use less register than backbenchers** (33.69 against 35.11
  per 1,000; Appendix D.4) — the managerial profile suppresses it, but modestly,
  nowhere near the farmers' gap.
- **Class II is the peak** (+0.02σ against class I's −0.09σ) and is populated by
  precisely the drone occupations: ~300 teachers, 73 journalists, 63 nurses, 47
  social workers.

So managers are predicted to be pulled down by commanding but not to the floor,
because they still report upward to boards, ministers and shareholders — the
downward cell is negative but the upward cell is not zero for them. The free
profile has neither.

**How it is tested.** Each occupation is scored for similarity to the three
profiles (its standardised cell values against each profile's predicted signs),
assigned to whichever it most resembles, and the three groups' mean register z
compared. Two things are reported, and they answer different questions:

- **the peak** — drone against each of the other two, which is the load-bearing
  claim and the only refutable one;
- **the ordering** — free < managerial < drone, by Jonckheere–Terpstra trend
  test against the ordered alternative rather than three pairwise comparisons.

The trend test is reported whichever way the two lower profiles fall, so a
missed ordering is visible rather than absorbed into a null.

**What would refute it, and what would not (Matthew).** The load-bearing claim
is that **drone is the peak** — free and managerial both sit below it. Only that
can be refuted here:

- **managerial ≥ drone, or free ≥ drone** — refuting. Commanding others, or
  answering to nobody, would then go with *more* register than reporting upward,
  which no version of the hypothesis survives, and the Stage 1 sign pattern
  should be re-read accordingly.
- **managerial < free**, reversing the predicted order of the two lower
  profiles, is **not** refuting. Both remain below the drone peak and the shape
  is unchanged; what flips is only which of the two non-drone profiles sits
  lower. Recorded as a prediction missed on the ordering, not a hypothesis
  failed.

That second case is worth watching for its own sake rather than as a scoring
question. Every U we have measured so far — class, education, prominence in the
national chambers — has its peak one rung below the top, but we have never seen
one *side* of a U fall below the other in a way that distinguishes them, because
the two arms have always been the high-status and low-status ends of a single
ranking. Free and managerial are different: both are "not drone", but one
answers to nobody and the other commands. If the commanding side sits lower, the
suppression is coming from directing others rather than from lacking someone to
report to, which is a claim about mechanism that the class table cannot make and
this profile split can.

**The downward sign is what makes this falsifiable.** Every rival account
predicts something different there:

- **positive downward** → a *managerial* register: the form belongs to people
  who direct others, and this hypothesis is wrong.
- **flat across all three** → *sociality without hierarchy*: what matters is
  working with people at all, and direction is decoration. This is hypothesis
  (M2) winning over (M1) and is a different finding, not a weaker version of
  this one.
- **upward only, lateral null** → pure deference rather than the drone profile;
  the service half is doing nothing and the construct should be narrowed.

Confirmation requires the **pattern**, not any single cell. Two of six in the
right direction is not partial support, it is noise.

### The rest, in order

1. **The occupational cells add to EGP class.** Across the lattice,
   specifications containing the six cells outperform the otherwise-identical
   specifications without them, EGP present or absent. If they do not,
   occupational structure adds nothing beyond class and the hypothesis fails on
   its own terms.
2. **The sign pattern is stable, not merely present.** The headline is the share
   of the *pattern-eligible* specifications in which the full pattern holds —
   those containing every pattern cell — with that count stated explicitly so it
   is never confused with the size of the whole lattice. A pattern surviving
   most of them is a different result from one appearing in a favourable corner,
   and "some specification shows it" is not a finding. Cohort is expected to
   attenuate most, being the strongest predictor in the study and confounded
   with occupation, so each cell's with-cohort specifications are compared
   against its without-cohort ones directly; a pattern surviving only where
   cohort is absent is reported as a statement about generations rather than
   occupations.
3. **M1a is the strongest single cell.** If any one predictor carries the
   result it should be upward account-giving. If `combined` beats every
   individual cell by a wide margin, the construct is diffuse rather than
   specific and should be described that way.
4. **M2a is uninformative either way.** The cell is thin by construction
   (no clean O\*NET element for sociality directed at a superior), so a null
   there is a measurement gap, not evidence.
5. **Farmers are the diagnostic case.** EGP ranks IVc mid-table; the observed
   register places it at the floor. If the grid beats EGP anywhere, it is here:
   farmers should score low on M1a (nobody to report to) and low on M2b (working
   with land, not people).
6. **The manual classes are not a counter-case, and that must not be claimed as
   a success.** V/VI and VIIab score low on measured autonomy yet sit at the
   floor. Under the sufficient-not-necessary reading this is expected — they
   hold effective autonomy the nominal scales miss — but that reading was
   adopted *after* seeing them there, so it earns no credit unless the
   effective-autonomy score places them near farmers independently.
7. **Police are predicted to be MISSED.** Police other-ranks write heavily, so
   they score high on M1a, yet they sit at −0.200. Recorded as an expected
   failure in advance; no cell will be modified to accommodate them. A simple
   grid that misses one occupation is more informative than a bespoke rule that
   misses none.
8. **The two-factor account is NOT tested here.** It needs education in the
   model and education is deliberately out, so the cells absorb whatever
   education would have explained. No result here bears on demand-versus-ability;
   that becomes the follow-up if the grid succeeds.
9. **The military absence caps what any success can claim.** Military officers
   are the paradigm of M1a-high and M1c-low — the drone profile in its purest
   institutional form — and O\*NET rates no military occupation, so they are
   structurally absent. A confirmed pattern cannot be said to hold "generally"
   while omitting the occupation that instantiates it most sharply.

## Deferred to future work: the unconstrained model

An earlier draft carried a second arm here — train a maximally free model over
all ~271 rated elements and let it report which ones matter. **Deferred
2026-08-18 (Matthew)**, so this pre-registration covers only the confirmatory
comparison above and the study can be run and closed without waiting on it.

The design as worked out is kept in §8.6 of the write-up rather than discarded,
because its constraints were the useful part: keep every member-level row
(element values are constant within occupation, but birth decade, chamber,
education and prominence vary within it); a fixed training procedure repeated
over many random holdouts, reporting selection **frequencies** across runs
rather than one fit's chosen set, since regularised regression picks one member
of a correlated cluster arbitrarily; and a secondary grouped-by-occupation
holdout for the model-comparison leg alone, where a 271-feature model can
fingerprint an occupation in a way a six-item composite cannot.

Nothing above depends on it. If the confirmatory test succeeds, the free model
asks whether the hand-built composite left signal on the table; if it fails, the
free model asks whether anything occupational predicts at all. Either is a
better question once the pre-registered answer is on record.

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
- **The mapping is a coding pass, and its own instrument.** 4,402 distinct
  occupations (deduplicated from 6,200 codeable strings) → O\*NET-SOC, via the
  same double-blind-with-adjudication harness as the EGP coding, keyed off the
  coders' cleaned `coded_occupation` field. **Raw agreement 90.41%** — lower
  than the EGP pass's 95.96%, as expected against ~900 categories rather than
  seven. Not model-homogeneous: most first votes were Fable, while the 727
  singleton second votes and all 421 adjudications were Opus at high effort.
  Eighteen invalid codes survived agreement and were caught only by validating
  against the published taxonomy — see METHODOLOGY §6.1b on correlated error.
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
missing at random. Reviewed occupation by occupation on 2026-08-18, the losses
fall into three kinds, and only the third is a coding question:

| kind | slots | recoverable? |
|---|---|---|
| **military** (`55-xxxx`) | 203 | **no** — O\*NET rates 0 of its 19 military codes |
| specific occupations O\*NET happens not to rate | 179 | no — Public Relations Managers, Financial and Investment Analysts, Taxi Drivers, Paramedics, and every surgeon code |
| genuine "All Other" residuals | ~280 | no — the source strings name no discipline, branch or process |

The residual codings were audited and stand. "Professor" and "lecturer" with no
discipline really are *Postsecondary Teachers, All Other* against O\*NET's 25
discipline-specific codes; "factory worker" with no process really is
*Production Workers, All Other*; "professional engineer" with no branch really
is *Engineers, All Other*. One case is arguable — `29-1229.00` Physicians, All
Other (15 slots), where rated general codes do exist (`29-1216.00` General
Internal Medicine, `29-1229.02` Hospitalists) — and it is **deliberately left
alone**: re-coding an unspecified physician to General Internal Medicine because
that code carries ratings would be choosing a code for having data rather than
for being correct, which is fitting the instrument to the analysis.

**THE MILITARY LOSS IS A DIRECT WEAKNESS IN THIS TEST, not just missing data.**
Military officers are the paradigm case of the construct being measured —
hierarchical rank, standing orders, written reporting to a named superior, and
minimal nominal discretion. They are the occupation the accountability
hypothesis should predict most confidently, and they are entirely absent from
the instrument because O\*NET rates no military occupation at all. 203 member
slots, the second-largest unrated block. Any result must be read as excluding
the case that would have discriminated hardest, and a claim that accountability
drives the register cannot be supported by evidence that structurally omits the
most accountable occupation in the panel. If the composite succeeds, an
independent check on military members — via a non-O\*NET rating source — is the
obvious next test rather than an optional extra.

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
