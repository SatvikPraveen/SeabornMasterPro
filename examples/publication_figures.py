#!/usr/bin/env python3
"""Publication-ready figure generation.

Figure dimensions and typography come from the venue presets in
:data:`seabornmasterpro.theme.JOURNALS` (Nature, Science, IEEE, Elsevier, PLOS,
ACM, presentation, poster). Each figure is drawn inside
:func:`seabornmasterpro.theme.journal_context`, sized with
:func:`seabornmasterpro.theme.figsize_for`, and exported in several formats with
embedded provenance via :func:`seabornmasterpro.io.save_publication_figure`.

Usage::

    python publication_figures.py
    python publication_figures.py --size nature_single --dpi 600 --formats pdf svg
    python publication_figures.py --show-sizes
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import matplotlib

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # allow running without `pip install -e .`
    sys.path.insert(0, str(REPO_ROOT))
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from seabornmasterpro import set_seed  # noqa: E402
from seabornmasterpro.io import save_publication_figure  # noqa: E402
from seabornmasterpro.layout import label_panels  # noqa: E402
from seabornmasterpro.theme import JOURNALS, JournalSpec, figsize_for, journal_context  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "publication"


def build_size_presets() -> dict[str, tuple[str, int]]:
    """Map preset name -> (journal key, columns), derived from :data:`JOURNALS`.

    Every venue gets ``<venue>_single`` and ``<venue>_double`` entries (presentation
    and poster are full-width only). Legacy names used by earlier versions of this
    script are kept as aliases.
    """
    presets: dict[str, tuple[str, int]] = {}
    for key in JOURNALS:
        if key in ("presentation", "poster"):
            presets[key] = (key, 2)
        else:
            presets[f"{key}_single"] = (key, 1)
            presets[f"{key}_double"] = (key, 2)
    presets.update(
        {
            "journal_single": ("ieee", 1),
            "journal_double": ("ieee", 2),
            "presentation_wide": ("presentation", 2),
            "nature": ("nature", 1),
            "science": ("science", 1),
        }
    )
    return presets


SIZE_PRESETS = build_size_presets()

# Optional typography override (default "auto" uses the venue's own font sizes).
FONT_PRESETS: dict[str, dict[str, float]] = {
    "journal": {"title": 10, "label": 9, "tick": 8, "legend": 8},
    "presentation": {"title": 16, "label": 14, "tick": 12, "legend": 12},
    "poster": {"title": 24, "label": 20, "tick": 18, "legend": 18},
}


def _font_rc(font: str) -> dict[str, float]:
    if font == "auto":
        return {}
    f = FONT_PRESETS[font]
    return {
        "font.size": f["label"],
        "axes.titlesize": f["title"],
        "axes.labelsize": f["label"],
        "xtick.labelsize": f["tick"],
        "ytick.labelsize": f["tick"],
        "legend.fontsize": f["legend"],
    }


@contextmanager
def publication_context(
    preset: str, dpi: int, font: str = "auto", aspect: float = 1.618
) -> Iterator[tuple[JournalSpec, tuple[float, float]]]:
    """Enter the venue rc context and yield ``(spec, figsize)`` for the preset."""
    journal, columns = SIZE_PRESETS[preset]
    figsize = figsize_for(journal, columns=columns, aspect=aspect)
    with journal_context(journal, columns=columns, dpi=dpi), matplotlib.rc_context(_font_rc(font)):
        yield JOURNALS[journal], figsize


def _marker_size(width: float) -> float:
    return 8.0 if width < 4 else 20.0


def create_journal_scatter(
    data: pd.DataFrame, output_dir: Path, preset: str, formats: list[str], dpi: int, font: str
) -> None:
    with publication_context(preset, dpi, font) as (_spec, figsize):
        fig, ax = plt.subplots(figsize=figsize)
        scatter = ax.scatter(
            data["total_bill"], data["tip"], c=data["size"], s=_marker_size(figsize[0]),
            alpha=0.7, cmap="viridis", edgecolors="black", linewidths=0.2,
        )  # fmt: skip
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Party size", rotation=270, labelpad=10)
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Tip ($)")
        ax.set_title("Tip amount vs total bill")
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.4)
        fig.tight_layout()
        save_publication_figure(fig, output_dir / f"scatter_plot_{preset}", formats, dpi=dpi)
        plt.close(fig)
    print(f"  ✓ Created scatter plot ({preset})")


def create_journal_multiplot(
    data: pd.DataFrame, output_dir: Path, preset: str, formats: list[str], dpi: int, font: str
) -> None:
    with publication_context(preset, dpi, font, aspect=1.25) as (_spec, figsize):
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        sns.histplot(data=data, x="total_bill", kde=True, ax=axes[0, 0], color="steelblue")
        axes[0, 0].set_xlabel("Total bill ($)")
        axes[0, 0].set_ylabel("Frequency")

        sns.boxplot(
            data=data, x="day", y="total_bill", hue="day", legend=False, palette="Set2",
            linewidth=0.6, fliersize=1.5, ax=axes[0, 1],
        )  # fmt: skip
        axes[0, 1].set_xlabel("Day of week")
        axes[0, 1].set_ylabel("Total bill ($)")

        sns.violinplot(
            data=data, x="time", y="tip", hue="time", legend=False, palette="muted",
            linewidth=0.6, ax=axes[1, 0],
        )  # fmt: skip
        axes[1, 0].set_xlabel("Time of day")
        axes[1, 0].set_ylabel("Tip ($)")

        sns.regplot(
            data=data, x="total_bill", y="tip", ax=axes[1, 1],
            scatter_kws={"s": _marker_size(figsize[0]) / 2, "alpha": 0.5},
            line_kws={"color": "crimson"},
        )  # fmt: skip
        axes[1, 1].set_xlabel("Total bill ($)")
        axes[1, 1].set_ylabel("Tip ($)")

        label_panels(axes.ravel(), loc=(-0.25, 1.02))
        fig.tight_layout()
        save_publication_figure(fig, output_dir / f"multiplot_{preset}", formats, dpi=dpi)
        plt.close(fig)
    print(f"  ✓ Created multi-panel plot ({preset})")


def create_journal_barplot(
    data: pd.DataFrame, output_dir: Path, preset: str, formats: list[str], dpi: int, font: str
) -> None:
    with publication_context(preset, dpi, font) as (spec, figsize):
        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(
            data=data, x="day", y="total_bill", hue="day", legend=False, palette="colorblind",
            errorbar=("ci", 95), edgecolor="black", linewidth=0.5, capsize=0.15,
            err_kws={"linewidth": spec.line_width}, ax=ax,
        )  # fmt: skip
        ax.set_xlabel("Day of week")
        ax.set_ylabel("Mean total bill ($)")
        ax.set_title("Daily revenue (mean, 95% bootstrap CI)")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f", padding=2, fontsize=spec.min_font_size)  # type: ignore[arg-type]
        fig.tight_layout()
        save_publication_figure(fig, output_dir / f"barplot_{preset}", formats, dpi=dpi)
        plt.close(fig)
    print(f"  ✓ Created bar plot ({preset})")


def create_high_contrast_plot(
    data: pd.DataFrame, output_dir: Path, preset: str, formats: list[str], dpi: int, font: str
) -> None:
    """Encode groups with marker shape rather than colour (survives greyscale printing)."""
    markers = ("o", "s", "^", "D")
    with publication_context(preset, dpi, font) as (_spec, figsize):
        fig, ax = plt.subplots(figsize=figsize)
        for marker, (day, sub) in zip(markers, data.groupby("day", observed=True), strict=False):
            ax.scatter(
                sub["total_bill"], sub["tip"], marker=marker, s=_marker_size(figsize[0]),
                label=str(day), color="black", alpha=0.6, linewidths=0,
            )  # fmt: skip
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Tip ($)")
        ax.set_title("Greyscale-safe encoding")
        ax.legend(title="Day", frameon=False)
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.4)
        fig.tight_layout()
        save_publication_figure(fig, output_dir / f"grayscale_{preset}", formats, dpi=dpi)
        plt.close(fig)
    print(f"  ✓ Created greyscale plot ({preset})")


def create_heatmap_publication(
    data: pd.DataFrame, output_dir: Path, preset: str, formats: list[str], dpi: int, font: str
) -> None:
    with publication_context(preset, dpi, font, aspect=1.1) as (spec, figsize):
        fig, ax = plt.subplots(figsize=figsize)
        corr = data[["total_bill", "tip", "size"]].corr()
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, square=True,
            linewidths=0.4, linecolor="white", cbar_kws={"shrink": 0.8, "label": "Pearson r"},
            annot_kws={"size": spec.font_size}, ax=ax,
        )  # fmt: skip
        ax.set_title("Correlation matrix")
        fig.tight_layout()
        save_publication_figure(fig, output_dir / f"heatmap_{preset}", formats, dpi=dpi)
        plt.close(fig)
    print(f"  ✓ Created heatmap ({preset})")


def print_size_table() -> None:
    print("\nAvailable size presets (from seabornmasterpro.theme.JOURNALS):\n")
    print(f"  {'preset':<20} {'venue':<20} {'width':>7} {'height':>7}  font")
    for name, (journal, columns) in SIZE_PRESETS.items():
        spec = JOURNALS[journal]
        w, h = figsize_for(journal, columns=columns)
        print(f'  {name:<20} {spec.name:<20} {w:>6.2f}" {h:>6.2f}"  {spec.font_size:g} pt')
    print()


def create_size_comparison_grid(data: pd.DataFrame, output_dir: Path, dpi: int = 150) -> None:
    """One demo scatter per (non-alias) preset so sizes can be compared side by side."""
    print("  Creating size comparison figures...")
    seen: set[tuple[str, int]] = set()
    for preset, key in SIZE_PRESETS.items():
        if key in seen:
            continue
        seen.add(key)
        with publication_context(preset, dpi) as (spec, figsize):
            fig, ax = plt.subplots(figsize=figsize)
            sns.scatterplot(
                data=data,
                x="total_bill",
                y="tip",
                hue="time",
                s=_marker_size(figsize[0]),
                alpha=0.7,
                ax=ax,
            )
            ax.set_xlabel("Total bill ($)")
            ax.set_ylabel("Tip ($)")
            ax.set_title(f"{spec.name}: {figsize[0]:.2f} x {figsize[1]:.2f} in")
            ax.legend(title="Time", frameon=False)
            fig.tight_layout()
            save_publication_figure(
                fig, output_dir / f"demo_{preset}", ["png"], dpi=dpi, verbose=False
            )
            plt.close(fig)
        print(f'    ✓ {preset}: {figsize[0]:.2f}" × {figsize[1]:.2f}"')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publication-ready figure generation")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument(
        "--size", default="journal_double", choices=list(SIZE_PRESETS), help="Figure size preset"
    )
    parser.add_argument(
        "--font",
        default="auto",
        choices=["auto", *FONT_PRESETS],
        help="Typography override ('auto' = the venue's own font sizes)",
    )
    parser.add_argument(
        "--dpi", type=int, default=300, choices=[150, 300, 600, 1200], help="Raster resolution"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png", "pdf"],
        choices=["png", "pdf", "svg", "eps"],
        help="Output formats",
    )
    parser.add_argument(
        "--show-sizes",
        action="store_true",
        help="List every size preset and render a demo figure for each",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed for bootstrap error bars")
    args = parser.parse_args(argv)

    print("\n" + "=" * 60)
    print("📄 PUBLICATION-READY FIGURE GENERATION")
    print("=" * 60)

    if args.show_sizes:
        print_size_table()

    set_seed(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    tips = sns.load_dataset("tips")
    print(f"✅ Loaded tips dataset: {len(tips)} rows\n")

    journal, columns = SIZE_PRESETS[args.size]
    width, height = figsize_for(journal, columns=columns)
    print("Settings:")
    print(
        f"  • Size: {args.size} -> {JOURNALS[journal].name}, {columns} column(s), {width:.2f} x {height:.2f} in"
    )
    print(f"  • Font: {args.font}")
    print(f"  • DPI: {args.dpi}")
    print(f"  • Formats: {', '.join(args.formats)}\n")

    print("Creating publication figures...\n")
    common = (tips, args.output, args.size, args.formats, args.dpi, args.font)
    create_journal_scatter(*common)
    create_journal_multiplot(*common)
    create_journal_barplot(*common)
    create_high_contrast_plot(*common)
    create_heatmap_publication(*common)

    if args.show_sizes:
        print()
        create_size_comparison_grid(tips, args.output)

    print("\n" + "=" * 60)
    print(f"✅ Publication figures saved to: {args.output}")
    print(f"   Formats: {', '.join(args.formats)}  |  Resolution: {args.dpi} DPI")
    print("=" * 60 + "\n")
    print("💡 Tips:")
    print("  • --show-sizes lists every venue preset with its dimensions")
    print("  • PDF/SVG are vector formats with editable text (fonttype 42)")
    print("  • Use 300-600 DPI for print submissions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
