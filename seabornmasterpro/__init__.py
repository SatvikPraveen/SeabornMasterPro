"""SeabornMasterPro: research-grade statistical visualization on top of Seaborn.

The package is organised into focused modules:

- :mod:`seabornmasterpro.theme`     - consistent themes and journal-specific rc presets
- :mod:`seabornmasterpro.io`        - figure/data export with embedded provenance
- :mod:`seabornmasterpro.stats`     - bootstrap intervals, effect sizes, corrected pairwise tests
- :mod:`seabornmasterpro.annotate`  - significance brackets, labels, reference lines
- :mod:`seabornmasterpro.color`     - palette construction and accessibility validation
- :mod:`seabornmasterpro.layout`    - grids, comparisons, date axes
- :mod:`seabornmasterpro.repro`     - seeding, environment capture, manifests
- :mod:`seabornmasterpro.datasets`  - deterministic synthetic datasets with data cards
- :mod:`seabornmasterpro.benchmark` - timing harness for plotting functions

The most common helpers are re-exported at the top level for convenience.
"""

from __future__ import annotations

from seabornmasterpro.annotate import (
    add_reference_line,
    add_statistical_annotations,
    annotate_pairwise,
    annotate_points,
    stylize_plot,
)
from seabornmasterpro.color import (
    contrast_ratio,
    create_color_palette,
    simulate_cvd,
    validate_palette,
)
from seabornmasterpro.io import (
    export_plot_data,
    figure_provenance,
    save_fig,
    save_publication_figure,
)
from seabornmasterpro.layout import create_plot_grid, format_date_axis, plot_comparison
from seabornmasterpro.repro import capture_environment, set_seed
from seabornmasterpro.stats import (
    bootstrap_ci,
    cliffs_delta,
    cohens_d,
    compare_groups,
    hedges_g,
    p_to_stars,
    permutation_test,
)
from seabornmasterpro.theme import apply_theme, journal_context, publication_rc

__version__ = "2.0.0"

__all__ = [
    "__version__",
    # theme
    "apply_theme",
    "journal_context",
    "publication_rc",
    # io
    "save_fig",
    "save_publication_figure",
    "export_plot_data",
    "figure_provenance",
    # annotate
    "stylize_plot",
    "add_reference_line",
    "annotate_points",
    "add_statistical_annotations",
    "annotate_pairwise",
    # color
    "create_color_palette",
    "simulate_cvd",
    "contrast_ratio",
    "validate_palette",
    # layout
    "plot_comparison",
    "create_plot_grid",
    "format_date_axis",
    # stats
    "bootstrap_ci",
    "cohens_d",
    "hedges_g",
    "cliffs_delta",
    "compare_groups",
    "permutation_test",
    "p_to_stars",
    # repro
    "set_seed",
    "capture_environment",
]
