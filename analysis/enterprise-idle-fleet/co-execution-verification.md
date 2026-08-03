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
