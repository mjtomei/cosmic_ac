# Enterprise idle fleets as a federation substrate

Question (Matthew, 2026-08-02): are business machines at the place of business a
more reliable federation resource than household consumer devices, with owners
incentivised to sell the idle capacity?

**Framing correction (Matthew, same day) — this note was first written against
the wrong question.** The first pass asked whether machines are *currently left
on overnight*, which made sleep defaults look like a blocker. They are not. Sleep
timers are shipping defaults that bind manufacturers; a group policy or MDM
profile overrides them, and enterprise fleets are centrally controlled by
definition. The machines do not need to be awake today — they need to be
**present**, **remotely controllable**, and **profitable to run**. Everything
below is organised on those three axes.

Method: four agent sweeps over primary sources only — EIA CBECS microdata, EIA
Electric Power Monthly, Eurostat APIs, BEA fixed assets, SEC filings, EPA
ENERGY STAR's open dataset, EUR-Lex, NIST's OSCAL catalog, and peer-reviewed
papers. Raw results with per-item provenance and caveats: `sweep-findings.json`
(57 findings). Anything the agents could not fetch is marked UNVERIFIED there
and is **not** repeated as fact here.

## The answer in one line

**Presence and free headroom are the only real constraints, and the economics
clear them by one to two orders of magnitude.** Both device classes count: all
111.6M business PCs are in scope, and they fail differently — laptops go home,
desktops stay but are more likely to be in use. Control is solved (that is what
MDM is), and profitability is not close: energy is ~$0.003/hr against
$0.05–0.20/hr of spot-like revenue.

## 1. Presence — the binding constraint

Neither class is excluded; they fail on different axes, and the addressable
resource is the sum of what survives each failure.

**Desktops — present, but less free than the count implies.** All **63.85M** are
at the place of business, mains-powered, with no battery to age and better
sustained thermals. The offsetting factor is that office desktops are more likely
to be *remotely accessed* and to carry higher baseline utilisation — they are the
machines people connect back into, and the ones that quietly host shared or
long-running work. Their raw count therefore overstates their free headroom.

**Laptops — free when present, but often absent.** The one after-hours census
found **80% of docking stations empty** (LBNL-53729, 2004, n=107); those that
stayed were 95% plugged in and 60% docked. A laptop left at the office is more
likely to be genuinely idle than a desktop is.

**The symmetry worth noting:** hybrid work degrades both classes through a single
cause. It takes laptops out of the building (35% of employed people worked from
home on a given day in 2025, 51% among degree-holders — BLS ATUS 2025) *and*
drives remote sessions into the office desktops that remain. The two device
classes are not independent hedges against the same trend.

**But "went home" is not "in use" (Matthew, 2026-08-02).** A company laptop
carried home for emergencies and rarely opened is still idle, still
company-owned, and — since modern MDM is cloud-based — still centrally
reachable. The resource is *relocated*, not destroyed. What actually changes is
who pays for power (residential 18.11 c/kWh vs commercial 13.79, so the employee's
meter is ~31% more expensive) and what the uplink looks like. That splits the
supply into two tiers that should be sized separately:

- **Tier A — on premises, no behaviour change.** Desktops plus docked laptops.
  Business pays power at commercial rates, business-grade uplink, single
  policy decision enrols the fleet. This is the conservative floor.
- **Tier B — at-home sharing.** Company laptops sitting idle at employees'
  homes. Requires consent or compensation because the cost lands on the
  employee's bill, and the uplink is residential. Larger population, weaker
  per-device economics, extra governance.

Sizing them separately is the honest way to present the resource: Tier A is what
the argument can claim without asking anyone to change behaviour, and Tier B is
the upside if the incentive is arranged.

### Tier sizing, from time-use duration (sweep 2026-08-02, `sweep-tier-b.json`)

The key correction to the incidence figures everyone quotes: BLS ATUS reports
*duration*, and it is short. **On a day someone works at home they work there
5.10 hours** (5.35 full-time; 5.18 for degree-holders, the population most
likely to hold a company laptop). At-home workdays are ~2.9 h *shorter* than
on-premises ones (5.35 vs 8.21 full-time).

| | Work-active | Idle | Idle share |
|---|---|---|---|
| Tier A, on premises (weekday) | 8.21 h | 15.8 h | 66% |
| Tier A, on premises (full week) | 41 h | 127 h | **76%** |
| Tier B, at home, laptop used | 5.10 h | 18.9 h | **79%** |
| Tier B, at home, laptop unopened | 0 h | 24 h | 100% |

**The emergency-laptop population is measurable, and Matthew's read is right.**
34.5% of people who worked did *any* work at home (ATUS 2025), while only 28% of
paid full days were work-from-home days (SWAA, Sept 2024) — the gap is partial
and incidental use. And 61% of US full-time employees are fully on-site (SWAA),
so most laptops that leave the building are not doing a workday at anyone's
kitchen table. Averaged across all workers and workdays, at-home work is
**~1.76 h per worker per day** (0.345 × 5.10, our arithmetic).

