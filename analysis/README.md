# Analysis — data behind the paper's novel numbers

Convention (2026-07 review): any novel analysis in the paper gets a CSV here with
computations written out, sources for every number we did not derive, and
assumptions documented.

| File | What it backs |
|---|---|
| `cost_model.py` → `consumer_vs_datacenter_cost.csv` | Consumer-device vs datacenter economics, **hardware excluded** (stranded-compute case) and **hardware included** (new-market case), with margins at spot-like discounts (60/75/90% off two reference prices). Sources and assumptions are commented in the script header. |
| `fig3_coordination_anchors.csv` | Figure 3 (coordination gap): which points are measured (DiLoCo/OpenDiLoCo/INTELLECT-1) and which are illustrative. |
| `fig4_demand_anchors.csv` | Figure 4 (machine demand): the $0.50 / $0.08 anchors, the spot-discount band, and what is conceptual. |

Headline from `cost_model.py` (see csv for the grid): marginal cost of a serving
Mac-class device is ~$0.005/hr hardware-excluded; hardware-included it is
~$0.04/hr at 50% utilization, ~$0.06 at 30%, ~$0.18 at 10%. Against the
$0.50/hr datacenter reference priced at spot-like discounts (60–90% off →
$0.05–0.20/hr revenue): the hardware-excluded case clears margin everywhere;
the hardware-included case clears margin at ≥30% utilization for all but the
deepest (90%) discount, and fails at 10% utilization for everything but the
mildest discount. Translation for the business plan: stranded compute is
profitable at any utilization; giving devices away only pays if the network
keeps them ≥~30% sold or prices above the deepest spot tier.
