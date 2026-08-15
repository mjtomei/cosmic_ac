#!/usr/bin/env python3
"""cession_params.py — build params_cession.json: the sealed Fable-Carson
parameters PLUS a fourth regime, "negotiated cession," expressed in their own
parameter vocabulary (S18).

EVERY number added here is OURS, not theirs. Their parameters are sealed
(Aug 10, 2026) and carried unchanged from params_sealed.json (CC-BY 4.0,
doi:10.5281/zenodo.21879325). The cession regime answers Matthew's question
(2026-08-10/15): what has to be true for ceding negotiated control of one's
compute to be individually rational, and how does that change the model?

THE REGIME, in one paragraph. A material share of endpoints runs
manufacturer-partitioned shared-execution domains (S16 Case 3/4:
hardware-partitioned, owner-untouchable, underwriter-insured), and access to
them is SOLD under negotiated contracts rather than TAKEN by exploitation.
Four channels follow, each mapped to one of their parameter families:
  (a) the unnegotiated compute-acquisition market (botnets, cryptojacking)
      is partially displaced -> S1 frequency shades down;
  (b) blast radius is architecturally bounded and the insider/misconfig
      category is eliminated on the shared path -> severity truncation UP;
  (c) defense spend partially converts to rent-funded, underwriter-bundled
      protection -> Ch1 growth delta NEGATIVE;
  (d) remaining losses increasingly resolve as negotiated transfers
      (breach-of-contract damages, bounty-style settlements), not resource
      destruction -> per-regime transfer share UP (resource_only basis).
And one honest COUNTER-channel: a single partition design plus a single
negotiation protocol on the whole installed base is Bohme-Kataria's
same-production-batch cell -> dependence shift HIGHER than balanced, between
balanced and offense. Correlation is the price of the architecture.

Prior encoding follows their convention exactly: (p10/mode/p90) triples
matched on p10/p90 (lognormal/normal analytic, beta numeric); mode is a
consistency check only.

Sources for anchors: S16 = analysis/enterprise-idle-fleet/ (actuarial_model.py,
profit_per_machine.py, README); DBIR/KEV/Cyentia/Verizon figures are S16's
fetched inputs (actuarial-findings.json); Bohme & Kataria WEIS 2006;
Anderson et al. "Measuring the Cost of Cybercrime" 2013/2019; Grossman 1981
(warranties); Finifter, Akhawe & Wagner USENIX Security 2013 (VRP economics);
DOJ CFAA good-faith charging policy (May 2022).

Run: python cession_params.py   -> params_cession.json, cession_regime_params.csv
"""
import csv
import json
import pathlib

import numpy as np
from scipy.optimize import brentq
from scipy.stats import beta as beta_dist

HERE = pathlib.Path(__file__).parent
Z90 = 1.2815515655446004          # standard normal 90th percentile


# ---------------------------------------------------------- encoding helpers
def lognormal(p10, p90):
    return {"dist": "lognormal", "median": float(np.sqrt(p10 * p90)),
            "sigma_log": float(np.log(p90 / p10) / (2 * Z90))}


def normal(p10, p90):
    return {"dist": "normal", "mean": float((p10 + p90) / 2),
            "sd": float((p90 - p10) / (2 * Z90))}


def beta_fit(p10, p90):
    """Fit (alpha, beta) so the Beta's 10th/90th percentiles hit p10/p90.
    One-dimensional search on concentration at fixed mean (their betas are
    near-symmetric in this parameterization; residual checked below)."""
    mean = (p10 + p90) / 2

    def spread_err(conc):
        a, b = mean * conc, (1 - mean) * conc
        return (beta_dist.ppf(0.9, a, b) - beta_dist.ppf(0.1, a, b)) - (p90 - p10)

    conc = brentq(spread_err, 0.5, 5000.0)
    a, b = mean * conc, (1 - mean) * conc
    q10, q90 = beta_dist.ppf([0.1, 0.9], a, b)
    assert abs(q10 - p10) < 0.02 and abs(q90 - p90) < 0.02, (q10, q90)
    return {"dist": "beta", "alpha": round(float(a), 4), "beta": round(float(b), 4)}


def entry(prior, anchor, citation):
    return {"value_or_prior": prior, "anchor": anchor, "citation": citation,
            "verified": False, "knob": True, "placeholder": False,
            "s18_ours": True}


