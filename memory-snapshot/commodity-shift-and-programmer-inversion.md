---
name: commodity-shift-and-programmer-inversion
description: Why computing went big→small/commodity (killer micros + designing for the programmers you have); the inversion — beyond-human programmers let us architect for harder targets again
metadata: 
  node_type: memory
  type: project
  originSessionId: aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b
---

Matthew's point (2026-06-22) for the paper — anchors §2 / §4 / §10, esp. §10(1) "build for the compiler you'll have":

**Why we moved from big machines to small/commodity, and away from custom supercomputer networking — two forces:**
1. **Commodity parts advanced faster** — volume economics; the "killer micros" displaced custom big-iron (clusters of commodity nodes + commodity networking beat custom MPP/vector).
2. **Designs had to support bad / poorly-resourced programmers** — architecture was constrained to what the available (often weak) programmer talent could use.

**Empirical anchor:** **Itanium / EPIC / VLIW failed because it bet on a compiler that didn't exist** — you were punished for targeting a better-than-available compiler.

**The inversion (the forward bet):** machine intelligence — beyond-human programmers / the commons — lifts force #2. Now we are *allowed* to architect machines targeting beyond-human programmers: harder-to-program, reconfigurable, custom, exotic, big. The Itanium bet becomes winnable. This historicizes §10's "build for the compiler you will have, not the one you had."

**Honest nuance:** the inversion clearly lifts the *programmability* constraint (#2); it does NOT automatically repeal *commodity volume economics* (#1) — though ML demand (§3) creates volume for new classes and a commons can lower custom-design cost. Keep the cleanest claim to #2.

**STATUS: incorporated into §10 (the inversion paragraph), 2026-06-22.**

**Citations (VERIFIED 2026-06-22 by web search, now cited inline in §10):**
- Wood & Hill, "Cost-Effective Parallel Computing," *IEEE Computer* 28(2):69–72, Feb 1995, DOI 10.1109/2.348002 — the costup/speedup framework (cost-effective without linear speedup). NB it is the *framework*, not a "small wins" polemic; cited for the cost analysis, paired with NOW/killer-micros for the displacement claim.
- Anderson, Culler & Patterson (+NOW Team), "A Case for NOW (Networks of Workstations)," *IEEE Micro* 15(1):54–64, Feb 1995, DOI 10.1109/40.342018.
- E. D. Brooks III, "The Attack of the Killer Micros," invited talk, **SC'90** (1990, NOT 1989 — a talk/coinage, no formal paper; lean on a secondary source for the written record).
- Gordon Bell, "Bell's Law for the Birth and Death of Computer Classes," *CACM* 51(1):86–94, Jan 2008, DOI 10.1145/1327452.1327453.
- Becker, Sterling et al., "BEOWULF: A Parallel Workstation for Scientific Computation," ICPP 1995 (commodity COTS + Ethernet).
- (vector decline, optional: Espasa, Valero & Smith, "Vector Architectures: Past, Present and Future," ICS'98.)
- **Itanium anchor:** Knuth interview (Binstock), *CACM* Jul/Aug 2008 — "the wished-for compilers were basically impossible to write" (best quote); Hennessy & Patterson, "A New Golden Age for Computer Architecture," *CACM* 62(2), Feb 2019.

**CONFIRMED (point D):** no paper states "design for the programmers/compilers you actually have" as a forward thesis — it appears only as the implicit moral of Itanium + scattered codesign folklore. The inversion is genuinely under-articulated (relatively original).

(Matthew confirmed 2026-06-22: this is the only point — no separate second one.)

Related: [[doc-purpose-forward-looking-positioning-bet]], [[distributed-logical-machine-telos]] (custom networking now returning as commodity-ish via DPU/CXL/RDMA — the pendulum, enabled by the commons).
