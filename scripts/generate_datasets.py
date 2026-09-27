#!/usr/bin/env python3
"""Regenerate all synthetic datasets and the SHA-256 manifest.

Thin wrapper kept for backwards compatibility; the implementation lives in
:mod:`seabornmasterpro.datasets` (also available as the ``smp-datasets`` CLI).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from seabornmasterpro.datasets import main

if __name__ == "__main__":
    raise SystemExit(main())