# ------------------------------------------------------- the cession regime
# (name, family, p10, mode, p90, encoder, anchor, citation)
CESSION = [
    ("ai_shift.cession.s1_freq_mult", lognormal, 0.90, 1.05, 1.30,
     "S1 freq mult 0.90/1.05/1.30 — balanced regime (1.0/1.15/1.4) shaded ~8-10% "
     "for displacement of the compute-acquisition slice of volume crime (botnet "
     "rental, cryptojacking, DDoS capacity — the unnegotiated market); AI offense "
     "on fraud/BEC, the bulk of S1 dollars, unchanged. OURS.",
     "Anderson et al. 2013/2019 cybercrime-cost composition; S18 construction"),
    ("ai_shift.cession.s2_freq_mult", lognormal, 0.90, 1.20, 1.60,
     "S2 freq mult carried from balanced unchanged (0.9/1.2/1.6): negotiated "
     "access does not deter targeted single-firm breaches; data theft targets "
     "remain. Declared carry-over.",
     "Fable-Carson sheet section 4 (balanced); S18 carry"),
    ("ai_shift.cession.severity_shift", lognormal, 1.00, 1.05, 1.15,
     "Severity shift carried from balanced unchanged (0/+5/+15%): offense-side "
     "severity gains are orthogonal to the cession channel. Declared carry-over.",
     "Fable-Carson sheet section 4 (balanced); S18 carry"),
    ("ai_shift.cession.s3_prob_mult", lognormal, 0.90, 1.30, 2.00,
     "S3a prob mult 0.9/1.3/2.0 — balanced (1.0/1.4/2.2) shaded ~10%: an "
     "attested negotiated-access fabric shrinks the exploitable initiation "
     "surface (agents that can buy access need not exploit it); modest because "
     "the S3a scenarios (payments infra, cloud) are not primarily "
     "endpoint-initiated. OURS.",
     "S16 Case-3 partition (owner-untouchable shared path); S18 construction"),
    ("ai_shift.cession.dependence_shift", normal, 0.05, 0.20, 0.40,
     "Dependence shift: target rho 0.15/0.30/0.50 minus modal baseline 0.10. "
     "HIGHER than balanced (0.125), between balanced and offense (0.275): one "
     "partition design + one negotiation protocol on the whole installed base "
     "is Bohme-Kataria's same-production-batch cell. Correlation is the price "
     "of the architecture — the regime's honest counter-channel. OURS.",
     "Bohme & Kataria WEIS 2006 (rho_G, same-batch exception); S16 actuarial "
     "model section 4; S18 construction"),
    ("defense.cession.severity_truncation", lognormal, 0.20, 0.35, 0.55,
     "Severity haircut 20/35/55% — S16 two-factor decomposition: a correlated "
     "boundary failure converts to per-machine reimaging (~$200) unless the "
     "attacker independently defeats each firm's own IT; Case-3 partition "
     "eliminates the insider/misconfiguration category on the shared path "
     "(11-33% of DBIR breach patterns); realized boundary-exploitation index "
     "502 (endpoint) -> 0.5 (hardware-partitioned) in KEV. Above "
     "defense-dominant (15/25/40) because architectural, not reactive. "
     "OURS — THE WEAKEST LINK of this study: our cession-lowers-losses channel "
     "enters through this parameter, which we choose.",
     "S16 actuarial_model.py (A1 boundary index, A4 category elimination, "
     "section 5 decomposition); Verizon DBIR; CISA KEV; S18 construction"),
    ("ch1.ai_growth_delta_pp.cession", normal, -6.0, -3.0, 0.0,
     "Ch1 growth delta -6/-3/0 pp/yr — security spend partially converts to "
     "rent-funded, underwriter-bundled protection (the cession contract prices "
     "residual risk into the rent split; warranty as quality signal). More "
     "negative than defense-dominant (-5/-2/+1) because the conversion is "
     "structural, not just unit-cost deflation. P(>0)=10% keeps D-10's "
     "straddle-zero spirit. OURS.",
     "S16 Path 1 (builder as underwriter); Grossman 1981; S18 construction"),
    ("ch2.transfer_share_cession", beta_fit, 0.50, 0.65, 0.80,
     "Transfer share of remaining measured losses 0.50/0.65/0.80 vs baseline "
     "blended 0.35/0.45/0.60: under negotiated access, a larger share of what "
     "is still recorded as loss resolves as contract transfers — "
     "breach-of-contract damages, bounty-style settlements — rather than "
     "resource destruction. Legal reclassification precedent: DOJ's 2022 CFAA "
     "good-faith policy; priced precedent: vulnerability-reward programs. "
     "Affects the resource_only basis ONLY (D-09 headline unchanged). OURS.",
     "DOJ CFAA charging policy May 2022; Finifter-Akhawe-Wagner 2013; "
     "S18 construction"),
]


def build():
    with open(HERE / "params_sealed.json") as f:
        params = json.load(f)

    params["_meta"]["s18_extension"] = (
        "Fourth regime 'cession' added by S18 (performance_commons, "
        "analysis/negotiated-cession/). All s18_ours entries are OUR "
        "constructions; sealed parameters carried unchanged.")

    rows = []
    for path, enc, p10, mode, p90, anchor, citation in CESSION:
        prior = enc(p10, p90)
        node = params
        parts = path.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = entry(prior, anchor, citation)
        rows.append({"path": path, "p10": p10, "mode": mode, "p90": p90,
                     "dist": prior["dist"],
                     "encoded": json.dumps({k: round(v, 6) if isinstance(v, float)
                                            else v for k, v in prior.items()}),
                     "anchor": anchor, "citation": citation})

    # four-regime weight PRESETS (mix-time knob, not sealed): cession weight
    # w_c taken from the sealed 30/45/25 proportionally (primary) or
    # offense-first (sensitivity: cession is the adaptation TO offense
    # pressure, so it plausibly displaces offense-regime mass first).
    params["knobs"]["cession_weight_presets"] = {
        "value_or_prior": {"none": 0.0, "early": 0.10, "mid": 0.25, "high": 0.50},
        "anchor": "S18 mix-time sensitivity grid; not a sealed belief",
        "citation": "S18", "verified": False, "knob": True, "placeholder": False}

    with open(HERE / "params_cession.json", "w") as f:
        json.dump(params, f, indent=1)
    with open(HERE / "cession_regime_params.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote params_cession.json ({len(rows)} cession entries), "
          f"cession_regime_params.csv")
    return params


if __name__ == "__main__":
    build()