**Tier B is flat, not growing** — worth knowing before betting on it:
2.94 h/day and 23.7% incidence (2018) → 5.41 h and 33.8% (2022) → 5.10 h and
34.5% (2025). The step change happened once, in 2020–22, and has since plateaued.
Geography matters more than time now: in the EU only 8.9% usually work from home
and 77.4% never do (Eurostat lfsa_ehomp 2024), so Tier B is proportionally much
smaller there while Tier A is correspondingly larger.

### Tier B is technically operable; the constraint is consent and billing

Cloud MDM reaches a laptop at a kitchen table exactly as it reaches one at a
desk. Microsoft Intune "runs entirely in the cloud, with no on-premises
infrastructure required" and evaluates device posture "not on whether the device
is on the corporate network," over public HTTPS endpoints; Apple's push service
needs only Ethernet, Wi-Fi or cellular reachability to Apple's range. **There is
no technical gap between the tiers** — the differences are that the employee's
meter pays (18.11 vs 13.79 c/kWh, ~31% more) and the uplink is residential.

Two governance facts follow. **The employer may be legally obliged to pay**:
California Labor Code 2802(a) requires indemnifying employees for "all necessary
expenditures or losses incurred… in direct consequence of the discharge of
duties," which is the statute under which home-utility reimbursement claims are
brought. And **paying households for a controllable in-home resource is already
routine at scale**: 10.66M US residential customers were enrolled in utility
demand-response programmes in 2024, receiving $273.3M in incentives — about
**$25.60 per household per year** (our arithmetic on EIA Electric Power Annual
Tables 10.3/10.4). That is a real anchor for what household consent costs, and
it is low relative to the 18–73× energy margin above.

**Unmeasured, and it matters:** the prevalence of off-hours remote access to
business desktops, and their actual baseline utilisation in 2026. The only
measured fleet idleness on hand is 97.9% mean CPU idleness across a managed
institutional fleet (Domingues et al., ICPPW 2005) — university teaching labs,
pre-dating both mass remote access and hybrid work, so it is an upper bound and
almost certainly a loose one.

## 2. Control — solved, and it is the structural advantage

Sleep-as-shipped rules (EU Ecodesign 617/2013; ENERGY STAR v8 §3.3.1) bind
*manufacturers at the point of sale*, not operators: a GPO or MDM profile
changes fleet power policy centrally. ENERGY STAR in fact *requires* notebook
Wake-on-LAN to function on AC power (§3.3.1 ii), so the docked subset is
remotely wakeable by specification. Central management is near-universal at
scale — 98.1% of employees at EU firms of 250+ work somewhere issuing managed
portable devices (Eurostat), and one MDM vendor alone administers 33.2M Apple
devices across 76,500 organisations (Jamf 10-K FY2024).

**The decisive point is the decision unit.** One IT policy change enrols ten
thousand machines at once; consumer federation needs ten thousand separate
consent decisions for the same capacity. Since this paper's whole thesis is that
the resource stays stranded for *coordination* reasons rather than physical
ones, an owner who can commit a fleet with a single decision is not a marginal
improvement on the household case — it is a different order of coordination
cost, and it is the reason to prefer enterprise supply.

## 3. Profitability — not close

Energy is the only marginal cost, since the hardware is already bought,
amortised, and managed (the S3 "stranded compute" case). At the measured 20 W
for an Apple-class SoC under sustained load and the commercial rate of
13.79 c/kWh: **$0.0028/hr**, about 3 cents per twelve-hour night, ~$8/machine/yr
over 250 nights. A 65 W desktop under load is $0.009/hr. Against the project's
own revenue reference (datacenter $0.50/hr at 60/75/90% spot-like discounts →
$0.20/$0.125/$0.05 per hour), margins run **73×, 45× and 18×** on energy.
Businesses also buy power ~24% below households (13.79 vs 18.11 c/kWh), so the
same machine is cheaper to run at the office than at home.

Remaining real costs, unquantified here and needed before this is a business
case: office HVAC penalty for rejecting the heat, IT administration, security
review, and hardware wear. The 18–73× headroom is what those have to eat.

## The total figure

`fleet_sizing.py` → `fleet_sizing.csv`. **US commercial buildings only** — the
one population with a weighted device census. Global would be several times
larger; no fetchable global commercial installed-base figure exists, so we do
not extrapolate.

| Scenario | Devices | Idle device-hours/yr | Value at $0.05–0.20/hr | Net of energy |
|---|---|---|---|---|
| **S1 — no policy change** (desktops already left on) | 40.9M | 272B | **$13.6–54.4bn** | $12.9–53.7bn |
| **S2 — Tier A, policy change** (all on-premises) | 73.4M | 489B | **$24.4–97.7bn** | $23.1–96.4bn |
| **S3 — Tier A + B** (adds at-home laptops) | 111.6M | 773B | **$38.7–154.6bn** | $36.3–152.3bn |

