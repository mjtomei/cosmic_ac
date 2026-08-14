# The inverted-U in register by class: what the literature already says

**Status: framing note, partially verified.** Citations below were gathered
2026-08-13 by direct fetch of reference pages, not from the primary texts. Two
are known-suspect and are flagged. Nothing here should enter the paper before
someone opens the actual books.

## The result this is trying to place

Register rate by EGP class, within province, year fixed effects, word-weighted,
baseline = class I (`covariate_study.py`, `occupation_coding.json`):

| class | | vs I | t | members |
|---|---|---|---|---|
| III | routine non-manual | **+2.00** | 4.98 | 29 |
| II | lower service | **+0.84** | 4.23 | 435 |
| IVab | petty bourgeoisie | **+0.80** | 3.24 | 180 |
| I | higher service | — | — | 186 |
| V/VI | skilled manual | +0.21 | 0.34 | 45 |
| IVc | farmers | −0.24 | −0.58 | 53 |
| VIIab | semi/unskilled manual | **−1.66** | −4.22 | 16 |

Not monotone in status. An inverted U with the peak one to two rungs BELOW the
top. The three-class NS-SEC collapse destroys it, because it pools III with IVc
and V/VI with VIIab and the opposite signs cancel — the collapsed version reads
professional 35.5 / intermediate 35.3 / working 34.9, i.e. nothing.

Matthew's reading, which is sharper than "familiarity with institutional
prose": the bottom is unfamiliar with the register or actively rejects it as
untrue to themselves; the middle is familiar but has not mastered it, and so
overuses it for signalling; the top uses it correctly, which means sparingly.

## That is hypercorrection, and it is a named finding

**Labov's crossover pattern.** In the New York City stratification work,
lower-middle-class speakers produce the prestige variant (rhotic /r/) at higher
rates than upper-middle-class speakers do, and the gap is largest in the most
self-conscious styles. Labov coined "linguistic insecurity" for the attitude
behind it. The shape — second-highest group exceeding the highest — is exactly
our III/II over I.

  - Labov, W. *The Social Stratification of English in New York City* (1966).
  - Labov, W. *Sociolinguistic Patterns*. **VERIFY**: the reference page gave
    "1991, University of Philadelphia Press", which is wrong on both counts —
    the book is 1972, University of Pennsylvania Press. Fix before citing.
  - Labov, W. "Hypercorrection by the Lower Middle Class as a Factor in
    Linguistic Change", in *Sociolinguistics: Proceedings of the UCLA
    Sociolinguistics Conference 1964*. **VERIFY** the 1985 De Gruyter reprint
    date against the 1964/1966 original.

**Linguistic insecurity, measured.** The lower middle class scores highest, and
the described signature is "wide range of stylistic variation, fluctuation in
given stylistic contexts, conscious striving for correctness" — which is the
mechanism Matthew's middle tier proposes, stated in the 1960s.

  - Owens, T. & Baker, P. (1984), Index of Linguistic Insecurity, validated in
    **Winnipeg**. Directly relevant: Manitoba is one of our eight chambers, and
    an existing Canadian ILI instrument is a possible external comparator.
  - Winford, D. (1978), phonological hypercorrection in Trinidadian English.
  - Canut & Keita (1994), Mandingo/Bambara continuum, Mali.

**The class-signalling frame.** Bourdieu's cultural capital and symbolic
violence give the general form: dominated groups define themselves in the terms
of the dominant aesthetic. The petit-bourgeois-anxiety strand that would map
most directly onto the middle tier was NOT confirmed in what was fetched, and
needs checking in the text.

  - Bourdieu, P. *Distinction: A Social Critique of the Judgement of Taste*
    (1979; English translation 1984).
  - Elias, N. *The Civilizing Process* (1939) — named alongside it.

## Chase-and-flight: the better account of what we actually measured

Matthew, 2026-08-13, on finding that class I has the LOWEST share of the
most-risen style words while every other class sits above it: the top signals
by ABSENCE. As the marker is copied, its grossest forms are abandoned so the
signal keeps its value.

