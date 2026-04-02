"""Command normalization and dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from animyst.commands.parser import ParsedCommand, parse_command


@dataclass
class CommandAction:
    """Normalized action for the UI shell."""

    kind: str
    args: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


class CommandDispatcher:
    """Convert user text into action intents."""

    def dispatch(self, raw: str) -> CommandAction:
        command = parse_command(raw)
        if not command.name:
            return CommandAction(kind="noop")

        name = command.name
        args = command.args

        if name == "help":
            return CommandAction(kind="help")
        if name in ("agents", "ls"):
            return CommandAction(kind="list_agents")
        if name == "mcps":
            return CommandAction(kind="list_mcps")
        if name == "models":
            return CommandAction(kind="list_models")
        if name in ("run", "awaken") and args:
            return CommandAction(kind="run_agent", args=[args[0]])
        if name == "manifest" and args:
            return CommandAction(kind="run_agent", args=[args[0]])
        if name in ("manifest", "new"):
            if args and args[0] == "mcp":
                return CommandAction(kind="bind_mcp")
            return CommandAction(kind="manifest_agent")
        if name == "bind" and args and args[0] == "mcp":
            return CommandAction(kind="bind_mcp")
        if name == "check" and len(args) > 1 and args[0] == "mcp":
            return CommandAction(kind="check_mcp", args=[args[1]])
        if name == "inspect" and len(args) > 1 and args[0] == "mcp":
            return CommandAction(kind="inspect_mcp", args=[args[1]])
        if name == "inspect" and args:
            return CommandAction(kind="inspect_agent", args=[args[0]])
        if name in ("delete", "banish") and args:
            return CommandAction(kind="delete_agent", args=[args[0]])
        if name == "export" and args:
            return CommandAction(kind="export_agent", args=[args[0]])
        if name == "clear":
            return CommandAction(kind="clear_console")
        if name == "git" and args:
            return CommandAction(kind="git", args=args)
        if name == "status":
            return CommandAction(kind="status")
        if name == "ascii":
            return CommandAction(kind="ascii")
        return CommandAction(kind="unknown", payload={"command": raw})
