"""Themes and publication rc presets.

Journal presets encode column widths and typographic conventions published in
author guidelines. Widths are expressed in inches; fonts in points.

References
----------
- Nature: single column 89 mm, double column 183 mm, max height 247 mm.
- Science: single column 5.5 cm (2.17 in), double column 12 cm (4.72 in).
- IEEE Transactions: single column 3.5 in, double column 7.16 in.
- Elsevier: single column 90 mm, 1.5 column 140 mm, double column 190 mm.
- PLOS: width 5.2 in min ... 7.5 in max.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import matplotlib as mpl
import seaborn as sns

__all__ = [
    "JOURNALS",
    "JournalSpec",
    "apply_theme",
    "figsize_for",
    "journal_context",
    "publication_rc",
]

_MM_PER_INCH = 25.4


@dataclass(frozen=True)
class JournalSpec:
    """Figure dimension and typography constraints for a publication venue.

    Attributes
    ----------
    name
        Human-readable venue name.
    single_column
        Width of a single-column figure in inches.
    double_column
        Width of a full-width figure in inches.
    max_height
        Maximum figure height in inches.
    font_size
        Base font size in points.
    min_font_size
        Smallest permitted font size in points (used for tick labels).
    line_width
        Default line width in points.
    font_family
        Preferred font family list.
    """

    name: str
    single_column: float
    double_column: float
    max_height: float
    font_size: float = 8.0
    min_font_size: float = 6.0
    line_width: float = 0.8
    font_family: tuple[str, ...] = ("Arial", "Helvetica", "DejaVu Sans")


JOURNALS: dict[str, JournalSpec] = {
    "nature": JournalSpec(
        "Nature", 89 / _MM_PER_INCH, 183 / _MM_PER_INCH, 247 / _MM_PER_INCH, 7, 5, 0.75
    ),
    "science": JournalSpec("Science", 2.17, 4.72, 9.0, 7, 5, 0.75),
    "ieee": JournalSpec(
        "IEEE Transactions", 3.5, 7.16, 8.5, 8, 6, 0.8, ("Times New Roman", "Times", "DejaVu Serif")
    ),
    "elsevier": JournalSpec(
        "Elsevier", 90 / _MM_PER_INCH, 190 / _MM_PER_INCH, 240 / _MM_PER_INCH, 8, 6, 0.8
    ),
    "plos": JournalSpec("PLOS", 5.2, 7.5, 8.75, 9, 7, 0.8),
    "acm": JournalSpec("ACM", 3.33, 7.0, 9.0, 8, 6, 0.8),
    "presentation": JournalSpec("Presentation (16:9)", 6.0, 13.33, 7.5, 16, 12, 1.5),
    "poster": JournalSpec("Poster", 8.0, 16.0, 24.0, 20, 14, 2.0),
}


def apply_theme(
    style: str = "whitegrid",
    context: str = "notebook",
    palette: str | list[Any] = "deep",
    font_scale: float = 1.0,
    rc: dict[str, Any] | None = None,
) -> None:
    """Apply a consistent Seaborn theme across the project.

    Parameters
    ----------
    style
        Seaborn axes style (``darkgrid``, ``whitegrid``, ``dark``, ``white``, ``ticks``).
    context
        Seaborn plotting context (``paper``, ``notebook``, ``talk``, ``poster``).
    palette
        Default color cycle.
    font_scale
        Multiplicative scale for all font sizes.
    rc
        Additional matplotlib rc overrides.
    """
    sns.set_theme(style=style, context=context, palette=palette, font_scale=font_scale, rc=rc)


def publication_rc(journal: str = "nature", *, columns: int = 1, dpi: int = 300) -> dict[str, Any]:
    """Build an rcParams dictionary tuned for a venue.

    Parameters
    ----------
    journal
        Key in :data:`JOURNALS`.
    columns
        ``1`` for single column, ``2`` for full width.
    dpi
        Raster export resolution.

    Returns
    -------
    dict
        rcParams suitable for ``matplotlib.rc_context`` or ``plt.rcParams.update``.
    """
    spec = _spec(journal)
    width = spec.double_column if columns == 2 else spec.single_column
    height = min(width / 1.618, spec.max_height)  # golden ratio by default
    fs = spec.font_size
    return {
        "figure.figsize": (width, height),
        "figure.dpi": 100,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "font.family": "sans-serif" if "Serif" not in spec.font_family[-1] else "serif",
        "font.sans-serif": list(spec.font_family),
        "font.serif": list(spec.font_family),
        "font.size": fs,
        "axes.titlesize": fs,
        "axes.labelsize": fs,
        "xtick.labelsize": max(spec.min_font_size, fs - 1),
        "ytick.labelsize": max(spec.min_font_size, fs - 1),
        "legend.fontsize": max(spec.min_font_size, fs - 1),
        "legend.title_fontsize": fs,
        "lines.linewidth": spec.line_width,
        "lines.markersize": 3.0,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42,  # embed TrueType so text stays editable in Illustrator
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }


@contextmanager
def journal_context(
    journal: str = "nature", *, columns: int = 1, dpi: int = 300, style: str = "ticks"
) -> Iterator[JournalSpec]:
    """Temporarily configure matplotlib for a venue.

    Examples
    --------
    >>> with journal_context("nature", columns=2) as spec:
    ...     fig, ax = plt.subplots()
    ...     ...
    """
    spec = _spec(journal)
    rc = publication_rc(journal, columns=columns, dpi=dpi)
    with mpl.rc_context(rc):  # type: ignore[arg-type]
        with sns.axes_style(style):
            yield spec


def figsize_for(
    journal: str = "nature", *, columns: int = 1, aspect: float = 1.618
) -> tuple[float, float]:
    """Return ``(width, height)`` in inches for a venue and aspect ratio (width / height)."""
    spec = _spec(journal)
    width = spec.double_column if columns == 2 else spec.single_column
    return width, min(width / aspect, spec.max_height)


def _spec(journal: str) -> JournalSpec:
    try:
        return JOURNALS[journal.lower()]
    except KeyError as exc:
        raise KeyError(f"Unknown journal '{journal}'. Choose from {sorted(JOURNALS)}") from exc
