#!/usr/bin/env python3
"""Custom styling, themes and colour-vision-deficiency (CVD) checks.

Demonstrates:

- the five Seaborn axes styles and the four plotting contexts
- sequential / diverging / qualitative palettes from :mod:`seabornmasterpro.color`
- custom brand colours and explicit category → colour mappings
- gradient colormaps built from brand colours
- palette accessibility: :func:`seabornmasterpro.color.validate_palette` reports the
  minimum CIELAB ΔE between colours in normal vision and under simulated
  protanopia / deuteranopia / tritanopia, and :func:`cvd_palette_grid` renders
  how each palette looks to each viewer.

Usage::

    python custom_styling.py
    python custom_styling.py --show-palettes
    python custom_styling.py --check Set1 husl --output ./style_examples
"""

from __future__ import annotations

import argparse
import json
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
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from seabornmasterpro import apply_theme, save_fig  # noqa: E402
from seabornmasterpro.color import (  # noqa: E402
    create_color_palette,
    cvd_palette_grid,
    to_rgb_array,
    validate_palette,
)

DEFAULT_OUTPUT = REPO_ROOT / "exports" / "examples"

BRAND_COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "success": "#06A77D",
    "warning": "#F4B942",
    "danger": "#D62828",
}

# Seaborn's "colorblind" palette (Okabe-Ito inspired).
ACCESSIBLE_PALETTE = ["#0173B2", "#DE8F05", "#029E73", "#CC78BC", "#CA9161", "#949494"]

THEMES = ("darkgrid", "whitegrid", "dark", "white", "ticks")
CONTEXTS = ("paper", "notebook", "talk", "poster")


def _draw_swatches(ax: Axes, colors: np.ndarray, title: str) -> None:
    """Render a row of colour swatches on ``ax``."""
    ax.imshow(np.asarray(colors)[None, :, :], aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(colors)))
    ax.set_xticklabels([str(i) for i in range(len(colors))], fontsize=8)
    ax.set_yticks([])
    ax.set_title(title, fontweight="bold", fontsize=11, loc="left")


def demonstrate_themes(output_dir: Path) -> None:
    """Draw the same scatter under each axes style, using context managers."""
    tips = sns.load_dataset("tips")
    fig = plt.figure(figsize=(15, 8))
    for idx, theme in enumerate(THEMES, start=1):
        with sns.axes_style(theme):
            ax = fig.add_subplot(2, 3, idx)
            sns.scatterplot(data=tips, x="total_bill", y="tip", hue="day", palette="Set2", ax=ax)
            ax.set_title(f"Style: {theme}", fontweight="bold")
            ax.legend(fontsize=8, title="day")
    fig.suptitle("Seaborn Axes Styles", fontsize=16, fontweight="bold")
    fig.tight_layout()
    save_fig(output_dir / "theme_comparison.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created theme comparison")


def demonstrate_color_palettes(output_dir: Path) -> None:
    """Sequential, diverging and qualitative palettes from the package."""
    palettes = (
        ("Sequential (ordered data)", create_color_palette(n_colors=8, palette_type="sequential")),
        (
            "Diverging (meaningful centre)",
            create_color_palette(n_colors=9, palette_type="diverging"),
        ),
        ("Qualitative (categories)", create_color_palette(n_colors=6, palette_type="qualitative")),
    )
    fig, axes = plt.subplots(3, 1, figsize=(12, 6))
    for ax, (title, pal) in zip(axes, palettes, strict=True):
        _draw_swatches(ax, to_rgb_array(pal), title)
    fig.tight_layout()
    save_fig(output_dir / "palette_types.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created palette type comparison")


