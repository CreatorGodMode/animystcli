"""MCP registration and health checks."""

from __future__ import annotations

import shlex
import shutil
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from animyst.domain import utc_now
from animyst.storage import McpRepository


class McpService:
    """Create, inspect, and health-check bound MCPs."""

    def __init__(self, mcp_repository: McpRepository) -> None:
        self.mcp_repository = mcp_repository

    def list_mcps(self) -> list[dict[str, Any]]:
        return self.mcp_repository.list_mcps()

    def get_mcp(self, name_or_id: str) -> dict[str, Any] | None:
        key = name_or_id.lower()
        return next(
            (
                mcp
                for mcp in self.list_mcps()
                if mcp["id"].lower() == key or mcp["name"].lower() == key
            ),
            None,
        )

    def bind_mcp(self, mcp: dict[str, Any]) -> tuple[bool, dict[str, Any] | str]:
        mcps = self.list_mcps()
        if any(
            existing["id"].lower() == mcp["id"].lower() or existing["name"].lower() == mcp["name"].lower()
            for existing in mcps
        ):
            return False, "MCP already exists"

        normalized = self.mcp_repository._normalize_mcp(mcp)
        mcps.append(normalized)
        self.mcp_repository.save_mcps(mcps)
        return True, normalized

    def check_mcp(self, name_or_id: str) -> tuple[bool, dict[str, Any] | str]:
        mcps = self.list_mcps()
        checked: dict[str, Any] | None = None

        for index, mcp in enumerate(mcps):
            if mcp["id"].lower() != name_or_id.lower() and mcp["name"].lower() != name_or_id.lower():
                continue

            checked = dict(mcp)
            checked["last_checked"] = utc_now()

            if checked.get("type") == "stdio":
                ok, detail = self._check_stdio(checked.get("command", ""))
            else:
                ok, detail = self._check_httpish(checked.get("url", ""))

            checked["health_status"] = "healthy" if ok else "error"
            checked["last_error"] = None if ok else detail
            checked["health_detail"] = detail
            mcps[index] = {key: value for key, value in checked.items() if key != "health_detail"}
            self.mcp_repository.save_mcps(mcps)
            return ok, checked

        return False, f"MCP '{name_or_id}' not found"

    def _check_stdio(self, command: str) -> tuple[bool, str]:
        if not command.strip():
            return False, "No command configured"
        try:
            executable = shlex.split(command)[0]
        except ValueError as error:
            return False, f"Invalid command: {error}"
        resolved = shutil.which(executable)
        if resolved:
            return True, f"Executable found at {resolved}"
        return False, f"Executable '{executable}' not found on PATH"

    def _check_httpish(self, url: str) -> tuple[bool, str]:
        if not url.strip():
            return False, "No URL configured"
        request = Request(url, headers={"User-Agent": "animyst/0.1.0"})
        try:
            with urlopen(request, timeout=5) as response:
                status = getattr(response, "status", None) or response.getcode()
            return 200 <= status < 400, f"HTTP {status}"
        except URLError as error:
            return False, str(error.reason)
        except Exception as error:
            return False, str(error)
