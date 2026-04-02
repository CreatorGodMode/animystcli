"""Modal screens used by the Textual app."""

from __future__ import annotations

from typing import Any, Callable, Optional

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from animyst.storage import ModelRepository
from animyst.ui.formatting import status_color


class ManifestAgentModal(ModalScreen[Optional[dict[str, Any]]]):
    """Modal to manifest a new agent."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, model_repository: ModelRepository):
        super().__init__()
        self.model_repository = model_repository

    def compose(self):
        models = self.model_repository.list_models()
        model_options = [(model["name"], model["id"]) for model in models]

        with Container(id="modal-dialog"):
            yield Static("[bold #c026d3]◬ MANIFEST AGENT ◬[/]", id="modal-title")
            yield Label("[#504d78]AGENT NAME[/]", classes="modal-label")
            yield Input(placeholder="e.g. scout, coder, reviewer", id="agent-name", classes="modal-input")
            yield Label("[#504d78]MODEL[/]", classes="modal-label")
            yield Select(model_options, value=model_options[1][1] if len(model_options) > 1 else Select.BLANK, id="agent-model", classes="modal-select")
            yield Label("[#504d78]INCANTATION (system prompt)[/]", classes="modal-label")
            yield Input(placeholder="You are a...", id="agent-prompt", classes="modal-input")
            yield Label("[#504d78]TEMPERATURE (0.0-1.0)[/]", classes="modal-label")
            yield Input(placeholder="0.7", id="agent-temp", classes="modal-input", value="0.7")
            with Horizontal(id="modal-actions"):
                yield Button("⚡ MANIFEST", id="btn-create", classes="modal-btn")
                yield Button("✕ CANCEL", id="btn-cancel", classes="modal-btn-cancel")

    @on(Button.Pressed, "#btn-create")
    def on_create(self) -> None:
        name = self.query_one("#agent-name", Input).value.strip()
        if not name:
            self.app.notify("Agent name is required", severity="error")
            return
        model = self.query_one("#agent-model", Select).value
        prompt = self.query_one("#agent-prompt", Input).value or "You are a helpful assistant."
        try:
            temp = float(self.query_one("#agent-temp", Input).value)
        except ValueError:
            temp = 0.7

        self.dismiss(
            {
                "name": name,
                "model": str(model),
                "incantation": prompt,
                "mcps": [],
                "temperature": temp,
                "max_tokens": 4096,
                "status": "dormant",
            }
        )

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class AgentDetailModal(ModalScreen[None]):
    """View agent config details."""

    BINDINGS = [Binding("escape", "cancel", "Close")]

    def __init__(
        self,
        agent: dict[str, Any],
        model_repository: ModelRepository,
        history_line: str,
        on_delete: Callable[[str], None],
        on_awaken: Callable[[dict[str, Any]], None],
    ):
        super().__init__()
        self.agent = agent
        self.model_repository = model_repository
        self.history_line = history_line
        self.on_delete_agent = on_delete
        self.on_awaken_agent = on_awaken

    def compose(self):
        model_name = self.agent.get("model", "unknown")
        for model in self.model_repository.list_models():
            if model["id"] == self.agent.get("model"):
                model_name = model["name"]
                break

        mcps_list = ", ".join(self.agent.get("mcps", [])) or "none"
        detail = f"""[bold #00fff7]{self.agent['name'].upper()}[/]
[#504d78]{'─' * 40}[/]
[#c026d3]MODEL       [/] [#c8c4e0]{model_name}[/]
[#c026d3]INCANTATION [/] [#c8c4e0]{self.agent.get('incantation', 'N/A')[:60]}[/]
[#c026d3]TEMP        [/] [#c8c4e0]{self.agent.get('temperature', 0.7)}[/]
[#c026d3]TOKENS      [/] [#c8c4e0]{self.agent.get('max_tokens', 4096)}[/]
[#c026d3]MCPs        [/] [#c8c4e0]{mcps_list}[/]
[#c026d3]STATUS      [/] [{status_color(self.agent.get('status', 'dormant'))}]● {self.agent.get('status', 'dormant').upper()}[/]
[#c026d3]HISTORY     [/] {self.history_line}"""

        with Container(id="modal-dialog"):
            yield Static("[bold #c026d3]◬ AGENT CONFIG ◬[/]", id="modal-title")
            yield Static(detail)
            with Horizontal(id="modal-actions"):
                yield Button("▶ AWAKEN", id="btn-run", classes="modal-btn")
                yield Button("✕ BANISH", id="btn-delete", classes="modal-btn-cancel")
                yield Button("CLOSE", id="btn-cancel", classes="modal-btn-cancel")

    @on(Button.Pressed, "#btn-run")
    def on_run(self) -> None:
        self.dismiss(None)
        self.on_awaken_agent(self.agent)

    @on(Button.Pressed, "#btn-delete")
    def on_delete(self) -> None:
        self.dismiss(None)
        self.on_delete_agent(self.agent["name"])

    @on(Button.Pressed, "#btn-cancel")
    def on_close(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class SettingsModal(ModalScreen[None]):
    """Modal to configure API keys and settings."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, settings_repository):
        super().__init__()
        self.settings_repository = settings_repository

    def compose(self):
        settings = self.settings_repository.load()
        keys = settings.get("api_keys", {})

        with Container(id="modal-dialog"):
            yield Static("[bold #c026d3]◬ SETTINGS ◬[/]", id="modal-title")
            yield Label("[#504d78]ANTHROPIC API KEY[/]", classes="modal-label")
            yield Input(
                placeholder="sk-ant-...",
                value=keys.get("anthropic", ""),
                password=True,
                id="key-anthropic",
                classes="modal-input",
            )
            yield Label("[#504d78]OPENAI API KEY[/]", classes="modal-label")
            yield Input(
                placeholder="sk-...",
                value=keys.get("openai", ""),
                password=True,
                id="key-openai",
                classes="modal-input",
            )
            yield Label("[#504d78]GOOGLE API KEY[/]", classes="modal-label")
            yield Input(
                placeholder="AI...",
                value=keys.get("google", ""),
                password=True,
                id="key-google",
                classes="modal-input",
            )
            with Horizontal(id="modal-actions"):
                yield Button("💾 SAVE", id="btn-save", classes="modal-btn")
                yield Button("✕ CANCEL", id="btn-cancel", classes="modal-btn-cancel")

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        settings = self.settings_repository.load()
        keys = {}
        for provider in ("anthropic", "openai", "google"):
            value = self.query_one(f"#key-{provider}", Input).value.strip()
            if value:
                keys[provider] = value
        settings["api_keys"] = keys
        self.settings_repository.save(settings)
        self.app.notify("Settings saved", severity="information")
        self.app.log_mind("[#00ff88]SETTINGS[/] API keys updated")
        self.dismiss(None)

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

