#!/usr/bin/env python3
"""Reusable visualization pipeline template.

Copy this file as the starting point for a new analysis script. It shows the
structure we recommend for production use: a small pipeline class with input
validation, structured logging, deterministic seeding, provenance-embedding
exports from :mod:`seabornmasterpro.io`, and an argparse CLI.

Usage::

    python reusable_template.py --help
    python reusable_template.py --data ../datasets/sales_data.csv --scatter \\
        --x "Units Sold" --y "Total Sales" --hue Region
    python reusable_template.py --data ../datasets/sales_data.csv \\
        --dist "Total Sales" --cat Product "Total Sales" --heatmap
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import matplotlib

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # allow running without `pip install -e .`
    sys.path.insert(0, str(REPO_ROOT))
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from seabornmasterpro import (  # noqa: E402
    apply_theme,
    export_plot_data,
    save_publication_figure,
    set_seed,
    stylize_plot,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CATEGORICAL_KINDS = ("bar", "box", "violin", "point")


class VisualizationPipeline:
    """Load a table, validate columns, draw plots and export them with provenance."""

    def __init__(
        self,
        data_path: Path,
        output_dir: Path,
        *,
        theme_style: str = "whitegrid",
        color_palette: str = "deep",
        formats: tuple[str, ...] = ("png",),
        dpi: int = 300,
        seed: int = 0,
    ) -> None:
        self.data_path = data_path
        self.output_dir = output_dir
        self.formats = formats
        self.dpi = dpi
        self.data: pd.DataFrame | None = None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        set_seed(seed)
        apply_theme(style=theme_style, palette=color_palette)
        logger.info("Initialized pipeline with style=%s, palette=%s", theme_style, color_palette)

    # ---------------------------------------------------------------- data
    def load_data(self, **read_kwargs: Any) -> pd.DataFrame:
        logger.info("Loading data from %s", self.data_path)
        suffix = self.data_path.suffix.lower()
        if suffix == ".csv":
            self.data = pd.read_csv(self.data_path, **read_kwargs)
        elif suffix in {".xlsx", ".xls"}:
            self.data = pd.read_excel(self.data_path, **read_kwargs)
        elif suffix == ".json":
            self.data = pd.read_json(self.data_path, **read_kwargs)
        elif suffix == ".parquet":
            self.data = pd.read_parquet(self.data_path, **read_kwargs)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        logger.info("Loaded %d rows, %d columns", len(self.data), len(self.data.columns))
        return self.data

    def _require(self, columns: list[str]) -> pd.DataFrame:
        """Return the loaded frame or raise if it (or any column) is missing."""
        if self.data is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        missing = [c for c in columns if c not in self.data.columns]
        if missing:
            raise KeyError(f"Missing columns {missing}; available: {list(self.data.columns)}")
        return self.data

    def _save(self, fig: Figure, filename: str | None) -> list[Path]:
        if not filename:
            return []
        written = save_publication_figure(
            fig, self.output_dir / filename, self.formats, dpi=self.dpi, verbose=False
        )
        for path in written:
            logger.info("Saved %s", path)
        return written

    # --------------------------------------------------------------- plots
    def create_scatter_plot(
        self,
        x: str,
        y: str,
        hue: str | None = None,
        title: str | None = None,
        filename: str | None = None,
    ) -> Figure:
        df = self._require([x, y] + ([hue] if hue else []))
        logger.info("Creating scatter plot: %s vs %s", x, y)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df, x=x, y=y, hue=hue, s=60, alpha=0.7, ax=ax)
        stylize_plot(title=title or f"{y} vs {x}", xlabel=x, ylabel=y, ax=ax)
        if hue:
            ax.legend(title=hue, bbox_to_anchor=(1.02, 1), loc="upper left")
        fig.tight_layout()
        self._save(fig, filename)
        return fig

    def create_distribution_plot(
        self, column: str, title: str | None = None, filename: str | None = None
    ) -> Figure:
        df = self._require([column])
        logger.info("Creating distribution plot for %s", column)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=df, x=column, kde=True, bins=30, ax=ax)
        stylize_plot(
            title=title or f"Distribution of {column}", xlabel=column, ylabel="Frequency", ax=ax
        )
        self._save(fig, filename)
        return fig

    def create_categorical_plot(
        self,
        x: str,
        y: str,
        kind: str = "bar",
        title: str | None = None,
        filename: str | None = None,
    ) -> Figure:
        df = self._require([x, y])
        if kind not in CATEGORICAL_KINDS:
            raise ValueError(f"Unknown plot kind {kind!r}; choose from {CATEGORICAL_KINDS}")
        logger.info("Creating %s plot: %s by %s", kind, y, x)
        fig, ax = plt.subplots(figsize=(10, 6))
        common: dict[str, Any] = {"data": df, "x": x, "y": y, "hue": x, "legend": False, "ax": ax}
        if kind == "bar":
            sns.barplot(errorbar=("ci", 95), **common)
        elif kind == "box":
            sns.boxplot(**common)
        elif kind == "violin":
            sns.violinplot(**common)
        else:
            sns.pointplot(errorbar=("ci", 95), **common)
        stylize_plot(title=title or f"{y} by {x}", xlabel=x, ylabel=y, rotate_xticks=45, ax=ax)
        self._save(fig, filename)
        return fig

    def create_correlation_heatmap(
        self, title: str | None = None, filename: str | None = None
    ) -> Figure | None:
        df = self._require([])
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) < 2:
            logger.warning("Not enough numeric columns for a correlation matrix")
            return None
        logger.info("Creating correlation heatmap with %d columns", len(numeric_cols))
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax,
        )  # fmt: skip
        ax.set_title(title or "Correlation Matrix", fontsize=16, fontweight="bold", pad=20)
        fig.tight_layout()
        self._save(fig, filename)
        return fig

    # -------------------------------------------------------------- export
    def export_summary(self, filename: str = "summary") -> Path | None:
        df = self._require([])
        logger.info("Exporting summary statistics")
        summary = df.describe(include="all").T.reset_index().rename(columns={"index": "column"})
        summary["dtype"] = summary["column"].map(df.dtypes.astype(str))
        summary["missing"] = summary["column"].map(df.isna().sum())
        return export_plot_data(None, summary, self.output_dir / f"{filename}.csv", verbose=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reusable visualization template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --data sales.csv --scatter --x "Units Sold" --y "Total Sales" --hue Region
  %(prog)s --data data.csv --dist Price --cat Category Revenue --kind box
  %(prog)s --data data.csv --heatmap --formats png pdf
        """,
    )
    parser.add_argument("--data", type=Path, required=True, help="Input data file")
    parser.add_argument("--output", type=Path, default=Path("./output"), help="Output directory")

    parser.add_argument(
        "--scatter", action="store_true", help="Create scatter plot (needs --x/--y)"
    )
    parser.add_argument("--dist", metavar="COLUMN", help="Create distribution plot for column")
    parser.add_argument("--cat", nargs=2, metavar=("X", "Y"), help="Create categorical plot")
    parser.add_argument("--heatmap", action="store_true", help="Create correlation heatmap")

    parser.add_argument("--x", help="X-axis column")
    parser.add_argument("--y", help="Y-axis column")
    parser.add_argument("--hue", help="Hue grouping column")
    parser.add_argument(
        "--kind", default="bar", choices=CATEGORICAL_KINDS, help="Categorical plot type"
    )

    parser.add_argument(
        "--style",
        default="whitegrid",
        choices=["darkgrid", "whitegrid", "dark", "white", "ticks"],
        help="Seaborn axes style",
    )
    parser.add_argument("--palette", default="deep", help="Colour palette")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png"],
        choices=["png", "pdf", "svg"],
        help="Export formats",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Raster resolution")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    args = parser.parse_args(argv)

    if args.scatter and not (args.x and args.y):
        parser.error("--scatter requires --x and --y")

    print("\n" + "=" * 60)
    print("🎨 VISUALIZATION PIPELINE")
    print("=" * 60 + "\n")

    pipeline = VisualizationPipeline(
        data_path=args.data,
        output_dir=args.output,
        theme_style=args.style,
        color_palette=args.palette,
        formats=tuple(args.formats),
        dpi=args.dpi,
        seed=args.seed,
    )
    pipeline.load_data()

    plots_created = 0
    if args.scatter:
        pipeline.create_scatter_plot(args.x, args.y, args.hue, filename="scatter")
        plots_created += 1
    if args.dist:
        pipeline.create_distribution_plot(args.dist, filename="distribution")
        plots_created += 1
    if args.cat:
        pipeline.create_categorical_plot(
            args.cat[0], args.cat[1], args.kind, filename="categorical"
        )
        plots_created += 1
    if args.heatmap and pipeline.create_correlation_heatmap(filename="heatmap") is not None:
        plots_created += 1
    plt.close("all")

    pipeline.export_summary()

    print("\n" + "=" * 60)
    print(f"✅ Created {plots_created} visualization(s)")
    print(f"📁 Output directory: {args.output}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
