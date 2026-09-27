"""Palette construction and accessibility validation.

Colour-vision-deficiency simulation uses the physiologically based model of
Machado, Oliveira & Fernandes (2009), *IEEE TVCG* 15(6), at full severity.
Contrast follows WCAG 2.1 relative luminance. Perceptual distance is the
Euclidean distance in CIELAB (ΔE*ab, CIE 1976) under D65.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns

from seabornmasterpro._typing import ColorType

__all__ = [
    "CVDType",
    "PaletteReport",
    "contrast_ratio",
    "create_color_palette",
    "cvd_palette_grid",
    "delta_e",
    "linear_to_srgb",
    "min_pairwise_distance",
    "relative_luminance",
    "rgb_to_lab",
    "simulate_cvd",
    "srgb_to_linear",
    "to_rgb_array",
    "validate_palette",
]

CVDType = Literal["protanopia", "deuteranopia", "tritanopia", "achromatopsia"]

# Machado et al. (2009), severity = 1.0, applied in linear RGB.
_CVD_MATRICES: dict[str, np.ndarray] = {
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "tritanopia": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ]
    ),
}
_LUMA = np.array([0.2126, 0.7152, 0.0722])
_RGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
_D65 = np.array([0.95047, 1.0, 1.08883])


def create_color_palette(
    colors: Sequence[ColorType] | None = None,
    n_colors: int | None = None,
    palette_type: str = "qualitative",
) -> list[tuple[float, float, float]]:
    """Generate a palette by explicit colours or by semantic type.

    Parameters
    ----------
    colors
        Explicit colour list (names or hex); takes precedence.
    n_colors
        Number of colours to return.
    palette_type
        ``qualitative`` (colorblind), ``sequential`` (viridis) or ``diverging`` (RdBu_r).
        The defaults are chosen to be colour-vision-deficiency safe.
    """
    if colors:
        return list(sns.color_palette(list(colors), n_colors=n_colors))
    if palette_type == "sequential":
        return list(sns.color_palette("viridis", n_colors=n_colors or 8))
    if palette_type == "diverging":
        return list(sns.color_palette("RdBu_r", n_colors=n_colors or 11))
    if palette_type == "qualitative":
        return list(sns.color_palette("colorblind", n_colors=n_colors or 8))
    raise ValueError("palette_type must be qualitative, sequential or diverging")


def to_rgb_array(colors: Sequence[ColorType] | str) -> np.ndarray:
    """Convert colour specs (or a named Seaborn palette) to an ``(n, 3)`` float array in sRGB."""
    if isinstance(colors, str):
        colors = sns.color_palette(colors)
    return np.asarray([mcolors.to_rgb(c) for c in colors], dtype=float)


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    """Inverse sRGB companding."""
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(lin: np.ndarray) -> np.ndarray:
    """SRGB companding."""
    lin = np.clip(np.asarray(lin, dtype=float), 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(lin, 1 / 2.4) - 0.055)


def simulate_cvd(colors: Sequence[ColorType] | str, kind: CVDType = "deuteranopia") -> np.ndarray:
    """Simulate how a palette appears under a colour vision deficiency.

    Returns
    -------
    numpy.ndarray
        ``(n, 3)`` sRGB array clipped to [0, 1].
    """
    rgb = to_rgb_array(colors)
    lin = srgb_to_linear(rgb)
    if kind == "achromatopsia":
        y = lin @ _LUMA
        sim = np.repeat(y[:, None], 3, axis=1)
    else:
        try:
            m = _CVD_MATRICES[kind]
        except KeyError as exc:
            raise ValueError(
                "kind must be protanopia, deuteranopia, tritanopia or achromatopsia"
            ) from exc
        sim = lin @ m.T
    return np.clip(linear_to_srgb(sim), 0, 1)


def relative_luminance(color: ColorType) -> float:
    """WCAG 2.1 relative luminance in [0, 1]."""
    lin = srgb_to_linear(np.asarray(mcolors.to_rgb(color)))
    return float(lin @ _LUMA)


def contrast_ratio(color_a: ColorType, color_b: ColorType) -> float:
    """WCAG 2.1 contrast ratio (1:1 to 21:1). AA text requires >= 4.5, graphics >= 3."""
    la, lb = relative_luminance(color_a), relative_luminance(color_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert ``(n, 3)`` sRGB to CIELAB (D65)."""
    lin = srgb_to_linear(np.atleast_2d(rgb))
    xyz = lin @ _RGB_TO_XYZ.T / _D65
    eps, kappa = 216 / 24389, 24389 / 27
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16) / 116)
    lab = np.empty_like(xyz)
    lab[:, 0] = 116 * f[:, 1] - 16
    lab[:, 1] = 500 * (f[:, 0] - f[:, 1])
    lab[:, 2] = 200 * (f[:, 1] - f[:, 2])
    return lab


