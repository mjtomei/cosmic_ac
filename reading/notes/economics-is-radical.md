# "Economics is breathtakingly radical if you take it seriously"

**Source:** Teles, in Loury & Teles, *The Glenn Show*, 29 July 2026, ~54:05.
Transcript: `teles-loury-2026-transcript.txt`. Sweep results:
`economics-radical-sweep.json`.

> "If you just look at the economic textbook, the basic one, it's breathtakingly
> radical if you take it seriously… There's a really incredibly sweeping and
> ambitious and radical agenda there if you want to take it… getting back some of
> the **radical energy that economics once had**. Not just being seen as the house
> doctrine of the establishment, but as a thing that allows you to do deep
> fundamental root-and-branch criticism of the status quo. That's what I tried to
> do in *The Captured Economy* with Brink Lindsey."

## Is he pointing at what we are? Structurally yes — and the match is closer than the podcast suggests

Not through *The Captured Economy*, whose four rent domains (finance, IP,
occupational licensing, land use) touch technology only via legal monopoly. The
match is his earlier essay, and it is close enough to quote.

**Teles, "Kludgeocracy in America," *National Affairs* 17 (Fall 2013)** —
fetched, verbatim:

> "Policy complexity is valuable for those seeking to extract rents… because it
> makes it hard to see just who is benefitting and how; **complexity so thoroughly
> obscures the actual mechanism of political action that it is difficult to
> mobilize** against it."

and

> "**Complexity is the friend of the organized and well-resourced.**"

Substitute *toolchain* for *policy* and that is §2.2.2 — the herd bound by
competence and encoding, unbound by legibility. He is describing our mechanism
in another domain, and he published it in 2013.

**And the term made a round trip.** Teles took "kludge" *from programming* to
describe policy. Bringing it back to computing is cheap, honest, and lets a
published author carry the framing.

He also extends Olson in a way we should adopt. From "The Scourge of Upward
Redistribution" (*National Affairs*, Fall 2015), his precursor essay:

> "Economists from Mancur Olson on have traced the political success of
> rent-seeking to the unbalanced incentives to organize… **the problem extends
> even further than imbalanced organization. Many of the most powerful forms of
> upward-redistributing rent-seeking take place in obscure decision-making
> contexts.**"

*Obscurity*, not merely diffuseness. That is the sharper version of our argument
too: optimization goes unpooled not only because the beneficiaries are diffuse
but because the thing being forgone is illegible to them.

## Where they genuinely differ

His failure is **extraction** — incumbents capturing rules to collect rents.
Ours is **omission** — a non-rival good nobody supplies because no one captures
its aggregate return. Rent-seeking has a beneficiary; under-provision does not.
Same engine (Olson), sibling failure modes, different remedies: remove the
capture versus pay someone to supply the thing.

## The expansions worth having

**Olson, "Big Bills Left on the Sidewalk: Why Some Nations are Rich, and Others
Poor," *JEP* 10(2), 1996** — the single best find. Large, well-understood gains
sit unexploited because institutions do not organise to capture them. That is
this paper's thesis in economics language, from the author §2.1 already cites.

**Olson, *The Rise and Decline of Nations* (1982)** — accumulated distributional
coalitions *retard the adoption of new technology* and the reallocation of
resources. The paper cites Olson 1965 for free-riding; 1982 supplies the other
half, so the bridge exists inside an author already on the page.

**Frischmann, "An Economic Theory of Infrastructure and Commons Management," 89
*Minn. L. Rev.* 917 (2005)** — the closest published form of our technical
claim: non-rival infrastructure yields externalities suppliers cannot
appropriate, markets under-provide it, commons management is the corrective.
Full text grepped: 31 hits for "free rid", **zero for "rent-seek"** — which is
exactly the gap.

**Bessen & Nuvolari, "Diffusing new technology without dissipating rents,"
*Industrial and Corporate Change* 28(2)** — models *why* inventors share freely
with competitors without destroying their returns. This is the missing published
answer to "who pays to defect into the commons," which §5 currently argues from
fitness rather than from a model.

**Gutiérrez & Philippon, NBER w24700** — federating enforcement *above* the
captured level defeats concentrated interests: "countries in a single market
willingly promote a supranational regulator that enforces free markets beyond
the preferences of any individual country." A published precedent for the
federation and underwriter arguments.

