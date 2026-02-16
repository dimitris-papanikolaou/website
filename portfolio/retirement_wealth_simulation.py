"""
Retirement wealth distribution under:
- Constant annual savings X
- Constant risk-free rate
- Stock return r_t = x_t + e_t, with x_t AR(1) and Corr(x_t innovation, e_t) = rho
- Age-based allocation: fraction (stock_allocation_offset - Age) in stocks, rest in bonds

Parameters can be set in sim_params.txt (key = value, one per line; # for comments).
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend so script exits after saving plot
import matplotlib.pyplot as plt
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SimParams:
    """Parameters for the retirement wealth simulation."""
    X: float                    # Annual savings in first year (then grows by savings_growth_rate per year)
    r_f: float                  # Risk-free rate (constant)
    phi: float                  # AR(1) persistence for x_t: x_t = phi*x_{t-1} + eta_t
    sigma_eta: float            # Std of AR(1) innovation eta_t
    sigma_e: float              # Std of idiosyncratic return shock e_t
    rho: float                  # Correlation between eta_t and e_t
    x_mean: float = 0.0         # Unconditional mean of x_t (equity premium), for phi < 1
    start_age: int = 25
    retire_age: int = 65
    stock_allocation_offset: int = 120  # fraction in stocks = (offset - age) / 100, clipped to [0,1]
    initial_savings: float = 0.0        # Wealth at start (age start_age)
    savings_growth_rate: float = 0.0    # Decimal: annual savings grow by this rate (e.g. 0.02 = 2%/year)
    n_sim: int = 50_000
    seed: Optional[int] = None


def params_from_adams_jmp(
    X: float = 20_000,
    start_age: int = 30,
    retire_age: int = 65,
    n_sim: int = 5_000,
    seed: Optional[int] = 42,
) -> SimParams:
    """
    Stock return parameters calibrated to Adams (2026) JMP,
    "Stocks for the Long Run or Liquidity? Tax Data Evidence and Portfolio Choice Implications".

    The paper specifies expected stock returns via an AR(1) equity premium x_t with
    persistence φ_x = 0.85 and innovation std 2.3%; realized return has cash-flow and
    discount-rate news with σ_CF = 7.5%, σ_DR = 12%, ρ_CF,DR = -0.75, giving annual
    return volatility ≈ 18.3%. We map this to r_t = x_t + e_t with correlated (η_t, e_t):
    - r_f = 2%, x_mean = 5%, phi = 0.85, sigma_eta = 2.3%
    - sigma_e and rho chosen so Var(η_t + e_t) ≈ (18.3%)^2 and Corr(η_t, e_t) = -0.75.
    """
    return SimParams(
        X=X,
        r_f=0.02,           # Adams: annual real log risk-free return 2%
        phi=0.85,           # Adams: φ_x, equity premium persistence
        sigma_eta=0.023,    # Adams: std of risk premium innovation ξ_{x,t} = 2.3%
        sigma_e=0.20,       # Chosen so Var(η_t + e_t) ≈ (18.3%)^2 with rho = -0.75
        rho=-0.75,          # Adams: correlation of cash-flow and discount-rate news ρ_CF,DR
        x_mean=0.05,        # Adams: unconditional equity premium x = 5%
        start_age=start_age,
        retire_age=retire_age,
        stock_allocation_offset=120,
        n_sim=n_sim,
        seed=seed,
    )


# Default parameter file name (next to this script)
_DEFAULT_PARAMS_FILE = Path(__file__).resolve().parent / "sim_params.txt"

# Keys expected in the config file and their types
_PARAM_SPEC = {
    "X": float,
    "r_f": float,
    "phi": float,
    "sigma_eta": float,
    "sigma_e": float,
    "rho": float,
    "x_mean": float,
    "start_age": int,
    "retire_age": int,
    "stock_allocation_offset": int,
    "initial_savings": float,
    "savings_growth_rate": float,
    "n_sim": int,
    "seed": lambda s: None if str(s).strip().lower() in ("none", "") else int(s),
}


def load_params_from_file(path: Optional[Path] = None) -> SimParams:
    """
    Read simulation parameters from a text file.

    Format: one parameter per line, "key = value". Lines starting with #
    or blank lines are ignored. Unknown keys are ignored.
    """
    path = path or _DEFAULT_PARAMS_FILE
    values: dict[str, object] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key not in _PARAM_SPEC:
                continue
            conv = _PARAM_SPEC[key]
            values[key] = conv(val)
    return SimParams(
        X=float(values.get("X", 20_000)),
        r_f=float(values.get("r_f", 0.02)),
        phi=float(values.get("phi", 0.85)),
        sigma_eta=float(values.get("sigma_eta", 0.023)),
        sigma_e=float(values.get("sigma_e", 0.20)),
        rho=float(values.get("rho", -0.75)),
        x_mean=float(values.get("x_mean", 0.05)),
        start_age=int(values.get("start_age", 30)),
        retire_age=int(values.get("retire_age", 65)),
        stock_allocation_offset=int(values.get("stock_allocation_offset", 120)),
        initial_savings=float(values.get("initial_savings", 0)),
        savings_growth_rate=float(values.get("savings_growth_rate", 0)),
        n_sim=int(values.get("n_sim", 5_000)),
        seed=values.get("seed", 42),
    )


def _stock_weight(age: int, allocation_offset: int) -> float:
    """Fraction of portfolio in stocks: (allocation_offset - age) / 100, clipped to [0, 1]."""
    return np.clip((allocation_offset - age) / 100.0, 0.0, 1.0)


def simulate_path(
    params: SimParams,
    T: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate one path of (x_t, r_stock_t, wealth_t).
    Returns arrays of length T+1 (time 0 = start, time T = retirement).
    """
    # Build covariance matrix for (eta_t, e_t): correlation rho
    cov_ee = params.rho * params.sigma_eta * params.sigma_e
    cov_matrix = np.array([
        [params.sigma_eta**2, cov_ee],
        [cov_ee, params.sigma_e**2],
    ])
    mean_innov = np.zeros(2)

    x = np.zeros(T + 1)
    x[0] = params.x_mean  # start at long-run mean
    r_stock = np.zeros(T)
    ages = np.arange(params.start_age, params.retire_age)

    for t in range(T):
        eta_t, e_t = rng.multivariate_normal(mean_innov, cov_matrix)
        x[t + 1] = params.x_mean + params.phi * (x[t] - params.x_mean) + eta_t
        r_stock[t] = x[t] + e_t  # r_t = x_t + e_t (x_t is "current" predictable part)

    # Wealth path: W[0] = initial_savings; contribution in year t is X * (1 + savings_growth_rate)^t
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
    """
    Run n_sim paths and return array of wealth at retirement (one per path).
    """
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
        "mean": np.mean(wealth),
        "median": np.median(wealth),
        "std": np.std(wealth),
        "min": np.min(wealth),
        "max": np.max(wealth),
        "p5": np.percentile(wealth, 5),
        "p25": np.percentile(wealth, 25),
        "p75": np.percentile(wealth, 75),
        "p95": np.percentile(wealth, 95),
    }


