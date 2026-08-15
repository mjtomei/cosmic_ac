# S18 — The negotiated-cession regime: extending the Fable–Carson cyber-cost model

Question (Matthew, 2026-08-10/15): **what has to be true for it to be
economically and personally beneficial for a human or company to cede control
of their own compute in certain negotiated cases — to where the meaning of
malware, compromise, and ownership changes? And how does that change the
model?**

Base model: Fable, C. & Carson, B. (2026), *Projected Cyber Security Costs
from Frontier AI: A Response to Tyler Cowen*, doi:10.5281/zenodo.21879325,
github.com/bradrcarson/cowen-cyber @ fc73ac89, CC-BY 4.0. Their headline was
reproduced exactly from their untouched code before anything here was built
(2028: anchored median $107.2B / mean $240.6B, fresh $122.9B / $282.6B,
P(>$200B) 38.0% / 40.5% — matching their published RESULTS_SUMMARY.md to the
decimal; run 2026-08-15, seed 20260810, 10⁴×10⁴).

## Read this first: where defense lives in their model (Q3, by inspection)

**Defense in the Fable–Carson engine is a per-regime severity-truncation
haircut and nothing else.** Their own config notes state "the placeholder
detection/patch/containment machinery is removed." The offense side of
autonomy is fully modeled (S3b: an 8-parameter fresh agentic event tree,
autonomous campaigns/yr, agentic self-propagation as common-shock factors,
anchored to the Hugging Face and Anthropic postmortems); the defense side is
one number per regime. Continuous autonomous defense — agents persistently
hunting, patching, containing — **structurally cannot appear in this model
except as a regime label**. That is the sharp form of Matthew's 2026-08-10
objection, conceded by the paper itself from the other side (defense-dominant
gets the lowest sealed weight because 2–3 years is too short for
enterprise-wide deployment). It also bounds this study: our
negotiated-cession regime necessarily enters through the same narrow door
(see Honest limits).

## What we built

A fourth regime, **negotiated cession**, added to their three-regime mixture
in their own parameter vocabulary, plus the microeconomic crossover that
would rationalize it, plus a labeled horizon extension to 2032.

The regime, in one paragraph: a material share of endpoints runs
manufacturer-partitioned shared-execution domains (S16 Case 3/4 —
hardware-partitioned, owner-untouchable, underwriter-insured), and access to
them is **sold under negotiated contracts rather than taken by
exploitation**. Unauthorized becomes unnegotiated; compromise becomes
breach-of-contract; ownership becomes residual control rights over a
negotiated bundle (Grossman–Hart 1986 / Hart–Moore 1990).

| File | What it is |
|---|---|
| `engine_ext.py`, `counterfactual_ext.py` | Their engine, forked (CC-BY, provenance headers); every change marked `# S18-EXT`: fourth regime, per-regime transfer share, `years=`/`regimes=` params, chained D-15 damping. |
| `params_sealed.json` | Their sealed parameters, vendored unchanged. |
| `cession_params.py` → `params_cession.json`, `cession_regime_params.csv` | The 8 cession-regime priors — **all OURS**, each with p10/mode/p90, encoding, anchor, and source. |
| `run_cession.py` → `per_regime.csv`, `mixture_2028.csv` | 2027–28 four-regime runs: each regime's own distribution + the sealed mixture with cession mixed in at w_c ∈ {0, .05, .10, .25, .50}. |
| `crossover.py` → `crossover.csv` | **The S16×S18 join (the novel number)**: per-machine cession-vs-defense inequality solved for the crossover rent rate R*, by isolation case, incident probability, severity tier, hardware tier, enterprise/household. |
| `horizon.py` → `horizon.csv` | 2027–2032 roll (OUR construction), baseline arm vs cession-phase-in arm, with the rent ledger side-by-side. |

Reproduce: `python3.12 -m venv venv && venv/bin/pip install numpy scipy`,
then run the four scripts in the order of the table. Full-size runs
(`--full`) take ~10 and ~30 minutes.

## The cession regime's parameters (all ours; their vocabulary)

Full documentation with encodings in `cession_regime_params.csv`. The four
channels and the one counter-channel:

1. **Attack surface falls** — S1 frequency mult 0.90/1.05/1.30 (balanced
   shaded ~8–10% for displacement of the compute-acquisition slice of volume
   crime — the unnegotiated botnet/cryptojacking market of Anderson et al.;
   fraud/BEC, the bulk of S1 dollars, unchanged); S3a probability
   mult 0.9/1.3/2.0 (attested access shrinks the exploitable initiation
   surface).
   S2 frequency and severity shift carried from balanced unchanged.
