"""Shared JSON persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any) -> Any:
    """Load JSON content, returning a default on any error."""
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def save_json(path: Path, data: Any, *, mode: int | None = None) -> None:
    """Write JSON data with optional file permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    if mode is not None:
        path.chmod(mode)


def ensure_json_file(path: Path, default: Any, *, mode: int | None = None) -> None:
    """Create a JSON file if it does not exist yet."""
    if not path.exists():
        save_json(path, default, mode=mode)

