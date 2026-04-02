from animyst.domain import ConversationSession
from animyst.services import ChatService
from animyst.storage.repositories import HistoryRepository, ModelRepository


def test_chat_service_starts_new_session_when_none_exists(tmp_path):
    history_repository = HistoryRepository(tmp_path / "history")
    model_repository = ModelRepository(tmp_path / "models.json")
    service = ChatService(history_repository, model_repository)

    session, resumed = service.start_session("scout")

    assert resumed is False
    assert session.agent_name == "scout"
    assert history_repository.load_latest_session("scout") is not None


def test_chat_service_resumes_existing_session(tmp_path):
    history_repository = HistoryRepository(tmp_path / "history")
    session = ConversationSession(agent_name="scout")
    session.append_message("user", "hello")
    history_repository.save_session(session)
    service = ChatService(history_repository, ModelRepository(tmp_path / "models.json"))

    resumed_session, resumed = service.start_session("scout")

    assert resumed is True
    assert resumed_session.message_count == 1


def test_chat_service_persists_user_message_and_assistant_response(tmp_path):
    history_repository = HistoryRepository(tmp_path / "history")
    service = ChatService(history_repository, ModelRepository(tmp_path / "models.json"))
    session, _ = service.start_session("scout")

    session = service.append_user_message(session, "hello")
    session = service.complete_assistant_message(
        session,
        "hi there",
        {"input_tokens": 1, "output_tokens": 2},
    )

    stored = history_repository.load_latest_session("scout")

    assert stored is not None
    assert [message.role for message in stored.messages] == ["user", "assistant"]
    assert stored.usage_events[0]["input_tokens"] == 1


def test_chat_service_resolves_provider_from_models(tmp_path):
    models_path = tmp_path / "models.json"
    models_path.write_text(
        '[{"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "provider": "google"}]'
    )
    service = ChatService(HistoryRepository(tmp_path / "history"), ModelRepository(models_path))

    assert service.resolve_provider("gemini-2.5-pro") == "google"
    assert service.resolve_provider("missing-model") == "anthropic"
