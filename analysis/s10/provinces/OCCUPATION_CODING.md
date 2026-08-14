# Occupation coding — methods note

`occupation_coding.json`, 778 distinct occupation strings covering 1,071 member
records across eight provincial legislatures (ON 160, BC 159, SK 108, NS 95,
NL 81, MB 73, AB 72, PE 40 strings). Each string is coded to an EGP class
(Erikson, Goldthorpe & Portocarero 1979, seven-class collapse).

## How the codes were produced

Two independent Claude coding passes over the same rubric, blind to each other.
Each pass coded all 778 strings; the second pass was not shown the first pass's
answers, so agreement between them measures how determinate the strings are
rather than how persuasive one agent was. Every disagreement went to a third
agent who adjudicated from the rubric, with instructions to rule `unknown` where
both readings were defensible rather than split the difference. The rubric, the
batching and the prompts are in the workflow script that produced this file; the
rubric text was given verbatim and identically to both passes.

This replaced an earlier regex coder (removed from `class_origin.py` on
2026-08-13, with its post-mortem kept in that file's docstring). The regex
reached only **73% coverage**, and it mis-specified two rules in ways its own
output did not reveal: a `director` pattern swept communications directors and
associate producers into the higher service class, and Erikson's dominance
rule — which combines two *spouses* — was applied within a single person's
career list, so anyone who had ever been a director was coded as one. Together
those returned 81% "professional", which is not a credible distribution. The
decisive argument is not that the regex was wrong but that it could not report
a reliability figure about itself.

## Agreement between the two passes

**750 of 778 strings, 96.4% raw agreement.** 28 strings (3.6%) required
adjudication.

This is the instrument reliability figure. It is a raw percentage agreement, not
a chance-corrected coefficient; because the class distribution is heavily
concentrated in II, a kappa would be lower and would be the fairer number if one
were reported. Treat 96.4% as an upper bound on reliability, not as a kappa.

The number is also not independent evidence in the way two human coders would
be: both passes are the same model family reading the same rubric, so shared
priors will produce shared errors that agreement cannot detect. What agreement
does establish is that the codes are reproducible from the rubric rather than
improvised per string — which the regex could not establish at all.

Where the passes split, they split along the schema's real seams:

| disagreement | n |
|---|---|
| I vs II (scale of a managerial or professional post) | 7 |
| II vs V/VI (service class vs skilled manual) | 5 |
| II vs IVab (employee professional vs own-account proprietor) | 3 |
| II vs unknown | 3 |
| II vs none-political | 3 |
| none-political vs unknown | 2 |
| other (I/V-VI, IVab/unknown, V-VI/VIIab, III/unknown, VIIab/none-political) | 5 |

Confidence self-ratings across the final codes: 355 high, 392 medium, 31 low.
Roughly half the corpus is coded on a stated assumption rather than on a
directly named occupation.

## Distribution

Weighted by members, since "Lawyer" covers many members and a sixty-word career
description covers one.

| EGP | strings | members | % of members | NS-SEC three-class |
|---|---|---|---|---|
| I higher service | 116 | 186 | 19.7% | professional |
| II lower service | 325 | 435 | 46.1% | professional |
| III routine non-manual | 25 | 29 | 3.1% | intermediate |
| IVab petty bourgeoisie | 127 | 180 | 19.1% | intermediate |
| IVc farmers/smallholders | 39 | 53 | 5.6% | intermediate |
| V/VI technicians, skilled manual | 35 | 45 | 4.8% | working |
| VIIab semi/unskilled manual | 13 | 16 | 1.7% | working |
| none-political | 36 | 48 | — | not a class |
| unknown | 62 | 79 | — | not a class |

**NS-SEC three-class collapse** (of the 680 strings / 944 members that carry a
class): professional 66%, intermediate 28%, working 6%. IVc is mapped to
intermediate with the small-employer group, following ONS's treatment of
own-account farmers.

## unknown and none-political are kept apart

**62 strings (79 members) are `unknown`** — the source names a sector, an
employer or a tenure but no occupation or grade. "Senior positions in the oil
and gas industry" does not say rig hand or vice-president. These are gaps in the
record.

**36 strings (48 members) are `none-political`** — the source records only
elected or party roles (councillor, trustee, mayor, MLA, ministerial staffer).
That is not a coding failure: the source correctly records no pre-political
occupation.

The two are never merged. One is a hole in the measurement, the other is an
answer, and collapsing them would turn the answer into a hole. Both are also
kept out of the class distribution rather than being folded into a residual
category.

## Rubric ambiguities the adjudicators flagged

Fifteen of the 28 adjudications came with a note saying the disagreement
exposed the rubric rather than the string. These are findings about the
instrument, and they are quoted rather than paraphrased. Full text sits in the
`rubric_note` field of each record.

**Rule 1 contradicts itself on scale (occ0180, and behind the seven I/II
splits).**

> "Rule 1 contradicts itself: its worked example codes a managing director of a
> firm as I with no scale stated, while its closing sentence says prefer II
> wherever scale is not stated. Read together the workable rule is 'head of an
> actual firm is I unless the organisation is evidently tiny; functional
> directors and unspecified managers are II', and the rubric should say so."

**Rules 1 and 2 collide for heads of small firms (occ0084).**

> "Rules 1 and 2 collide for heads of small firms: rule 1 says default to II
> when scale is unstated, rule 2 says ownership goes to IVab, and neither says
> which fires when a president/CEO title implies ownership that the string never
> states."

**Rule 2's professional exception is written for partners only (occ0041,
occ0103).**

