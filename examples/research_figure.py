#!/usr/bin/env python3
"""
Research-Grade Comparison Figure
================================

End-to-end example of the ``seabornmasterpro`` research workflow:

1. Load a dataset with a documented data card and verify its manifest hash.
2. Estimate per-group means with bootstrap confidence intervals.
3. Run pairwise Welch t-tests with Holm correction and Hedges' g effect sizes.
4. Validate the palette for colour-vision deficiency and contrast.
5. Render a two-panel figure sized for a journal column and export it with
   embedded provenance (package versions, git revision, timestamp) plus the
   statistics table and a JSON sidecar.

Usage:
    python research_figure.py
    python research_figure.py --journal science --columns 2 --test mannwhitney
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from seabornmasterpro import (  # noqa: E402
    annotate_pairwise,
    compare_groups,
    export_plot_data,
    save_publication_figure,
    set_seed,
    validate_palette,
)
from seabornmasterpro.annotate import annotate_effect_sizes  # noqa: E402
from seabornmasterpro.datasets import REGISTRY, default_dir, load  # noqa: E402
from seabornmasterpro.layout import label_panels  # noqa: E402
from seabornmasterpro.repro import verify_manifest  # noqa: E402
from seabornmasterpro.stats import group_summary  # noqa: E402
from seabornmasterpro.theme import journal_context  # noqa: E402

ARM_ORDER = ["Placebo", "Low Dose", "High Dose"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--journal", default="nature", help="venue preset (nature, science, ieee, elsevier, plos, acm)")
    parser.add_argument("--columns", type=int, default=2, choices=[1, 2])
    parser.add_argument("--test", default="welch", choices=["welch", "student", "mannwhitney", "permutation"])
    parser.add_argument("--correction", default="holm", choices=["none", "bonferroni", "holm", "fdr_bh"])
    parser.add_argument("--palette", default="colorblind")
    parser.add_argument("--n-boot", type=int, default=5000)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent.parent / "exports" / "research")
    args = parser.parse_args()

    rng = set_seed(2024)
    args.output.mkdir(parents=True, exist_ok=True)

    # 1. Data with integrity check -------------------------------------------------
    card = REGISTRY["clinical_trial"]
    integrity = verify_manifest(default_dir() / "MANIFEST.json")
    status = "verified" if integrity.get(card.filename) else "NOT VERIFIED"
    print(f"📄 {card.name}: {card.description}\n   model: {card.generative_model}\n   manifest: {status}")
    df = load("clinical_trial")

    # 2-3. Statistics --------------------------------------------------------------
    summary = group_summary(df, "Arm", "Outcome", n_boot=args.n_boot, seed=rng)
    summary = summary.set_index("Arm").loc[ARM_ORDER].reset_index()
    pairwise = compare_groups(df, "Arm", "Outcome", test=args.test, correction=args.correction, order=ARM_ORDER, seed=rng)
    print("\n" + pairwise[["group_a", "group_b", "p_value", "p_adjusted", "effect_kind", "effect_size", "effect_label", "stars"]].to_string(index=False))

    # 4. Palette accessibility -----------------------------------------------------
    colors = sns.color_palette(args.palette, n_colors=len(ARM_ORDER))
    report = validate_palette(colors)
    print(f"\n🎨 palette '{args.palette}': min ΔE={report.min_delta_e:.1f}, CVD min ΔE=" + ", ".join(f"{k[:4]}={v:.1f}" for k, v in report.min_delta_e_cvd.items()) + (" ✅" if report.distinguishable else " ⚠️"))
    for w in report.warnings:
        print(f"   - {w}")

    # 5. Figure ---------------------------------------------------------------------
    with journal_context(args.journal, columns=args.columns) as spec:
        w, h = plt.rcParams["figure.figsize"]
        fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(w, h), gridspec_kw={"width_ratios": [1.3, 1]})

        sns.stripplot(data=df, x="Arm", y="Outcome", order=ARM_ORDER, hue="Arm", palette=colors, legend=False, alpha=0.45, size=2.2, jitter=0.22, ax=ax_a)
        ax_a.errorbar(range(len(ARM_ORDER)), summary["estimate"], yerr=[summary["estimate"] - summary["low"], summary["high"] - summary["estimate"]], fmt="o", color="black", ms=3.5, capsize=2.5, lw=1.0, zorder=5)
        ax_a.set_xlabel("")
        ax_a.set_ylabel("Outcome score")
        ax_a.set_title(f"Mean with {int(summary['confidence'][0] * 100)}% bootstrap CI (B={args.n_boot:,})", fontsize=spec.font_size)
        annotate_pairwise(ax_a, pairwise, order=ARM_ORDER, show_effect=True, fontsize=spec.min_font_size, line_offset=0.04)
        annotate_effect_sizes(ax_a, summary, "Arm", fontsize=spec.min_font_size)

        sns.kdeplot(data=df, x="Outcome", hue="Arm", hue_order=ARM_ORDER, palette=colors, fill=True, common_norm=False, alpha=0.25, lw=1.0, ax=ax_b)
        ax_b.set_xlabel("Outcome score")
        ax_b.set_ylabel("Density")
        ax_b.set_title("Outcome distributions", fontsize=spec.font_size)
        sns.move_legend(ax_b, "upper left", title=None, frameon=False, fontsize=spec.min_font_size)
        label_panels([ax_a, ax_b], fmt="{}", fontsize=spec.font_size + 1)
        fig.tight_layout()

        base = args.output / f"clinical_trial_{args.test}_{args.correction}"
        paths = save_publication_figure(fig, base, formats=("png", "pdf", "svg"), dpi=600, verbose=False)
        plt.close(fig)

    export_plot_data(None, pairwise, base.with_name(base.name + "_pairwise.csv"), verbose=False)
    export_plot_data(None, summary, base.with_name(base.name + "_summary.csv"), verbose=False)
    with open(base.with_name(base.name + "_palette_report.json"), "w", encoding="utf-8") as fh:
        import json

        json.dump(report.to_dict(), fh, indent=2)

    print("\n✅ wrote:")
    for p in paths:
        print(f"   {p}")
    print(f"   {base.name}_pairwise.csv, {base.name}_summary.csv, {base.name}_palette_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
