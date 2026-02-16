"""
Browser-safe simulation module for Pyodide.
Same logic as retirement_wealth_simulation.py but no file I/O or matplotlib.
Call run_from_js(params_dict) with a dict of SimParams fields; returns
{ "summary": {...}, "histogram": { "counts": [...], "edges": [...] } }.
"""

import numpy as np
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SimParams:
    """Parameters for the retirement wealth simulation."""
    X: float
    r_f: float
    phi: float
    sigma_eta: float
    sigma_e: float
    rho: float
    x_mean: float = 0.0
    start_age: int = 25
    retire_age: int = 65
    stock_allocation_offset: int = 120
    initial_savings: float = 0.0
    savings_growth_rate: float = 0.0
    n_sim: int = 50_000
    seed: Optional[int] = None


def _stock_weight(age: int, allocation_offset: int) -> float:
    """Fraction of portfolio in stocks: (allocation_offset - age) / 100, clipped to [0, 1]."""
    return float(np.clip((allocation_offset - age) / 100.0, 0.0, 1.0))


def simulate_path(
    params: SimParams,
    T: int,
    rng: np.random.Generator,
) -> tuple:
    """Simulate one path; returns (x, r_stock, W)."""
    cov_ee = params.rho * params.sigma_eta * params.sigma_e
    cov_matrix = np.array([
        [params.sigma_eta**2, cov_ee],
        [cov_ee, params.sigma_e**2],
    ])
    mean_innov = np.zeros(2)

    x = np.zeros(T + 1)
    x[0] = params.x_mean
    r_stock = np.zeros(T)
    ages = np.arange(params.start_age, params.retire_age)

    for t in range(T):
        eta_t, e_t = rng.multivariate_normal(mean_innov, cov_matrix)
        x[t + 1] = params.x_mean + params.phi * (x[t] - params.x_mean) + eta_t
        r_stock[t] = x[t] + e_t

    W = np.zeros(T + 1)
    W[0] = params.initial_savings
    for t in range(T):
        age = ages[t]
        w_stock = _stock_weight(age, params.stock_allocation_offset)
        w_bond = 1.0 - w_stock
        r_port = w_stock * r_stock[t] + w_bond * params.r_f
        contribution_t = params.X * ((1.0 + params.savings_growth_rate) ** t)
        W[t + 1] = (W[t] + contribution_t) * (1.0 + r_port)

    return x, r_stock, W


def run_simulation(params: SimParams) -> np.ndarray:
    """Run n_sim paths; return array of wealth at retirement."""
    rng = np.random.default_rng(params.seed)
    T = params.retire_age - params.start_age
    wealth_at_retirement = np.zeros(params.n_sim)
    for i in range(params.n_sim):
        _, _, W = simulate_path(params, T, rng)
        wealth_at_retirement[i] = W[-1]
    return wealth_at_retirement


def summary_stats(wealth: np.ndarray) -> dict:
    """Summary statistics for the wealth distribution."""
    return {
        "mean": float(np.mean(wealth)),
        "median": float(np.median(wealth)),
        "std": float(np.std(wealth)),
        "min": float(np.min(wealth)),
        "max": float(np.max(wealth)),
        "p5": float(np.percentile(wealth, 5)),
        "p25": float(np.percentile(wealth, 25)),
        "p75": float(np.percentile(wealth, 75)),
        "p95": float(np.percentile(wealth, 95)),
    }


def run_from_js(params_dict) -> dict[str, Any]:
    """
    Entry point for JavaScript: build SimParams from dict, run simulation,
    return summary and histogram (JSON-serializable).
    JsProxy from Pyodide is not subscriptable; convert to Python dict first.
    """
    pd = params_dict.to_py() if hasattr(params_dict, "to_py") else dict(params_dict)
    p = SimParams(
        X=float(pd["X"]),
        r_f=float(pd["r_f"]),
        phi=float(pd["phi"]),
        sigma_eta=float(pd["sigma_eta"]),
        sigma_e=float(pd["sigma_e"]),
        rho=float(pd["rho"]),
        x_mean=float(pd["x_mean"]),
        start_age=int(pd["start_age"]),
        retire_age=int(pd["retire_age"]),
        stock_allocation_offset=int(pd["stock_allocation_offset"]),
        initial_savings=float(pd.get("initial_savings", 0)),
        savings_growth_rate=float(pd.get("savings_growth_rate", 0)),
        n_sim=int(pd["n_sim"]),
        seed=pd.get("seed"),
    )
    wealth = run_simulation(p)
    stats = summary_stats(wealth)
    counts, edges = np.histogram(wealth, bins=80)
    return {
        "summary": stats,
        "histogram": {"counts": counts.tolist(), "edges": edges.tolist()},
    }
