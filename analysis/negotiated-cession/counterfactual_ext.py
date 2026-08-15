"""counterfactual_ext.py — S18 vendored copy of the Fable-Carson baseline fits.

PROVENANCE: forked verbatim from sim/counterfactual.py of
github.com/bradrcarson/cowen-cyber @ fc73ac89 (2026-08-10), CC-BY 4.0.
ONE modification, marked "# S18-EXT": fit_baselines() takes years= so
projections can extend past 2028 (the fitted trend predicts any quarter;
extending the projection window is OUR construction, not their forecast).

Original docstring follows.
------------------------------------------------------------------------

counterfactual.py — baseline fitting for the 3x3 counterfactual matrix.

Implements D-05 / D-12: for Channel 1 (defensive spend trend) and Channel 2
(realized-loss stochastic-process level), fit three functional forms x three
windows on the quarterly history and project baselines for 2027 and 2028.

Forms (all fit in log space; D-12b conservatism ordering applies):
  log_linear   log y = a + b*t                       fit on window, data <= 2024Q4
  quadratic    log y = a + b*t + c*t^2               fit on window, data <= 2024Q4
  structural   log y = a + b*t, pre-committed break  fit on window PLUS the
               at 2026Q2 (D-12c)                     pre-break quarters
                                                     2025Q1..2026Q1; projection
                                                     beyond the break uses the
                                                     pre-break trend only

Windows (D-12a):
  full_2015_2024   2015Q1..2024Q4 (2021 spike left in — a tail observation)
  ex_covid         same, dropping 2020Q1..2021Q4 from the fit
  short_2018_2024  2018Q1..2024Q4

Placebo (D-12 falsification check): quarters 2025Q1..2026Q1 are out-of-sample
but pre-break for the non-structural forms, so measured excess there should be
~0. For the structural form those quarters are in-sample by construction; the
placebo is still computed and flagged `in_sample: true` so readers see it.

The Monte Carlo engine consumes:
  - annualized baseline projections per channel x cell x year (anchors S1/S2
    event frequencies and the Ch1 trend), and
  - per-cell scaling ratios relative to the 2024 observed level.

All series here come from config/params_placeholder.json and are PLACEHOLDERS.
"""

from __future__ import annotations
import numpy as np

FORMS = ("log_linear", "quadratic", "structural")
WINDOWS = ("full_2015_2024", "ex_covid", "short_2018_2024")
PLACEBO_QUARTERS = ("2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1")


# ---------------------------------------------------------------- utilities
def qindex(qstr: str) -> int:
    """Map '2015Q1'-style labels to a running quarter index (2000Q1 = 0)."""
    y, q = qstr.split("Q")
    return (int(y) - 2000) * 4 + (int(q) - 1)


def year_quarters(year: int) -> list[int]:
    return [qindex(f"{year}Q{k}") for k in (1, 2, 3, 4)]


def window_mask(quarters: list[str], window: str) -> np.ndarray:
    """Boolean mask of quarters used for trend estimation (data <= 2024Q4)."""
    idx = np.array([qindex(q) for q in quarters])
    m = idx <= qindex("2024Q4")
    if window == "full_2015_2024":
        m &= idx >= qindex("2015Q1")
    elif window == "ex_covid":
        m &= idx >= qindex("2015Q1")
        m &= ~((idx >= qindex("2020Q1")) & (idx <= qindex("2021Q4")))
    elif window == "short_2018_2024":
        m &= idx >= qindex("2018Q1")
    else:
        raise ValueError(f"unknown window: {window}")
    return m


# ---------------------------------------------------------------- fitting
def fit_cell(quarters: list[str], values: list[float], form: str, window: str,
             break_date: str = "2026Q2"):
    """Fit one matrix cell; return a predictor f(quarter_index) -> level ($B/q).

    Least squares in log space via numpy polyfit-style normal equations.
    """
    idx = np.array([qindex(q) for q in quarters], dtype=float)
    y = np.log(np.asarray(values, dtype=float))
    m = window_mask(quarters, window)

    if form == "structural":
        # D-12c: baseline fitted through 2026Q1 (window quarters + the
        # pre-break out-year quarters); break at break_date. Projections past
        # the break extrapolate the pre-break trend — the break itself is
        # where the AI-world data is allowed to diverge from baseline.
        pre_break = (idx > qindex("2024Q4")) & (idx < qindex(break_date))
        m = m | pre_break

    t = idx[m]
    yy = y[m]
    if form == "quadratic":
        X = np.column_stack([np.ones_like(t), t, t * t])
    else:  # log_linear and structural share the linear-in-logs functional form
        X = np.column_stack([np.ones_like(t), t])
    coef, *_ = np.linalg.lstsq(X, yy, rcond=None)

    def predict(q_idx):
        q_idx = np.asarray(q_idx, dtype=float)
        if form == "quadratic":
            return np.exp(coef[0] + coef[1] * q_idx + coef[2] * q_idx * q_idx)
        return np.exp(coef[0] + coef[1] * q_idx)

    resid_sd_log = float(np.std(yy - np.log(predict(t)), ddof=X.shape[1]))
    return predict, coef, resid_sd_log


