#!/usr/bin/env python3
"""Statistical visualization with confidence intervals and corrected pairwise tests.

Demonstrates:

- estimator and error-bar comparisons with Seaborn's ``errorbar`` API
- bootstrap confidence intervals via :func:`seabornmasterpro.stats.bootstrap_ci`
  and :func:`seabornmasterpro.stats.group_summary`
- pairwise group comparisons with multiplicity correction and effect sizes via
  :func:`seabornmasterpro.stats.compare_groups`, drawn as stacked significance
  brackets by :func:`seabornmasterpro.annotate.annotate_pairwise`
- regression with confidence bands and custom estimators

Usage::

    python statistical_viz.py
    python statistical_viz.py --ci 99 --n-bootstrap 5000
    python statistical_viz.py --test mannwhitney --correction fdr_bh
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # allow running without `pip install -e .`
    sys.path.insert(0, str(REPO_ROOT))
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from seabornmasterpro import apply_theme, export_plot_data, save_fig, set_seed  # noqa: E402
from seabornmasterpro.annotate import annotate_effect_sizes, annotate_pairwise  # noqa: E402
from seabornmasterpro.stats import bootstrap_ci, compare_groups, group_summary  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "examples"
CATEGORIES = ("A", "B", "C", "D")


def generate_sample_data(n_samples: int, rng: np.random.Generator) -> pd.DataFrame:
    """Four groups drawn from normals with different means and spreads."""
    params = {"A": (100, 15), "B": (110, 20), "C": (95, 10), "D": (105, 25)}
    frames = [
        pd.DataFrame({"Category": cat, "Value": np.clip(rng.normal(mu, sd, n_samples), 0, None)})
        for cat, (mu, sd) in params.items()
    ]
    return pd.concat(frames, ignore_index=True)


def create_comparison_plots(data: pd.DataFrame, output_dir: Path, ci: int) -> None:
    """Mean / median / sum with the same bootstrap CI."""
    estimators = {"Mean": "mean", "Median": "median", "Sum": "sum"}
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"Estimator Comparison (CI={ci}%)", fontsize=16, fontweight="bold")
    for ax, (name, estimator) in zip(axes, estimators.items(), strict=True):
        sns.barplot(
            data=data, x="Category", y="Value", estimator=estimator, errorbar=("ci", ci),
            hue="Category", legend=False, palette="Set2", ax=ax,
        )  # fmt: skip
        ax.set_title(f"{name} estimator", fontweight="bold")
        ax.set_ylabel(f"{name} value")
    fig.tight_layout()
    save_fig(output_dir / f"estimator_comparison_ci{ci}.png", fig=fig)
    plt.close(fig)
    print(f"  ✓ Created estimator comparison (CI={ci}%)")


def create_errorbar_comparison(data: pd.DataFrame, output_dir: Path, ci: int) -> None:
    """Bootstrap CI vs standard deviation vs standard error."""
    error_types = (
        (("ci", ci), f"Bootstrap CI ({ci}%)"),
        ("sd", "Standard deviation"),
        ("se", "Standard error"),
    )
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    fig.suptitle("Error Bar Type Comparison", fontsize=16, fontweight="bold")
    for ax, (errorbar, title) in zip(axes, error_types, strict=True):
        sns.barplot(
            data=data, x="Category", y="Value", errorbar=errorbar, hue="Category",
            legend=False, palette="viridis", capsize=0.2, ax=ax,
        )  # fmt: skip
        ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    save_fig(output_dir / "errorbar_comparison.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created error bar type comparison")


def create_bootstrap_visualization(
    data: pd.DataFrame, output_dir: Path, ci: int, n_boot: int, seed: int
) -> None:
    """Histogram of bootstrap means per group with the percentile CI marked."""
    rng = np.random.default_rng(seed)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, category in zip(axes.ravel(), CATEGORIES, strict=True):
        values = data.loc[data["Category"] == category, "Value"].to_numpy()
        result = bootstrap_ci(values, np.mean, confidence=ci / 100, n_boot=n_boot, seed=seed)
        # Independent resamples for the histogram (bootstrap_ci returns only the interval).
        boots = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)

        ax.hist(boots, bins=30, alpha=0.7, color="steelblue", edgecolor="black")
        ax.axvline(
            result.estimate, color="crimson", linestyle="--", linewidth=2, label="Sample mean"
        )
        ax.axvline(result.low, color="seagreen", linestyle=":", linewidth=2, label=f"{ci}% CI")
        ax.axvline(result.high, color="seagreen", linestyle=":", linewidth=2)
        ax.set_title(
            f"Group {category}: {result.estimate:.1f} [{result.low:.1f}, {result.high:.1f}]",
            fontweight="bold",
        )
        ax.set_xlabel("Bootstrap mean")
        ax.set_ylabel("Frequency")
        ax.legend()
    fig.suptitle(
        f"Bootstrap Sampling Distributions (n_boot={n_boot})", fontsize=16, fontweight="bold"
    )
    fig.tight_layout()
    save_fig(output_dir / "bootstrap_visualization.png", fig=fig)
    plt.close(fig)
    print(f"  ✓ Created bootstrap visualization (n_boot={n_boot})")


def create_group_summary_plot(
    data: pd.DataFrame, output_dir: Path, ci: int, n_boot: int, seed: int
) -> pd.DataFrame:
    """Raw observations with the bootstrap mean ± CI per group, exported to CSV."""
    summary = group_summary(
        data, "Category", "Value", confidence=ci / 100, n_boot=n_boot, seed=seed
    )
    order = [str(c) for c in summary["Category"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.stripplot(
        data=data, x="Category", y="Value", order=order, color="0.6", alpha=0.35, size=3, ax=ax
    )
    x = np.arange(len(summary))
    yerr = np.vstack([summary["estimate"] - summary["low"], summary["high"] - summary["estimate"]])
    ax.errorbar(
        x, summary["estimate"], yerr=yerr, fmt="o", color="crimson", capsize=5, linewidth=2,
        markersize=8, zorder=3, label=f"Mean ± {ci}% bootstrap CI",
    )  # fmt: skip
    y0, y1 = ax.get_ylim()
    ax.set_ylim(y0 - 0.15 * (y1 - y0), y1)
    annotate_effect_sizes(ax, summary, "Category", fmt="{estimate:.1f}\n[{low:.1f}, {high:.1f}]")
    ax.set_title("Group Means with Bootstrap Confidence Intervals", fontweight="bold", fontsize=14)
    ax.legend(loc="upper right")
    fig.tight_layout()
    save_fig(output_dir / "group_summary_ci.png", fig=fig)
    plt.close(fig)
    export_plot_data(None, summary, output_dir / "group_summary.csv")
    print("  ✓ Created group summary plot with bootstrap CIs")
    return summary


def create_regression_with_ci(output_dir: Path, ci: int) -> None:
    """Linear fit with a bootstrap confidence band next to a LOWESS smoother."""
    tips = sns.load_dataset("tips")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    sns.regplot(
        data=tips, x="total_bill", y="tip", ci=ci, scatter_kws={"alpha": 0.5, "s": 40},
        line_kws={"color": "crimson", "linewidth": 2}, ax=axes[0],
    )  # fmt: skip
    axes[0].set_title(f"Linear Regression with {ci}% CI", fontweight="bold", fontsize=14)
    sns.regplot(
        data=tips, x="total_bill", y="tip", lowess=True, scatter_kws={"alpha": 0.5, "s": 40},
        line_kws={"color": "seagreen", "linewidth": 2}, ax=axes[1],
    )  # fmt: skip
    axes[1].set_title("LOWESS Smoothing", fontweight="bold", fontsize=14)
    for ax in axes:
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Tip ($)")
    fig.tight_layout()
    save_fig(output_dir / "regression_with_ci.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created regression with confidence intervals")


def create_pairwise_comparison(
    data: pd.DataFrame, output_dir: Path, ci: int, test: str, correction: str, seed: int
) -> pd.DataFrame:
    """Corrected pairwise tests drawn as significance brackets with effect sizes."""
    order = list(CATEGORIES)
    results = compare_groups(
        data, "Category", "Value", test=test, correction=correction, order=order, seed=seed
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(
        data=data, x="Category", y="Value", order=order, errorbar=("ci", ci), hue="Category",
        legend=False, palette="Set1", capsize=0.2, ax=ax,
    )  # fmt: skip
    annotate_pairwise(ax, results, order=order, show_effect=True)
    ax.set_title(
        f"Pairwise comparisons: {test} test, {correction} correction",
        fontweight="bold",
        fontsize=14,
    )
    ax.set_ylabel(f"Value (mean ± {ci}% CI)")
    fig.tight_layout()
    save_fig(output_dir / "statistical_annotations.png", fig=fig)
    plt.close(fig)

    export_plot_data(None, results, output_dir / "pairwise_tests.csv")
    cols = ["group_a", "group_b", "statistic", "p_value", "p_adjusted", "effect_size", "stars"]
    print("  ✓ Created pairwise comparison plot\n")
    print(results[cols].to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print()
    return results


def create_custom_estimator_demo(data: pd.DataFrame, output_dir: Path) -> None:
    """Any callable reducing an array to a scalar can be an estimator."""

    def iqr(x: np.ndarray) -> float:
        return float(np.percentile(x, 75) - np.percentile(x, 25))

    def percentile_90(x: np.ndarray) -> float:
        return float(np.percentile(x, 90))

    def value_range(x: np.ndarray) -> float:
        return float(np.max(x) - np.min(x))

    estimators = {"IQR": iqr, "90th percentile": percentile_90, "Range": value_range}
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Custom Estimator Functions", fontsize=16, fontweight="bold")
    for ax, (name, func) in zip(axes, estimators.items(), strict=True):
        sns.barplot(
            data=data, x="Category", y="Value", estimator=func, errorbar=None, hue="Category",
            legend=False, palette="rocket", ax=ax,
        )  # fmt: skip
        ax.set_title(name, fontweight="bold")
        ax.set_ylabel(name)
    fig.tight_layout()
    save_fig(output_dir / "custom_estimators.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created custom estimator examples")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Statistical visualization demonstrations")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument(
        "--ci", type=int, default=95, choices=[68, 90, 95, 99], help="Confidence level (%%)"
    )
    parser.add_argument("--n-bootstrap", type=int, default=1000, help="Bootstrap resamples")
    parser.add_argument("--n-samples", type=int, default=100, help="Observations per group")
    parser.add_argument(
        "--test",
        default="welch",
        choices=["welch", "student", "mannwhitney", "permutation"],
        help="Pairwise test used for the significance brackets",
    )
    parser.add_argument(
        "--correction",
        default="holm",
        choices=["none", "bonferroni", "holm", "fdr_bh"],
        help="Multiple-comparison correction",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args(argv)

    print("\n" + "=" * 60)
    print("📊 STATISTICAL VISUALIZATION DEMONSTRATION")
    print("=" * 60 + "\n")

    rng = set_seed(args.seed)
    apply_theme(style="whitegrid", context="notebook", palette="deep")
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Generating sample data (n={args.n_samples} per group, seed={args.seed})...\n")
    data = generate_sample_data(args.n_samples, rng)

    print("Creating statistical visualizations...\n")
    create_comparison_plots(data, args.output, args.ci)
    create_errorbar_comparison(data, args.output, args.ci)
    create_bootstrap_visualization(data, args.output, args.ci, args.n_bootstrap, args.seed)
    create_group_summary_plot(data, args.output, args.ci, args.n_bootstrap, args.seed)
    create_regression_with_ci(args.output, args.ci)
    create_pairwise_comparison(data, args.output, args.ci, args.test, args.correction, args.seed)
    create_custom_estimator_demo(data, args.output)

    print("=" * 60)
    print(f"✅ All visualizations saved to: {args.output}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
