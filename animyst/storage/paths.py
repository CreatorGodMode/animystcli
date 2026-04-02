"""Filesystem paths used by Animyst."""

from __future__ import annotations

import os
from pathlib import Path

ANIMYST_DIR = Path(os.environ.get("ANIMYST_DIR", Path.home() / ".animyst")).expanduser()
AGENTS_FILE = ANIMYST_DIR / "agents.json"
MCPS_FILE = ANIMYST_DIR / "mcps.json"
MODELS_FILE = ANIMYST_DIR / "models.json"
SETTINGS_FILE = ANIMYST_DIR / "settings.json"
HISTORY_DIR = ANIMYST_DIR / "history"
