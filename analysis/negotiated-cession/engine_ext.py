"""engine_ext.py — S18 EXTENSION of the Fable-Carson cyber-cost engine.

PROVENANCE: forked verbatim from sim/engine.py of
github.com/bradrcarson/cowen-cyber @ fc73ac89 (2026-08-10), CC-BY 4.0.
Cite: Fable, C. & Carson, B. (2026), "Projected Cyber Security Costs from
Frontier AI: A Response to Tyler Cowen," doi:10.5281/zenodo.21879325.

Every modification is marked "# S18-EXT". The extensions (OURS, not theirs):
  1. A fourth regime, "cession" (negotiated cession of compute control),
     added to the mixture; its parameters live in params_cession.json and are
     OUR constructions, documented in cession_params.py.
  2. simulate() takes regimes= and years= so the horizon can be rolled past
     the sealed 2026-2028 window. Beyond 2028: AI deviation ramp HELD at the
     sealed 2028 value (1.5), Ch4 phase-in held at 1.0, D-15 damping chained
     year-over-year (year y-1's systemic outcome damps year y). All of that
     is our labeled construction; the sealed forecast remains 2027-2028 only.
  3. Optional per-regime transfer share: a schema entry at
     ch2.transfer_share_<regime> overrides the global draw for that regime
     (used to encode "negotiated payments are transfers, not resource
     losses" for the cession regime; affects the resource_only basis only).

Original module docstring follows.
------------------------------------------------------------------------

engine.py — compound frequency-severity Monte Carlo core (SEALED params).

Implements D-03/D-04 plus the late-sealed D-14 and D-15:

Strata
  S1  routine volume crime   negative-binomial frequency (gamma-Poisson
                             mixture) x lognormal severity, CLT aggregate.
                             Parameterized by frequency x MEAN severity (the
                             sheet's "mu set to match mean"). Baseline growth
                             = fitted measured trend ^ (1 - reporting share).
  S2  major single-firm      Poisson frequency x generalized-Pareto severity,
      events                 event-by-event. Own sealed frequency trend
                             (+3/+8/+15%/yr). Per-event cap = knobs.s2_cap_busd
                             (D-14, $250B), applied to BOTH worlds (economic
                             saturation, not an AI effect).
  S3  systemic/correlated    two variants (D-04):
        s3a anchored — 5 scenario entries (infra failure, Bashe worm, Lloyd's
            payments triple x first-year share) correlated through a Gaussian
            common-shock factor; AI dependence shift raises the loading.
        s3b fresh agentic event tree — the sheet's 8 parameters. Event rate =
            campaigns x P(foothold) x P(damaging). Per event: cascade runs
            n_cycles ~ 1+Geometric(p_patch) containment cycles (cap
            max_cycles); affected share = min(seed_share * R^n, blast_cap);
            duration = n_cycles x cycle_time; severity = damage_rate x
            duration x share/ref_share. AI-world only. s3_prob_mult is NOT
            applied (sheet: S3a scenarios only).
      Annual aggregate S3 loss capped at knobs.s3_annual_cap_busd (D-14,
      $3.5T), both worlds, per variant stratum.

AI shift-factors (sheet section 4) are regime-dependent multipliers; the
defense side is a per-regime severity-truncation haircut h: AI-world
severities x (1 - h). 2028 deviations from baseline ramp at run.ai_ramp_2028
(sealed 1.5).

D-15 post-event damping: within each inner path, if the simulated 2027
AI-world aggregate systemic (S3) loss >= knobs.damping_trigger_busd, the 2028
deviation-from-baseline of ALL section-4 multipliers (S1/S2 freq, severity
shift, S3a prob mult, dependence shift, truncation haircut) and the S3b
campaign rate is multiplied by defense.safeguard_damping (drawn per outer
draw, prior 0.5/0.7/0.9). This creates negative 2027->2028 autocorrelation.
With variant=both the trigger uses the S3a+S3b AI-world total (one simulated
world); a single-variant run uses its own systemic total. Channel 1 is not
damped (not a section-4 multiplier; post-event spend rises, mechanism c).

Channels
  Ch1  d1 = category_deflator x vendor_2026 x (1+labor_mult)
            x ((1+g+delta_pp/100)^n - (1+g)^n),  n = year-2026,
       plus a lagged response to realized excess losses (structural), plus
       the per-cell baseline offset from the fitted spend matrix.
  Ch2  d2 = reporting_correction x (cell-scaled S1+S2 delta + S3 delta);
       the correction (1/(1+uplift), <1) converts apparent-basis excess to
       true excess (sheet section 6).
  Ch4  triangular knob draw, phase-in 0.5 (2027) / 1.0 (2028).

Counterfactual construction — common random numbers (CRN): each inner draw
simulates a PAIRED (baseline, AI) year sharing randomness; deltas can be
negative (D-10).

Baseline geometry: growth factors are the FITTED trend's own growth
(proj_year / fitted_2024), so the fit's level residual at the 2024 anchor does
not leak into the simulated level (the observed 2024 level anchors the strata
params; the fitted trend supplies growth). Cell ratios rescale the
trend-anchored S1+S2 delta; the Ch1 baseline offset uses the fitted spend
matrix. S3 severities are scenario-anchored in absolute dollars, not rescaled.

Units: $B unless a name says otherwise.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from scipy.special import ndtr
from scipy.stats import norm, beta as beta_dist

from counterfactual_ext import cell_key, FORMS, WINDOWS   # S18-EXT: vendored

REGIMES = ("offense", "balanced", "defense", "cession")   # S18-EXT: 4th regime
YEARS = (2027, 2028)
VARIANTS = ("anchored", "fresh")
BASES = ("transfer_inclusive", "resource_only")

# Histogram support for headline deltas ($B). 0.25B bins; values outside are
# clipped into the end bins (mean/sumsq accumulators stay exact regardless).
# Upper edge 8000 covers S3 cap 3500 + capped S2 sums + Ch1/Ch4.
HEAD_EDGES = np.linspace(-1500.0, 8000.0, 38001)
# AI-world insurable industry losses (ILS consistency check).
LOSS_EDGES = np.linspace(0.0, 8000.0, 32001)


# ===================================================================== priors
class Prior:
    """A named prior with vectorized sampling and analytic quantiles.

    Supported specs:
      {"dist": "normal",     "mean": m, "sd": s}
      {"dist": "lognormal",  "median": m, "sigma_log": s}
      {"dist": "beta",       "alpha": a, "beta": b}
      {"dist": "triangular", "min": a, "mode": c, "max": b}
      {"dist": "uniform",    "low": a, "high": b}
    Scalars in the params file are fixed structural constants, not priors.
    """

    def __init__(self, spec: dict):
        self.spec = spec
        self.dist = spec["dist"]

    def sample(self, rng: np.random.Generator, size) -> np.ndarray:
        s = self.spec
        if self.dist == "normal":
            return rng.normal(s["mean"], s["sd"], size)
        if self.dist == "lognormal":
            return np.exp(rng.normal(np.log(s["median"]), s["sigma_log"], size))
        if self.dist == "beta":
            return rng.beta(s["alpha"], s["beta"], size)
        if self.dist == "triangular":
            if not (s["max"] > s["min"]):
                return np.full(size, float(s["min"]))
            return rng.triangular(s["min"], s["mode"], s["max"], size)
        if self.dist == "uniform":
            return rng.uniform(s["low"], s["high"], size)
        raise ValueError(f"unknown dist {self.dist}")

    def ppf(self, q: float) -> float:
        s = self.spec
        if self.dist == "normal":
            return float(norm.ppf(q, s["mean"], s["sd"]))
        if self.dist == "lognormal":
            return float(np.exp(norm.ppf(q, np.log(s["median"]), s["sigma_log"])))
        if self.dist == "beta":
            return float(beta_dist.ppf(q, s["alpha"], s["beta"]))
        if self.dist == "triangular":
            a, c, b = s["min"], s["mode"], s["max"]
            if not (b > a):
                return float(a)
            fc = (c - a) / (b - a)
            if q < fc:
                return float(a + np.sqrt(q * (b - a) * (c - a)))
            return float(b - np.sqrt((1 - q) * (b - a) * (b - c)))
        if self.dist == "uniform":
            return float(s["low"] + q * (s["high"] - s["low"]))
        raise ValueError(self.dist)


def _is_prior(v) -> bool:
    return isinstance(v, dict) and "dist" in v


def collect_priors(params: dict) -> dict[str, Prior]:
    """Walk the params tree; return {dotted.path: Prior} for every prior spec.
    Scenario-list entries are addressed as
    'strata.s3a.scenarios.<name>.annual_prob'. This registry is the tornado's
    parameter list."""
    out: dict[str, Prior] = {}

    def walk(node, path):
        if isinstance(node, dict):
            if set(node) >= {"value_or_prior", "placeholder"}:  # schema entry
                if _is_prior(node["value_or_prior"]):
                    out[path] = Prior(node["value_or_prior"])
                return
            for k, v in node.items():
                if k.startswith("_"):
                    continue
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, dict) and "name" in item:
                    walk({k: v for k, v in item.items() if k != "name"},
                         f"{path}.{item['name']}")

    walk({k: v for k, v in params.items() if k not in ("knobs", "_meta")}, "")
    return out


def val(params: dict, path: str):
    """Fetch a fixed structural constant's value_or_prior by dotted path."""
    node = params
    for part in path.split("."):
        if isinstance(node, list):
            node = next(x for x in node if x.get("name") == part)
        else:
            node = node[part]
    return node["value_or_prior"] if isinstance(node, dict) and "value_or_prior" in node else node