So the headline: **on the order of $10–50bn/yr of idle business compute is
available with no behaviour change at all, roughly doubling to $25–100bn with a
fleet-policy change, and reaching $40–155bn if at-home machines are enrolled** —
in US commercial buildings alone, before any of the unmodelled costs.

Energy is negligible against it: **1–5% of gross value**, which is the whole
point — the hardware is already bought, powered, and administered.

**Read the ranges, not the midpoints.** The width comes from the price
assumption (a 4× spread between spot-like discount tiers), and the scenario
spread comes from policy, which is the actionable variable. The *ordering* is
robust; the absolute values are not better than one significant figure.

**In raw FP32 this is 118–324 EFLOPS, nominally 1.8–4.8M H100-equivalents — and
that comparison should be used with great care or not at all.** It counts FP32
non-tensor throughput on machines with no tensor cores, no HBM, and no
interconnect. For the AI workloads that make H100s valuable, effective parity is
lower by more than an order of magnitude. The honest use of the fleet number is
for embarrassingly-parallel and loosely-coupled work, which is exactly the class
§4 says federates.

**Sensitivity.** The per-device throughput assumption (A7) dominates everything:
at 0.5 TFLOPS/device rather than 2.9, S2 falls from 213 to 37 EFLOPS. Since
Apple silicon is ~9% of PC units and typical business integrated graphics sit
well below the measured M4 figure, **the low end of that sweep is the more
defensible planning number.** The docked-laptop share (A5) barely matters —
sweeping 10–40% moves S2 by only $23–28bn, because desktops dominate.

**What is not modelled, all of it reducing the result:** office HVAC penalty for
rejecting the heat, IT administration, security review, hardware wear, network
egress, the utilisation discount on remotely-accessed desktops, and redundancy
overhead (volunteer-computing practice runs ~2× for unreliable hosts). The
18–73× energy margin is what these have to eat, and they will eat a lot of it.

## v5 — the fungible-compute denomination, and the paper's thesis measured

Requested (Matthew, 2026-08-02): a number denominated in FP8/FP16 rather than
FP32, because that corresponds to the predicted future in which compute is
fungible. The result is the strongest on-thesis finding in this study.

### The ladder, by reachability

| Denomination | Per device | Fleet continuous | Reachable today? |
|---|---|---|---|
| FP32 sustained | 0.51 TFLOPS | **39.5 EFLOPS** | yes — and worth ~$0 (v4) |
| FP16 packed (2×) | 1.02 T | 79 E | **yes** — ordinary ALU rate |
| INT8 via DP4a (4×) | 2.04 T | **158 EOPS** | **yes** — plain OpenCL/SYCL/Vulkan |
| Platform TOPS, AMD 8700G business desktop | 34 TOPS | 2,635 EOPS | **no** — NPU framework-gated |
| Platform TOPS, AMD HX 370 laptop | 80 TOPS | 6,201 EOPS | no |
| Platform TOPS, Intel Lunar Lake | 120 TOPS | 9,301 EOPS | no |

The 4× INT8 ratio is not an assumption: Intel's Xe-LPG iGPU delivers 18 TOPS
against 4.6 FP32 TFLOPS — exactly the DP4a ratio — and it is reachable from
ordinary compute APIs, so it genuinely pools.

### The NPU tier is stranded, and that is the paper's argument, measured

Every vendor now ships a neural engine, and **none of it is reachable by
arbitrary workloads**:

- **Apple**: "No public low-level ANE API. Core ML model graphs only; MLX
  exposes cpu and gpu devices only, no ANE backend." Stranded for general compute.
- **Intel**: OpenVINO NPU plugin only, which Intel's own docs say "may offer a
  limited set of supported OpenVINO features." The NITRO paper (arXiv:2412.11053)
  adds: "The NPU currently has a constraint in that it only supports static
  models" — LLM decode does not work out of the box; the authors had to rewrite
  the transformer for static shapes.
- **AMD**: ONNX Runtime plus Vitis AI execution provider only, with mandatory
  quantization or bf16 recompilation.

And when the best available tools are pointed at it, the yield is dismal:
**NPUEval (arXiv:2507.14403) measures frontier LLMs achieving ~10% average
vectorization efficiency** writing AMD NPU kernels, noting that "unlike GPU
programming… NPU programming is new, with smaller and more fragmented developer
communities." **Peak TOPS is gated by toolchain, not silicon.**

Worse for the vendor numbers, measured NPU performance frequently *loses*:
"When NPUs Are Not Always Faster" (arXiv:2605.27435) finds the NPU behind the
CPU by up to 1.6× on prefill and only 1.05–1.2× ahead on decode, at +51% energy —
because achieved-versus-peak is dominated by quantization, cross-backend fallback
and scheduling overhead rather than peak MACs.

### Why this matters more than the dollar figures

Stack the three findings from v3, v4 and v5 and they say one thing:

