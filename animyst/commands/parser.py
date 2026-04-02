"""Command parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedCommand:
    """A parsed command line."""

    raw: str
    name: str
    args: list[str] = field(default_factory=list)


def parse_command(raw: str) -> ParsedCommand:
    """Parse a command string into a name and arguments."""
    stripped = raw.strip()
    if not stripped:
        return ParsedCommand(raw=raw, name="", args=[])
    parts = stripped.split()
    return ParsedCommand(raw=stripped, name=parts[0].lower(), args=parts[1:])

