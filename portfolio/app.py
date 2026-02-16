"""
Flask app for the retirement wealth simulation web UI.
Loads defaults from sim_params.txt; GET /api/defaults and POST /api/run.
"""

from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request, send_from_directory

from retirement_wealth_simulation import (
    SimParams,
    load_params_from_file,
    params_from_adams_jmp,
    run_simulation,
    summary_stats,
)

app = Flask(__name__, static_folder="static")

# Default params: loaded from sim_params.txt on first use, or fallback
_default_params: SimParams | None = None
_DEFAULT_PARAMS_FILE = Path(__file__).resolve().parent / "sim_params.txt"

# Bounds for validation
N_SIM_MAX = 100_000
N_SIM_MIN = 1_000


def get_default_params() -> SimParams:
    global _default_params
    if _default_params is None:
        if _DEFAULT_PARAMS_FILE.exists():
            _default_params = load_params_from_file(_DEFAULT_PARAMS_FILE)
        else:
            _default_params = params_from_adams_jmp(
                X=15_000,
                start_age=25,
                retire_age=65,
                n_sim=30_000,
                seed=42,
            )
    return _default_params


def sim_params_to_dict(p: SimParams) -> dict:
    """Convert SimParams to JSON-serializable dict."""
    return {
        "X": p.X,
        "r_f": p.r_f,
        "phi": p.phi,
        "sigma_eta": p.sigma_eta,
        "sigma_e": p.sigma_e,
        "rho": p.rho,
        "x_mean": p.x_mean,
        "start_age": p.start_age,
        "retire_age": p.retire_age,
        "stock_allocation_offset": p.stock_allocation_offset,
        "initial_savings": p.initial_savings,
        "savings_growth_rate": p.savings_growth_rate,
        "n_sim": p.n_sim,
        "seed": p.seed,
    }


def parse_request_body(data: dict) -> dict:
    """Parse and coerce types for SimParams fields from request JSON."""
    out = {}
    default = get_default_params()
    d = default.__dict__

    # Float params
    for key in ("X", "r_f", "phi", "sigma_eta", "sigma_e", "rho", "x_mean", "initial_savings", "savings_growth_rate"):
        if key in data and data[key] is not None:
            try:
                out[key] = float(data[key])
            except (TypeError, ValueError):
                pass
    # Int params
    for key in ("start_age", "retire_age", "stock_allocation_offset", "n_sim"):
        if key in data and data[key] is not None:
            try:
                out[key] = int(data[key])
            except (TypeError, ValueError):
                pass
    # seed: int or None
    if "seed" in data:
        v = data["seed"]
        if v is None or str(v).strip().lower() in ("none", ""):
            out["seed"] = None
        else:
            try:
                out["seed"] = int(v)
            except (TypeError, ValueError):
                pass

    return out


def validate_params(p: SimParams) -> tuple[bool, str]:
    """Validate SimParams. Returns (ok, error_message)."""
    if p.start_age >= p.retire_age:
        return False, "Current age must be less than target retirement age."
    if p.X <= 0:
        return False, "Annual savings must be positive."
    if p.initial_savings < 0:
        return False, "Initial savings cannot be negative."
    if not (0 <= p.stock_allocation_offset <= 200):
        return False, "Stock allocation offset (X - age) should be between 0 and 200."
    if not (N_SIM_MIN <= p.n_sim <= N_SIM_MAX):
        return False, f"Number of simulations must be between {N_SIM_MIN} and {N_SIM_MAX}."
    if p.r_f <= -1:
        return False, "Risk-free rate must be greater than -100%."
    return True, ""


@app.route("/")
def index():
    """Serve the single-page app."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/defaults", methods=["GET"])
def api_defaults():
    """Return default parameter values from sim_params.txt (or fallback)."""
    p = get_default_params()
    return jsonify(sim_params_to_dict(p))


@app.route("/api/run", methods=["POST"])
def api_run():
    """Run simulation with merged params; return summary stats and histogram."""
    default = get_default_params()
    raw = request.get_json(silent=True) or {}
    merged = sim_params_to_dict(default)
    for k, v in parse_request_body(raw).items():
        merged[k] = v
    # Rebuild seed: allow None
    seed = merged.get("seed")
    params = SimParams(
        X=float(merged["X"]),
        r_f=float(merged["r_f"]),
        phi=float(merged["phi"]),
        sigma_eta=float(merged["sigma_eta"]),
        sigma_e=float(merged["sigma_e"]),
        rho=float(merged["rho"]),
        x_mean=float(merged["x_mean"]),
        start_age=int(merged["start_age"]),
        retire_age=int(merged["retire_age"]),
        stock_allocation_offset=int(merged["stock_allocation_offset"]),
        initial_savings=float(merged["initial_savings"]),
        savings_growth_rate=float(merged["savings_growth_rate"]),
        n_sim=int(merged["n_sim"]),
        seed=seed,
    )
    ok, err = validate_params(params)
    if not ok:
        return jsonify({"error": err}), 400

    wealth = run_simulation(params)
    stats = summary_stats(wealth)
    # Convert numpy scalars to Python floats for JSON
    summary = {k: float(v) for k, v in stats.items()}

    counts, edges = np.histogram(wealth, bins=80)
    histogram = {
        "counts": counts.tolist(),
        "edges": edges.tolist(),
    }

    return jsonify({"summary": summary, "histogram": histogram})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
