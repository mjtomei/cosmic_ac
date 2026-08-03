#!/usr/bin/env python3
"""
Actuarial comparison of three isolation architectures for shared enterprise compute.

METHOD — correcting the intuition. "Rate of attack surfaces leading to incidents
x cost of incidents" is the ATTRITIONAL layer only, and cyber is priced in two:

  (1) ATTRITIONAL: frequency x severity from claims experience. This is where
      the intuition applies.
  (2) ACCUMULATION / SYSTEMIC: priced by scenario, then capped, reinsured or
      excluded outright. Bohme & Kataria (WEIS 2006) give the canonical model —
      internal correlation rhoI (within one firm) and GLOBAL correlation rhoG
      (across the insurer's portfolio). Insurance is viable at high rhoI and LOW
      rhoG; high rhoG breaks risk-pooling and forces safety loadings that choke
      supply. Zeller & Scherer (European Actuarial J. 14:711-748, 2024) quantify
      the error from ignoring it: expected loss is UNCHANGED while VaR(0.995)
      rises from 76 to 113 — the mean is right and the capital requirement is
      ~33% too low.

VERIFIED INPUTS (all fetched; see actuarial-findings.json for URLs)
 F1 Frequency: 9.3% annual probability a typical firm suffers a significant
    cyber incident (2024), up from 2.5% in 2008. Cyentia IRIS 2025.
 S1 Severity, insurance claims: median insurable loss $83k; top 10% > $920k;
    top 2.5% > $5.0M; mean/median ~12x. n=69,683 US claims (~24,873 non-zero).
    Verizon 2026 Breach Impact Study.
 S2 Severity by insured size: SMB ~$38k, mid-market ~$96k, large enterprise
    ~$283k median; large-enterprise top 2.5% > $22M. Same source.
 S3 Severity, broader loss dataset: median $603k, geometric mean $464k,
    arithmetic mean $14M, 95th pct $32M. Cyentia IRIS 2025. The 7x gap to the
    claims median is population difference; both are carried as a band.
 S4 Business interruption dominates: highest median (~$90k) AND highest tail
    (~$5M) of the four loss types — relevant because a shared-compute failure
    is an availability failure first.
 B1 CASE 1 boundary: endpoint OS/app is the most-exploited boundary in
    existence — 502 of 1,656 CISA KEV entries (30%); Microsoft alone 382.
 B2 CASE 2 boundary: Xen Security Advisories 2011-2026, 508 total, of which 45
    unambiguous guest->host escalation (64 hedged, 118 loosest) = ~3-8
    host-compromise advisories/year. But REALISED exploitation is rare: ~11 of
    1,656 KEV are hypervisor products, only ~4-6 true guest->host escapes.
 B3 CASE 3 boundary: ZERO of 1,656 KEV entries relate to Spectre, Meltdown,
    transient execution, speculative side channels, SGX, TrustZone or CPU
    enclaves — despite 49 NVD CVEs matching "speculative execution" and 47
    matching "Intel SGX". Eight years of published attacks, no confirmed
    in-the-wild exploitation.
 C1 What CASE 3 uniquely removes: internal actors + misconfiguration. Misc
    Errors + Privilege Misuse = 11% of breaches (2026), 19% (2025), 33% (2024).
    Within internal-actor breaches error beats malice ~2:1. Verizon DBIR.
 C2 Insiders/third parties contributed to 34 of 50 extreme multi-party events —
    so the category elimination has tail value, not just attritional value.

MODELLING ASSUMPTIONS (clearly ours, not fetched)
 A5 CASE 3 vs CASE 4 (Matthew, 2026-08-03). These are different cases and
    should not be conflated:
      CASE 3 = manufacturer-engineered partition on EXISTING silicon (core and
        memory-controller partitioning, IOMMU, separate boot domain, firmware
        enforcement). This is what delivers the COMPANY-NON-INTERFERENCE
        property — nobody at the firm can touch the sharing mechanism — and
        that property alone eliminates the insider/misconfiguration category
        (C1), which is the largest actuarial win available. It needs no new
        chip.
      CASE 4 = NEW SILICON designed for shared execution from the start. Its
        justification is NOT insurance economics — Case 3 already banks the
        category elimination — it is (a) scale, if the goal is to carry a
        substantial share of all compute, and (b) buying down the RESIDUAL
        classes that Case 3 cannot reach: DRAM-substrate attacks (Rowhammer,
        RAMBleed) via memory architecture, DMA via bus topology, and stale
        on-core state via architectural flush primitives. The security
        literature points the same way — Ge et al.'s follow-up concludes "the
        current architecture does not provide the OS sufficient means to
        enforce time protection, and hardware support is needed." Case 4 is
        also the paper's own Appendix A phase three, "hardware built for this
        from birth."
 A0 IDLE-GATING (verified 2026-08-03, see co-execution-verification.md): the
    premise that hardware attacks need simultaneous execution is FALSE as a
    general claim. Only a minority (PortSmash, TLBleed, cross-thread RSB, and
    the live-victim cache channels) require concurrency; ~20 families attack
    state the victim left behind, and Meltdown/RAMBleed need no victim
    execution at all. Whole-machine idle admission DOES retire the
    concurrency-dependent class plus the cross-core cache channels that
    flush-on-switch cannot reach — a real, creditable control — but it is NOT
    immunity, so Case 3's index below is NOT reduced further for it.
 A1 Boundary exposure index, used as a RELATIVE frequency multiplier: taken
    from realised in-the-wild exploitation of each boundary type. Case 1 = 502
    (KEV endpoint entries), Case 2 = 5 (true guest->host escapes), Case 3 = 0.5
    (zero observed in 8 years; floored above zero because absence of evidence
    in a forensically hard-to-attribute class is not evidence of absence).
 A2 Baseline incremental frequency: we do NOT know how much sharing adds to a
    firm's 9.3% base rate. The model is therefore PARAMETRIC in p_base — the
    annual probability that shared workload causes an incident under Case 1 —
    and the cases scale from it by A1.
 A3 Expense/profit loading: premium = expected loss / 0.65, i.e. a 65% target
    loss ratio, mid-range for commercial cyber.
 A4 Category elimination: Case 3 removes internal-actor and misconfiguration
    exposure ON THE SHARED PATH only (11-33% of breach patterns, C1).
"""

