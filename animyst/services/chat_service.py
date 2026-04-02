"""Session and conversation history orchestration."""

from __future__ import annotations

from typing import Any

from animyst.domain import ConversationSession
from animyst.storage import HistoryRepository, ModelRepository


class ChatService:
    """Manage active sessions and model/provider lookup."""

    def __init__(
        self,
        history_repository: HistoryRepository,
        model_repository: ModelRepository,
    ) -> None:
        self.history_repository = history_repository
        self.model_repository = model_repository

    def start_session(self, agent_name: str) -> tuple[ConversationSession, bool]:
        session = self.history_repository.load_latest_session(agent_name)
        if session:
            return session, True
        session = ConversationSession(agent_name=agent_name)
        self.history_repository.save_session(session)
        return session, False

    def append_user_message(self, session: ConversationSession, text: str) -> ConversationSession:
        session.append_message("user", text)
        self.history_repository.save_session(session)
        return session

    def complete_assistant_message(
        self,
        session: ConversationSession,
        text: str,
        usage: dict[str, Any] | None = None,
    ) -> ConversationSession:
        session.append_message("assistant", text)
        if usage:
            session.append_usage(usage)
        self.history_repository.save_session(session)
        return session

    def record_usage(
        self,
        session: ConversationSession,
        usage: dict[str, Any] | None,
    ) -> ConversationSession:
        if usage:
            session.append_usage(usage)
            self.history_repository.save_session(session)
        return session

    def end_session(self, session: ConversationSession) -> ConversationSession:
        self.history_repository.save_session(session)
        return session

    def resolve_provider(self, model_id: str) -> str:
        models = self.model_repository.list_models()
        for model in models:
            if model["id"] == model_id:
                return model.get("provider", "anthropic")
        return "anthropic"

