#!/usr/bin/env python3
"""Production-ready multi-panel dashboard.

Builds a GridSpec dashboard (KPI panel + several linked charts) and exports it
through :func:`seabornmasterpro.io.save_publication_figure`, which embeds a
provenance record (Python/package versions, platform, git revision, timestamp)
in the PNG/PDF/SVG metadata. The same record is written next to the figure as
``<name>.provenance.json`` so it can be inspected without opening the image.

Usage::

    python production_dashboard.py
    python production_dashboard.py --dataset ecommerce_data --format png pdf svg
    python production_dashboard.py --dataset sales_data --dpi 200 --output ./reports
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # allow running without `pip install -e .`
    sys.path.insert(0, str(REPO_ROOT))
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

from seabornmasterpro import apply_theme, set_seed  # noqa: E402
from seabornmasterpro.io import figure_provenance, save_publication_figure  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "examples"


class DashboardGenerator:
    """Generate a dashboard figure for a DataFrame."""

    def __init__(self, data: pd.DataFrame, title: str | None = None) -> None:
        self.data = data
        self.title = title

    # -------------------------------------------------------------- pieces
    @staticmethod
    def add_header(fig: Figure, title: str) -> None:
        fig.text(0.5, 0.985, title, ha="center", va="top", fontsize=20, fontweight="bold")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        fig.text(
            0.99,
            0.01,
            f"Generated: {stamp}",
            ha="right",
            va="bottom",
            fontsize=8,
            style="italic",
            alpha=0.7,
        )

    @staticmethod
    def add_kpi_panel(ax: Axes, metrics: dict[str, str]) -> None:
        ax.axis("off")
        y = 0.88
        for label, value in metrics.items():
            ax.text(0.02, y, label, fontsize=11, color="0.35", transform=ax.transAxes)
            ax.text(0.02, y - 0.09, value, fontsize=16, fontweight="bold", transform=ax.transAxes)
            y -= 0.22
        ax.set_title("Key Metrics", fontsize=14, fontweight="bold", loc="left")

    # ----------------------------------------------------------- dashboards
    def create_ecommerce_dashboard(self) -> Figure:
        """Dashboard for ``datasets/ecommerce_data.csv`` (sessions, page views, age)."""
        df = self.data.copy()
        session, views, age = "Session Time (min)", "Page Views", "Age"
        df["Age Group"] = pd.cut(
            df[age],
            bins=[17, 25, 35, 45, 55, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "56+"],
        )

        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.3, top=0.92, bottom=0.06)
        self.add_header(fig, self.title or "E-Commerce Engagement Dashboard")

        self.add_kpi_panel(
            fig.add_subplot(gs[0, 0]),
            {
                "Users": f"{df['User ID'].nunique():,}",
                "Median session": f"{df[session].median():.1f} min",
                "Mean page views": f"{df[views].mean():.2f}",
                "Median age": f"{df[age].median():.0f} yrs",
            },
        )

        ax = fig.add_subplot(gs[0, 1:])
        sns.histplot(data=df, x=session, bins=30, kde=True, ax=ax, color="steelblue")
        ax.set_title("Session Time Distribution", fontweight="bold")
        ax.set_xlabel("Session time (min)")

        ax = fig.add_subplot(gs[1, :2])
        sns.barplot(
            data=df, x="Age Group", y=views, hue="Age Group", legend=False,
            palette="viridis", errorbar=("ci", 95), ax=ax,
        )  # fmt: skip
        ax.set_title("Page Views by Age Group (mean, 95% bootstrap CI)", fontweight="bold")
        ax.set_ylabel("Page views")

        ax = fig.add_subplot(gs[1, 2])
        sns.histplot(data=df, x=age, bins=20, ax=ax, color="slategray")
        ax.set_title("Age Distribution", fontweight="bold")

        ax = fig.add_subplot(gs[2, :2])
        sns.scatterplot(
            data=df, x=session, y=views, hue="Age Group", palette="viridis", alpha=0.6, s=40, ax=ax
        )
        ax.set_title("Page Views vs Session Time", fontweight="bold")
        ax.set_xlabel("Session time (min)")
        ax.legend(title="Age group", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)

        ax = fig.add_subplot(gs[2, 2])
        sns.heatmap(
            df[[age, session, views]].corr(), annot=True, fmt=".2f", cmap="coolwarm",
            center=0, vmin=-1, vmax=1, square=True, ax=ax, cbar=False,
        )  # fmt: skip
        ax.set_title("Correlation", fontweight="bold")
        ax.tick_params(axis="x", rotation=30)
        return fig

    def create_generic_dashboard(self) -> Figure:
        """Fallback dashboard for any table with at least two numeric columns."""
        numeric_cols = list(self.data.select_dtypes(include="number").columns)
        if len(numeric_cols) < 2:
            raise ValueError("generic dashboard needs at least two numeric columns")
        c0, c1 = numeric_cols[:2]

        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25, top=0.9, bottom=0.07)
        self.add_header(fig, self.title or "Data Analysis Dashboard")

        for col, spec in ((c0, gs[0, 0]), (c1, gs[0, 1])):
            ax = fig.add_subplot(spec)
            sns.histplot(data=self.data, x=col, kde=True, ax=ax)
            ax.set_title(f"Distribution: {col}", fontweight="bold")

        ax = fig.add_subplot(gs[1, 0])
        sns.heatmap(
            self.data[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax
        )
        ax.set_title("Correlation Matrix", fontweight="bold")

        ax = fig.add_subplot(gs[1, 1])
        sns.scatterplot(data=self.data, x=c0, y=c1, alpha=0.6, ax=ax)
        ax.set_title(f"{c1} vs {c0}", fontweight="bold")
        return fig

    def generate(self, dataset_type: str = "ecommerce") -> Figure:
        if dataset_type == "ecommerce":
            return self.create_ecommerce_dashboard()
        return self.create_generic_dashboard()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Production dashboard generator")
    parser.add_argument("--dataset", default="ecommerce_data", help="Dataset name (without .csv)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument(
        "--format",
        nargs="+",
        default=["png"],
        choices=["png", "pdf", "svg"],
        help="Output format(s)",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Raster resolution")
    parser.add_argument("--title", default=None, help="Override the dashboard title")
    parser.add_argument("--seed", type=int, default=0, help="Seed for bootstrap error bars")
    args = parser.parse_args(argv)

    print("\n" + "=" * 60)
    print("📊 PRODUCTION DASHBOARD GENERATOR")
    print("=" * 60 + "\n")

    set_seed(args.seed)
    apply_theme(style="whitegrid", context="notebook", palette="deep")

    data_path = REPO_ROOT / "datasets" / f"{args.dataset}.csv"
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {args.dataset}: {df.shape[0]} rows, {df.shape[1]} columns\n")

    print("Generating dashboard...\n")
    dataset_type = "ecommerce" if "ecommerce" in args.dataset else "generic"
    fig = DashboardGenerator(df, title=args.title).generate(dataset_type)

    args.output.mkdir(parents=True, exist_ok=True)
    base = args.output / f"{args.dataset}_dashboard"
    written = save_publication_figure(fig, base, formats=args.format, dpi=args.dpi, provenance=True)
    plt.close(fig)

    record = figure_provenance(
        {"dataset": str(data_path.relative_to(REPO_ROOT)), "n_rows": len(df), "dpi": args.dpi}
    )
    sidecar = base.with_suffix(".provenance.json")
    with open(sidecar, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=str)

    print(f"\n✅ Dashboard saved to: {args.output}")
    print(f"   Files: {', '.join(p.name for p in written)} + {sidecar.name}")
    print(
        f"   Git revision: {record.get('git_revision')}  |  seaborn {record['packages'].get('seaborn')}"
    )
    print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
