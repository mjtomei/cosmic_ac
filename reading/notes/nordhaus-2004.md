# Reading notes — Nordhaus 2004 (read in full for S17, 2026-08-04)

"Schumpeterian Profits in the American Economy: Theory and Measurement,"
NBER Working Paper 10433, April 2004. Read against the PDF (37pp), not the
abstract. All numbers below checked against the text.

## What the paper does

Defines Schumpeterian profits as profits above the risk-adjusted normal
return, arising when firms appropriate returns from innovation. Builds a
small model, estimates it on BLS multifactor-productivity data for the US
nonfarm business sector 1948–2001, and concludes innovators capture ~2.2%
of the total present value of social returns to innovation (range across
specifications 1.3–3.3%).

## The model (the part S17 extends)

Two-period seed: innovation lowers cost C₀→C₁; the innovator prices at
P₁ = C₁ + a(C₀−C₁). `a` is the **fundamental appropriability ratio** —
the fraction of the cost saving the innovator captures at introduction.

Dynamic version: appropriability decays exponentially at rate λ, so an
innovation θ years old is appropriated at rate a·e^(−λθ). Erosion causes:
patent expiry/non-enforcement, **imitation**, superior successors, loss of
first-mover advantage (p.9 — imitation is named as a decay channel; this
is the hook for measuring λ via imitation lag).

Steady state with productivity growth h*:

    (6)  μ* = a·h*/(λ − h*)      — Schumpeterian profit margin

(the h* in the denominator because older innovations were made against
higher cost bases). Estimating equations (8)/(10) regress the BLS margin
on h(t) or h(t)/(λ−h(t)).

## The empirical results (verified against Tables 1–3)

- **a = 5.9–10.4%** across 8 specifications (annual/decadal ×
  linear/non-linear × level/difference); central value **0.07**.
  Robust to labor-productivity substitution (Table 3).
- **λ = 0.20/yr is NOT estimated — it is imposed a priori**, justified by
  patent-renewal data (Pakes & Simpson, BPEA 1989, fn.8). Table 2 sweeps
  λ ∈ {0.1, 0.2, 0.3, 0.4}: `a` is sensitive to λ, but the *margin* is
  not (0.42–0.79% of output across everything). The 10–25%/yr range in
  the R&D-depreciation literature is acknowledged.
- Capture ratio: combining a=0.07, λ=0.20 with economy growth g=3%/yr and
  discount rate r=10%/yr "implies that 2.2 percent of the total present
  value of social returns to innovation are captured by innovators"
  (p.22). Extremes over Tables 1–2: 1.3% and 3.3%.
- Schumpeterian profits ≈ **3.8% of total corporate profits** 1948–2001
  (Fig. 8; annual range −1.3% to +6.3%); ≈ **0.19–0.20 percentage points**
  of the rate of profit on capital (pp.34–35).
- The dynamic specification (eq. 7) failed on the data (cyclicality);
  only equilibrium specs are used.

**Caveat the paper states itself (p.18):** the method measures US
appropriation of US productivity growth; spill-outs abroad and spill-ins
from foreign innovation distort in opposite directions. Worth carrying —
S17's AI sector is far more internationally porous than 1948–2001 US
nonfarm business.

**The capture formula is not printed.** The natural continuous-time
derivation — private PV = a/(λ+r−g), social PV = 1/(r−g), ratio
= a(r−g)/(λ+r−g) — gives 1.8% at (a=.07, λ=.2, r=.10, g=.03), not 2.2%;
his 1.3–3.3% extremes are also not exactly reproduced by it. Presumably
his exact calculation differs in discretization or in an h* term. S17's
recompute therefore (i) states its formula explicitly, (ii) reports both
the formula value and Nordhaus's published 2.2% at his parameters, and
(iii) makes its headline the *ratio* of capture at measured λ to capture
at λ=0.2 — which depends only on (λ+r−g) factors and is insensitive to
the unprinted constant.

## The passage that hands S17 its thesis (pp.30–32, §V)

Nordhaus, on why the dot-com valuations implied implausible capture,
third reason: "the information revolution concerns information, which is
generally hard to appropriate... The low costs of imitation, transmission,
and distribution of information technologies are likely to erode the
value of property rights in intellectual property and reduce the
durability of Schumpeterian profits in the new economy." His example is
Encyclopedia Britannica vs free online encyclopedias — the depreciation
rate "is likely to be very high in new-economy sectors." S17 is this
paragraph, measured, twenty years on, with the imitator now a machine.
Also note his valuation arithmetic (pp.29–30): plugging capture ~7% into
the 1990s new-economy story supports ~$410B of excess value against the
~$5.8T the market priced — the same accounting move as
assets-rents-socialized-buildout.pdf, made in 2004 about the last bubble.
State the pair when drafting IV.3.

## Placement

- IV.2/IV.3: the capture-ratio baseline (2.2%) and the λ-recompute (S17).
- The 97.8% line: consumers get essentially all of it — Nordhaus's own
  framing ("passed on to consumers"), so the "prize is the 97.8%" framing
  builds on his conclusion rather than inverting it.
- Matched pair with assets-rents: the report says valuations need durable
  moats; Nordhaus's machinery prices the moat's depreciation directly.
