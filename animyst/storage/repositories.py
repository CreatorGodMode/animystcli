"""Repository layer for persisted Animyst data."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from animyst.domain import AgentConfig, ConversationSession, HistorySummary
from animyst.storage.json_store import ensure_json_file, load_json, save_json
from animyst.storage.paths import (
    AGENTS_FILE,
    ANIMYST_DIR,
    HISTORY_DIR,
    MCPS_FILE,
    MODELS_FILE,
    SETTINGS_FILE,
)

DEFAULT_MODELS = [
    {"id": "claude-opus-4-6", "name": "Claude Opus 4.6", "provider": "anthropic"},
    {"id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "provider": "anthropic"},
    {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5", "provider": "anthropic"},
    {"id": "gpt-4.1", "name": "GPT-4.1", "provider": "openai"},
    {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "provider": "openai"},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "provider": "google"},
]

DEFAULT_MCPS = [
    {"id": "filesystem", "name": "Filesystem", "type": "stdio", "command": "npx -y @modelcontextprotocol/server-filesystem"},
    {"id": "github", "name": "GitHub", "type": "stdio", "command": "npx -y @modelcontextprotocol/server-github"},
    {"id": "web-search", "name": "Web Search", "type": "stdio", "command": "npx -y @anthropic/web-search-mcp"},
    {"id": "postgres", "name": "PostgreSQL", "type": "stdio", "command": "npx -y @modelcontextprotocol/server-postgres"},
    {"id": "memory", "name": "Memory", "type": "stdio", "command": "npx -y @modelcontextprotocol/server-memory"},
]


def ensure_animyst_dir() -> None:
    """Initialize the Animyst config directory and default JSON files."""
    ANIMYST_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ensure_json_file(MODELS_FILE, DEFAULT_MODELS)
    ensure_json_file(MCPS_FILE, DEFAULT_MCPS)
    ensure_json_file(AGENTS_FILE, [])
    ensure_json_file(SETTINGS_FILE, {}, mode=0o600)


class AgentRepository:
    """CRUD access to manifested agents."""

    def __init__(self, path: Path = AGENTS_FILE):
        self.path = path

    def list_agents(self) -> list[dict[str, Any]]:
        data = load_json(self.path, [])
        return [AgentConfig.from_dict(agent).to_dict() for agent in data if isinstance(agent, dict)]

    def save_agents(self, agents: list[dict[str, Any]]) -> None:
        normalized = [AgentConfig.from_dict(agent).to_dict() for agent in agents]
        save_json(self.path, normalized)


class McpRepository:
    """Access to bound MCP definitions."""

    def __init__(self, path: Path = MCPS_FILE):
        self.path = path

    def list_mcps(self) -> list[dict[str, Any]]:
        data = load_json(self.path, DEFAULT_MCPS)
        return [mcp for mcp in data if isinstance(mcp, dict)]

    def save_mcps(self, mcps: list[dict[str, Any]]) -> None:
        save_json(self.path, mcps)


class ModelRepository:
    """Access to available model definitions."""

    def __init__(self, path: Path = MODELS_FILE):
        self.path = path

    def list_models(self) -> list[dict[str, Any]]:
        data = load_json(self.path, DEFAULT_MODELS)
        return [model for model in data if isinstance(model, dict)]


class SettingsRepository:
    """Access to user settings and provider keys."""

    def __init__(self, path: Path = SETTINGS_FILE):
        self.path = path

    def load(self) -> dict[str, Any]:
        data = load_json(self.path, {})
        return data if isinstance(data, dict) else {}

    def save(self, settings: dict[str, Any]) -> None:
        save_json(self.path, settings, mode=0o600)


class HistoryRepository:
    """Per-agent session history persisted under ~/.animyst/history."""

    def __init__(self, history_dir: Path = HISTORY_DIR):
        self.history_dir = history_dir

    def _history_path(self, agent_name: str) -> Path:
        safe_name = agent_name.strip().lower().replace(" ", "-")
        return self.history_dir / f"{safe_name}.json"

    def _load_payload(self, agent_name: str) -> dict[str, Any]:
        path = self._history_path(agent_name)
        payload = load_json(path, {"agent_name": agent_name, "sessions": []})
        if not isinstance(payload, dict):
            return {"agent_name": agent_name, "sessions": []}
        payload.setdefault("agent_name", agent_name)
        payload.setdefault("sessions", [])
        return payload

    def list_sessions(self, agent_name: str) -> list[ConversationSession]:
        payload = self._load_payload(agent_name)
        sessions = []
        for session in payload.get("sessions", []):
            if isinstance(session, dict):
                try:
                    sessions.append(ConversationSession.from_dict(session))
                except Exception:
                    continue
        sessions.sort(key=lambda item: item.updated_at)
        return sessions

    def load_latest_session(self, agent_name: str) -> ConversationSession | None:
        sessions = self.list_sessions(agent_name)
        return sessions[-1] if sessions else None

    def save_session(self, session: ConversationSession) -> None:
        payload = self._load_payload(session.agent_name)
        sessions = [
            existing
            for existing in payload.get("sessions", [])
            if isinstance(existing, dict)
            and existing.get("session_id") != session.session_id
        ]
        sessions.append(session.to_dict())
        payload["agent_name"] = session.agent_name
        payload["sessions"] = sessions
        save_json(self._history_path(session.agent_name), payload)

    def history_summary(self, agent_name: str) -> HistorySummary:
        sessions = self.list_sessions(agent_name)
        if not sessions:
            return HistorySummary(agent_name=agent_name)
        return HistorySummary(
            agent_name=agent_name,
            session_count=len(sessions),
            turn_count=sum(session.turn_count for session in sessions),
            message_count=sum(session.message_count for session in sessions),
            last_updated=max(session.updated_at for session in sessions),
        )