# ---------------------------------------------------------------- placebo
def placebo_excess(quarters, values, predict, form, resid_sd_log=None) -> dict:
    """Annualized observed-minus-predicted excess over 2025Q1..2026Q1 ($B/yr).

    Expected ~0 (D-12). Nonzero = misfitted counterfactual, published so every
    reader can see it. 5 quarters are annualized with a 4/5 factor.
    """
    obs = {q: v for q, v in zip(quarters, values)}
    missing = [q for q in PLACEBO_QUARTERS if q not in obs]
    if missing:  # placeholder history should cover the window; guard anyway
        return {"excess_busd_annualized": None, "in_sample": form == "structural",
                "note": f"missing observed quarters: {missing}"}
    o = np.array([obs[q] for q in PLACEBO_QUARTERS])
    p = predict([qindex(q) for q in PLACEBO_QUARTERS])
    point = float((o - p).sum() * 4.0 / len(PLACEBO_QUARTERS))
    base = float(p.sum() * 4.0 / len(PLACEBO_QUARTERS))
    out = {
        "excess_busd_annualized": point,
        "baseline_busd_annualized": base,
        # structural form fits through 2026Q1, so its placebo is in-sample —
        # reported anyway, flagged so it is not over-read as a pass.
        "in_sample": form == "structural",
    }
    # Residual-normal 90% band: annualized excess = sum(o-p)*4/5 over 5
    # quarters; with iid log residuals of sd s, sd_ann ~ sqrt(5)*(4/5)*s*level.
    if resid_sd_log is not None:
        sd_ann = float(np.sqrt(5.0) * 0.8 * resid_sd_log * (p.mean() * 4.0))
        out["p05_busd"] = point - 1.6449 * sd_ann
        out["p95_busd"] = point + 1.6449 * sd_ann
        out["resid_sd_log"] = float(resid_sd_log)
    return out


# ---------------------------------------------------------------- top level
def cell_key(form: str, window: str) -> str:
    return f"{form}|{window}"


def fit_baselines(params: dict, years=(2027, 2028)) -> dict:   # S18-EXT
    """Fit the full 3x3 matrix for both channels.

    Returns
    -------
    {
      "ch1": { "log_linear|full_2015_2024": {"proj_busd": {2027: x, 2028: y},
                                             "placebo": {...}}, ... 9 cells },
      "ch2": { ... 9 cells ... },
      "observed_2024_busd": {"ch1": a, "ch2": b},
    }
    Projections are annual totals in $B.
    """
    break_date = params["knobs"]["break_date"]["value_or_prior"]
    out = {"ch1": {}, "ch2": {}, "observed_2024_busd": {}}

    for ch, block in (("ch1", "ch1"), ("ch2", "ch2")):
        key = "spend_series_busd_quarterly" if ch == "ch1" else "loss_series_busd_quarterly"
        s = params[block][key]["value_or_prior"]
        quarters, values = s["quarters"], s["values"]
        obs = dict(zip(quarters, values))
        out["observed_2024_busd"][ch] = float(sum(obs[f"2024Q{k}"] for k in (1, 2, 3, 4)))

        for form in FORMS:
            for window in WINDOWS:
                predict, coef, rsd = fit_cell(quarters, values, form, window, break_date)
                proj = {yr: float(np.sum(predict(year_quarters(yr)))) for yr in years}  # S18-EXT
                out[ch][cell_key(form, window)] = {
                    "form": form, "window": window,
                    "coef": [float(c) for c in coef],
                    "proj_busd": proj,
                    # fitted-trend level at the 2024 anchor year — the engine
                    # anchors strata levels at observed 2024 and takes GROWTH
                    # from the fitted trend (proj/fit_2024), so the fit's
                    # level residual at 2024 does not leak into levels.
                    "fit_2024_busd": float(np.sum(predict(year_quarters(2024)))),
                    "placebo": placebo_excess(quarters, values, predict, form, rsd),
                }
    return out


def cell_ratios(baselines: dict, channel: str, ref_cell: dict) -> dict:
    """Per-cell projection ratio vs the reference cell, per year.

    The engine simulates the loss process anchored at the reference cell's
    baseline and rescales trend-anchored strata (S1, S2) by this ratio per
    cell. Exact in expectation (frequencies are linear in the anchor level);
    higher moments differ negligibly at S1/S2 event counts.
    """
    ref = cell_key(ref_cell["form"], ref_cell["window"])
    out = {}
    for key, cell in baselines[channel].items():
        out[key] = {yr: cell["proj_busd"][yr] / baselines[channel][ref]["proj_busd"][yr]
                    for yr in (2027, 2028)}
    return out