# ============================================================== accumulators
@dataclass
class Acc:
    """Streaming histogram + exact moments for one output distribution."""
    edges: np.ndarray
    counts: np.ndarray = None
    n: int = 0
    s: float = 0.0
    s2: float = 0.0

    def __post_init__(self):
        if self.counts is None:
            self.counts = np.zeros(len(self.edges) - 1, dtype=np.float64)

    def add(self, x: np.ndarray):
        x = x.ravel()
        nb = len(self.counts)
        width = (self.edges[-1] - self.edges[0]) / nb
        idx = np.clip(((x - self.edges[0]) / width).astype(np.int64), 0, nb - 1)
        self.counts += np.bincount(idx, minlength=nb)
        self.n += x.size
        self.s += float(x.sum())
        self.s2 += float((x * x).sum())

    def mean(self) -> float:
        return self.s / max(self.n, 1)

    def quantile(self, q: float) -> float:
        cum = np.cumsum(self.counts)
        target = q * self.n
        i = int(np.searchsorted(cum, target))
        i = min(i, len(self.counts) - 1)
        prev = cum[i - 1] if i > 0 else 0
        inbin = self.counts[i]
        frac = (target - prev) / inbin if inbin > 0 else 0.5
        w = self.edges[i + 1] - self.edges[i]
        return float(self.edges[i] + frac * w)

    def quantiles(self, qs: np.ndarray) -> np.ndarray:
        """Vectorized histogram quantiles (for site sample thinning)."""
        cum = np.cumsum(self.counts)
        targets = np.asarray(qs) * self.n
        idx = np.minimum(np.searchsorted(cum, targets), len(self.counts) - 1)
        prev = np.where(idx > 0, cum[np.maximum(idx - 1, 0)], 0.0)
        inbin = self.counts[idx]
        frac = np.where(inbin > 0, (targets - prev) / np.maximum(inbin, 1e-300), 0.5)
        w = (self.edges[-1] - self.edges[0]) / len(self.counts)
        return self.edges[idx] + np.clip(frac, 0, 1) * w

    def exceedance(self, x: float) -> float:
        i = int(np.searchsorted(self.edges, x, side="right")) - 1
        i = max(0, min(i, len(self.counts) - 1))
        above = self.counts[i + 1:].sum()
        w = self.edges[i + 1] - self.edges[i]
        frac_bin = (self.edges[i + 1] - x) / w
        return float((above + self.counts[i] * frac_bin) / max(self.n, 1))

    @classmethod
    def mix(cls, accs: list["Acc"], weights: list[float]) -> "Acc":
        """Weighted mixture of same-edge accumulators (regime mixture, D-07)."""
        m = cls(edges=accs[0].edges)
        ntot = sum(a.n for a in accs) / len(accs)
        m.counts = sum(w * a.counts * (ntot / max(a.n, 1)) for a, w in zip(accs, weights))
        m.n = ntot
        m.s = sum(w * a.s * (ntot / max(a.n, 1)) for a, w in zip(accs, weights))
        m.s2 = sum(w * a.s2 * (ntot / max(a.n, 1)) for a, w in zip(accs, weights))
        return m


