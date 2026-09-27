"""Timing harness for Seaborn plotting functions.

Measures wall-clock draw time (figure creation through ``canvas.draw``) as a
function of sample size, reporting the median and inter-quartile range across
repeats. Results are tidy DataFrames so they can be plotted with Seaborn itself.
"""

from __future__ import annotations

import argparse
import statistics
import time
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

__all__ = ["DEFAULT_CASES", "main", "make_data", "plot_benchmark", "run_benchmark", "time_call"]

Case = tuple[str, Callable[[pd.DataFrame, Any], Any]]

DEFAULT_CASES: dict[str, Callable[[pd.DataFrame, Any], Any]] = {
    "scatterplot": lambda d, ax: sns.scatterplot(data=d, x="x", y="y", hue="g", ax=ax),
    "lineplot(ci)": lambda d, ax: sns.lineplot(data=d, x="t", y="y", hue="g", ax=ax),
    "lineplot(no ci)": lambda d, ax: sns.lineplot(
        data=d, x="t", y="y", hue="g", errorbar=None, ax=ax
    ),
    "histplot": lambda d, ax: sns.histplot(data=d, x="x", hue="g", ax=ax),
    "kdeplot": lambda d, ax: sns.kdeplot(data=d, x="x", hue="g", ax=ax),
    "boxplot": lambda d, ax: sns.boxplot(data=d, x="g", y="y", ax=ax),
    "violinplot": lambda d, ax: sns.violinplot(data=d, x="g", y="y", ax=ax),
    "barplot(bootstrap)": lambda d, ax: sns.barplot(data=d, x="g", y="y", ax=ax),
    "barplot(sd)": lambda d, ax: sns.barplot(data=d, x="g", y="y", errorbar="sd", ax=ax),
    "stripplot": lambda d, ax: sns.stripplot(data=d, x="g", y="y", ax=ax),
    "regplot": lambda d, ax: sns.regplot(data=d, x="x", y="y", ax=ax),
}


def make_data(n: int, seed: int = 0, n_groups: int = 4) -> pd.DataFrame:
    """Synthetic long-form frame with numeric ``x``, ``y``, time index ``t`` and group ``g``."""
    rng = np.random.default_rng(seed)
    g = rng.integers(0, n_groups, n)
    x = rng.normal(0, 1, n) + g
    return pd.DataFrame(
        {
            "x": x,
            "y": 0.5 * x + rng.normal(0, 1, n),
            "t": np.arange(n) % 50,
            "g": pd.Categorical([f"G{i}" for i in g]),
        }
    )


def time_call(fn: Callable[[], Any], repeats: int = 5, warmup: int = 1) -> list[float]:
    """Run ``fn`` ``repeats`` times after ``warmup`` discarded calls, returning seconds per call."""
    for _ in range(warmup):
        fn()
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return times


def run_benchmark(
    sizes: Sequence[int] = (100, 1_000, 10_000),
    cases: dict[str, Callable[[pd.DataFrame, Any], Any]] | None = None,
    *,
    repeats: int = 5,
    seed: int = 0,
    verbose: bool = True,
) -> pd.DataFrame:
    """Time each plotting case at each sample size.

    Returns
    -------
    pandas.DataFrame
        Columns ``function``, ``n``, ``median_s``, ``q1_s``, ``q3_s``, ``min_s``, ``repeats``.
    """
    cases = cases or DEFAULT_CASES
    rows = []
    for n in sizes:
        data = make_data(n, seed)
        for name, fn in cases.items():

            def draw(
                fn: Callable[[pd.DataFrame, Any], Any] = fn, data: pd.DataFrame = data
            ) -> None:
                fig, ax = plt.subplots(figsize=(4, 3))
                fn(data, ax)
                fig.canvas.draw()
                plt.close(fig)

            t = time_call(draw, repeats=repeats)
            q1, med, q3 = statistics.quantiles(t, n=4) if len(t) >= 2 else (t[0], t[0], t[0])
            rows.append(
                {
                    "function": name,
                    "n": n,
                    "median_s": med,
                    "q1_s": q1,
                    "q3_s": q3,
                    "min_s": min(t),
                    "repeats": repeats,
                }
            )
            if verbose:
                print(f"  {name:22s} n={n:>7,}  median={med * 1000:8.1f} ms")
    return pd.DataFrame(rows)


def plot_benchmark(results: pd.DataFrame, ax: Any | None = None) -> Any:
    """Log-log plot of median draw time versus sample size, one line per function."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=results, x="n", y="median_s", hue="function", marker="o", ax=ax)
    ax.set(
        xscale="log",
        yscale="log",
        xlabel="Sample size (rows)",
        ylabel="Median draw time (s)",
        title="Seaborn draw time vs. sample size",
    )
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    fig = ax.get_figure(root=True)
    if fig is not None:
        fig.tight_layout()
    return ax


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point: ``smp-benchmark --sizes 100 1000 10000 --out benchmarks/results``."""
    parser = argparse.ArgumentParser(description="Benchmark Seaborn plotting functions.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 1_000, 10_000])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path, default=Path("benchmarks/results"))
    parser.add_argument("--only", nargs="*", default=None, help="subset of case names")
    args = parser.parse_args(list(argv) if argv is not None else None)
    plt.switch_backend("Agg")  # the CLI never needs a display
    cases = {k: v for k, v in DEFAULT_CASES.items() if not args.only or k in args.only}
    results = run_benchmark(args.sizes, cases, repeats=args.repeats)
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    results.to_csv(out / "benchmark_results.csv", index=False)
    ax = plot_benchmark(results)
    ax.figure.savefig(out / "benchmark_results.png", dpi=150, bbox_inches="tight")
    print(f"✅ wrote {out / 'benchmark_results.csv'} and .png")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