1. The fleet has **39.5 EFLOPS** of sustained FP32 sitting idle 76% of the week.
2. It is worth **~$0**, because no marketplace accepts integrated graphics.
3. Refreshed silicon carries **17× more** capability again in NPU form, and
   effectively **none of it is reachable** — the best measured yield from
   frontier-model kernel-writing is ~10% of peak.

**Each barrier is a coordination failure, not a physical one.** No runtime
targets the hardware; no marketplace lists it; no toolchain reaches the neural
engines. This study set out to size a resource and instead produced a
measurement of the thing the paper argues exists — with the NPU tier as the
purest instance yet found: capability shipped in hundreds of millions of units,
physically present, and stranded behind a programmability barrier that the
industry has not been paid to solve.

**Register note:** the FP32 and INT8 rows are [REAL] and reachable. The platform
TOPS rows are [MIXED] — the silicon is real and verified from vendor
specifications, the accessibility is not. Never present the platform-TOPS
figures as available capacity; present them as the size of the barrier.

## v4 — priced at OBSERVED market rates. The headline finding is a zero.

Rates fetched live 2026-08-02 from the markets that actually buy idle compute
(Salad's demand-monitor API, Vast.ai's bundles API, Akash's pricing API,
RunPod's price page).

### The business fleet as it exists today has no bid

> **"Salad does not currently support Intel dedicated GPUs, or Intel integrated
> GPUs."** — Salad support docs, fetched 2026-08-02. Container jobs require
> RTX 2070 or better with 8GB VRAM.

- **Salad**: integrated graphics → not eligible for any paying workload.
- **Vast.ai**: no CPU-only offer type exists; hosting requires Ubuntu, NVIDIA
  drivers and inbound router ports — a managed Windows business desktop
  cannot participate at all.
- **Akash**: a listed GTX 1050 2GB carries *no price*. Never leased.
- Across all three, **below ~8GB VRAM there is no bid.**

**What hosts are actually paid** (Salad, per idle machine-hour): $0.014 floor
(GTX 1660 / RTX 2060 class) · $0.028 (RTX 3060 12GB) · $0.068 (RTX 3090) ·
$0.180 (RTX 4090) · $0.229 (RTX 5090). CPU-only comparables exist on the
*renter* side only — Salad $0.024/hr for 4 vCPU/8GB, Akash $0.066/hr for
4 vCPU/16GB, against $0.25–0.29/hr for the same spec on AWS/GCP/Azure.

### Fleet value, re-priced

| Basis | $/device-hour | Fleet value/yr |
|---|---|---|
| v1/v2 assumption | $0.05–0.20 | $34–136bn |
| **iGPU business PC, today** | **$0.00** | **~$0** |
| If a CPU-slice market existed (host ≈30–50% of renter) | $0.008–0.033 | $5–22bn |
| With an entry discrete GPU added | $0.014–0.048 | $10–33bn |
| With RTX 4090/5090-class | $0.180–0.229 | $122–156bn |

**The v1/v2 range did not merely overstate the price — it priced a class of
machine that has no bid at all.** The correction is not a discount; it is a
category error, now fixed.

### What this does to the argument — it sharpens it

The resource is not stranded by physics, or by economics, or even by the
consent and control problems examined above. **It is stranded because the
market will not accept that hardware class**: no runtime targets it, no
marketplace lists it, no buyer bids for it. The machines are present, powered,
centrally managed, cheap to run, and idle 76% of the week — and worth nothing,
because nobody has built the thing that would buy what they have.

That is this paper's collective-action thesis appearing inside its own supply
estimate. The gap between the fleet's physical capacity (39.5 EFLOPS sustained)
and its market value (~$0) is not a modelling artifact — **it is a measurement
of the coordination failure the paper is about.**

### What the GPU upgrade actually buys

Not "more compute" — **eligibility**. The 8GB-VRAM threshold is the line between
a machine with no bid and a machine with a published price. That reframes the
optimisation case: a business does not add a card to earn proportionally more,
it adds a card to enter the market at all. The 70 W A2000 with 12GB clears the
VRAM bar while fitting an SFF chassis, which is why it remains the efficient
rung despite its modest FP32.

### Honest caveats on the zero

The $0 is the price on *existing consumer-GPU marketplaces*, which are built for
CUDA workloads. It is not proof that business CPU capacity is worthless — CI/CD
runners, batch, transcoding and simulation all consume ordinary CPU, and the
CPU-slice comparables above show real prices in that shape. It is proof that
**no such market presently reaches this fleet**, which is a different and more
interesting claim. The host-share of renter price is unpublished on Vast and
Akash; the 30–50% band is inferred from Salad's disclosed split.

## v3 — regenerated on the real installed mix (`fleet_sizing_v3.py`)

The installed-mix sweep (4 agents, 2026-08-02) verified the volume business SKU
from **nine Lenovo PSREF official spec PDFs**. Dell (403) and HP (503) blocked
fetching, so this is single-vendor evidence — but it is unambiguous:

- **ThinkPad T14/L14 (volume laptop): every graphics option is integrated.
  There is no discrete GPU on the spec sheet at all.**
- **ThinkCentre M70q/M75q (volume tiny/SFF desktop): all integrated** — Intel
  UHD 710/730/770, AMD Radeon 740M/760M/780M.
- Only the M70t **tower** offers discrete cards.
- Volume CPU tier is low-power: T-suffix i3/i5, U-series Core Ultra.
- Lenovo's own footnote: Arc graphics requires 16GB **dual-channel** memory
  "otherwise it will function as Intel Graphics" — single-channel fleets are
  derated below even these figures.

### The headline correction

| Basis | FP32/device | Fleet EFLOPS | vs v1 |
|---|---|---|---|
| v1 assumption (measured Apple M4) | 2.9 | 224.8 | 1.00× |
| Peak, weighted low | 0.6 | 46.5 | 0.21× |
| **Peak, weighted central** | **0.85** | **65.9** | 0.29× |
| Peak, weighted high | 1.2 | 93.0 | 0.41× |
| **Sustained central (peak × 0.6 derate)** | **0.51** | **39.5** | **0.18×** |

**The fleet is ~5.7× smaller than v1 said.** Every compute-denominated figure in
v1/v2 should be divided by roughly six. Two compounding reasons: the volume
business machine is an integrated-graphics part around 0.85 TFLOPS peak, and an
iGPU shares the CPU's DDR bus (~90 GB/s dual-channel DDR5-5600), so it is
memory-bound well below peak.

**Note the asymmetry that makes even this generous:** the 2.9 figure for the M4
was *sustained and measured*; the 0.85 here is *peak*. Comparing them already
flatters the business fleet, so the true gap is wider than 5.7×.

### What optimisation buys, per device — power is the constraint

| Config | FP32 | × base | Card | Watts | Energy/yr | Net vs $355–1,419 budget |
|---|---|---|---|---|---|---|
| Business PC as-is | 0.51 | 1× | — | 65 | $79 | +$276 / +$1,340 |
| **+ RTX A2000 (SFF-safe)** | **8.0** | **16×** | $525 | 135 | $163 | **+$192 / +$1,256** |
| + RTX 5070 | 30.9 | 61× | $549 | 315 | $381 | −$26 / +$1,038 |
| + RTX 5090 | 104.8 | 205× | $1,999 | 640 | $773 | −$418 / +$646 |

**The efficient rung is the 70 W low-profile professional card** — 16× the
capability, fits an existing small-form-factor chassis without a PSU upgrade, and
leaves the revenue budget intact. The 5070 is **already loss-making at the low
end of the budget** once power is charged, and the 5090 is loss-making by $418
before any other cost. Above ~250 W this stops being an idle-capacity business
and becomes a power-purchasing business.

### Fleetwide optimisation — an upper bound, not a forecast

As-is 39.5 EFLOPS → +A2000 fleetwide 620 EFLOPS → +5070 fleetwide 2,395 EFLOPS.
**Treat these as ceilings.** They assume every machine takes a card, which the
SKU evidence says is impossible: laptops and tiny/SFF desktops have no slot, and
only the tower chassis accepts one. The tower share of commercial desktop volume
was not verified and is the single input that would make this real.

### Dollars deliberately omitted from v3

v3 reports **capacity, not dollars**, because the dollar anchor was shown to be
inflated — the EC2 Mac rate embeds a macOS-licence scarcity rent — and its
replacement is still in flight. Two denominations are being fetched: observed
market rates per machine-hour (today), and FP16/FP8/NPU throughput (the fungible
-compute future). Dollar figures return when those land.

## The device specs, answered (sweep 2026-08-02) — and two surprises

Earlier the "optimised hardware" scenario had a justified budget with **no specs
on the other side of it**. Now it has specs, and they change the answer.

### The baseline was wrong: a business PC is not an M4

Our fleet model assumed **2.9 FP32 TFLOPS/device** — a *measured Apple M4*, on a
fleet that is ~91% not Apple. A standard business desktop has integrated
graphics only:

| Baseline | FP32 | Basis |
|---|---|---|
| Intel UHD 770 (typical i5/i7 business tower) | **~0.79 TFLOPS** | derived, 32 EU × 8 × 2 × 1.55 GHz |
| Intel Arc iGPU (Core Ultra 7 155H) | ~4.6 TFLOPS | derived, 128 EU × 8 × 2 × 2.25 GHz |
| AMD Radeon 780M | 4.15 TFLOPS (8.29 only on dual-issue-friendly code) | vendor peak |
| Apple M4 (our old assumption) | 2.9 TFLOPS | **sustained-measured** |

**The typical business desktop is plausibly ~0.79 TFLOPS — roughly a quarter of
what we assumed.** This is also the weakest-verified number in the whole model:
Intel blocks automated fetching, so the figure is derived from architecture
arithmetic, and the fleet multiplier swings 7×–39× depending on whether the mix
is UHD-770-era or Arc-era. **Pending the installed-mix sweep, the 0.5 TFLOPS
sensitivity row is the honest planning figure, not 2.9.**

### Surprise 1 — the Apple ladder is flat in $/TFLOPS

| Config | Price | FP32 | $/TFLOPS |
|---|---|---|---|
| Mac mini M4 | $799 | 2.9 | $276 |
| mini M4 Pro (20c) | $1,799 | ~5.8 | $310 |
| Studio M4 Max (40c) | $3,499 | ~11.6 | $302 |
| Studio M3 Ultra (80c) | $6,799 | ~21 | $324 |

Buying up the Apple line buys **density, memory capacity and bandwidth — not
cheaper FLOPS**. For a compute-resale motive, *N* minis beat one Studio; the
Studio wins only when a single job needs 96–512GB of unified memory. (All rungs
above the base M4 are our linear core-scaling of the one measured point, ±20%.)
Also: Apple has raised prices since launch — the mini is **$799 now versus the
$599 MSRP** our `cost_model.py` still assumes.

### Surprise 2 — a discrete GPU is ~16× better $/TFLOPS, and power becomes the constraint

| Card | Price | FP32 | $/TFLOPS | Power |
|---|---|---|---|---|
| RTX A2000 12GB | ~$525 | 8.0 | $66 | **70 W, fits SFF** |
| RTX 5070 | $549 | 30.9 | $18 | 250 W |
| RTX 5080 | $999 | 56.3 | $18 | 360 W |
| RTX 5090 | $1,999 | 104.8 | $19 | 575 W |

**So the profit-optimising business does not buy a bigger Mac — it buys an
ordinary business desktop and adds a GPU.** That is a 7×–39× capability
multiplier for ~$549, well inside the justified budget, and $/TFLOPS is
near-linear across the GPU range (no bargain tier, no cliff).

**But the binding constraint moves from price to power**, which our earlier
"energy is 1–5% of value" finding no longer survives:

| Configuration | Always-on energy |
|---|---|
| Business PC, iGPU only (65 W) | $79/yr |
| + RTX A2000 (135 W) | $163/yr |
| + RTX 5070 (315 W) | $381/yr |
| + RTX 5090 (640 W) | **$773/yr** |

Against a justified budget of $355–1,419/yr, **an RTX 5090 burns most of the
revenue it was bought with.** The efficient rung is the low-profile 70 W
professional card: it fits existing small-form-factor business chassis without a
PSU upgrade, and costs $163/yr to run. Anything above ~250 W turns this from an
idle-capacity story into a power-purchasing story, which is a different business.

### The precision trap, confirmed in vendor text

NVIDIA's own newsroom pairs "$549" with **"988 AI TOPS"** for a card whose FP32
is 30.9 TFLOPS — a **32× gap**, because AI TOPS is sparse FP4/INT8. The A2000
datasheet prints 8.0 FP32 / 15.6 RT / 63.9 Tensor in one column. Any comparison
that crosses those columns is meaningless. *This cuts both ways: for the
fungible-compute denomination (below), the low-precision figures are the
relevant ones and FP32 is the wrong metric.*

## Method, and a correction to the headline (2026-08-02)

**How the compute was sized.** Device-hours (devices × hours × idle fraction)
priced at $0.05–0.20 per device-hour, that price being the project's existing
$0.50/hr datacenter reference at 60–90% spot-like discounts (`cost_model.py`).
TFLOPS were reported separately and **never reconciled with the price** — which
turns out to matter.

**The reconciliation, and why the dollar headline is too high.** The $/device-hour
anchor traces to EC2 Mac dedicated at $0.65/hr. Against the measured 2.9 FP32
TFLOPS of an M4, that is **$0.22 per TFLOPS-hour** — roughly **5–8× what a
commodity GPU costs per FP32 TFLOPS-hour** (H100 ≈ $0.03–0.045; the H100 $/hr
input is UNVERIFIED and needs checking). The gap is not a compute price at all:
EC2 Mac carries a macOS-licence scarcity rent, because iOS CI/CD must legally run
on Apple hardware. Anchoring 111M heterogeneous business PCs to it imports a
premium that does not generalise.

**Consequence: treat the $13–155bn figures as an upper bound with a known upward
bias, not an estimate.** They are the right shape and the wrong level.

**Compute-denominated sizing** (679B available device-hours/yr, Tier A+B):

| Per-device throughput | TFLOPS-hours/yr | @$0.03/TFLOPS-h | @$0.01 | @$0.003 |
|---|---|---|---|---|
| 0.5 TFLOPS (typical integrated graphics) | 0.3T | $10bn | $3bn | $1bn |
| 1.0 TFLOPS | 0.7T | $20bn | $7bn | $2bn |
| 2.9 TFLOPS (measured M4) | 2.0T | $59bn | $20bn | $6bn |

**So the defensible market range is single-digit to low-tens of billions per
year, not $155bn** — and the number is governed by the price column, which is
where the honest uncertainty lives.

**Why total market size cannot be answered from the supply side alone.** Every
figure above sizes a *resource*. A market is the intersection with demand, and
this supply is price-taking: adding hundreds of billions of device-hours moves
down the demand curve, so the realised price is *endogenous to the supply being
added*. Two things bound it in opposite directions, and the paper already
contains both — §4's no-floor argument (machine demand extends toward
arbitrarily low value, so the curve is long) against the plain fact that
commodity GPU capacity sets a ceiling price this fleet cannot exceed.

