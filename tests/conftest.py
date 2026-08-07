"""Test-suite configuration: force a headless matplotlib backend."""
from __future__ import annotations

import os

os.environ.setdefault("MPLBACKEND", "Agg")
