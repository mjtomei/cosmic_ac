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

O\*NET (US Department of Labor), which publishes numeric per-occupation ratings
on standard scales. The composite is fixed here as the **equally weighted mean
of the four scales below, each standardised across occupations**:

| O\*NET element | block | direction |
|---|---|---|
| Letters and Memos | Work Context | + |
| Documenting / Recording Information | Generalized Work Activities | + |
| Communicating with Supervisors, Peers, or Subordinates | Generalized Work Activities | + |
| Performing Administrative Activities | Generalized Work Activities | + |

**Freedom to Make Decisions** enters as a SEPARATE covariate, not as part of the
composite, precisely so that "accountability" and "autonomy" can be told apart.
**Education Level Required** (or Job Zone) enters as a second separate covariate,
because producing this register plausibly requires literacy resources
independently of any demand for it.

No item will be added, dropped or reweighted after the join. If the composite
needs adjustment to fit, that is a negative result, not a calibration step.

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