**What would settle it, and is missing:** a demand-side anchor — total addressable
spend for loosely-coupled, interruptible, non-GPU-class compute. Cloud
infrastructure spend and AI capex are the obvious references and neither is
verified here. **Until that exists, the honest claim is the physical resource
(679B device-hours, 0.3–2.0T TFLOPS-hours/yr) rather than a dollar market size.**

## Two corrections to the sizing (Matthew, 2026-08-02) — `fleet_sizing_v2.py`

### (a) Daytime sharing: right in principle, small in effect

"Work-active" is not "CPU-saturated" — someone editing a document uses a few
percent of a modern machine, so availability should be *(hours powered) ×
(fraction of cycles unused)*, not *(hours nobody is at the keyboard)*. This is
what cycle-stealing has always harvested; HTCondor yields to the interactive
user rather than waiting for them to leave.

Recomputing on measured idleness (97.9% across a managed institutional fleet —
Domingues et al., ICPPW 2005; we use a conservative 90%, and reserve a further
10% of cycles so the user never contends) moves Tier A from **489B to 498B**
device-hours/yr — **1.02×**. Tier A+B actually *falls* slightly, because v1 gave
at-home laptops a generous 85% idle share against v2's explicit 16 h/day powered
window.

**So the honest finding is that this correction buys defensibility, not
magnitude.** The after-hours model already captured ~76% of the week; the daytime
cycles are real but they are a small addition to a number that was already
mostly idle time. What improves is the *basis*: measured CPU idleness rather than
an assumption about keyboard presence. Sensitivity across 85–97.9% idleness spans
641–739B device-hours — a ±7% band, far narrower than the price or
throughput assumptions.

