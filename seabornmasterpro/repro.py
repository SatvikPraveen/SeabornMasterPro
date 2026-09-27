"""Reproducibility helpers: seeding, environment capture, file manifests."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

import numpy as np

from seabornmasterpro._typing import PathType

__all__ = [
    "capture_environment",
    "file_sha256",
    "git_revision",
    "set_seed",
    "verify_manifest",
    "write_manifest",
]

_TRACKED_PACKAGES = ("numpy", "pandas", "scipy", "matplotlib", "seaborn", "statsmodels", "sklearn")


def set_seed(seed: int = 0) -> np.random.Generator:
    """Seed Python, NumPy's legacy global state, and return a fresh :class:`numpy.random.Generator`.

    Prefer passing the returned generator explicitly to functions that draw random
    numbers; the global seeding is provided for code paths (including Seaborn's
    bootstrap) that still rely on ``np.random``.
    """
    random.seed(seed)
    np.random.seed(seed)  # noqa: NPY002  (legacy global state used by Seaborn's bootstrap)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    return np.random.default_rng(seed)


def git_revision(repo: PathType | None = None, short: bool = True) -> str | None:
    """Return the current git commit hash, or ``None`` when not in a repository."""
    cmd = ["git", "rev-parse", "--short" if short else "--verify", "HEAD"]
    try:
        out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, check=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def capture_environment(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Snapshot interpreter, platform, key package versions and git state.

    Returns
    -------
    dict
        JSON-serialisable mapping suitable for embedding in figure metadata or a
        sidecar file.
    """
    versions: dict[str, str] = {}
    for name in _TRACKED_PACKAGES:
        try:
            mod = import_module(name)
        except ImportError:
            continue
        versions[name] = str(getattr(mod, "__version__", "unknown"))
    from seabornmasterpro import __version__

    info: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "seabornmasterpro": __version__,
        "packages": versions,
        "git_revision": git_revision(),
    }
    if extra:
        info.update(extra)
    return info


def file_sha256(path: PathType, chunk_size: int = 1 << 20) -> str:
    """Compute the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(
    paths: list[PathType],
    manifest_path: PathType,
    *,
    relative_to: PathType | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write a JSON manifest of SHA-256 digests and sizes for ``paths``.

    Parameters
    ----------
    paths
        Files to fingerprint.
    manifest_path
        Destination JSON file.
    relative_to
        Base directory used to relativise keys in the manifest.
    extra
        Additional top-level fields (e.g. generator seed).
    """
    base = Path(relative_to) if relative_to else None
    files: dict[str, dict[str, Any]] = {}
    for p in sorted(Path(x) for x in paths):
        key = str(p.relative_to(base)) if base else str(p)
        files[key] = {"sha256": file_sha256(p), "bytes": p.stat().st_size}
    manifest = {"generated": capture_environment(), "files": files}
    if extra:
        manifest.update(extra)
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return manifest


def verify_manifest(
    manifest_path: PathType, *, relative_to: PathType | None = None
) -> dict[str, bool]:
    """Check files against a manifest. Returns ``{path: matches}``."""
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    base = Path(relative_to) if relative_to else Path(manifest_path).parent
    results: dict[str, bool] = {}
    for key, meta in manifest["files"].items():
        p = base / key
        results[key] = p.exists() and file_sha256(p) == meta["sha256"]
    return results
