"""Annotation helpers: labels, reference lines and significance brackets."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from seabornmasterpro.layout import _tight
from seabornmasterpro.stats import p_to_stars

__all__ = [
    "add_reference_line",
    "add_statistical_annotations",
    "annotate_effect_sizes",
    "annotate_pairwise",
    "annotate_points",
    "stylize_plot",
]


def stylize_plot(
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    rotate_xticks: int = 0,
    rotate_yticks: int = 0,
    ax: Axes | None = None,
) -> Axes:
    """Set title, axis labels and tick rotation on an axes (defaults to current)."""
    ax = ax or plt.gca()
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if rotate_xticks:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(rotate_xticks)
            lbl.set_horizontalalignment("right")
    if rotate_yticks:
        for lbl in ax.get_yticklabels():
            lbl.set_rotation(rotate_yticks)
    _tight(ax)
    return ax


def add_reference_line(
    value: float,
    axis: str = "h",
    linestyle: str = "--",
    color: str = "gray",
    ax: Axes | None = None,
    label: str | None = None,
    **kwargs: Any,
) -> Any:
    """Draw a horizontal (``'h'``) or vertical (``'v'``) reference line."""
    ax = ax or plt.gca()
    if axis == "h":
        return ax.axhline(y=value, linestyle=linestyle, color=color, label=label, **kwargs)
    if axis == "v":
        return ax.axvline(x=value, linestyle=linestyle, color=color, label=label, **kwargs)
    raise ValueError("axis must be 'h' or 'v'")


def annotate_points(
    x: Sequence[float],
    y: Sequence[float],
    labels: Sequence[Any] | None = None,
    offset: float = 0.3,
    ax: Axes | None = None,
    **text_kwargs: Any,
) -> None:
    """Write a label next to each ``(x, y)`` point."""
    ax = ax or plt.gca()
    defaults: dict[str, Any] = {"fontsize": 9, "color": "black"}
    defaults.update(text_kwargs)
    for i, (xi, yi) in enumerate(zip(x, y, strict=True)):
        label = labels[i] if labels is not None else f"{xi}, {yi}"
        ax.text(xi + offset, yi, str(label), **defaults)


def add_statistical_annotations(
    ax: Axes,
    x1: float,
    x2: float,
    y: float,
    p_value: float,
    height: float = 0.05,
    *,
    text: str | None = None,
    linewidth: float = 1.5,
    fontsize: float = 12,
) -> None:
    """Draw a single significance bracket between two x positions."""
    sig_text = text if text is not None else p_to_stars(p_value)
    ax.plot([x1, x1, x2, x2], [y, y + height, y + height, y], "k-", lw=linewidth)
    ax.text((x1 + x2) / 2, y + height, sig_text, ha="center", va="bottom", fontsize=fontsize)


def annotate_pairwise(
    ax: Axes,
    results: pd.DataFrame,
    *,
    order: Sequence[str] | None = None,
    p_column: str = "p_adjusted",
    only_significant: bool = False,
    show_effect: bool = False,
    fontsize: float = 10,
    line_offset: float = 0.05,
    line_height: float = 0.02,
    text_gap: float = 0.005,
) -> Axes:
    """Stack significance brackets for the output of :func:`seabornmasterpro.stats.compare_groups`.

    Brackets are laid out above the current data limits so they never overlap the
    marks. Categories must be plotted on the x axis in ``order`` (defaults to the
    axes' tick labels).

    Parameters
    ----------
    ax
        Axes holding a categorical plot (bar/box/violin/strip...).
    results
        DataFrame with ``group_a``, ``group_b``, ``p_adjusted`` (or ``p_column``) and ``stars``.
    order
        Category order on the x axis; inferred from tick labels when omitted.
    only_significant
        Skip pairs with p >= 0.05.
    show_effect
        Append the effect size (e.g. ``g=0.52``) to the star label.
    """
    if order is None:
        order = [t.get_text() for t in ax.get_xticklabels()]
    pos = {str(name): i for i, name in enumerate(order)}
    y0, y1 = ax.get_ylim()
    span = y1 - y0
    rows = results.copy()
    if only_significant:
        rows = rows[rows[p_column] < 0.05]
    if rows.empty:
        return ax
    rows["_span"] = [
        abs(pos[str(a)] - pos[str(b)])
        for a, b in zip(rows["group_a"], rows["group_b"], strict=True)
    ]
    rows = rows.sort_values("_span")
    y = y1 + line_offset * span
    for _, r in rows.iterrows():
        xa, xb = pos[str(r["group_a"])], pos[str(r["group_b"])]
        h = line_height * span
        ax.plot([xa, xa, xb, xb], [y, y + h, y + h, y], color="0.2", lw=1.0)
        label = r["stars"] if "stars" in r else p_to_stars(float(r[p_column]))
        if show_effect and "effect_size" in r:
            sym = "g" if r.get("effect_kind", "") == "hedges_g" else "δ"
            label = f"{label}  {sym}={r['effect_size']:.2f}"
        ax.text(
            (xa + xb) / 2,
            y + h + text_gap * span,
            label,
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )
        y += (line_height + 0.06) * span
    ax.set_ylim(y0, y + 0.02 * span)
    return ax


def annotate_effect_sizes(
    ax: Axes,
    summary: pd.DataFrame,
    x: str,
    *,
    fmt: str = "{estimate:.2f}\n[{low:.2f}, {high:.2f}]",
    fontsize: float = 8,
    y_frac: float = 0.02,
) -> Axes:
    """Print estimate and CI beneath each category using :func:`seabornmasterpro.stats.group_summary` output."""
    order = [t.get_text() for t in ax.get_xticklabels()]
    y0, y1 = ax.get_ylim()
    for i, name in enumerate(order):
        row = summary.loc[summary[x].astype(str) == str(name)]
        if row.empty:
            continue
        r = row.iloc[0]
        ax.text(
            i,
            y0 + y_frac * (y1 - y0),
            fmt.format(**{str(k): v for k, v in r.to_dict().items()}),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color="0.25",
        )
    return ax