### (b) Hardware chosen with resale in mind — this is the large effect

Today a business specifies a machine for one employee's workload, because
surplus capacity is pure waste. If surplus earns revenue, the optimum moves up.
Converting available hours into a justified up-front budget at the depreciation
life stated in Dell's own 10-K (3–5 years, midpoint 4):

| Device | Available h/yr | Revenue/yr | Justified extra spend over 4y |
|---|---|---|---|
| Desktop (always on) | 7,096 | $355–1,419 | **$1,419–5,676** |
| Laptop (16 h/day) | 4,730 | $237–946 | **$946–3,784** |

**Against a typical business PC at $600–1,500, the idle revenue is of the same
order as the entire device, and at the upper end several times it.** That does
not merely shift the specification decision — it removes the employee's workload
as the binding constraint on it. The machine can be specified for what it can
*sell*, with the employee's needs met incidentally.

This is the demand-side twin of the paper's existing financing instrument
(§8 / Omerta: a device that sells its own time, with the builder underwriting the
risk). The supply side says the buyer can be lent the hardware against its future
earnings; this says the buyer would rationally want a *bigger* machine than they
need. Same instrument, both ends.

Capacity if specification rises by multiplier M (a capacity statement, not a
revenue one): M=2 → 1,358B device-hour-equivalents/yr; M=3 → 2,037B; M=5 →
3,395B. Business PCs with integrated graphics sit at the worst end of
compute-per-dollar, so M is bounded well above 1 — but we do not assert a value,
because $/TFLOPS at the margin is a moving figure we did not verify.

