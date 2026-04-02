"""High-level agent operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from animyst.storage import AgentRepository, HistoryRepository


class AgentService:
    """Application service for agent lifecycle and summaries."""

    def __init__(
        self,
        agent_repository: AgentRepository,
        history_repository: HistoryRepository,
    ) -> None:
        self.agent_repository = agent_repository
        self.history_repository = history_repository

    def list_agents(self) -> list[dict[str, Any]]:
        return self.agent_repository.list_agents()

    def get_agent(self, name: str) -> dict[str, Any] | None:
        return next(
            (agent for agent in self.list_agents() if agent["name"].lower() == name.lower()),
            None,
        )

    def create_agent(self, agent: dict[str, Any]) -> bool:
        agents = self.list_agents()
        if any(existing["name"].lower() == agent["name"].lower() for existing in agents):
            return False
        agents.append(agent)
        self.agent_repository.save_agents(agents)
        return True

    def set_status(self, name: str, status: str) -> bool:
        agents = self.list_agents()
        updated = False
        for agent in agents:
            if agent["name"].lower() == name.lower():
                agent["status"] = status
                updated = True
        if updated:
            self.agent_repository.save_agents(agents)
        return updated

    def delete_agent(self, name: str) -> bool:
        agents = self.list_agents()
        remaining = [agent for agent in agents if agent["name"].lower() != name.lower()]
        if len(remaining) == len(agents):
            return False
        self.agent_repository.save_agents(remaining)
        return True

    def export_agent(self, name: str, export_path: Path) -> bool:
        agent = self.get_agent(name)
        if not agent:
            return False
        export_path.write_text(json.dumps(agent, indent=2))
        return True

    def history_summary(self, name: str):
        return self.history_repository.history_summary(name)