def plot_distribution(
    wealth: np.ndarray,
    title: str = "Distribution of wealth at retirement",
    figsize: tuple = (10, 5),
    save_path: Optional[str] = None,
) -> None:
    """Histogram and summary text."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    ax1.hist(wealth, bins=80, density=True, alpha=0.7, color="steelblue", edgecolor="white")
    ax1.axvline(np.mean(wealth), color="red", linestyle="--", label="Mean")
    ax1.axvline(np.median(wealth), color="orange", linestyle="-.", label="Median")
    ax1.set_xlabel("Wealth at retirement")
    ax1.set_ylabel("Density")
    ax1.set_title(title)
    ax1.legend()

    stats = summary_stats(wealth)
    text = (
        f"Mean:   {stats['mean']:,.0f}\n"
        f"Median: {stats['median']:,.0f}\n"
        f"Std:    {stats['std']:,.0f}\n"
        f"5%:     {stats['p5']:,.0f}\n"
        f"95%:    {stats['p95']:,.0f}"
    )
    ax2.text(0.1, 0.5, text, transform=ax2.transAxes, fontsize=12, verticalalignment="center", family="monospace")
    ax2.axis("off")
    ax2.set_title("Summary statistics")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def main():
    if _DEFAULT_PARAMS_FILE.exists():
        params = load_params_from_file()
        print(f"Parameters loaded from {_DEFAULT_PARAMS_FILE.name}")
    else:
        params = params_from_adams_jmp(
            X=15_000,
            start_age=25,
            retire_age=65,
            n_sim=30_000,
            seed=42,
        )
        print("Using default parameters (Adams 2026 JMP); create sim_params.txt to customize.")

    print("Running simulation...")
    wealth = run_simulation(params)
    print("\nWealth at retirement (distribution summary):")
    for k, v in summary_stats(wealth).items():
        print(f"  {k}: {v:,.0f}")

    plot_distribution(
        wealth,
        title=f"Wealth at retirement (age {params.retire_age})\nSavings X={params.X:,.0f}, r_f={params.r_f:.2%}, {params.n_sim:,} paths",
        save_path="retirement_wealth_distribution.png",
    )


if __name__ == "__main__":
    main()