**The price caveat that governs all of this.** Value does *not* scale with M.
These $/device-hour references are current spot-like prices for scarce compute;
adding hundreds of billions of device-hours would move down the demand curve, and
the equilibrium price would fall. The paper's own §4 answer applies — machine
demand has no floor, because there is always a lower-value next-best task — but
that argument caps how much revenue a supply expansion of this size can claim.
**Treat the dollar figures as an upper bound at today's prices, not a forecast.**

## What supports the idea

| Fact | Number | Source |
|---|---|---|
| Business PCs in US commercial buildings | 63.85M desktops + 47.76M laptops = 111.6M | EIA CBECS 2018 public microdata (FINALWT-weighted; our computation, not an EIA table) |
| PCs per worker in those buildings | 1.30 | Same |
| Desktops left on after hours | ~64% turn-off rate 36%, n=1,453 | Roberson/Webber et al., LBNL-53729 (2004), doi:10.2172/821675 |
| Power management essentially absent | 6% of not-off desktops in low power | Same |
| Laptops present after hours were mains-connected | 95% plugged in, 60% docked (n=37) | Same |
| Commercial electricity vs residential | 13.79 vs 18.11 c/kWh (YTD May 2026) | EIA Electric Power Monthly T5.3 — **the business pays ~24% less than a household** |
| Notebook idle power | 5.15 W short idle / 0.90 W long idle (mean, n=1,140 certified models) | EPA ENERGY STAR Certified Computers V9.0 |
| Apple silicon throughput / efficiency | 2.9 FP32 TFLOPS (M4 GPU), 10–20 W, 0.33 TFLOPS/W | Hübner et al., IPDPSW 2025, arXiv:2502.05317 |
| Managed CPU idleness, institutional fleet | 97.9% mean, 169 machines, 77 days | Domingues et al., ICPPW 2005 |
| Volunteer (household) host availability — the baseline to beat | ~0.61 of wall time (product of on/connected/active/efficiency) | Anderson & Fedak, CCGrid 2006 |
| Commercial share of PC vendor revenue | Dell 86.4% CSG; HP 71.2% Personal Systems | Dell 10-K FY2026; HP 10-K FY2025 |

