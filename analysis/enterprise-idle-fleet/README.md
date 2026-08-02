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
the upside if the incentive is arranged. *Sweep in flight for the duration data
that sets Tier B's size — how many hours a work laptop is actually used at home,
as opposed to merely present.*

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