> "Rule 2 as written ('OWNERSHIP MOVES PEOPLE TO IV') reads as routing every
> own-account worker to IVab, and its carve-out is written only for partners in
> professional firms. That contradicts the parent scheme, where self-employed
> professionals and semi-professionals are coded on the profession and IVab
> holds small proprietors and artisans. The carve-out should be widened from
> 'partner in a professional firm' to 'anyone practising a profession or
> semi-profession on own account'."

**The class I exemplar list is a 1979 credential list (occ0020, occ0024).**

> "The rubric's class I exemplar list is a 1979 credential list (physician,
> lawyer, engineer, professor, accountant). Finance and investment professionals
> have no stated home in the I/II split… The rubric should say where
> uncredentialled business/finance professionals sit."

> "Standard ISCO-to-EGP mappings put computing professionals in I, so this
> string codes I or II purely as a function of whether the coder works from the
> rubric's list or from the conversion tables."

**Crosswalk-compatible or self-contained? (occ0385).**

> "Coder A's I is what the standard ISCO-88-to-EGP mapping gives for business
> professionals; coder B's II is what this rubric's text gives. Both are right
> about their source. The instrument should say explicitly whether it is a
> crosswalk-compatible instrument or a self-contained one — that single decision
> moves occ0020, occ0024, occ0385 and occ0607."

**Paramedics and health technologists sit on the schema's most consequential cut
(occ0388, occ0398, occ0472, occ0698).**

> "The rubric does not name paramedics, and this is its largest live gap in
> Canadian legislature records… ISCO-based EGP mappings put registered
> paramedics and certified health technologists in II as health associate
> professionals; this rubric's text puts uniformed and unsupervised technical
> staff in V/VI. That is the service-class/manual boundary, the schema's most
> consequential cut, decided by an unstated rule. Note both coders were
> internally inconsistent across the three paramedic strings, which is itself
> evidence the rubric, not the strings, is at fault."

All four were ruled V/VI for internal consistency. If a later pass moves them to
II, it should move all four.

**Rule 6 versus rule 7 when a political role is first-listed (occ0022, occ0703,
and behind the none-political/unknown and II/none-political splits).**

> "Rules 5, 6 and 7 do not say what happens when a rule-6 political item is
> first-listed and the remaining non-political item is itself uncodeable.
> none-political and unknown mean different things downstream — 'source records
> no pre-political occupation' versus 'source records one but does not specify
> it'… The rubric should state that none-political requires the political roles
> to exhaust the string."

**Rule 5 deflates within a single career (occ0221).**

> "Rule 5 was written against inflation (do not take the highest role anyone
> ever held), but applied inside a single item — 'police officer, rising to
> Superintendent' — it codes the entry grade of one continuous career and
> deflates just as systematically. The rubric should say that rule 5 selects
> between listed occupations, not between grades within one of them."

**Bare "consultant" strings have no convention (occ0281, occ0607).**

> "The workable line… is whether the string names a substantive professional
> field… or only a clientele or activity… The rubric names no such test, which
> is why four consultant strings in this batch split between coders across three
> different classes."

> "Whichever convention is adopted for bare consultant strings, it has to be
> written down and applied to all of occ0041, occ0281, occ0385 and occ0607
> together. At present each coder is inventing it per string."

**Youth and casual jobs are not marked as such (occ0772).**

> "These are casual, probably pre-adult jobs, and the rubric gives no way to
> mark a code as resting on a youth or vacation job rather than a career
> occupation. Coding them VIIab is faithful to the rubric but is not the same
> measurement as a career labourer, and there is no field carrying that
> distinction."

Taken together these concentrate on two boundaries — I/II and service/manual —
and both are load-bearing for the NS-SEC collapse. The 96.4% agreement figure
should be read knowing that the disagreements are not scattered noise but sit
exactly where the schema's cuts do.

## Standing caveat: destination, not origin

**These are the members' OWN occupations.** That is class *destination*. Class
*origin* — the thing the mobility literature is about, and the thing S10 needs —
requires the parental occupation strings, which are still being collected. The
parent-combination rules (dominance, main-earner, average) are implemented in
`class_origin.py` and sit idle until those strings land. Nothing in this file
should be reported as a class-origin distribution.

## Files

- `occupation_coding.json` — one record per string: `string`, `n_members`,
  `provs`, `egp`, `confidence`, `resolution` (agreed/adjudicated), `coder_a`,
  `coder_b`, `rationale`, `coded_occupation`, `other_occupations`,
  `rubric_note`. Both passes' raw codes are retained so the agreement rate can
  be recomputed by anyone.
- `occupation_strings.json` — the deduplicated input strings.
- `../class_origin.py` — arithmetic over this coding (`--dist`, `--origin`,
  `--unresolved`). It makes no coding judgements.
