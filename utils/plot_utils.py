"""Backward-compatible facade over :mod:`seabornmasterpro`.

The curriculum notebooks import ``from utils.plot_utils import ...``. Every name
exported here is now implemented in the ``seabornmasterpro`` package; new code
should import from there directly.
"""

from __future__ import annotations

from seabornmasterpro.annotate import (
    add_reference_line,
    add_statistical_annotations,
    annotate_pairwise,
    annotate_points,
    stylize_plot,
)
from seabornmasterpro.color import create_color_palette, simulate_cvd, validate_palette
from seabornmasterpro.io import export_plot_data, save_fig, save_publication_figure
from seabornmasterpro.layout import (
    create_plot_grid,
    format_date_axis,
    label_panels,
    plot_comparison,
)
from seabornmasterpro.stats import bootstrap_ci, compare_groups, group_summary
from seabornmasterpro.theme import apply_theme, journal_context, publication_rc

__all__ = [
    "add_reference_line",
    "add_statistical_annotations",
    "annotate_pairwise",
    "annotate_points",
    "apply_theme",
    "bootstrap_ci",
    "compare_groups",
    "create_color_palette",
    "create_plot_grid",
    "export_plot_data",
    "format_date_axis",
    "group_summary",
    "journal_context",
    "label_panels",
    "plot_comparison",
    "publication_rc",
    "save_fig",
    "save_publication_figure",
    "simulate_cvd",
    "stylize_plot",
    "validate_palette",
]
