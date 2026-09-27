#!/usr/bin/env python3
"""Batch-process every dataset in a directory with a consistent set of plots.

For each CSV matching ``--pattern`` the script writes distribution, correlation
and categorical-overview figures plus a ``summary.json``; a master comparison
report is produced across datasets, and every output is fingerprinted into a
``MANIFEST.json`` via :func:`seabornmasterpro.repro.write_manifest` so results
can later be verified with :func:`seabornmasterpro.repro.verify_manifest`.

Usage::

    python batch_processing.py
    python batch_processing.py --pattern "s*.csv" --plots distribution correlation
    python batch_processing.py --parallel --output ./batch_results
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
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

from seabornmasterpro import apply_theme, save_fig, set_seed  # noqa: E402
from seabornmasterpro.repro import write_manifest  # noqa: E402

DEFAULT_DATA_DIR = REPO_ROOT / "datasets"
DEFAULT_OUTPUT = REPO_ROOT / "exports" / "batch_processing"
PLOT_TYPES = ("distribution", "correlation", "category")
MAX_NUMERIC_COLUMNS = 12  # keep the distribution grid readable for wide tables


def _setup_theme(seed: int) -> None:
    """Theme + seed; called in every worker because processes do not inherit rc state."""
    set_seed(seed)
    apply_theme(style="whitegrid", context="notebook", palette="deep")


class BatchProcessor:
    """Process multiple datasets in batch."""

    def __init__(self, data_dir: Path, output_dir: Path, seed: int = 0) -> None:
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.seed = seed
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ I/O
    def find_datasets(self, pattern: str = "*.csv") -> list[Path]:
        return sorted(self.data_dir.glob(pattern))

    @staticmethod
    def load_dataset(filepath: Path) -> pd.DataFrame | None:
        try:
            return pd.read_csv(filepath)
        except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            print(f"  ⚠ Error loading {filepath.name}: {exc}")
            return None

    @staticmethod
    def summarize(filepath: Path, df: pd.DataFrame) -> dict[str, Any]:
        numeric_cols = df.select_dtypes(include="number").columns
        categorical_cols = df.select_dtypes(include="object").columns
        summary: dict[str, Any] = {
            "filename": filepath.name,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "numeric_columns": int(len(numeric_cols)),
            "categorical_columns": int(len(categorical_cols)),
            "missing_values": int(df.isnull().sum().sum()),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024**2),
        }
        if len(numeric_cols):
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
        return summary

    # ---------------------------------------------------------------- plots
    def _dataset_dir(self, filepath: Path) -> Path:
        out = self.output_dir / filepath.stem
        out.mkdir(parents=True, exist_ok=True)
        return out

    def create_distribution_plots(self, filepath: Path, df: pd.DataFrame) -> Path | None:
        numeric_cols = list(df.select_dtypes(include="number").columns)
        if not numeric_cols:
            return None
        if len(numeric_cols) > MAX_NUMERIC_COLUMNS:
            print(f"    • showing first {MAX_NUMERIC_COLUMNS} of {len(numeric_cols)} numeric columns")
            numeric_cols = numeric_cols[:MAX_NUMERIC_COLUMNS]

        n_cols = min(3, len(numeric_cols))
        n_rows = -(-len(numeric_cols) // n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows), squeeze=False)
        flat = axes.ravel()
        for ax, col in zip(flat, numeric_cols, strict=False):
            sns.histplot(data=df, x=col, kde=True, ax=ax, color="steelblue")
            ax.set_title(f"Distribution: {col}", fontweight="bold")
            ax.set_ylabel("Frequency")
        for ax in flat[len(numeric_cols) :]:
            ax.axis("off")
        fig.suptitle(f"Distributions: {filepath.stem}", fontsize=16, fontweight="bold")
        fig.tight_layout()
        path = save_fig(self._dataset_dir(filepath) / "distributions.png", fig=fig, verbose=False)
        plt.close(fig)
        return path

    def create_correlation_matrix(self, filepath: Path, df: pd.DataFrame) -> Path | None:
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) < 2:
            return None
        n = len(numeric_cols)
        fig, ax = plt.subplots(figsize=(max(8, 0.6 * n + 4), max(6, 0.6 * n + 3)))
        sns.heatmap(
            df[numeric_cols].corr(),
            annot=n <= 12,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
        )
        ax.set_title(f"Correlation Matrix: {filepath.stem}", fontsize=14, fontweight="bold", pad=20)
        fig.tight_layout()
        path = save_fig(self._dataset_dir(filepath) / "correlation.png", fig=fig, verbose=False)
        plt.close(fig)
        return path

    def create_category_overview(self, filepath: Path, df: pd.DataFrame) -> Path | None:
        categorical_cols = df.select_dtypes(include="object").columns
        valid_cols = [c for c in categorical_cols if df[c].nunique() <= 20]
        if not valid_cols:
            return None

        n_cols = min(2, len(valid_cols))
        n_rows = -(-len(valid_cols) // n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(7 * n_cols, 5 * n_rows), squeeze=False)
        flat = axes.ravel()
        for ax, col in zip(flat, valid_cols, strict=False):
            counts = df[col].value_counts().head(10).rename_axis(col).reset_index(name="count")
            sns.barplot(
                data=counts, x="count", y=col, hue=col, legend=False, palette="viridis", ax=ax
            )
            ax.set_title(f"Top values: {col}", fontweight="bold")
            ax.set_xlabel("Count")
        for ax in flat[len(valid_cols) :]:
            ax.axis("off")
        fig.suptitle(f"Categorical Overview: {filepath.stem}", fontsize=16, fontweight="bold")
        fig.tight_layout()
        path = save_fig(self._dataset_dir(filepath) / "categories.png", fig=fig, verbose=False)
        plt.close(fig)
        return path

    # ------------------------------------------------------------ pipeline
    def process_single_dataset(
        self, filepath: Path, plot_types: list[str]
    ) -> dict[str, Any] | None:
        """Process one dataset; safe to call from a worker process."""
        _setup_theme(self.seed)
        print(f"\n  Processing: {filepath.name}")
        df = self.load_dataset(filepath)
        if df is None:
            return None

        summary = self.summarize(filepath, df)
        print(f"    • {summary['rows']} rows, {summary['columns']} columns")
        outputs: list[Path] = []
        wanted = set(PLOT_TYPES) if "all" in plot_types else set(plot_types)

        steps = (
            ("distribution", self.create_distribution_plots, "distribution plots"),
            ("correlation", self.create_correlation_matrix, "correlation matrix"),
            ("category", self.create_category_overview, "category overview"),
        )
        for key, func, label in steps:
            if key in wanted:
                path = func(filepath, df)
                if path is not None:
                    outputs.append(path)
                    print(f"    ✓ Created {label}")

        summary_path = self._dataset_dir(filepath) / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, default=str)
        outputs.append(summary_path)

        summary["outputs"] = [str(p) for p in outputs]
        return summary

    def process_all(
        self, pattern: str = "*.csv", plot_types: list[str] | None = None, parallel: bool = False
    ) -> list[dict[str, Any]]:
        plot_types = plot_types or ["all"]
        datasets = self.find_datasets(pattern)
        if not datasets:
            print(f"⚠ No datasets found matching pattern: {pattern}")
            return []
        print(f"\nFound {len(datasets)} datasets to process")

        summaries: list[dict[str, Any]] = []
        if parallel and len(datasets) > 1:
            print("\n🚀 Processing in parallel...")
            with ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(self.process_single_dataset, fp, plot_types): fp
                    for fp in datasets
                }
                for future in as_completed(futures):
                    summary = future.result()
                    if summary:
                        summaries.append(summary)
            summaries.sort(key=lambda s: s["filename"])
        else:
            for filepath in datasets:
                summary = self.process_single_dataset(filepath, plot_types)
                if summary:
                    summaries.append(summary)
        return summaries

    def create_master_report(self, summaries: list[dict[str, Any]]) -> list[Path]:
        """Cross-dataset comparison figure and CSV table."""
        if not summaries:
            return []
        table = pd.DataFrame(summaries).drop(columns=["numeric_summary", "outputs"], errors="ignore")

        panels = (
            ("rows", "Dataset Sizes (Rows)", "Set2"),
            ("columns", "Number of Columns", "Set3"),
            ("missing_values", "Missing Values", "Reds_r"),
            ("memory_usage_mb", "Memory Usage (MB)", "Blues"),
        )
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        for ax, (col, title, palette) in zip(axes.ravel(), panels, strict=True):
            sns.barplot(
                data=table, x="filename", y=col, hue="filename", legend=False, palette=palette, ax=ax
            )
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("")
            ax.tick_params(axis="x", rotation=45)
            for label in ax.get_xticklabels():
                label.set_horizontalalignment("right")
        fig.suptitle("Dataset Comparison Report", fontsize=16, fontweight="bold")
        fig.tight_layout()
        report = save_fig(self.output_dir / "master_report.png", fig=fig, verbose=False)
        plt.close(fig)

        csv_path = self.output_dir / "batch_summary.csv"
        table.to_csv(csv_path, index=False)
        print(f"\n  ✓ Master report saved: {report}")
        print(f"  ✓ Summary table saved: {csv_path}")
        return [report, csv_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch dataset processing")
    parser.add_argument(
        "--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing datasets"
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--pattern", default="*.csv", help="Glob pattern to match")
    parser.add_argument(
        "--plots",
        nargs="+",
        default=["all"],
        choices=["all", *PLOT_TYPES],
        help="Types of plots to generate",
    )
    parser.add_argument("--parallel", action="store_true", help="Process datasets in parallel")
    parser.add_argument("--seed", type=int, default=0, help="Seed for bootstrap error bars")
    args = parser.parse_args(argv)

    print("\n" + "=" * 60)
    print("🔄 BATCH DATASET PROCESSING")
    print("=" * 60)

    _setup_theme(args.seed)
    processor = BatchProcessor(args.data_dir, args.output, seed=args.seed)
    summaries = processor.process_all(args.pattern, args.plots, args.parallel)

    outputs: list[Path] = [Path(p) for s in summaries for p in s["outputs"]]
    if summaries:
        print("\nCreating master comparison report...")
        outputs.extend(processor.create_master_report(summaries))

    if outputs:
        manifest_path = args.output / "MANIFEST.json"
        write_manifest(
            outputs,
            manifest_path,
            relative_to=args.output,
            extra={
                "seed": args.seed,
                "pattern": args.pattern,
                "plots": args.plots,
                "data_dir": str(args.data_dir),
            },
        )
        print(f"  ✓ Manifest with {len(outputs)} entries: {manifest_path}")

    print("\n" + "=" * 60)
    print(f"✅ Processed {len(summaries)} datasets")
    print(f"📁 Output directory: {args.output}")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