FREQ_BASE = 0.093            # F1
SEV_MED_CLAIM, SEV_P90, SEV_P975 = 83_000, 920_000, 5_000_000     # S1
SEV_MED_IRIS, SEV_MEAN_IRIS, SEV_P95_IRIS = 603_000, 14_000_000, 32_000_000  # S3
LOSS_RATIO = 0.65            # A3
BOUNDARY = {"Case 1 same OS/network": 502, "Case 2 separate VM + NIC": 5,
            "Case 3 hardware-partitioned": 0.5}                    # A1
CAT_ELIM = {"Case 1 same OS/network": 0.0, "Case 2 separate VM + NIC": 0.0,
            "Case 3 hardware-partitioned": 0.11}                   # A4, conservative end of C1

print("=== 1. Severity: why the mean is the wrong number ===")
print(f"  claims median      ${SEV_MED_CLAIM:>12,}")
print(f"  claims 90th pct    ${SEV_P90:>12,}   ({SEV_P90/SEV_MED_CLAIM:.0f}x median)")
print(f"  claims 97.5th pct  ${SEV_P975:>12,}   ({SEV_P975/SEV_MED_CLAIM:.0f}x median)")
print(f"  IRIS median        ${SEV_MED_IRIS:>12,}")
print(f"  IRIS ARITH. MEAN   ${SEV_MEAN_IRIS:>12,}   ({SEV_MEAN_IRIS/SEV_MED_IRIS:.0f}x its own median)")
print("  -> pricing off a mean overprices the typical case and still misses the tail;")
print("     insurers price the attritional layer off medians and hold capital for the rest.\n")

print("=== 2. Attritional layer, parametric in p_base ===")
print("  p_base = annual probability shared workload causes an incident under Case 1.")
print("  Expected loss uses the claims median (attritional proxy); premium = EL/0.65.\n")
hdr = f"{'p_base':>8s} | " + " | ".join(f"{k.split()[1]:>22s}" for k in BOUNDARY)
print(f"{'':>8s} | " + " | ".join(f"{k:>22s}" for k in BOUNDARY))
for p_base in (0.001, 0.005, 0.01, 0.05):
    row = f"{p_base:8.3f} | "
    cells = []
    for name, idx in BOUNDARY.items():
        p = p_base * idx / BOUNDARY["Case 1 same OS/network"]
        p *= (1 - CAT_ELIM[name])
        el = p * SEV_MED_CLAIM
        prem = el / LOSS_RATIO
        cells.append(f"EL ${el:8,.0f} P ${prem:8,.0f}")
    print(row + " | ".join(f"{c:>22s}" for c in cells))

print("\n  Relative premium, Case 1 = 1.00:")
base_idx = BOUNDARY["Case 1 same OS/network"]
for name, idx in BOUNDARY.items():
    rel = (idx / base_idx) * (1 - CAT_ELIM[name])
    print(f"    {name:30s} {rel:8.4f}   ({1/rel:,.0f}x cheaper)" if rel else f"    {name:30s} 0")