def delta_e(color_a: ColorType, color_b: ColorType) -> float:
    """CIE76 ΔE*ab between two colours. Roughly, ΔE < 2 is imperceptible; > 10 is clearly distinct."""
    lab = rgb_to_lab(to_rgb_array([color_a, color_b]))
    return float(np.linalg.norm(lab[0] - lab[1]))


def min_pairwise_distance(
    colors: Sequence[ColorType] | str | np.ndarray,
) -> tuple[float, tuple[int, int]]:
    """Smallest ΔE*ab between any two palette entries and the offending index pair."""
    rgb = (
        np.asarray(colors, dtype=float) if isinstance(colors, np.ndarray) else to_rgb_array(colors)
    )
    lab = rgb_to_lab(rgb)
    n = lab.shape[0]
    if n < 2:
        return float("inf"), (0, 0)
    diff = lab[:, None, :] - lab[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    dist[np.diag_indices(n)] = np.inf
    idx = np.unravel_index(np.argmin(dist), dist.shape)
    return float(dist[idx]), (int(idx[0]), int(idx[1]))


@dataclass
class PaletteReport:
    """Accessibility summary for a categorical palette."""

    n_colors: int
    min_delta_e: float
    closest_pair: tuple[int, int]
    min_delta_e_cvd: dict[str, float] = field(default_factory=dict)
    min_contrast_on_white: float = 0.0
    min_contrast_on_black: float = 0.0
    threshold: float = 10.0
    distinguishable: bool = False
    contrast_ok: bool = False
    warnings: list[str] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        """True when colours stay distinguishable (normal + CVD) and clear the contrast floor."""
        return self.distinguishable and self.contrast_ok

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict representation."""
        return {
            "n_colors": self.n_colors,
            "min_delta_e": self.min_delta_e,
            "closest_pair": list(self.closest_pair),
            "min_delta_e_cvd": dict(self.min_delta_e_cvd),
            "min_contrast_on_white": self.min_contrast_on_white,
            "min_contrast_on_black": self.min_contrast_on_black,
            "threshold": self.threshold,
            "distinguishable": self.distinguishable,
            "contrast_ok": self.contrast_ok,
            "passes": self.passes,
            "warnings": list(self.warnings),
        }


def validate_palette(
    colors: Sequence[ColorType] | str,
    *,
    threshold: float = 10.0,
    background: ColorType = "white",
    min_contrast: float = 3.0,
) -> PaletteReport:
    """Check that palette entries stay distinguishable under CVD and against the background.

    Parameters
    ----------
    colors
        Palette or Seaborn palette name.
    threshold
        Minimum acceptable ΔE*ab between any pair, both in normal vision and each
        simulated deficiency. 10 is a conservative choice for categorical encodings.
    background
        Background colour for the contrast check.
    min_contrast
        Minimum WCAG contrast for graphical objects (3:1 per SC 1.4.11).
    """
    rgb = to_rgb_array(colors)
    d, pair = min_pairwise_distance(rgb)
    report = PaletteReport(n_colors=len(rgb), min_delta_e=d, closest_pair=pair, threshold=threshold)
    if d < threshold:
        report.warnings.append(
            f"colours {pair[0]} and {pair[1]} differ by only ΔE={d:.1f} in normal vision"
        )
    for kind in ("protanopia", "deuteranopia", "tritanopia"):
        dk, pk = min_pairwise_distance(simulate_cvd(rgb, kind))  # type: ignore[arg-type]
        report.min_delta_e_cvd[kind] = dk
        if dk < threshold:
            report.warnings.append(
                f"under {kind}, colours {pk[0]} and {pk[1]} differ by only ΔE={dk:.1f}"
            )
    contrasts = [contrast_ratio(c, background) for c in rgb]
    report.min_contrast_on_white = min(contrast_ratio(c, "white") for c in rgb)
    report.min_contrast_on_black = min(contrast_ratio(c, "black") for c in rgb)
    report.distinguishable = d >= threshold and all(
        v >= threshold for v in report.min_delta_e_cvd.values()
    )
    report.contrast_ok = min(contrasts) >= min_contrast
    if not report.contrast_ok:
        report.warnings.append(
            f"minimum contrast against background is {min(contrasts):.2f}:1 (< {min_contrast}:1)"
        )
    return report


def cvd_palette_grid(colors: Sequence[ColorType] | str) -> dict[str, np.ndarray]:
    """Return the palette as seen in normal vision and each simulated deficiency."""
    rgb = to_rgb_array(colors)
    out = {"normal": rgb}
    for kind in ("protanopia", "deuteranopia", "tritanopia", "achromatopsia"):
        out[kind] = simulate_cvd(rgb, kind)  # type: ignore[arg-type]
    return out