# ======================================================== severity samplers
def gpd_inv(u: np.ndarray, xi, scale, threshold) -> np.ndarray:
    """Generalized Pareto inverse CDF (xi > 0 branch)."""
    xi = np.maximum(xi, 1e-6)
    return threshold + scale / xi * ((1.0 - u) ** (-xi) - 1.0)


# ================================================================== engine
@dataclass
class SimResult:
    """head: (year, variant, regime, cell, basis) -> Acc (headline incl. Ch4
    phase-in). core: (year, regime, cell) -> Acc of transfer-inclusive
    d1+d2 EXCLUDING Ch4, pooled over variants (site export). loss_ai:
    (year, variant, regime) -> Acc of AI-world S2+systemic loss (ILS)."""
    head: dict = field(default_factory=dict)
    core: dict = field(default_factory=dict)
    loss_ai: dict = field(default_factory=dict)
    diag: dict = field(default_factory=dict)


def _outer_draws(params, priors, n_outer, rng, overrides=None):
    """Epistemic layer. The prior is ALWAYS sampled (then discarded if pinned)
    so the RNG stream is identical across tornado reruns (CRN)."""
    th = {}
    for path, prior in priors.items():
        draw = prior.sample(rng, n_outer)
        if overrides and path in overrides:
            draw = np.full(n_outer, float(overrides[path]))
        th[path] = draw
    return th


