#!/usr/bin/env python3
"""Basic Seaborn visualization workflow.

Demonstrates a complete end-to-end workflow: load a dataset from ``datasets/``,
draw a handful of standard plots (distribution, scatter, bar with bootstrap CI,
correlation heatmap) and save them with provenance metadata embedded in the
PNG via :func:`seabornmasterpro.save_fig`.

Usage::

    python basic_workflow.py
    python basic_workflow.py --dataset employee_data --output ./my_plots
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
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from seabornmasterpro import apply_theme, save_fig, set_seed, stylize_plot  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "examples"


def _slug(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")


def load_data(dataset_name: str) -> pd.DataFrame:
    """Load ``datasets/<dataset_name>.csv``."""
    data_path = REPO_ROOT / "datasets" / f"{dataset_name}.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {dataset_name}.csv: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def create_distribution_plot(df: pd.DataFrame, column: str, output_dir: Path) -> Path:
    """Histogram with a KDE overlay."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x=column, kde=True, bins=30, ax=ax)
    stylize_plot(title=f"Distribution of {column}", xlabel=column, ylabel="Frequency", ax=ax)
    path = save_fig(output_dir / f"{_slug(column)}_distribution.png", fig=fig)
    plt.close(fig)
    print(f"  ✓ Created distribution plot for {column}")
    return path


def create_scatter_plot(df: pd.DataFrame, x: str, y: str, hue: str, output_dir: Path) -> Path:
    """Scatter plot coloured by a categorical column."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, s=60, alpha=0.7, ax=ax)
    stylize_plot(title=f"{y} vs {x}", xlabel=x, ylabel=y, ax=ax)
    ax.legend(title=hue, bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    path = save_fig(output_dir / f"{_slug(y)}_vs_{_slug(x)}.png", fig=fig)
    plt.close(fig)
    print(f"  ✓ Created scatter plot: {y} vs {x}")
    return path


def create_categorical_plot(df: pd.DataFrame, x: str, y: str, output_dir: Path) -> Path:
    """Bar plot of the mean with a 95% bootstrap confidence interval."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df, x=x, y=y, hue=x, legend=False, palette="viridis", errorbar=("ci", 95), ax=ax
    )
    stylize_plot(title=f"Average {y} by {x}", xlabel=x, ylabel=f"Average {y}", ax=ax)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = save_fig(output_dir / f"{_slug(y)}_by_{_slug(x)}.png", fig=fig)
    plt.close(fig)
    print(f"  ✓ Created bar plot: {y} by {x}")
    return path


def create_correlation_heatmap(df: pd.DataFrame, output_dir: Path) -> Path | None:
    """Correlation heatmap for the numeric columns."""
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) < 2:
        print("  ⚠ Skipping heatmap: not enough numeric columns")
        return None

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        df[numeric_cols].corr(),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title("Correlation Heatmap", fontsize=16, fontweight="bold", pad=20)
    fig.tight_layout()
    path = save_fig(output_dir / "correlation_heatmap.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created correlation heatmap")
    return path


def _pick_generic_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """Return (categorical, numeric) column names suitable for a bar plot."""
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical = [c for c in df.columns if df[c].dtype == object and 1 < df[c].nunique() <= 12]
    return (categorical[0] if categorical else None, numeric[-1] if numeric else None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Basic Seaborn visualization workflow")
    parser.add_argument(
        "--dataset", default="sales_data", help="Dataset name in datasets/ (without .csv)"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--seed", type=int, default=0, help="Seed for bootstrap error bars")
    args = parser.parse_args(argv)

    print("\n" + "=" * 60)
    print("🎨 BASIC SEABORN WORKFLOW")
    print("=" * 60 + "\n")

    set_seed(args.seed)
    apply_theme(style="whitegrid", context="notebook", palette="husl")

    args.output.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {args.output}\n")

    df = load_data(args.dataset)
    print(f"\nDataset columns: {list(df.columns)}\n")
    print("Creating visualizations...\n")

    if args.dataset == "sales_data":
        create_distribution_plot(df, "Total Sales", args.output)
        create_scatter_plot(df, "Units Sold", "Total Sales", "Region", args.output)
        create_categorical_plot(df, "Product", "Total Sales", args.output)
        create_correlation_heatmap(df, args.output)
    else:
        cat_col, num_col = _pick_generic_columns(df)
        if num_col is not None:
            create_distribution_plot(df, num_col, args.output)
        if cat_col is not None and num_col is not None:
            create_categorical_plot(df, cat_col, num_col, args.output)
        create_correlation_heatmap(df, args.output)

    print("\n" + "=" * 60)
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
