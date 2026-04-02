"""Typed domain models for Animyst."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentConfig:
    """Agent manifest persisted in the registry."""

    name: str
    model: str = "claude-sonnet-4-5-20250929"
    incantation: str = "You are a helpful assistant."
    mcps: list[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096
    status: str = "dormant"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentConfig":
        return cls(
            name=data["name"],
            model=data.get("model", cls.model),
            incantation=data.get("incantation", cls.incantation),
            mcps=list(data.get("mcps", [])),
            temperature=float(data.get("temperature", cls.temperature)),
            max_tokens=int(data.get("max_tokens", cls.max_tokens)),
            status=data.get("status", cls.status),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConversationMessage:
    """One persisted conversation message."""

    role: str
    content: str
    timestamp: str = field(default_factory=utc_now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationMessage":
        return cls(
            role=data["role"],
            content=data.get("content", ""),
            timestamp=data.get("timestamp", utc_now()),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConversationSession:
    """Persisted conversation session for one agent."""

    agent_name: str
    session_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    messages: list[ConversationMessage] = field(default_factory=list)
    usage_events: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationSession":
        return cls(
            agent_name=data["agent_name"],
            session_id=data.get("session_id", uuid4().hex),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", data.get("created_at", utc_now())),
            messages=[
                ConversationMessage.from_dict(message)
                for message in data.get("messages", [])
                if isinstance(message, dict)
            ],
            usage_events=[
                usage
                for usage in data.get("usage_events", [])
                if isinstance(usage, dict)
            ],
        )

    @property
    def turn_count(self) -> int:
        return sum(1 for message in self.messages if message.role == "assistant")

    @property
    def message_count(self) -> int:
        return len(self.messages)

    def append_message(self, role: str, content: str) -> ConversationMessage:
        message = ConversationMessage(role=role, content=content)
        self.messages.append(message)
        self.updated_at = message.timestamp
        return message

    def append_usage(self, usage: dict[str, Any]) -> None:
        if usage:
            event = dict(usage)
            event.setdefault("timestamp", utc_now())
            self.usage_events.append(event)
            self.updated_at = event["timestamp"]

    def to_llm_messages(self) -> list[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in self.messages]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [message.to_dict() for message in self.messages],
            "usage_events": list(self.usage_events),
        }


@dataclass
class HistorySummary:
    """Aggregate history details shown in the UI."""

    agent_name: str
    session_count: int = 0
    turn_count: int = 0
    message_count: int = 0
    last_updated: str | None = None

