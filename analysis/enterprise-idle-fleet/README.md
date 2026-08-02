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
