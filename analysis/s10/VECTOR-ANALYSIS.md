# Style-vector analysis: methodology and results log

**2026-08-14.** Scripts: `build_member_vectors.py` (corpus pass),
`vector_analysis.py` (all analyses). Data: `member_word_vectors.json`
(per-member style-word counts, pre/post 2023 split), `scored_seg_texts.jsonl`
(every Pangram-scored 2025-26 prevalence segment in the eight Canadian
provinces, joined to its corpus speaker by seg_id and carrying its text).

## Methodology, exactly

**Vector.** For a speaker or text set: counts over the 407 Kobak style words,
divided by their own sum — a COMPOSITION vector describing which instrument
words are favoured, with overall rate divided out. Rate questions (how much
register) are §4.6/§4.6a's; everything here is about mix.

**Eras.** Members enter with ≥30,000 post-era (2023-26) words and ≥200
instrument occurrences; 1,356 qualify.

**Raw cosine is useless on these vectors** — every pool lands at ~0.98 against
every centroid because the common words (`this`, `their`, `these`) dominate.
All similarity below is on Z-SCORED vectors: each word standardised across the
1,356 members, so similarity is between *distinctive* mixes. This choice was
forced by the data and made after seeing the 0.98s; it is the standard fix,
but it was not pre-registered.

**Joins.** Verdict→member by seg_id through the corpus (1,531 segments
captured; the earlier speaker-string join matched only 243 of 840 and is not
used). Member→class via `occupation_coding.json` (double-blind Claude coding,
96.4% agreement). Member→education via the official files plus the all-source
pass, ladder levels only.

## Results

**1. AI usage by class** (300 scored segments joining to a class, machine
share word- and fraction-weighted):

| class | segs | machine % |
|---|---|---|
| I | 27 | **11.3%** |
| II | 181 | 5.7% |
| IVab | 60 | 2.5% |
| V/VI | 12 | 19.5% |

Class I uses the machines about twice as much as class II and four times
IVab — the inverse of the register-rate ordering. **Suggestive only**: 27
segments for class I, no cluster bootstrap yet, and V/VI's 19.5% on 12
segments should not be read at all. Direction held under two different join
methods.

**2. No natural clusters.** PC1 carries 71.3% of composition variance — the
space is a single continuum. Silhouettes fall monotonically in k (0.41 at k=2
to 0.17 at k=8) and never beat a shuffled null. No prior-free clusters exist
in member word-mix.

**3. Weak attribute alignment.** Best correlations of any top-5 PC: education
r = −0.19 (PC1), birth year r = +0.20 (PC4), class never above 0.17.
**Class, education and cohort live in the RATE of register use, not the mix.**
Consistent with the markedness null (§Appendix A item 13): the class effect is
a uniform scaling of the instrument.

**4. Machine-flagged legislature speech resembles no class.** Its z-scored
similarity peaks at +0.12 (IVab) and +0.14 (bachelor), against a human-scored
control that reaches +0.47 (II) and +0.48 (graduate). Machine text sits
outside the human class geometry rather than inside any tier of it.

**5. No per-member class pull.** For the 20 members with usable flagged text,
the shift from their own baseline mix to their flagged mix projects at
−0.007 (se 0.011) on the class axis. Null at this n.

**6. Post-training moves a model UP the class and education register.**
Z-scored similarity of generated traces to member centroids:

| set | nearest class | nearest education |
|---|---|---|
| llama3 base | II (+0.157) | bachelor |
| mistral base | II (+0.066) | professional |
| qwen3 base | II (+0.092) | professional |
| qwen3 **instruct** | **I (+0.155)** | **graduate** |
| mistral instruct | ~0 everywhere | — |

Base models sound most like class II — the teacher/journalist tier. The two
measurable instruct moves go DIFFERENT ways:

  qwen3    UP: class I +0.164, graduate +0.081, II->I axis −0.094 -> +0.116
  mistral  OUT: every human similarity shrinks toward zero (I −0.061,
           II −0.065, graduate −0.066, professional −0.076); the II->I
           projection does not move. Its instruct mix leaves the human class
           geometry — which is what the machine-flagged legislature speech
           looks like (result 4).

llama3 has no instruct trace in this set.

**The Claude traces decided it: OUT is the modal move.** Sonnet 5, Opus 5 and
Fable 5 (400 continuations each, same prompt pool, thinking off, generated
2026-08-14) are NEGATIVE against every human class and education centroid
(−0.04 to −0.17), show no direction on the II->I axis (+0.04 to −0.03), and
are the only sets positively similar to the machine-flagged legislature pool:
sonnet **+0.186**, fable +0.083, opus +0.032. The wild flagged text resembles
the frontier models that presumably wrote much of it, and neither resembles
any human class tier. qwen3's upward move is the outlier, not the pattern.

Register RATE differs sharply across the three (a side observation, rate not
mix): sonnet ~5,100 instrument occurrences per 100k words — half again the
human corpus level — fable ~3,400 (human-level), opus ~2,800 (below).

## Interpretation on the record (Matthew, 2026-08-14) — flagged as such

Two implications worth carrying, both interpretation rather than measurement:

**Post-training as class mobility for the register — REVISED after the
Claude traces.** The upward move was qwen3 only. The frontier pattern is
EXIT: post-trained models leave the human class geometry rather than climbing
it, and the wild machine-flagged speech sits where they sit. What survives of
the original observation: base models start at class II, and no post-trained
model stays there.

**The equalizer hypothesis** (Matthew's formulation, corrected 2026-08-14
after an earlier note misstated it as a forecast): this is an
INSTITUTIONAL-DESIGN claim, not a prediction about sociolinguistic drift. A
mechanism can be created for a legislature that is fairer INDEPENDENT of human
social dynamics — measure register and prevalence explicitly, control for
them, and the signaling §4.6a documents stops functioning as covert
information about class. The social games themselves are expected to PERSIST:
they are heuristics compensating for limited human understanding, and both the
games and the limits remain. The claim is that such mechanisms will arise
naturally wherever they are incentivized — a legislature with a stated goal of
fair representation being the canonical case — because an LLM intermediary
removes register as a mechanism of deception without requiring anyone's social
behaviour to change.

**Two paths to the mechanism** (Matthew, same session): it can be built
CONSCIOUSLY — a legislature adopts measurement and control as design — and it
may also be EMERGENT, arising on its own if these results hold and LLM usage
keeps rising. The emergent path runs directly through result 4: machine text
carries no class information in its mix, so every machine-drafted word in the
record is a word not carrying class signal, and equalization scales
mechanically with prevalence — no design required, no change in anyone's
social behaviour required.

The two paths have different observables, which is what makes the distinction
useful rather than rhetorical:

  designed   an institution names register/prevalence measurement in its
             rules; visible as policy, whenever it happens
  emergent   the §4.6a class gradients compress as prevalence rises;
             visible in this study's own yearly series

The compression corollary I earlier misattached to the hypothesis is exactly
the emergent path's observable — it belongs to that branch, not to the claim
as a whole. The designed path needs no gradient to move at all. Yearly
re-estimation (plans/S10-power-expansion.md, Tier 3) tracks the emergent one.

Item 1 cuts both ways for the hypothesis and should be kept next to it:
class I currently uses the machines most, so in the short run the intermediary
is adopted first by exactly the tier whose distinction it erodes.

## Next: power

The study's limiting factor is now member-level n — the small classes (III 29,
VIIab 16, secondary 40) and the 27-segment AI-by-class cells. Expansion plan
in `plans/S10-power-expansion.md`.