def simulate(params: dict, baselines: dict, n_outer: int, n_inner: int,
             seed: int, s3_variant: str = "both", overrides: dict | None = None,
             chunk_outer: int | None = None,
             regimes: tuple | None = None,          # S18-EXT
             years: tuple | None = None) -> SimResult:   # S18-EXT
    """Run the full two-layer simulation. See module docstring for design."""
    regimes = tuple(regimes) if regimes else REGIMES      # S18-EXT
    years = tuple(years) if years else YEARS              # S18-EXT
    rng = np.random.default_rng(seed)
    priors = collect_priors(params)
    th = _outer_draws(params, priors, n_outer, rng, overrides)

    knobs = {k: v["value_or_prior"] for k, v in params["knobs"].items()}
    ref_cell = knobs["reference_cell"]
    ref_key = cell_key(ref_cell["form"], ref_cell["window"])
    variants = VARIANTS if s3_variant == "both" else (s3_variant,)
    cells = [cell_key(f, w) for f in FORMS for w in WINDOWS]
    chunk = chunk_outer or int(val(params, "run.chunk_outer"))
    ramp = float(val(params, "run.ai_ramp_2028"))

    # --- D-14 caps + D-15 trigger (knobs) ---
    s2_cap = float(knobs["s2_cap_busd"])
    s3_cap = float(knobs["s3_annual_cap_busd"])
    trig_busd = float(knobs["damping_trigger_busd"])

    # --- fixed structural constants ---
    gpd_thresh = float(val(params, "strata.s2.gpd_threshold_busd"))
    cyc_sig = float(val(params, "strata.s3b.cycle_sigma_log"))
    seed_share = float(val(params, "strata.s3b.seed_share"))
    ref_share = float(val(params, "strata.s3b.ref_share"))
    max_cyc = int(val(params, "strata.s3b.max_cycles"))
    ch4_phase = {int(k): float(v) for k, v in val(params, "ch4.phase_in").items()}
    scen_names = [s["name"] for s in params["strata"]["s3a"]["scenarios"]]
    scen_sig = {s["name"]: float(s["sev_sigma_log"]["value_or_prior"])
                for s in params["strata"]["s3a"]["scenarios"]}

    # --- per-cell baseline geometry (fitted-trend growth; see docstring) ---
    ch2_proj = {c: baselines["ch2"][c]["proj_busd"] for c in cells}
    ch1_proj = {c: baselines["ch1"][c]["proj_busd"] for c in cells}
    fit24 = baselines["ch2"][ref_key]["fit_2024_busd"]
    g_year = {yr: ch2_proj[ref_key][yr] / fit24 for yr in years}   # S18-EXT: years
    cell_ratio = {c: {yr: ch2_proj[c][yr] / ch2_proj[ref_key][yr] for yr in years}
                  for c in cells}

    # --- accumulators ---
    res = SimResult()
    for yr in years:                                     # S18-EXT: years
        for v in variants:
            for rg in regimes:                           # S18-EXT: regimes
                res.loss_ai[(yr, v, rg)] = Acc(edges=LOSS_EDGES)
                for c in cells:
                    for b in BASES:
                        res.head[(yr, v, rg, c, b)] = Acc(edges=HEAD_EDGES)
        for rg in regimes:
            for c in cells:
                res.core[(yr, rg, c)] = Acc(edges=HEAD_EDGES)
    d1_neg = 0; d1_tot = 0
    d2_neg = 0; d2_tot = 0
    trig_frac_n = 0; trig_frac_d = 0

    def T(path, sl):
        return th[path][sl].reshape(-1, 1)

    for start in range(0, n_outer, chunk):
        sl = slice(start, min(start + chunk, n_outer))
        c_sz = sl.stop - sl.start
        shape = (c_sz, n_inner)

        # ---- epistemic parameters for this chunk (column vectors) ----
        s1_lam24 = T("strata.s1.freq_mean_2024", sl)
        s1_k = np.maximum(T("strata.s1.freq_dispersion", sl), 0.5)
        s1_meansev = T("strata.s1.sev_mean_usd", sl)
        s1_sig = np.clip(T("strata.s1.sev_sigma_log", sl), 0.05, None)
        s1_share = np.clip(T("strata.s1.reporting_growth_share", sl), 0.0, 0.95)
        s2_lam24 = T("strata.s2.poisson_rate_2024", sl)
        s2_trend = T("strata.s2.freq_trend_pct", sl) / 100.0
        s2_xi = np.clip(T("strata.s2.gpd_shape", sl), 0.01, 2.0)
        s2_sc = np.maximum(T("strata.s2.gpd_scale_busd", sl), 1e-3)
        rho0 = np.clip(T("strata.s3a.common_shock_loading", sl), 0.0, 0.95)
        meas = T("ch2.reporting_correction", sl)
        tshare = np.clip(T("ch2.transfer_share", sl), 0.0, 1.0)
        resp = T("ch1.loss_response_coef", sl)
        vend26 = T("ch1.vendor_spend_2026_busd", sl)
        g_ch1 = T("ch1.baseline_growth", sl)
        labor = np.maximum(T("ch1.labor_mult", sl), 0.0)
        defl = np.clip(T("ch1.category_deflator", sl), 0.0, 1.0)
        damp_col = np.clip(T("defense.safeguard_damping", sl), 0.0, 1.0)
        ch4b = knobs["ch4_bounds_busd"]
        ch4 = rng.triangular(ch4b["min"], ch4b["mode"], ch4b["max"], (c_sz, 1))

        s1_var_sev = (np.exp(s1_sig**2) - 1.0) * s1_meansev**2

        scen_p = {nm: T(f"strata.s3a.scenarios.{nm}.annual_prob", sl) for nm in scen_names}
        scen_med = {nm: T(f"strata.s3a.scenarios.{nm}.sev_median_busd", sl) for nm in scen_names}

        b_camp = T("strata.s3b.campaigns_per_year", sl)
        b_foot = np.clip(T("strata.s3b.p_foothold", sl), 0.0, 1.0)
        b_dmgp = np.clip(T("strata.s3b.p_damaging", sl), 0.0, 1.0)
        b_R = np.maximum(T("strata.s3b.branching_factor", sl), 0.05)
        b_cyc = np.maximum(T("strata.s3b.cycle_time_days", sl), 0.25)
        b_patch = np.clip(T("strata.s3b.patch_race_win_prob", sl), 0.02, 0.98)
        b_blast = np.clip(T("strata.s3b.blast_radius_share", sl), 1e-4, 1.0)
        b_rate = b_camp * b_foot * b_dmgp          # damaging systemic events/yr
        b_dmg = T("strata.s3b.damage_rate_busd_per_day", sl)

        for rg in regimes:                               # S18-EXT: regimes
            m1 = T(f"ai_shift.{rg}.s1_freq_mult", sl)
            m2 = T(f"ai_shift.{rg}.s2_freq_mult", sl)
            msev = T(f"ai_shift.{rg}.severity_shift", sl)
            mp3 = T(f"ai_shift.{rg}.s3_prob_mult", sl)
            dep0 = T(f"ai_shift.{rg}.dependence_shift", sl)
            h0 = np.clip(T(f"defense.{rg}.severity_truncation", sl), 0.0, 0.95)
            ai_gd = T(f"ch1.ai_growth_delta_pp.{rg}", sl) / 100.0
            # S18-EXT: optional per-regime transfer share (cession regime)
            tsh_key = f"ch2.transfer_share_{rg}"
            tshare_rg = (np.clip(T(tsh_key, sl), 0.0, 1.0)
                         if tsh_key in th else tshare)

            # S18-EXT: D-15 damping chained — year y-1's systemic outcome
            # damps year y (their code: 2027 -> 2028; identical on the sealed
            # window, our labeled generalization beyond it). First year: D=1.
            trig = None
            for yr in years:       # ascending — order load-bearing for D-15
                if trig is None:
                    D = np.ones(shape)
                else:
                    D = np.where(trig, damp_col, 1.0)          # (c_sz, n_inner)
                # S18-EXT: sealed ramp 1.0 (2027) / 1.5 (2028); HELD at 1.5
                # beyond 2028 (our construction, "no sealed growth" precedent)
                r = 1.0 if yr <= 2027 else ramp
                # section-4 multipliers: deviation ramped (2028) and damped
                f1 = 1.0 + (m1 - 1.0) * r * D
                f2 = 1.0 + (m2 - 1.0) * r * D
                sev_m = 1.0 + (msev - 1.0) * r * D
                p3m = np.maximum(1.0 + (mp3 - 1.0) * r * D, 0.0)
                dep = dep0 * r * D
                hfac = 1.0 - np.clip(h0 * r * D, 0.0, 0.95)    # truncation
                gy = g_year[yr]

                # ================= S1 (CLT aggregate, CRN shared) =========
                G = rng.gamma(np.broadcast_to(s1_k, shape), 1.0) / s1_k
                zN = rng.standard_normal(shape)
                zA = rng.standard_normal(shape)
                gy_s1 = gy ** (1.0 - s1_share)     # reporting-share-corrected

                def s1_agg(lam, mean_sev, var_sev):
                    lamG = np.maximum(lam * G, 1.0)
                    N = np.maximum(lamG + np.sqrt(lamG) * zN, 0.0)
                    agg = N * mean_sev + np.sqrt(N * var_sev) * zA
                    return np.maximum(agg, 0.0) / 1e9          # USD -> $B

                lam_base = s1_lam24 * gy_s1
                s1_base = s1_agg(lam_base, s1_meansev, s1_var_sev)
                s1_ai = s1_agg(lam_base * f1, s1_meansev * sev_m * hfac,
                               s1_var_sev * (sev_m * hfac) ** 2)
                d2_s1 = s1_ai - s1_base

                # ================= S2 (event-level, CRN by thinning) ======
                g2 = (1.0 + s2_trend) ** (yr - 2024)
                lam_b = np.broadcast_to(s2_lam24 * g2, shape)
                lam_a = s2_lam24 * g2 * f2
                lam_hi = np.maximum(lam_b, lam_a)
                K = rng.poisson(lam_hi)
                tot = int(K.sum())
                s2_base = np.zeros(shape); s2_ai = np.zeros(shape)
                if tot > 0:
                    flat_idx = np.repeat(np.arange(K.size), K.ravel())
                    row = flat_idx // n_inner
                    u_keep = rng.random(tot)
                    u_sev = rng.random(tot)
                    sev = np.minimum(
                        gpd_inv(u_sev, s2_xi.ravel()[row], s2_sc.ravel()[row],
                                gpd_thresh),
                        s2_cap)                    # D-14 cap, BOTH worlds
                    keep_b = u_keep < (lam_b.ravel()[flat_idx] / lam_hi.ravel()[flat_idx])
                    keep_a = u_keep < (lam_a.ravel()[flat_idx] / lam_hi.ravel()[flat_idx])
                    sev_mf = np.broadcast_to(sev_m * hfac, shape).ravel()[flat_idx]
                    sev_a = np.minimum(sev * sev_mf, s2_cap)
                    nb = np.bincount(flat_idx, weights=sev * keep_b, minlength=K.size)
                    na = np.bincount(flat_idx, weights=sev_a * keep_a, minlength=K.size)
                    s2_base = nb.reshape(shape); s2_ai = na.reshape(shape)
                d2_s2 = s2_ai - s2_base

                # ================= S3a (anchored scenario set) ============
                Z = rng.standard_normal(shape)
                rho_b = rho0
                rho_a = np.clip(rho0 + dep, 0.0, 0.95)
                s3a_base = np.zeros(shape); s3a_ai = np.zeros(shape)
                for nm in scen_names:
                    eps = rng.standard_normal(shape)
                    w = rng.standard_normal(shape)             # shared severity
                    u_b = ndtr(rho_b * Z + np.sqrt(1 - rho_b**2) * eps)
                    u_a = ndtr(rho_a * Z + np.sqrt(1 - rho_a**2) * eps)
                    p_b = scen_p[nm]
                    p_a = np.clip(p_b * p3m, 0.0, 1.0)
                    sev_b = np.minimum(scen_med[nm] * np.exp(scen_sig[nm] * w),
                                       s3_cap)
                    sev_a = np.minimum(sev_b * sev_m * hfac, s3_cap)
                    s3a_base += (u_b < p_b) * sev_b
                    s3a_ai += (u_a < p_a) * sev_a
                # D-14 annual aggregate cap, both worlds
                s3a_base = np.minimum(s3a_base, s3_cap)
                s3a_ai = np.minimum(s3a_ai, s3_cap)
                d2_s3a = s3a_ai - s3a_base

                # ================= S3b (fresh agentic event tree) =========
                s3b_ai = np.zeros(shape)
                if "fresh" in variants:
                    lam3 = np.broadcast_to(b_rate, shape) * D   # S18-EXT: D=1 first year
                    M = rng.poisson(lam3)
                    tot3 = int(M.sum())
                    if tot3 > 0:
                        fi = np.repeat(np.arange(M.size), M.ravel())
                        rw = fi // n_inner
                        p = b_patch.ravel()[rw]
                        u = rng.random(tot3)
                        ncyc = np.minimum(
                            1 + np.floor(np.log(u) / np.log(1.0 - p)), max_cyc)
                        cyc_t = b_cyc.ravel()[rw] * np.exp(
                            cyc_sig * rng.standard_normal(tot3))
                        R = b_R.ravel()[rw]
                        blast = b_blast.ravel()[rw]
                        growth = np.where(
                            R > 1.0,
                            np.minimum(R ** ncyc, blast / seed_share),
                            R ** ncyc)
                        share = np.minimum(seed_share * growth, blast)
                        dur = ncyc * cyc_t
                        hfe = np.broadcast_to(hfac, shape).ravel()[fi]
                        loss = b_dmg.ravel()[rw] * dur * (share / ref_share) * hfe
                        s3b_ai = np.bincount(fi, weights=loss,
                                             minlength=M.size).reshape(shape)
                        s3b_ai = np.minimum(s3b_ai, s3_cap)    # D-14 cap

                # ---- D-15 trigger from THIS year's systemic outcome ----
                # S18-EXT: computed every year (chained damping); their code
                # computed it for 2027 only. Diagnostics still count 2027.
                s3_tot_yr = s3a_ai + s3b_ai
                trig = s3_tot_yr >= trig_busd
                if yr == 2027:
                    trig_frac_n += int(trig.sum()); trig_frac_d += trig.size

                # ================= channels -> headline ===================
                d2_trend = d2_s1 + d2_s2
                d2_ref = {"anchored": d2_s3a, "fresh": s3b_ai}
                n_ch1 = yr - 2026
                d1_trend = defl * vend26 * (1.0 + labor) * (
                    (1.0 + g_ch1 + ai_gd) ** n_ch1 - (1.0 + g_ch1) ** n_ch1)
                d2_for_resp = meas * (d2_trend + d2_s3a)
                d1_core = d1_trend + resp * np.clip(d2_for_resp, 0.0, None) * 0.5
                ch4_yr = ch4 * ch4_phase.get(yr, 1.0)   # S18-EXT: 1.0 past 2028
                for v in variants:
                    d2v = d2_ref[v]
                    tot_ai = s2_ai + (s3a_ai if v == "anchored" else s3a_ai + s3b_ai)
                    res.loss_ai[(yr, v, rg)].add(tot_ai)
                    for c in cells:
                        rc = cell_ratio[c][yr]
                        off1 = ch1_proj[ref_key][yr] - ch1_proj[c][yr]
                        d2_cell = meas * (d2_trend * rc + d2v)
                        d1_cell = d1_core + off1
                        core_ti = d1_cell + d2_cell
                        res.head[(yr, v, rg, c, "transfer_inclusive")].add(core_ti + ch4_yr)
                        res.head[(yr, v, rg, c, "resource_only")].add(
                            d1_cell + d2_cell * (1.0 - tshare_rg) + ch4_yr)  # S18-EXT
                        res.core[(yr, rg, c)].add(core_ti)     # site export, no Ch4

                # diagnostics at the reference cell
                d1_neg += int((d1_core < 0).sum()); d1_tot += d1_core.size
                d2_ref_ti = meas * (d2_trend + d2_s3a)
                d2_neg += int((d2_ref_ti < 0).sum()); d2_tot += d2_ref_ti.size

    res.diag = {
        "frac_negative_d1": d1_neg / max(d1_tot, 1),
        "frac_negative_d2": d2_neg / max(d2_tot, 1),
        "frac_2027_damping_triggered": trig_frac_n / max(trig_frac_d, 1),
        "n_outer": n_outer, "n_inner": n_inner, "seed": seed,
        "variants": list(variants),
    }
    return res


# ============================================= dependence-shift diagnostic
def s3_occurrence_correlation(params: dict, dep_shift: float, n: int = 200_000,
                              seed: int = 7) -> float:
    """Correlation between the first two S3a scenario occurrence indicators
    under common-shock loading rho0 + dep_shift (smoke-test diagnostic)."""
    rng = np.random.default_rng(seed)
    scens = params["strata"]["s3a"]["scenarios"][:2]
    rho_prior = Prior(val(params, "strata.s3a.common_shock_loading"))
    rho = float(np.clip(rho_prior.ppf(0.5) + dep_shift, 0.0, 0.95))
    Z = rng.standard_normal(n)
    occ = []
    for s in scens:
        p = Prior(s["annual_prob"]["value_or_prior"]).ppf(0.5)
        p = min(p * 10.0, 0.5)   # inflate marginals for conditioning
        eps = rng.standard_normal(n)
        occ.append((ndtr(rho * Z + np.sqrt(1 - rho**2) * eps) < p).astype(float))
    return float(np.corrcoef(occ[0], occ[1])[0, 1])
