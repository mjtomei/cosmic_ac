# Does idle-gating defeat hardware attacks? Verification result

**Question (Matthew, 2026-08-03):** "those hardware attacks require simultaneous
execution. So a system that checks whether anything is running at the hardware
level before sharing isn't vulnerable to those without a bypass of that check."

**Verdict: the co-execution premise is FALSE as a general claim.** Verified
2026-08-03 against vendor security advisories, Linux kernel hardware-vulnerability
documentation, and the original academic papers. I had endorsed this reasoning
before checking it; the check does not support it.

## What actually requires simultaneous execution — a minority

| Attack | Needs concurrency | Needs SMT |
|---|---|---|
| PortSmash (CVE-2018-5407) | **yes** | yes |
| TLBleed | **yes** | yes |
| Cross-Thread Return Address Predictor (CVE-2022-27672) | **yes** | yes |
| Flush+Reload, LLC Prime+Probe | **yes** (live victim) | no — works cross-core |
| Foreshadow/L1TF *residual after L1D flush* | yes | yes |

PortSmash and TLBleed are pure *contention* channels — they sample a bandwidth
resource with no persistent state, so a stopped victim leaves nothing to read.
These are genuinely defeated by idle admission.

## What does NOT require it — the larger and more recent set

Roughly twenty families work against state the victim **left behind after it
stopped**: MDS (RIDL, Fallout, ZombieLoad, MLPDS, MDSUM), TAA, Downfall/GDS,
RFDS, Zenbleed, Retbleed, Inception/SRSO, SRBDS, Processor MMIO Stale Data,
Indirect Target Selection / Training Solo, Branch Privilege Injection, AMD TSA,
FP-DSS, VMSCAPE, the 2026 Cross-VM L1D leak on Zen 4 — plus **Meltdown and
RAMBleed, which read the victim's memory with no victim execution at all.**

The vendors' own words refute the premise directly:

- **RFDS (CVE-2023-28746):** "None of the affected cores support SMT."
- **AMD TSA:** "TSA-L1 will not result in information leakage between SMT
  threads. The microtag structure is not shared between SMT threads."
- **Zenbleed (Project Zero):** "Note that it is not sufficient to disable SMT."
- **Cross-VM L1D leak (S&P 2026):** the precondition is "the victim VM has
  previously accessed (i.e., cached) this bit" — residency, not execution.
- **Downfall** defeats SGX at its *highest* configuration — SMT disabled, all
  buffer and L1D flushes applied — because VERW and L1D_FLUSH do not clear the
  vector register file.

## What idle admission genuinely buys — real, but narrower

1. **It retires the entire concurrency-dependent class.** This is precisely the
   "Cross-Thread" attack vector that the Linux kernel now models as separable:
   *"Cross-thread mitigation may not be required if core-scheduling or similar
   techniques are used to prevent untrusted workloads from running on SMT
   siblings."* Intel's own MDS guidance endorses the same move — group
   scheduling *"or ensuring the other thread is idle."*
2. **Because it idles the whole machine rather than one core, it also kills the
   cross-core LLC and interconnect channels that flush-on-switch provably
   cannot.** Ge, Yarom, Cock & Heiser (EuroSys 2019): *"flushing cannot prevent
   cross-core attacks through a shared cache."* Whole-machine idleness defeats
   Flush+Reload and Prime+Probe; per-core SMT avoidance does not. **This is a
   real advantage over the standard mitigation set, and it is Matthew's point in
   its defensible form.**

## The honest residual — five classes idle-gating does not touch

1. **Stale on-core state.** Closable only by correct, current microcode plus
   VERW / L1D_FLUSH / IBPB at *every* transition including C-state entry. That
   mitigation has shipped broken at least twice (Intel's Skylake-client VERW;
   L1D Eviction Sampling, CVE-2020-0549) and **does not cover the vector
   register file at all.**
2. **Rowhammer and RAMBleed.** Need only the victim's bits in adjacent DRAM
   rows. RAMBleed is the sharpest counterexample: it reads another process's
   memory by hammering its *own*, with the victim never executing — and unlike
   Rowhammer it works against ECC. Current in-DRAM mitigations are broken on
   DDR5 (ZenHammer, Phoenix 2025).