print("""
=== 3. What actually separates the cases ===

  Frequency of boundary failure separates them LESS than expected. Realised
  exploitation of the Case 2 boundary is already rare (~4-6 confirmed
  guest->host escapes in 15 years of KEV) and of the Case 3 boundary is
  zero-observed. The real separation is elsewhere:

  CASE 1  sits on the most-attacked boundary in existence (30% of all KEV) and
          gives an underwriter nothing to credit. Shared work inherits the full
          endpoint frequency and the full loss mix.
  CASE 2  moves to a boundary with a measurable advisory rate (~3-8/yr) but very
          low realised exploitation, AND the separate NIC blocks lateral
          movement — which matters disproportionately because business
          interruption carries both the highest median (~$90k) and the highest
          tail (~$5M) of the four loss types.
  CASE 3  is the only one that removes an entire actuarial CATEGORY: internal
          actors and misconfiguration, 11% of breach patterns in 2026 and 33%
          in 2024. Nobody can misconfigure what nobody can touch. That value
          extends to the tail — insiders and third parties contributed to 34 of
          50 extreme multi-party events.

=== 4. The problem none of them fixes ===

  Global correlation rhoG is what determines insurability, and all three cases
  put ONE software or hardware design on every endpoint in the portfolio. In
  Bohme & Kataria's 2x2 that is the hard-to-insure quadrant — high internal AND
  high global correlation, the "worm/common software" cell.

  Case 3 is the sharpest version of the paradox: it has the best attritional
  profile and the WORST correlation profile, because a manufacturer-engineered
  partition is a single design shared by the whole installed base. Bohme &
  Kataria rate hardware failure as low-rhoG only with an explicit exception —
  "unless defective computers belong to same faulty production batch." A
  manufacturer partition IS one batch.

  Consequence for the plan: expect a real quote to rate the attritional layer
  off DBIR/IRIS experience and then CAP OR EXCLUDE the accumulation layer.
  The cap is the number that matters commercially. Isolation architecture does
  not move it directly — but the decomposition in section 5 does.

=== 5. The two-factor decomposition — why rhoG is smaller than it looks ===
    (Matthew, 2026-08-03)

  Compromise of the shared compute domain and loss of company data are two
  DIFFERENT events, and only the first is correlated. A loss requires BOTH:

     (a) the shared-domain boundary fails  — correlated: one design, every unit
     (b) the attacker then defeats THAT company's own IT security — idiosyncratic

  Factor (b) is independent across firms, because every company's security
  posture, segmentation, monitoring and credential hygiene is its own. So the
  systemic event does not produce a systemic LOSS; it produces N independent
  conversion attempts.

  Two consequences, and the second is the important one:

  1. Expected systemic loss scales by p_conv. At p_conv = 0.10 across a
     1M-endpoint portfolio, $83bn of naive exposure becomes $8.3bn.
  2. The loss stops being a JUMP and becomes a SUM of independent Bernoullis.
     Its coefficient of variation collapses as ~1/sqrt(N) — about 0.003 at
     p_conv = 0.10 and N = 1M. A tightly concentrated distribution is exactly
     what an insurer can hold capital against; a single correlated jump is what
     it cannot. This is the difference between uninsurable and rateable.

  WHAT THE CORRELATED EVENT COSTS WHEN CONVERSION FAILS. If the boundary breaks
  but company defences hold, the loss is compute theft plus reimaging — bounded
  and per-unit. At an assumed ~$200/machine, a 1M-endpoint systemic event costs
  ~$200M rather than the ~$83bn implied by treating every foothold as a breach.
  The systemic scenario for Cases 2 and 3 is "N machines need reimaging," not
  "N data breaches."

  BUT IT DOES NOT RESCUE CASE 1. There, a boundary failure lands the attacker
  already inside the business OS and network with local context — the second
  factor barely exists, so most of the correlated event converts. The
  decomposition is worth the most exactly where the isolation is strongest,
  which compounds rather than substitutes for the case ranking above.

  HONEST RESIDUALS. Ransomware needs no exfiltration, though in Cases 2 and 3
  the shared domain cannot reach business storage, so it folds back into the
  conversion term. If the shared domain can observe memory or issue DMA,
  exfiltration may not need to defeat IT security separately — which is why
  IOMMU and memory partitioning are load-bearing rather than optional. And
  compute theft at scale may be reportable even when bounded in dollars.

  Portfolio construction still matters — multiple independent hardware designs,
  staged rollout, per-event limits — but the decomposition means the accumulation
  layer is a rateable exposure rather than an uninsurable one.
""")
