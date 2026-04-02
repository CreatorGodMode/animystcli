from urllib.error import URLError

from animyst.services.mcp_service import McpService
from animyst.storage.repositories import McpRepository


def test_bind_mcp_persists_new_entry(tmp_path):
    repository = McpRepository(tmp_path / "mcps.json")
    service = McpService(repository)

    ok, payload = service.bind_mcp(
        {
            "id": "docs-api",
            "name": "Docs API",
            "type": "http",
            "url": "https://example.com/mcp",
        }
    )

    assert ok is True
    assert payload["name"] == "Docs API"
    assert service.get_mcp("docs-api")["url"] == "https://example.com/mcp"


def test_bind_mcp_rejects_duplicates(tmp_path):
    repository = McpRepository(tmp_path / "mcps.json")
    service = McpService(repository)
    service.bind_mcp({"id": "github", "name": "GitHub", "type": "stdio", "command": "npx github"})

    ok, error = service.bind_mcp({"id": "github", "name": "GitHub", "type": "stdio", "command": "npx github"})

    assert ok is False
    assert error == "MCP already exists"


def test_check_stdio_mcp_marks_missing_executable_as_error(tmp_path):
    repository = McpRepository(tmp_path / "mcps.json")
    service = McpService(repository)
    service.bind_mcp(
        {
            "id": "missing",
            "name": "Missing",
            "type": "stdio",
            "command": "definitely-not-a-real-executable --serve",
        }
    )

    ok, payload = service.check_mcp("missing")

    assert ok is False
    assert payload["health_status"] == "error"
    assert "not found on PATH" in payload["health_detail"]


def test_check_http_mcp_records_healthy_status(tmp_path, monkeypatch):
    repository = McpRepository(tmp_path / "mcps.json")
    service = McpService(repository)
    service.bind_mcp(
        {
            "id": "docs-api",
            "name": "Docs API",
            "type": "http",
            "url": "https://example.com/mcp",
        }
    )

    class FakeResponse:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def getcode(self):
            return self.status

    monkeypatch.setattr("animyst.services.mcp_service.urlopen", lambda request, timeout=5: FakeResponse())

    ok, payload = service.check_mcp("docs-api")

    assert ok is True
    assert payload["health_status"] == "healthy"
    assert payload["health_detail"] == "HTTP 204"


def test_check_http_mcp_records_errors(tmp_path, monkeypatch):
    repository = McpRepository(tmp_path / "mcps.json")
    service = McpService(repository)
    service.bind_mcp(
        {
            "id": "docs-api",
            "name": "Docs API",
            "type": "http",
            "url": "https://example.com/mcp",
        }
    )

    monkeypatch.setattr(
        "animyst.services.mcp_service.urlopen",
        lambda request, timeout=5: (_ for _ in ()).throw(URLError("offline")),
    )

    ok, payload = service.check_mcp("docs-api")

    assert ok is False
    assert payload["health_status"] == "error"
    assert payload["health_detail"] == "offline"
