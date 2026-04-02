import json

from animyst.domain import ConversationSession
from animyst.storage.repositories import (
    AgentRepository,
    HistoryRepository,
    McpRepository,
    ModelRepository,
    SettingsRepository,
)


def test_agent_repository_round_trip(tmp_path):
    repository = AgentRepository(tmp_path / "agents.json")
    repository.save_agents(
        [
            {
                "name": "scout",
                "model": "gpt-4.1",
                "incantation": "You scout.",
                "mcps": [],
                "temperature": 0.2,
                "max_tokens": 500,
                "status": "dormant",
            }
        ]
    )

    agents = repository.list_agents()

    assert agents[0]["name"] == "scout"
    assert agents[0]["model"] == "gpt-4.1"


def test_settings_repository_writes_restricted_permissions(tmp_path):
    repository = SettingsRepository(tmp_path / "settings.json")
    repository.save({"api_keys": {"openai": "sk-test"}})

    loaded = repository.load()

    assert loaded["api_keys"]["openai"] == "sk-test"
    assert oct((tmp_path / "settings.json").stat().st_mode & 0o777) == "0o600"


def test_model_and_mcp_repositories_ignore_non_dict_entries(tmp_path):
    model_path = tmp_path / "models.json"
    mcp_path = tmp_path / "mcps.json"
    model_path.write_text(json.dumps([{"id": "gpt-4.1", "name": "GPT-4.1"}, "bad"]))
    mcp_path.write_text(json.dumps([{"id": "filesystem", "name": "Filesystem"}, 1]))

    models = ModelRepository(model_path).list_models()
    mcps = McpRepository(mcp_path).list_mcps()

    assert models == [{"id": "gpt-4.1", "name": "GPT-4.1"}]
    assert mcps == [{"id": "filesystem", "name": "Filesystem"}]


def test_history_repository_persists_and_summarizes_sessions(tmp_path):
    repository = HistoryRepository(tmp_path / "history")
    session = ConversationSession(agent_name="scout")
    session.append_message("user", "hello")
    session.append_message("assistant", "hi")
    repository.save_session(session)

    loaded = repository.load_latest_session("scout")
    summary = repository.history_summary("scout")

    assert loaded is not None
    assert loaded.turn_count == 1
    assert summary.session_count == 1
    assert summary.message_count == 2
    assert summary.turn_count == 1


def test_history_repository_handles_malformed_payloads(tmp_path):
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    (history_dir / "scout.json").write_text("{not valid json")

    repository = HistoryRepository(history_dir)

    assert repository.load_latest_session("scout") is None
    assert repository.history_summary("scout").session_count == 0

