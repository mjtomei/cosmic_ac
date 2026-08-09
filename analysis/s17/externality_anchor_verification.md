# S17 externality-pricing half — anchor verification (2026-08-04, web agents)

Verification of the handoff's §4/§7 queue. Verdict per anchor, with the exact
citation to use and the framing constraint each one imposes.

## Verified, safe to build on

1. **SCC $51 — IWG Feb 2021.** *Technical Support Document: Social Cost of
   Carbon, Methane, and Nitrous Oxide — Interim Estimates under EO 13990*,
   Feb 26 2021 (86 FR 24669). Central SC-CO2 **~$51/tCO2, 2020 emissions,
   3% discount rate, 2020 dollars**.
2. **SCC $190 — EPA Nov 2023.** *EPA Report on the Social Cost of Greenhouse
   Gases: Estimates Incorporating Recent Scientific Advances* (EPA NCEE,
   Nov 2023, docket EPA-HQ-OAR-2021-0317). Table ES.1: **$120 at 2.5%, $190
   at 2.0% (central), $340 at 1.5%** near-term Ramsey rate, 2020 emissions,
   2020 dollars.
   **FRAMING CONSTRAINT: the 3.7× move is not discounting alone.** EPA also
   replaced socioeconomic projections (RFF-SPs), the climate module (FaIR),
   and all three damage modules per the NAS 2017 recommendations. Even EPA's
   2.5% value ($120) is 2.4× the IWG 3% value. Write "moved ~4× on
   methodological choices — discounting prominent among them — while measured
   emissions stayed fixed," never "moved 4× on the discount rate."
3. **SO2 monitoring share.** Ellerman, Joskow & Harrison, *Emissions Trading
   in the U.S.* (Pew Center, May 2003), p.16, verbatim: "CEMS added about
   seven percent to total Phase I compliance costs, and a less costly
   'materials balance' method could provide equally accurate estimates of
   total emissions." Primary behind it: Ellerman et al., *Markets for Clean
   Air* (CUP 2000), ch.9 Table 9.5. **The circulating $124k/unit/yr figure
   was NOT FOUND in any accessible source — do not use** (nor the $200k/unit
   figure, which traces to a patent filing). If a per-unit number becomes
   load-bearing, pull Table 9.5 from the physical book.
4. **Satellite methane validation.** Sherwin et al., "Single-blind test of
   nine methane-sensing satellite systems from three continents," *Atmos.
   Meas. Tech.* 17:765–782, 2024, doi:10.5194/amt-17-765-2024 (venue is AMT,
   not Sci Rep as the handoff guessed). 82 controlled releases: 0 false
   positives, smallest detection 0.0332 t CH4/h, 55% of nonzero estimates
   within ±50%. **Reports performance, not costs — never cite it for a
   dollar figure.**
5. **CRS counter.** CRS In Focus **IF12072, "Advances in Satellite Methane
   Emissions Measurement"** (title corrected from the handoff), updated
   Feb 13 2025, Haskett & Hammad. Verbatim: "At present, satellite- and
   aircraft-based measurements cost more than the BU strategy described
   above." (BU = bottom-up emissions-factor estimation.) This carries the
   honest form of the claim: the cost of an *accurate* estimate is falling;
   the cheap historical option was the inaccurate one.
6. **Sensor cost gap.** EPA *Enhanced Air Sensor Guidebook* (Clements &
   Duvall, EPA/600/R-22/213, Sept 2022), Table 2-3: reference monitors
   **$15,000–40,000**; air sensors **$100–5,000**; sensor data quality
   "Unknown and may vary," not usable for regulatory monitoring. Cite EPA
   directly for both ends of the gap.
7. **Valuation disagreement anchor.** Nordhaus, "A Review of the Stern
   Review," *JEL* 45(3):686–702, 2007, doi:10.1257/jel.45.3.686 — Stern's
   conclusions "depend decisively on the assumption of a near-zero time
   discount rate combined with a specific utility function." NAS 2017
   (*Valuing Climate Damages*) is the secondary anchor — canonical-tier,
   not independently re-verified this session.

## Verified as citations, dollar figures NOT verified

- **Esparza et al., RSER 178 (2023) 113265** (tiered Permian, satellite +
  aircraft vs 4×/yr OGI: "substantially more cost-effective"; 12% of
  targets carry >50% of emissions). Paywalled; **author team is
  GHGSat-affiliated — industry-authored, disclose if load-bearing.**
- **Kemp & Ravikumar, ES&T 55(13):9140–9149, 2021** (tiered LDAR equivalent
  reductions at lower cost). No numbers in open text.
- Net: peer-reviewed support exists for the *direction* (validated screening,
  modeled cheaper per equivalent mitigation) but **no clean peer-reviewed
  $-per-site figure survived verification. The handoff's vendor numbers
  ($1–2/km², $4,200/site/yr) stay out of the paper.**

## Consequence for open question 4 (own study vs cited structural argument)

The verification answers it halfway: the cost *series* the externality half
would need (a clean $/estimate trend) does not exist in the open literature —
the anchors support the qualitative claim only. Measuring that cost curve
properly would be an actual study (the S17-twin the handoff floats), not an
afternoon. Recommendation staged in plans/S17-proposed-text.md: keep the
externality half structural on these verified anchors for now.