3. **DMA from peripherals.** IOMMU is necessary and demonstrably insufficient
   (Thunderclap, NDSS 2019, against macOS/FreeBSD/Linux; Windows "uses the IOMMU
   only in limited cases"). Directly relevant to Case 2's added NIC.
4. **Cold-boot / DRAM remanence.** Physical access to a machine on someone
   else's premises.
5. **Plain memory disclosure** via the kernel physmap or a hypervisor escape.
   "Idle" is simply orthogonal to spatial isolation.

## The check itself, as a trust boundary

Partial precedent exists for enforcing a platform property from outside the
constrained domain: firmware-forced SMT-off (`nosmt=force`, not undoable from
the OS), MPAM's Secure-PARTID configuration lock, and — the closest analogue —
**SGX and SEV-SNP attestation reporting Hyper-Threading state and microcode
level to a remote verifier.**

But all of those attest **static platform configuration**. No shipped root of
trust or BMC attests **dynamic runtime idleness**. Linux core scheduling, the
nearest existing mechanism, documents its own race: *"there could be small
window of time during which untrusted tasks run concurrently."* That capability
would have to be designed and defended, not cited.

## The gap that is also the opportunity

**Idle-gated admission is completely standard, and nobody treats idleness as a
security boundary.** HTCondor gates on keyboard idle and load average, and its
security chapter never mentions idleness. BOINC's threat model runs the other
way. Borg separates security isolation (chroot jail) from performance isolation
in adjacent subsections. Azure Harvest VMs apply Intel CAT to harvested
workloads and state the reason as *interference*, not confidentiality.

The one published system that deliberately reads a scheduling knob as a
side-channel defence is Varadarajan, Ristenpart & Swift (USENIX Security 2014),
"soft isolation" — and its provenance is exactly this move: Xen's minimum-run-time
guarantee existed "for the stated purpose of improving the performance of batch
workloads," and they were first to analyse it as a defence.

**So the mechanism is established practice and the security claim on top of it
is genuinely unclaimed.** That is a real opening — but it has to be argued and
measured, not asserted, and the academic ceiling is known: *"in all processors we
studied, at least one significant channel remains… closing all timing channels
seems impossible on contemporary mainstream processors"* (Ge et al.).

## Consequence for the actuarial model

Case 3's attritional residual is **not** reduced to near-zero by idle-gating, as
I implied before checking. The defensible position is:

> Whole-machine idle admission plus mandatory scrub-on-transition (VERW,
> L1D_FLUSH, IBPB, and a decorrelation delay) is a **strong reduction in attack
> surface** — it retires the concurrency-dependent class outright and the
> cross-core cache channels that flushing cannot reach. It is **not immunity**,
> and the residual is dominated by DRAM-substrate attacks, DMA, and stale
> on-core state in structures no current flush instruction clears.

For an underwriter this is still creditable — it is a documented, testable
control that removes named attack classes — but it should be presented as
defence-in-depth, not as a boundary proof.


## Addendum — Case 4, and what it is actually for (Matthew, 2026-08-03)

The residual classes above are the argument for **new silicon as a separate
case**, not for abandoning Case 3.

**Case 3 — manufacturer partition on existing silicon** already banks the
largest actuarial prize: the company-non-interference property, which
eliminates the insider and misconfiguration category (11% of 2026 breach
patterns, 33% in 2024, and present in 34 of 50 extreme multi-party events).
Nobody at the firm can misconfigure what nobody at the firm can touch. That
needs core and memory-controller partitioning, an IOMMU, a separate boot
domain and firmware enforcement — all of which ship today. **It does not need
a new chip.**

**Case 4 — silicon designed for shared execution from the start** is justified
by two things Case 3 cannot supply:

1. **Scale.** If the goal is to carry a substantial share of all compute rather
   than to monetise idle time on machines bought for other reasons, the NRE
   amortises across a fleet large enough to change the arithmetic entirely.
   This is the paper's own Appendix A phase three — "hardware built for this
   from birth" — and its economics are the endgame's, not the retrofit's.
2. **The residual attack classes.** Everything idle-gating and flush-on-switch
   cannot reach is addressable in architecture but not in software: DRAM
   substrate attacks (Rowhammer, RAMBleed) via memory topology and per-domain
   DIMMs; DMA via bus separation rather than IOMMU configuration; and stale
   on-core state via architectural flush primitives that clear *every*
   structure rather than the subset current instructions happen to cover. The
   security literature reaches the same conclusion independently: Ge, Yarom,
   Cock & Heiser's follow-up work finds that "the current architecture does not
   provide the OS sufficient means to enforce time protection, and hardware
   support is needed," and proposes a new ISA instruction (fence.t) precisely
   because software cannot close the gap.

**So the ladder is:** Case 2 buys network and storage separation; Case 3 buys
the category elimination and needs no new silicon; Case 4 buys down the
residual and is justified by scale. Conflating 3 and 4 overstates what the
insurance argument requires — the underwriting case is complete at Case 3.


## Design invariants, stated (Matthew, 2026-08-03)

Confirmed: **every case under consideration assumes both**, and the analysis
above should be read against them rather than against a bare architecture.

  **I1 — No simultaneous execution.** Shared work is admitted only when no
  business workload is running, enforced from outside the shared domain.
  **I2 — Full scrub of shared storage at every transition**, in both
  directions (idle→admit and admit→resume).

### What I1 + I2 close

With both invariants, the *stale on-core state* residual — which the section
above lists as the largest — is mostly closed, because the structures those
attacks read are architecturally clearable:

| State | Clearing mechanism |
|---|---|
| Fill buffers, load ports, store buffers | VERW (with MD_CLEAR microcode) |
| L1 data cache | L1D_FLUSH |
| All cache levels incl. LLC | WBINVD |
| Branch predictors | IBPB |
| Vector / FP / integer register files | explicit zeroing (VZEROALL and equivalents) |

That covers the mechanisms behind MDS, TAA, L1TF, RFDS, Downfall and the
predictor-poisoning family. **I2 is what makes the difference** — the reason
Downfall defeats SGX at its highest configuration is that VERW and L1D_FLUSH
*alone* do not touch the vector register file. A scrub defined as "all shared
storage" rather than "the vendor's named flush instructions" closes that gap.

### What remains after I1 + I2 — and it is a different shape

1. **Microarchitectural state with no *documented* clearing instruction** —
   prefetchers, cache replacement policy, memory arbiters. See the correction
   below: these are not unflushable, they are undocumented. Note also the class
   change: these are *timing* channels that leak access patterns, not *data*
   channels that leak contents. Far lower bandwidth, far harder to weaponise,
   and not a register-contents disclosure.
2. **Zenbleed-class bugs in the clearing logic itself.** Zenbleed was not
   residual data awaiting a flush; it was a defect in the register-file
   management path (the vzeroupper optimisation), which needed a chicken bit
   rather than a scrub. **A scrub cannot fix a bug in the scrub.** This is
   irreducible and argues for microcode currency as a monitored control.
3. **Everything that was never about shared storage.** I1 and I2 are orthogonal
   to these, and they are what Case 4 exists to address:
   - **Rowhammer / RAMBleed** — perturbs or infers via *adjacent DRAM cells*.
     Nothing is read from shared storage at all; RAMBleed reads the attacker's
     own memory. Needs memory topology, not flushing.
   - **DMA from peripherals** — bypasses execution entirely; needs IOMMU
     discipline and, properly, bus separation.
   - **Cold-boot / remanence** — physical, post-power.
   - **Memory-resident secrets reachable after a spatial escape** — if the
     hypervisor or kernel boundary fails, "idle and scrubbed" is irrelevant.

### Net

I1 + I2 convert the residual from *"the attacker reads what the victim left in
registers and buffers"* to *"the attacker infers access patterns through
structures with no clearing interface, or attacks the memory substrate
directly."* That is a materially better position than the one the verification
section describes, and it is the position the actuarial model should credit —
provided both invariants are enforced from outside the shared domain and
microcode currency is monitored, since two of the three residual classes are
defects rather than design properties.


## I3 — decorrelating scrub for unflushable state (Matthew, 2026-08-03)

Proposed third invariant: **software that deliberately obfuscates or overwrites
the microarchitectural state that has no clearing interface**, as a second line
of defence behind I1 and I2.

### Why it is possible at all

The structures left over after I2 — prefetcher training, cache
replacement-policy state (PLRU trees, LFSRs), memory arbiter position — cannot
be *addressed*, so they cannot be flushed. But they can all be **driven**:

- **Prefetchers** train on access patterns; a workload with randomised strides
  overwrites that training.
- **Replacement-policy state** advances on every access; touching all ways in
  every set walks a PLRU tree to a known or random condition, and an LFSR
  advances regardless of intent.
- **Arbiters** hold round-robin position and queue depth; memory traffic moves
  them.

So the mechanism is: run a decorrelating workload at the transition. It is not
a flush — it is state saturation, which destroys the correlation between what
the victim did and what an attacker can later measure.

### The structural advantage: transition frequency

Time-protection research is bounded by cost. Ge et al. must flush on **every
partition switch**, so the mitigation competes directly with scheduler
throughput and every microsecond matters — which is why "pad the flush to
worst-case latency" is a real constraint for them and why they conclude
hardware support is needed.

**Idle harvesting transitions a few times a day, not thousands of times a
second.** A scrub that would be prohibitive in a general-purpose OS is
affordable here: seconds of decorrelating work per transition is a rounding
error against an idle window measured in hours. **This model can afford a
mitigation that the systems literature had to reject on cost** — which is a
genuine advantage of the harvesting shape, not a workaround.

### The honest limits

1. **Noise is a cost-raiser, not a channel-closer.** The standard objection to
   injected noise holds: it increases the attacker's required sample count
   rather than eliminating the channel, and a patient attacker with unlimited
   trials wins. As a *second* line behind I1 and I2 that is the correct role,
   and it should be described that way and not as a boundary.
   The bar it raises is real, though — AMD's own TSA guidance notes that "to
   reliably exfiltrate data, an attacker must typically be able to invoke the
   victim many times," and the victim here is gone.
2. **It does nothing for the memory substrate.** Rowhammer, RAMBleed, DMA and
   cold-boot are untouched — no amount of microarchitectural obfuscation
   affects an attack that reads adjacent DRAM cells. Those remain Case 4's
   territory.
3. **It is defeated by defects in itself**, exactly as I2 is: a decorrelator
   that a CPU bug lets an attacker distinguish from real work is not
   decorrelating.

### Why this one is worth building anyway: it is measurable

Unlike most controls in this space, the effectiveness of a decorrelating scrub
against a specific channel is **empirically testable**. Run the published
attack suite — Prime+Probe, Flush+Reload, the prefetcher channels — with and
without the scrub, and measure the achieved channel bandwidth. That produces a
number, repeatable by a third party.

That matters commercially rather than only technically. An underwriter cannot
credit "we believe this helps." It can credit "the published attack suite was
run against this configuration and measured channel bandwidth fell by X, audited
by Y." **I3 is the control most likely to convert into an actual premium
reduction, precisely because it is the one that yields a measurement** — and
building the harness that produces that measurement is a small, well-defined
piece of work that could be done before any hardware exists.


## Correction — "unflushable" was wrong (Matthew, 2026-08-03)

I called prefetcher, replacement-policy and arbiter state *unflushable*. That
is not right. **The state is finite and deterministic, so a driving sequence
into a known condition exists; what is missing is documentation, not
capability.** Reaching it requires reverse-engineering the microarchitecture.

**There is published precedent for exactly this reverse engineering.** Abel &
Reineke built `nanoBench` (arXiv:1911.03282) specifically to characterise
undocumented x86 microarchitectural behaviour from outside, and the same authors'
work measures and models cache replacement policies on real Intel parts. This is
an established research method with public tooling, not a speculative capability.

**For prefetchers there is an easier path still: they can simply be turned off.**
Intel exposes prefetcher control via MSR (0x1A4), so the shared domain can run
with prefetching disabled and the state question does not arise for the window.
Disabling costs throughput on the shared workload — which is a price paid in the
tenant's own performance, not the host's security.

So the honest limit is not impossibility, it is **maintenance**: the sequence is
microarchitecture-specific and must be re-derived for each CPU generation, and
validated against parts you may not have. That is an ongoing engineering
obligation with a real cost — and it is precisely the kind of obligation that
belongs in the *builder's* hands rather than each enterprise's, which is another
argument for the manufacturer-partition shape of Case 3.

**And it is a search problem, which is this paper's own thesis applied to itself.**
Finding an instruction sequence that drives an undocumented structure to a known
state is a search over sequences with a measurable objective — exactly the class
of problem §6 argues machine intelligence is now good at, and exactly the class
of tacit, per-part, never-pooled knowledge §2 says goes unproduced because no
individual actor is paid to produce it. If the argument is right anywhere, it
should be right here: this is optimization work that is valuable to everyone,
cheap for a model to search, and currently done by nobody.

**Consequence for I3:** the decorrelating scrub is the fallback for structures
whose flush sequence has not *yet* been derived, not the permanent answer for
structures that cannot be flushed. That is a better position — it converts an
open-ended residual into a work item with a known method, and the measurement
harness described above doubles as the validation harness for each derived
sequence.
