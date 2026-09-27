"""Multi-panel layouts and axis formatting."""

from __future__ import annotations

import string
from collections.abc import Callable, Iterable, Sequence
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

__all__ = ["create_plot_grid", "format_date_axis", "label_panels", "plot_comparison"]


def plot_comparison(
    plot_func: Callable[..., Any],
    data: pd.DataFrame,
    params_list: Sequence[dict[str, Any]],
    titles: Sequence[str],
    figsize: tuple[float, float] = (15, 5),
    sharey: bool = False,
) -> tuple[Figure, list[Axes]]:
    """Draw the same axes-level function with different parameters side by side.

    Parameters
    ----------
    plot_func
        Any Seaborn axes-level function accepting ``data=`` and ``ax=``.
    data
        Data passed to each call.
    params_list
        One keyword dictionary per panel.
    titles
        One title per panel.
    figsize
        Figure size in inches.
    sharey
        Share the y axis across panels (useful when comparing estimators).
    """
    if len(params_list) != len(titles):
        raise ValueError("params_list and titles must have the same length")
    n = len(params_list)
    fig, axes = plt.subplots(1, n, figsize=figsize, sharey=sharey, squeeze=False)
    axes_list: list[Axes] = list(axes[0])
    for ax, params, title in zip(axes_list, params_list, titles, strict=True):
        plot_func(data=data, ax=ax, **params)
        ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return fig, axes_list


def create_plot_grid(
    rows: int,
    cols: int,
    figsize: tuple[float, float] | None = None,
    *,
    verbose: bool = False,
    **kwargs: Any,
) -> tuple[Figure, np.ndarray]:
    """Create a subplot grid and return a flat array of axes.

    Parameters
    ----------
    rows, cols
        Grid shape.
    figsize
        Figure size; defaults to ``(5 * cols, 4 * rows)``.
    **kwargs
        Forwarded to :func:`matplotlib.pyplot.subplots` (``sharex``, ``sharey``, ...).
    """
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must be positive")
    figsize = figsize or (cols * 5, rows * 4)
    fig, axes = plt.subplots(rows, cols, figsize=figsize, squeeze=False, **kwargs)
    flat = np.asarray(axes).ravel()
    if verbose:
        print(f"✅ Created {rows}x{cols} plot grid")
    return fig, flat


def label_panels(
    axes: Iterable[Axes],
    *,
    fmt: str = "{}",
    uppercase: bool = True,
    loc: tuple[float, float] = (-0.12, 1.05),
    **text_kwargs: Any,
) -> None:
    """Add (a), (b), ... panel labels in the top-left corner of each axes.

    Parameters
    ----------
    axes
        Axes to label, in reading order.
    fmt
        Format applied to the letter, e.g. ``"({})"`` or ``"{}."``.
    uppercase
        Use ``A, B, C`` instead of ``a, b, c``.
    loc
        Axes-fraction coordinates of the label.
    """
    letters = string.ascii_uppercase if uppercase else string.ascii_lowercase
    defaults: dict[str, Any] = {
        "fontweight": "bold",
        "fontsize": "large",
        "va": "bottom",
        "ha": "right",
    }
    defaults.update(text_kwargs)
    for letter, ax in zip(letters, axes, strict=False):
        ax.text(*loc, fmt.format(letter), transform=ax.transAxes, **defaults)


def format_date_axis(
    ax: Axes | None = None,
    date_format: str = "%b %Y",
    major_locator: str = "month",
    rotate_xticks: int = 45,
    *,
    interval: int = 1,
) -> Axes:
    """Format a time axis with readable tick labels.

    Parameters
    ----------
    ax
        Target axes (defaults to current).
    date_format
        ``strftime`` pattern for tick labels.
    major_locator
        ``"year"``, ``"month"``, ``"week"``, ``"day"`` or ``"auto"``.
    rotate_xticks
        Rotation in degrees.
    interval
        Locator interval (every *n* months, weeks, ...).
    """
    ax = ax or plt.gca()
    locators: dict[str, Callable[[], mdates.DateLocator]] = {
        "year": lambda: mdates.YearLocator(base=interval),
        "month": lambda: mdates.MonthLocator(interval=interval),
        "week": lambda: mdates.WeekdayLocator(interval=interval),
        "day": lambda: mdates.DayLocator(interval=interval),
        "auto": mdates.AutoDateLocator,
    }
    try:
        locator = locators[major_locator]()
    except KeyError as exc:
        raise ValueError(f"major_locator must be one of {sorted(locators)}") from exc
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    for label in ax.get_xticklabels():
        label.set_rotation(rotate_xticks)
        label.set_horizontalalignment("right" if rotate_xticks else "center")
    _tight(ax)
    return ax


def _tight(ax: Axes) -> None:
    """Call ``tight_layout`` on the owning figure when it is a top-level figure."""
    fig = ax.get_figure(root=True)
    if isinstance(fig, Figure):
        fig.tight_layout()
