"""Shared type aliases."""

from __future__ import annotations

from collections.abc import Sequence
from os import PathLike

import numpy as np
import numpy.typing as npt

PathType = str | PathLike[str]
ArrayLike = Sequence[float] | npt.NDArray[np.floating] | npt.NDArray[np.integer]
ColorType = str | tuple[float, float, float] | tuple[float, float, float, float]