**The state-capacity cluster, rigorous versions rather than the trade books:**
Bagley, "The Procedure Fetish," 118 *Mich. L. Rev.* 345 (2019); Moynihan,
"Rescuing state capacity," *JPAM* 2025 (best single scholarly cite);
Moynihan, Herd & Harvey on administrative burden (2015) — with the important
finding that burden "will often be a **deliberate political choice** rather than
simply the product of historical accident or neglect." Pahlka quantifies the
accretion: the DoD 5000-series went from 7 pages to 2,000+ in 53 years, about
11% a year, and "we lack the tools for procedural deflation."

## The absence, confirmed — and how to handle it

**Nothing published bridges policy-capture economics to technical
under-provision of shared computing infrastructure.** Searched across Crossref,
OpenAlex full text, arXiv and Unpaywall on rent-seeking × open source, capture ×
technological stagnation, collective action × semiconductor tooling, compiler ×
public good. Zero hits. Frischmann has the infrastructure half without the
capture half; Teles has the capture half without the technical half.

Per the project's convention: **do not claim the bridge.** Assemble it from
Olson 1982 + Frischmann 2005 + Teles 2013 and let three published authors carry
the weight. State the absence once, quietly, if at all.

## Cautions

- **Lemley, "Property, Intellectual Property, and Free Riding," 83 *Tex. L. Rev.*
  1031 (2005)** is the live objection: uninternalised positive externalities are
  the *normal and desirable* state of an information economy, so under-provision
  inferred from unappropriated spillover is not by itself a market failure. §9
  should carry this.
- **Do not cite the abundance movement's headline number** — and note that the
  first version of this bullet got the contest wrong in two ways, corrected
  2026-08-05 against Greaney's actual text. **What is contested, precisely:**
  the *published* Hsieh & Moretti (2019, *AEJ:Macro*) claim is that easing
  land-use restrictions in three high-productivity cities "would have increased
  GDP in 2009 by 3.7%." The widely-quoted "lowered aggregate US growth by 36
  percent from 1964 to 2009" is the earlier working-paper framing of a
  *different* quantity (growth over a period, not the GDP level in 2009); the
  NBER WP on disk here reports 8.9% of GDP and ">50% of aggregate growth."
  Never quote the working paper's numbers as "Hsieh and Moretti (2019)."
  **What Greaney actually shows**, and the distinction matters: a straight
  replication using HM's own model and data predicts deregulation would
  *decrease* output, traced to errors in their code; separately, HM's model is
  unit-dependent — results change with the arbitrary choice of population unit —
  so it is not well-specified. But his *amended* model gives **+0.02%**, which he
  states is "consistent with HM's conclusion that relaxing land-use regulations
  can increase output," only two orders of magnitude smaller. So the corrected
  counterfactual does **not** run the other way; the failed replication does.
  The honest summary is that the direction survives and the magnitude collapses.
  (Comment dated October 2023 despite the 2026 filename.)
- Yackee & Yackee (*Regulation & Governance*) survey 1,460 agency leaders across
  50 states and find agencies issue many rules quickly, so ossification fears
  "may be misplaced." Empirical counter-evidence to the procedure story.
- *The Captured Economy* itself was verified only bibliographically (Oxford UP,
  2017, 232 pp, via indexed reviews). "Kludgeocracy" is its argued core and *is*
  fetched — quote that instead.


---

## Addendum (2026-08-06): the absence, narrowed by the citation-graph pass

The "confirmed absence" above was overstated — keyword sweeps missed what a
citation walk found. Published planks now known: **Holmes & Schmitz 1995**
(Minneapolis Fed QR — insiders politically block technology adoption to protect
rents, modelled), **Akcigit, Baslandze & Lotti 2023** (*Econometrica* —
political connections raise firm survival while suppressing innovation, Italian
registry microdata), **Bessen 2020** (*JLE* — proprietary IT as the rent
instrument), **Goodman & Lehto 2023** (*Public Choice* — IP economics bridged to
knowledge-commons governance). The unclaimed part is only the specific span to
the computing stack's continuous optimization, and **Kärnä, Karlsson & Engberg
2022** (*Econ. Innov. New Tech.*) states that gap in print. Cite the planks,
let Kärnä carry the absence, still assemble rather than claim. Full report:
`~/reading/governance-and-state-capacity/00-CITATION-GRAPH.md`.