def demonstrate_custom_palette(output_dir: Path) -> None:
    """Bar charts coloured with brand colours vs a CVD-safe palette."""
    data = pd.DataFrame({"Category": list("ABCDEF"), "Values": [85, 72, 93, 65, 88, 79]})
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, (title, palette) in zip(
        axes,
        (
            ("Custom Brand Colors", list(BRAND_COLORS.values())),
            ("CVD-Safe Palette", ACCESSIBLE_PALETTE),
        ),
        strict=True,
    ):
        sns.barplot(
            data=data,
            x="Category",
            y="Values",
            hue="Category",
            legend=False,
            palette=palette,
            ax=ax,
        )
        ax.set_title(title, fontweight="bold", fontsize=14)
        ax.set_ylabel("Performance Score")
    fig.tight_layout()
    save_fig(output_dir / "custom_palettes.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created custom palette examples")


def demonstrate_color_mapping(output_dir: Path) -> None:
    """Default colouring vs an explicit category → colour dictionary."""
    tips = sns.load_dataset("tips")
    day_colors = {
        "Thur": BRAND_COLORS["primary"],
        "Fri": BRAND_COLORS["secondary"],
        "Sat": BRAND_COLORS["accent"],
        "Sun": BRAND_COLORS["success"],
    }
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    sns.boxplot(data=tips, x="day", y="total_bill", ax=axes[0])
    axes[0].set_title("Single Colour (default)", fontweight="bold", fontsize=14)
    sns.boxplot(
        data=tips, x="day", y="total_bill", hue="day", legend=False, palette=day_colors, ax=axes[1]
    )
    axes[1].set_title("Explicit Colour Mapping", fontweight="bold", fontsize=14)
    fig.tight_layout()
    save_fig(output_dir / "color_mapping.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created color mapping examples")


def demonstrate_gradient_palette(output_dir: Path) -> None:
    """A continuous colormap interpolated between brand colours."""
    stops = [BRAND_COLORS["primary"], BRAND_COLORS["accent"], BRAND_COLORS["secondary"]]
    cmap = LinearSegmentedColormap.from_list("brand_gradient", stops, N=256)

    x = np.arange(20)
    y = x**1.5 + (x % 3) * 10
    matrix = np.outer(np.arange(10), np.arange(10))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(matrix, cmap=cmap, ax=axes[0], cbar_kws={"label": "Value"})
    axes[0].set_title("Custom Gradient Heatmap", fontweight="bold", fontsize=14)

    scatter = axes[1].scatter(
        x, y, c=y, cmap=cmap, s=200, alpha=0.8, edgecolors="black", linewidths=1
    )
    fig.colorbar(scatter, ax=axes[1], label="Y value")
    axes[1].set_title("Custom Gradient Scatter", fontweight="bold", fontsize=14)
    axes[1].set_xlabel("X")
    axes[1].set_ylabel("Y")
    fig.tight_layout()
    save_fig(output_dir / "gradient_palettes.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created gradient palette examples")


def demonstrate_context_scaling(output_dir: Path) -> None:
    """The same plot under each plotting context (font/line scaling)."""
    tips = sns.load_dataset("tips")
    fig = plt.figure(figsize=(16, 10))
    for idx, context in enumerate(CONTEXTS, start=1):
        with sns.plotting_context(context):
            ax = fig.add_subplot(2, 2, idx)
            sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time", ax=ax)
            ax.set_title(f"Context: {context}", fontweight="bold")
            ax.legend(fontsize="small")
    fig.suptitle("Seaborn Context Scaling", fontsize=18, fontweight="bold")
    fig.tight_layout()
    save_fig(output_dir / "context_scaling.png", fig=fig)
    plt.close(fig)
    print("  ✓ Created context scaling examples")