That is the trickle-down or chase-and-flight theory of fashion, and it is old.

  - **Rudolf von Jhering**, *Der Zweck im Recht* (1883) — the earliest
    statement. Durkheim's summary has fashion, once universally adopted,
    "condemned by its very nature to renew itself continuously".
  - **Thorstein Veblen**, *The Theory of the Leisure Class* (1899) —
    conspicuous consumption, with the upper class seeking new extravagances
    specifically to separate from those imitating the old ones.
  - **Georg Simmel**, "Fashion", *International Quarterly* (1904) — the
    canonical version: lower groups imitate to gain status, elites move on to
    preserve differentiation, and the cycle is the mechanism of change itself.
  - **Stanley Lieberson**, *A Matter of Taste: How Names, Fashions, and Culture
    Change* (Yale University Press, 2000) — **the closest parallel available**,
    because its markers are DISCRETE LEXICAL ITEMS. First names diffuse down
    the status ladder and are abandoned by higher-status parents once common,
    measured quantitatively over long series. That is our situation with style
    words substituted for names. **VERIFY** the mechanism against the book;
    the reference page confirms the title and thesis but not the detail.

WHY THIS BEATS BOTH EARLIER READINGS. Hypercorrection predicts the tilt toward
marked forms peaks in the MIDDLE. It does not — the strongest tilts are VIIab
(+1.76pp) and IVc (+1.66pp), the two classes with the lowest overall register
rate. Familiarity-with-institutional-prose predicts no compositional
difference at all. Chase-and-flight predicts exactly what is there: one group
avoiding the marked end while everyone else uses it freely.

AND IT IS SEPARABLE FROM THE YEAR CONFOUND, which the other readings were not.
A static composition difference — class I over-represented in earlier years,
when the marked words were rarer — reproduces the cross-sectional table
exactly. But chase-and-flight makes a DYNAMIC prediction that composition
cannot: class I's relative use of a given word should FALL as that word's
overall popularity RISES. Within word, over time. `build_class_word_year.py`
produces the (class, year, word) counts that test it.

## The assumption the whole reading rests on

Hypercorrection requires that speakers PERCEIVE the variant as prestigious and
are reaching for it. Our variant is machine-associated. So the reading commits
to a specific claim: that this register reads to legislators as polished,
professional, authoritative — not as "sounds like a chatbot".

That claim is testable and is not yet tested.

**A prestige-inversion prediction was drafted here and withdrawn** (Matthew,
2026-08-13). The idea was that once the register became publicly legible as
machine-written its prestige would invert and the middle tier would abandon it
fastest, giving the study a dated falsification target. Two objections, both
correct:

  - It assumed this work reaches enough people to move the variable. It will
    not. A study that has to be widely publicised to generate its own test
    condition is not making a prediction, it is hoping for an audience.
  - More seriously, it mistakes the depth of the thing. A register absorbed
    through daily contact with the machines that produce it is not held in
    place by an audience's ignorance of where it came from, and self-
    consciousness from reading an article does not reach that deep. Awareness
    and entrenchment operate on different timescales and entrenchment is
    winning by orders of magnitude.

WHAT THAT COSTS THE HYPERCORRECTION READING is worth being honest about. If
awareness cannot move the variable, then prestige-seeking is hard to separate
from plain exposure — and exposure has its own account of the inverted U,
since class II and III work is saturated in institutional prose while class I
professions write in their own trained genres. The cross-section cannot
distinguish "reaching for a prestigious form" from "steeped in the source
material". Both predict the same curve. Saying which one it is needs evidence
the register level alone does not carry.

## What would sharpen it

1. **Cluster the standard errors by member.** III and VIIab rest on 29 and 16
   people and the current t-statistics treat repeated years as independent.
   This is the first thing to do and may leave only II and IVab standing.
2. **Test the signalling mechanism through markedness.** If the middle overuses
   for signal while the top uses correctly, the middle's excess should
   concentrate in the most conspicuous instrument words rather than spreading
   evenly. Per-class word-level rates would show this.
3. **Test it through genre.** Signalling should be strongest where the audience
   is largest — prepared statements over spontaneous exchange. §4.3 already
   established that drafting concentrates in prepared business; the class
   interaction is the new part.
4. **More chambers, not more members.** III and VIIab cannot be grown within
   these eight provinces; there are not many former flight attendants or
   sawmill workers in provincial legislatures.