2. **Blast radius bounded** — severity truncation 20/35/55% vs
   defense-dominant's 15/25/40: S16's two-factor decomposition (a correlated
   boundary failure converts to per-machine reimaging unless the attacker
   independently defeats each firm's own IT), Case-3 elimination of the
   insider/misconfiguration category (11–33% of DBIR breach patterns),
   realized boundary-exploitation index 502 → 0.5 in CISA KEV. **This is the
   study's weakest link — named below.**
3. **Defense spend converts to rent-funded protection** — Ch1 growth delta
   −6/−3/0 pp/yr (underwriter bundles security into the cession contract;
   Grossman 1981 warranty; S16 Path 1).
4. **Negotiated payments are not losses** — per-regime transfer
   share 0.50/0.65/0.80 vs blended 0.35/0.45/0.60 (breach-of-contract damages and
   bounty-style settlements displace resource destruction; DOJ's 2022 CFAA
   good-faith policy is the legal precedent, vulnerability-reward programs
   the priced one). Affects the resource-only basis only.
5. **The honest counter-channel** — dependence shift targets ρ 0.15/0.30/0.50,
   *between* balanced and offense: one partition design + one negotiation
   protocol on the whole installed base is Böhme–Kataria's
   same-production-batch cell. **Correlation is the price of the
   architecture.**

## Findings

*(Numbers below from the full-size runs, seed 20260810; reduced-run values
within sampling noise of these.)*

### 1. The cession world in their currency (per_regime.csv)

2028, reference cell, anchored variant, transfer-inclusive basis:

| Regime | Weight | Median | Mean | P99 | P(>$200B) |
|---|---|---|---|---|---|
| offense-dominant | 0.30 | +$623B | +$774B | $2,993B | 94.7% |
| balanced | 0.45 | +$93B | +$124B | $751B | 21.1% |
| defense-dominant | 0.25 | −$151B | −$186B | $20B | 0.08% |
| **cession (ours)** | — | **−$125B** | **−$157B** | **$208B** | **1.06%** |

The cession regime lands **defense-like at the median but with a tenfold
fatter tail** (P99 $208B vs defense's $20B; P(>$200B) 13× higher) — exactly
the trade the parameters encode: severity truncation pulls the body down;
the same-batch correlation keeps the tail alive. In their headline currency,
a cession world turns the AI delta negative (the architecture attacks the
whole loss distribution, not just the AI increment — same semantics as their
defense-dominant regime). Fresh-variant and resource-only rows in the CSV
tell the same story with the reclassification channel visible (cession
resource-only median −$37B vs transfer-inclusive −$125B).

### 2. Early arrival moves their headline fast (mixture_2028.csv)

Sealed mixture with cession mixed in at weight w_c (2028, anchored,
transfer-inclusive; w_c=0 is their sealed forecast, reproduced here at
106.9/241.3 vs their published 107.2/240.6 — RNG-stream sampling noise only):

| w_c | Displacement | Median | Mean | P(>$200B) |
|---|---|---|---|---|
| 0 | — | $106.9B | $241.3B | 37.9% |
| 0.10 | proportional | $78.2B | $201.5B | 34.3% |
| 0.10 | offense-first | $55.7B | $148.2B | 28.6% |
| 0.25 | proportional | $30.1B | $141.7B | 28.7% |
| 0.25 | offense-first | −$16.8B | $8.7B | 14.5% |
| 0.50 | proportional | −$49.2B | $42.2B | 19.5% |

A 10% probability of the cession world already cuts their median headline by
~27% (proportional) to ~48% (offense-first — the thesis-aligned reading, in
which cession is the adaptation to offense pressure and eats the fat-tail
regime's mass first).

### 3. The crossover: cession already beats defense wherever hardware can participate (crossover.csv)

Per machine-year, uninsured owner, p_m = 10⁻³ (S16's pessimistic sweep
point), large-enterprise severity ($283k median):

| Config | Net of ceding | Crossover rent R* | Observed rate / R* |
|---|---|---|---|
| 4090-class, Case 1 (same-OS sharing) | +$661/yr | $0.00127/TFLOPS-hr | 1.7× |
| 4090-class, Case 3 (hw partition) | +$937/yr | $0.00088/TFLOPS-hr | 2.5× |
| iGPU business PC, Case 3 | −$97/yr | $0.02849/TFLOPS-hr | **0.08×** |
| 4090-class, Case 1, p_m = 10⁻² | **−$1,886/yr** | $0.00479/TFLOPS-hr | 0.46× |
| Household 3090, Case 3 | −$106/yr | $0.00225/TFLOPS-hr | 0.97× |

Three results:

- **Once isolation is architectural, risk is not the binding term.** At
  Case 3/4 the residual expected loss is ~$0.25/machine-yr (p_m=10⁻³ ×
  boundary index 9×10⁻⁴ × $283k); the observed market rate clears the
  crossover by 2.5×. The inequality is decided by **participation and
  energy** — the S16 barrier — not by security.
- **The only configuration where sharing destroys value is unnegotiated,
  unpartitioned access at pessimistic incident rates** (Case 1, p_m=10⁻²:
  −$1,886/yr). That configuration has a name: malware. The redefinition
  Matthew's question posits is, in this arithmetic, just the move from the
  loss-making cell to the profitable ones — same machine, same sharing,
  different boundary and different contract.
- **Enterprise before household.** Residential power (18.11 vs 13.79 ¢/kWh)
  plus the consent cost puts a mid-tier household machine right at breakeven
  (obs/R* ≈ 0.97); enterprises clear comfortably. Consistent with S16's
  conclusion that the institutional fleet is the natural first substrate.

### 4. The horizon wedge (horizon.csv — OUR construction, labeled)

Main phase-in schedule, anchored variant, transfer-inclusive (slow schedule
and fresh variant in the CSV):

| Year | w_c | Baseline med / mean | Cession arm med / mean | Wedge med / mean | Rent, US ($B) |
|---|---|---|---|---|---|
| 2029 | 0.05 | 128 / 291 | 110 / 266 | −18 / −25 | 0.3–2.0 |
| 2030 | 0.15 | 154 / 354 | 86 / 260 | −67 / −94 | 0.9–6.0 |
| 2031 | 0.30 | 185 / 434 | −2 / 199 | −187 / −235 | 1.8–12.0 |
| 2032 | 0.45 | 224 / 535 | **−136 / 93** | **−360 / −442** | 2.7–18.0 |

The wedge dwarfs the rent. **The value of the cession regime in this model
is overwhelmingly avoided losses and converted defense spend, not the rent
income itself** — the rent ledger (US commercial fleet, S16) is an order of
magnitude smaller than the Δ wedge. If something like this regime arrives,
its economic case will be written in the security budget, not the
electricity bill.

## Honest limits

1. **The weakest link, named plainly:** our cession-lowers-losses channel
   enters through a severity-truncation parameter **we choose ourselves**
   (20/35/55%). Their model prices defense as a haircut, so any defense-like
   mechanism — including ours — is one number asserted, not a mechanism
   simulated. The S16 anchors (KEV boundary indices, DBIR category shares,
   the two-factor decomposition) discipline the choice but do not measure
   post-cession truncation; nothing can, yet.
2. Everything past 2028 is our construction on their sealed dynamics: ramp
   held at 1.5, Ch4 at 1.0, D-15 chained, baselines extrapolated on their
   fitted log-linear trend. The 2032 baseline (~$2T/yr measured-basis
   losses) inherits the IC3 trend's ~30%/yr fitted growth; the **wedge**
   between arms is the object, not the levels.
3. The phase-in schedule (w_c to 0.45 by 2032) is a scenario justified by
   the crossover result and S16 Paths 2–3, not a forecast. Mixture weights
   are epistemic probabilities over regime-worlds; using them as a phase-in
   proxy conflates penetration with probability — we do it knowingly, as
   they do with their own regime weights over partial-deployment worlds.
4. The S3b agentic tree is not regime-indexed in their engine, so cession
   touches it only through the truncation haircut — negotiated access
   plausibly also reduces autonomous-campaign initiation, which we cannot
   express without deeper surgery.
5. The crossover's revenue side inherits every S16 caveat: Salad rates are
   one marketplace's, the iGPU fleet has **no bid at all today**, and the
   fungible-denomination row assumes a barrier falls that has not fallen.
6. Rent ledger is US-commercial-buildings-only vs a global Δ — scope
   mismatch flagged in the CSV; the illustrative global scaling (×2.449,
   their multiplier, our application) is labeled as such.
7. Their four-regime RNG stream differs from the sealed three-regime run, so
   w_c=0 rows differ from their published numbers by sampling noise only
   (verified: the sealed headline reproduces exactly on their untouched
   code).

## Sources

Fable & Carson 2026 (base model, CC-BY 4.0); S16
`analysis/enterprise-idle-fleet/` (rent, energy, actuarial inputs, all
fetched 2026-08-02/03); Grossman & Hart 1986; Hart & Moore 1990; Coase 1960;
Böhme & Kataria WEIS 2006; Anderson et al. 2013/2019; Grossman 1981;
Finifter, Akhawe & Wagner USENIX Security 2013; US DOJ CFAA charging policy
May 2022; Verizon 2026 Breach Impact Study; Cyentia IRIS 2025; CISA KEV;
FBI IC3 2024; EIA Electric Power Monthly T5.3. Verification status of each
handle: see `verification.md`.
