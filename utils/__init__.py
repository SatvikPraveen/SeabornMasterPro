"""Compatibility package; see :mod:`seabornmasterpro` for the maintained API."""

from seabornmasterpro import __version__

from .plot_utils import *  # noqa: F403
from .plot_utils import __all__

__all__ = [*__all__, "__version__"]