def check_palette_accessibility(
    output_dir: Path, palettes: dict[str, list[str] | str], threshold: float = 10.0
) -> dict[str, dict[str, object]]:
    """Validate palettes under CVD simulation and render the comparison grid.

    Returns the per-palette report dictionaries (also written to
    ``palette_accessibility.json``).
    """
    reports: dict[str, dict[str, object]] = {}
    grids = {name: cvd_palette_grid(pal) for name, pal in palettes.items()}
    kinds = list(next(iter(grids.values())).keys())

    fig, axes = plt.subplots(
        len(palettes),
        len(kinds),
        figsize=(3.2 * len(kinds), 1.4 * len(palettes) + 0.8),
        squeeze=False,
    )
    print(f"\n  Palette accessibility (CIELAB ΔE, threshold {threshold:.0f}):")
    for row, (name, pal) in enumerate(palettes.items()):
        report = validate_palette(pal, threshold=threshold)
        reports[name] = report.to_dict()
        verdict = "PASS" if report.passes else "WARN"
        cvd = ", ".join(f"{k[:6]}={v:.1f}" for k, v in report.min_delta_e_cvd.items())
        print(f"    [{verdict}] {name:<18} min ΔE={report.min_delta_e:.1f} | {cvd}")
        for warning in report.warnings:
            print(f"           - {warning}")
        for col, kind in enumerate(kinds):
            ax = axes[row, col]
            ax.imshow(grids[name][kind][None, :, :], aspect="auto", interpolation="nearest")
            ax.set_xticks([])
            ax.set_yticks([])
            if row == 0:
                ax.set_title(kind, fontsize=10, fontweight="bold")
            if col == 0:
                ax.set_ylabel(
                    f"{name}\n[{verdict}]", rotation=0, ha="right", va="center", fontsize=9
                )
    fig.suptitle("Palettes under simulated colour-vision deficiency", fontweight="bold")
    fig.tight_layout()
    save_fig(output_dir / "cvd_simulation.png", fig=fig)
    plt.close(fig)

    report_path = output_dir / "palette_accessibility.json"
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(reports, fh, indent=2)
    print(f"  ✓ Created CVD simulation grid and report ({report_path.name})")
    return reports


def print_palette_info() -> None:
    print("\n" + "=" * 60)
    print("🎨 AVAILABLE COLOR PALETTES")
    print("=" * 60 + "\n")
    print("Built-in Seaborn palettes:")
    for palette in (
        "deep", "muted", "bright", "pastel", "dark", "colorblind",
        "Set1", "Set2", "Set3", "Paired", "viridis", "plasma",
    ):  # fmt: skip
        print(f"  • {palette}")
    print("\nBrand colors (custom):")
    for name, color in BRAND_COLORS.items():
        print(f"  • {name}: {color}")
    print("\nAccessible palette (CVD-safe):")
    for i, color in enumerate(ACCESSIBLE_PALETTE, 1):
        print(f"  • Color {i}: {color}")
    print("\n" + "=" * 60 + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Custom styling demonstrations")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument(
        "--show-palettes", action="store_true", help="Print palette information and exit"
    )
    parser.add_argument(
        "--check",
        nargs="+",
        default=[],
        metavar="PALETTE",
        help="Extra Seaborn palette names to include in the CVD accessibility check",
    )
    parser.add_argument(
        "--threshold", type=float, default=10.0, help="Minimum acceptable ΔE between colours"
    )
    args = parser.parse_args(argv)

    if args.show_palettes:
        print_palette_info()
        return 0

    print("\n" + "=" * 60)
    print("🎨 CUSTOM STYLING DEMONSTRATION")
    print("=" * 60 + "\n")

    args.output.mkdir(parents=True, exist_ok=True)
    apply_theme(style="whitegrid", context="notebook")
    print("Creating styling examples...\n")

    demonstrate_themes(args.output)
    demonstrate_color_palettes(args.output)
    demonstrate_custom_palette(args.output)
    demonstrate_color_mapping(args.output)
    demonstrate_gradient_palette(args.output)
    demonstrate_context_scaling(args.output)

    palettes: dict[str, list[str] | str] = {
        "brand": list(BRAND_COLORS.values()),
        "accessible": ACCESSIBLE_PALETTE,
    }
    palettes.update({name: name for name in args.check})
    check_palette_accessibility(args.output, palettes, threshold=args.threshold)

    print("\n" + "=" * 60)
    print(f"✅ All examples saved to: {args.output}")
    print("=" * 60 + "\n")
    print("💡 Tip: run with --show-palettes to list colour options, --check Set1 to test more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