**Derived (our arithmetic, stated as such):** 63.85M desktops × ~64% left on
≈ **~41M business desktops powered and idle overnight in US commercial buildings**.
Energy to harvest one idle Apple-class SoC ≈ 20 W × 13.79 c/kWh ≈ **$0.003/hour**,
about 3 cents a night. Both figures combine sources across years; treat as
order-of-magnitude sizing, not measurement.

## What still cuts against it (after the reframe)

1. **Most laptops leave.** 80% of 107 docking stations were empty after hours,
   and only 24% of laptops found were clearly on (LBNL-53729). Hybrid work has
   sharpened this: 35% of employed people did some work at home on a given day
   in 2025, 51% among degree-holders (BLS ATUS 2025).
2. ~~**Sleep is mandated, as shipped.**~~ **Withdrawn on the reframe** — these
   are shipping defaults binding manufacturers, overridable by fleet policy. What
   survives is only the accounting point: the counterfactual is a ≤3 W sleeping
   machine, so the energy *delta* charged against revenue is the full load draw,
   which is what the margins above already use.
3. **Waking is an engineering detail, not a barrier — but a real one.** Windows
   WOL does not work from the default shutdown state (MS KB2776718) and Modern
   Standby machines have no S3 to wake from, so a fleet cannot simply be
   magic-packeted awake from off. The fix is policy, not hardware: set the fleet
   to stay awake or to scheduled-RTC-wake during the harvest window. Costs an
   MDM profile, not a capability.
4. **Endpoint policy gives IT the tooling to refuse.** NIST SP 800-53r5 CM-7(5)
   (deny-all, permit-by-exception execution), CM-10 (control P2P specifically),
   CM-6 (most restrictive setting consistent with operations). macOS Gatekeeper
   requires notarisation. None of this is prohibitive; all of it is friction and
   an approval gate. *Prevalence of enforcement is unmeasured — a real gap.*
5. **Sustained load on mobile hardware.** Battery calendar ageing accelerates at
   high state-of-charge and temperature (Stroe et al., IEEE TIA 2017); mobile-class
   silicon throttles under continuous inference (Wang et al., arXiv:2206.10849).

## The Mac claim, verified — and narrower than the advertisement

Apple's live wording (apple.com/business, fetched 2026-08-02) is **"84% of top
U.S. companies use Mac at scale,"** footnoted to *LinkedIn Top Companies 2026:
the 50 best large employers* plus undisclosed internal Apple data. So the
denominator is **50 companies (42 of 50)**, not the Fortune 500, and "at scale"
is undefined. **Do not repeat the popular ">80% of the Fortune 500" phrasing —
no primary Apple source supports it.**

For scale, Apple is **9.2% of worldwide PC units** (24.83M of 270.2M, 2025;
Gartner, via Wayback). The best hard number for managed Apple fleets is
**33.2M devices across 76,500 organisations** (Jamf 10-K FY2024) — but Jamf never
splits Mac from iPhone/iPad, and the base includes large K-12 iPad deployments,
so it is a loose upper bound. Apple's other enterprise claims are commissioned
studies with undefined denominators (Forrester TEI on help tickets; Omdia's
"57% of enterprise AI models can run locally on MacBook Air"). **The federation
argument should not lean on Macs specifically.**

## The open measurement

Under the corrected framing the question to measure is **presence, reachability,
and free headroom** — not current power state. For one organisation's fleet:
what fraction is physically on premises outside working hours, what fraction is
MDM-reachable, and what fraction is genuinely idle rather than carrying a remote
session or background work. All three come off the same management console, and
the third is the one nobody has measured in the remote-access era.

Nobody has repeated the after-hours census since 2004. LBNL-53729 predates
modern sleep defaults entirely, its laptop sample is 37 machines, and the
desktop-to-laptop shift and hybrid work have both happened since. **The central
number for this entire question — what fraction of business machines are
powered and reachable outside working hours in 2026 — is unmeasured.** It is
cheap to measure (a network sweep of one organisation's fleet) and would be
publishable on its own.
