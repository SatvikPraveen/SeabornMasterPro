"""Figure and data export with embedded provenance."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from seabornmasterpro._typing import PathType
from seabornmasterpro.repro import capture_environment

__all__ = [
    "export_plot_data",
    "figure_provenance",
    "save_fig",
    "save_publication_figure",
    "write_json",
]

log = logging.getLogger(__name__)

_PDF_KEYS = {"Title", "Author", "Subject", "Keywords", "Creator", "Producer"}


def figure_provenance(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a provenance record (environment + optional user fields) for a figure."""
    return capture_environment(extra)


def _metadata_for(
    fmt: str, provenance: dict[str, Any] | None, title: str | None
) -> dict[str, str] | None:
    if provenance is None:
        return None
    blob = json.dumps(provenance, sort_keys=True, default=str)
    if fmt == "png":
        md = {
            "Software": f"seabornmasterpro {provenance.get('seabornmasterpro', '')}",
            "Provenance": blob,
        }
        if title:
            md["Title"] = title
        return md
    if fmt == "pdf":
        md = {
            "Creator": f"seabornmasterpro {provenance.get('seabornmasterpro', '')}",
            "Subject": blob[:4000],
        }
        if title:
            md["Title"] = title
        return {k: v for k, v in md.items() if k in _PDF_KEYS}
    if fmt == "svg":
        return {"Creator": "seabornmasterpro", "Description": blob[:4000]}
    return None


def save_fig(
    filename: PathType,
    dpi: int = 300,
    fig: Figure | None = None,
    *,
    provenance: bool = True,
    sidecar: bool = False,
    title: str | None = None,
    verbose: bool = True,
    **savefig_kwargs: Any,
) -> Path:
    """Save a figure, creating parent folders and embedding provenance metadata.

    Parameters
    ----------
    filename
        Destination path, e.g. ``exports/01_setup/plot.png``. The suffix selects the format.
    dpi
        Raster resolution.
    fig
        Figure to save; defaults to the current figure.
    provenance
        Embed environment/git information in the file metadata (PNG, PDF, SVG).
    sidecar
        Additionally write ``<filename>.json`` with the same provenance record.
    title
        Optional title stored in the metadata.
    verbose
        Print a confirmation line (kept for notebook ergonomics).
    **savefig_kwargs
        Forwarded to :meth:`matplotlib.figure.Figure.savefig`.

    Returns
    -------
    pathlib.Path
        The written file.
    """
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = fig or plt.gcf()
    fmt = path.suffix.lstrip(".").lower() or "png"
    record = capture_environment() if provenance else None
    metadata = _metadata_for(fmt, record, title)
    kwargs: dict[str, Any] = {"dpi": dpi, "bbox_inches": "tight"}
    kwargs.update(savefig_kwargs)
    if metadata:
        kwargs["metadata"] = metadata
    fig.savefig(path, **kwargs)
    if sidecar and record is not None:
        with open(path.with_suffix(path.suffix + ".json"), "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, sort_keys=True, default=str)
    if verbose:
        print(f"✅ Plot saved to {path}")
    log.info("saved figure %s", path)
    return path


def save_publication_figure(
    fig: Figure,
    filename: PathType,
    formats: Iterable[str] = ("png", "pdf"),
    dpi: int = 600,
    transparent: bool = False,
    *,
    provenance: bool = True,
    sidecar: bool = False,
    title: str | None = None,
    verbose: bool = True,
) -> list[Path]:
    """Save a figure in several formats for submission.

    Parameters
    ----------
    fig
        Figure to export.
    filename
        Base path without extension.
    formats
        Any of ``png``, ``pdf``, ``svg``, ``eps``, ``tiff``.
    dpi
        Raster resolution (journals commonly require 300-600).
    transparent
        Transparent background.
    provenance
        Embed provenance metadata where the format supports it.
    sidecar
        Also write ``<file>.<ext>.json`` with the provenance record for each format.
    title
        Optional title stored in the file metadata.
    """
    base = Path(filename)
    written: list[Path] = []
    for fmt in formats:
        out = base.with_suffix(f".{fmt}")
        written.append(
            save_fig(
                out,
                dpi=dpi,
                fig=fig,
                provenance=provenance,
                sidecar=sidecar,
                title=title,
                transparent=transparent,
                verbose=verbose,
                format=fmt,
            )
        )
    return written


def export_plot_data(
    fig: Figure | None,
    data: pd.DataFrame | dict[str, Any] | None,
    filename: PathType,
    format: str | None = None,
    *,
    verbose: bool = True,
) -> Path | None:
    """Save the data underlying a plot alongside the figure.

    Parameters
    ----------
    fig
        Unused; accepted for API symmetry with :func:`save_fig`.
    data
        DataFrame or mapping convertible to one.
    filename
        Destination file. When ``format`` is omitted the suffix decides.
    format
        ``csv``, ``xlsx``, ``json`` or ``parquet``.
    """
    if data is None:
        return None
    df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = (format or path.suffix.lstrip(".") or "csv").lower()
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df.to_excel(path, index=False)
    elif fmt == "json":
        df.to_json(path, orient="records", indent=2)
    elif fmt == "parquet":
        df.to_parquet(path, index=False)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Use csv, xlsx, json or parquet.")
    if verbose:
        print(f"✅ Data exported to {path}")
    return path


def write_json(
    data: Any, filename: PathType, *, provenance: bool = False, verbose: bool = True
) -> Path:
    """Write any JSON-serialisable object (nested dicts, lists, NumPy scalars) next to a figure.

    Parameters
    ----------
    data
        Object to serialise. NumPy scalars/arrays, pandas objects and datetimes are converted.
    filename
        Destination ``.json`` path; parent folders are created.
    provenance
        Wrap the payload as ``{"data": ..., "provenance": capture_environment()}``.
    """
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"data": data, "provenance": capture_environment()} if provenance else data
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=_json_default)
        fh.write("\n")
    if verbose:
        print(f"✅ JSON written to {path}")
    return path


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)
