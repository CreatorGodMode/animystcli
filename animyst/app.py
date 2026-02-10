"""
 █████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗████████╗
██╔══██╗████╗  ██║██║████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝
███████║██╔██╗ ██║██║██╔████╔██║ ╚████╔╝ ███████╗   ██║
██╔══██║██║╚██╗██║██║██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║
██║  ██║██║ ╚████║██║██║ ╚═╝ ██║   ██║   ███████║   ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝

Breathe Life Into Code — Agent Development Environment
"""

from __future__ import annotations

import json
import os
import subprocess
import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.screen import ModalScreen
from textual.widgets import (
    Header,
    Footer,
    Static,
    Tree,
    RichLog,
    Input,
    Button,
    Label,
    Select,
)
from textual.widget import Widget
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape


# ═══════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════

ANIMYST_DIR = Path.home() / ".animyst"
AGENTS_FILE = ANIMYST_DIR / "agents.json"
MCPS_FILE = ANIMYST_DIR / "mcps.json"
MODELS_FILE = ANIMYST_DIR / "models.json"

DEFAULT_MODELS = [
    {"id": "claude-opus-4-5-20250929", "name": "Claude Opus 4.5", "provider": "anthropic"},
    {"id": "claude-sonnet-4-5-20250514", "name": "Claude Sonnet 4.5", "provider": "anthropic"},
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


@dataclass
class AgentConfig:
    name: str
    model: str = "claude-sonnet-4-5-20250514"
    incantation: str = "You are a helpful assistant."
    mcps: list[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096
    status: str = "dormant"  # dormant, awakened, error


def ensure_animyst_dir():
    """Initialize animyst config directory and defaults."""
    ANIMYST_DIR.mkdir(parents=True, exist_ok=True)
    if not MODELS_FILE.exists():
        MODELS_FILE.write_text(json.dumps(DEFAULT_MODELS, indent=2))
    if not MCPS_FILE.exists():
        MCPS_FILE.write_text(json.dumps(DEFAULT_MCPS, indent=2))
    if not AGENTS_FILE.exists():
        AGENTS_FILE.write_text(json.dumps([], indent=2))


def load_json(path: Path) -> list:
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def save_json(path: Path, data: list):
    path.write_text(json.dumps(data, indent=2))


def load_agents() -> list[dict]:
    return load_json(AGENTS_FILE)


def save_agents(agents: list[dict]):
    save_json(AGENTS_FILE, agents)


def load_mcps() -> list[dict]:
    return load_json(MCPS_FILE)


def save_mcps(mcps: list[dict]):
    save_json(MCPS_FILE, mcps)


def load_models() -> list[dict]:
    return load_json(MODELS_FILE)


# ═══════════════════════════════════════════════════════════════
# ASCII Art & Branding
# ═══════════════════════════════════════════════════════════════

LOGO = """[bold #c026d3]
 █████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗████████╗
██╔══██╗████╗  ██║██║████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝
███████║██╔██╗ ██║██║██╔████╔██║ ╚████╔╝ ███████╗   ██║
██╔══██║██║╚██╗██║██║██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║
██║  ██║██║ ╚████║██║██║ ╚═╝ ██║   ██║   ███████║   ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝[/]
[#504d78]    ◬ breathe life into code ◬[/]
"""

WELCOME_MSG = """[#504d78]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]
[bold #c026d3]  ◬ ANIMYST[/] [#504d78]v0.1.0 — agent development environment[/]
[#504d78]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]

[#c8c4e0]  Welcome, operator. The ether awaits.[/]
[#c8c4e0]  Manifest agents. Bind MCPs. Ship code.[/]

[#504d78]  Type [bold #c026d3]help[/bold #c026d3] to see available commands.[/]
[#504d78]  Press [bold #c026d3]Ctrl+N[/bold #c026d3] to manifest a new agent.[/]
[#504d78]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]
"""


# ═══════════════════════════════════════════════════════════════
# Modal Screens
# ═══════════════════════════════════════════════════════════════

class ManifestAgentModal(ModalScreen[Optional[dict]]):
    """Modal to manifest a new agent."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        models = load_models()
        model_options = [(m["name"], m["id"]) for m in models]

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

        agent = {
            "name": name,
            "model": str(model),
            "incantation": prompt,
            "mcps": [],
            "temperature": temp,
            "max_tokens": 4096,
            "status": "dormant",
        }
        self.dismiss(agent)

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class BindMCPModal(ModalScreen[Optional[dict]]):
    """Modal to bind a new MCP server."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Container(id="modal-dialog"):
            yield Static("[bold #c026d3]◬ BIND MCP SERVER ◬[/]", id="modal-title")
            yield Label("[#504d78]MCP NAME[/]", classes="modal-label")
            yield Input(placeholder="e.g. slack, notion, custom-api", id="mcp-name", classes="modal-input")
            yield Label("[#504d78]TRANSPORT TYPE[/]", classes="modal-label")
            yield Select([("stdio", "stdio"), ("SSE", "sse"), ("HTTP", "http")], value="stdio", id="mcp-type", classes="modal-select")
            yield Label("[#504d78]COMMAND / URL[/]", classes="modal-label")
            yield Input(placeholder="npx -y @org/mcp-server", id="mcp-command", classes="modal-input")
            with Horizontal(id="modal-actions"):
                yield Button("◈ BIND", id="btn-create", classes="modal-btn")
                yield Button("✕ CANCEL", id="btn-cancel", classes="modal-btn-cancel")

    @on(Button.Pressed, "#btn-create")
    def on_create(self) -> None:
        name = self.query_one("#mcp-name", Input).value.strip()
        if not name:
            self.app.notify("MCP name is required", severity="error")
            return
        mcp = {
            "id": name.lower().replace(" ", "-"),
            "name": name,
            "type": str(self.query_one("#mcp-type", Select).value),
            "command": self.query_one("#mcp-command", Input).value,
        }
        self.dismiss(mcp)

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_btn(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class AgentDetailModal(ModalScreen[None]):
    """View agent config details."""

    BINDINGS = [Binding("escape", "cancel", "Close")]

    def __init__(self, agent: dict):
        super().__init__()
        self.agent = agent

    def compose(self) -> ComposeResult:
        a = self.agent
        models = load_models()
        model_name = a.get("model", "unknown")
        for m in models:
            if m["id"] == a.get("model"):
                model_name = m["name"]
                break

        mcps_list = ", ".join(a.get("mcps", [])) or "none"
        status_color = {"dormant": "#504d78", "awakened": "#00ff88", "error": "#ff2244"}.get(a.get("status", "dormant"), "#504d78")

        detail = f"""[bold #00fff7]{a['name'].upper()}[/]
[#504d78]{'─' * 40}[/]
[#c026d3]MODEL       [/] [#c8c4e0]{model_name}[/]
[#c026d3]INCANTATION [/] [#c8c4e0]{a.get('incantation', 'N/A')[:60]}[/]
[#c026d3]TEMP        [/] [#c8c4e0]{a.get('temperature', 0.7)}[/]
[#c026d3]TOKENS      [/] [#c8c4e0]{a.get('max_tokens', 4096)}[/]
[#c026d3]MCPs        [/] [#c8c4e0]{mcps_list}[/]
[#c026d3]STATUS      [/] [{status_color}]● {a.get('status', 'dormant').upper()}[/]"""

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
        self.app.run_agent(self.agent)

    @on(Button.Pressed, "#btn-delete")
    def on_delete(self) -> None:
        agents = load_agents()
        agents = [a for a in agents if a["name"] != self.agent["name"]]
        save_agents(agents)
        self.dismiss(None)
        self.app.refresh_agent_tree()
        self.app.log_console(f"[#ff2244]✕ Agent '{self.agent['name']}' banished[/]")
        self.app.log_mind(f"[#ff2244]BANISH[/] {self.agent['name']} removed from registry")

    @on(Button.Pressed, "#btn-cancel")
    def on_close(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ═══════════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════════

class AnimystApp(App):
    """ANIMYST — Breathe Life Into Code."""

    TITLE = "ANIMYST"
    SUB_TITLE = "Agent Development Environment"
    CSS_PATH = "cyberpunk.tcss"

    BINDINGS = [
        Binding("ctrl+n", "manifest_agent", "Manifest", show=True),
        Binding("ctrl+m", "bind_mcp", "Bind MCP", show=True),
        Binding("ctrl+g", "git_status", "Git", show=True),
        Binding("ctrl+r", "refresh", "Refresh", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_console", "Clear", show=True),
    ]

    def compose(self) -> ComposeResult:
        # Header
        with Horizontal(id="header-bar"):
            yield Static(" ◬ ANIMYST", id="logo")
            yield Static("v0.1.0 │ breathe life into code", id="header-status")

        # Main 3-column layout
        with Horizontal(id="main-container"):
            # LEFT — Agent Registry
            with Vertical(id="left-panel"):
                yield Static(" ◬ REGISTRY", id="panel-title-agents")
                yield Tree("animyst", id="agent-tree")
                with Vertical(id="left-actions"):
                    yield Button("⚡ Manifest Agent", id="btn-new-agent", classes="action-btn")
                    yield Button("◈ Bind MCP", id="btn-new-mcp", classes="action-btn")
                    yield Button("⚙ Settings", id="btn-settings", classes="action-btn")

            # CENTER — Console
            with Vertical(id="center-panel"):
                yield Static(" ◬ CONSOLE", id="console-title")
                yield RichLog(highlight=True, markup=True, id="console-log")
                with Horizontal(id="input-bar"):
                    yield Static(" animyst › ", id="prompt-label")
                    yield Input(placeholder="type a command...", id="command-input")

            # RIGHT — Git + Agent Mind
            with Vertical(id="right-panel"):
                # Git panel (top)
                with Vertical(id="git-panel"):
                    yield Static(" ◬ GIT", id="panel-title-git")
                    yield RichLog(highlight=True, markup=True, id="git-log")
                    with Horizontal(id="git-actions"):
                        yield Button("PUSH", id="btn-push", classes="git-btn")
                        yield Button("PR", id="btn-pr", classes="git-btn")
                        yield Button("DIFF", id="btn-diff", classes="git-btn")

                # Agent Mind (bottom)
                with Vertical(id="mind-panel"):
                    yield Static(" ◬ AGENT MIND", id="panel-title-mind")
                    yield RichLog(highlight=True, markup=True, id="mind-log")

        yield Footer()

    def on_mount(self) -> None:
        ensure_animyst_dir()
        console = self.query_one("#console-log", RichLog)
        console.write(Text.from_markup(LOGO))
        console.write(Text.from_markup(WELCOME_MSG))
        self.refresh_agent_tree()
        self.refresh_git_panel()
        self.log_mind(f"[#00fff7]SYS [/] Animyst initialized")
        self.log_mind(f"[#504d78]SYS [/] Config: {ANIMYST_DIR}")
        self.log_mind(f"[#504d78]SYS [/] The ether is listening")
        # Focus on command input
        self.query_one("#command-input", Input).focus()

    # ── Tree Management ──────────────────────────────────────

    def refresh_agent_tree(self) -> None:
        tree = self.query_one("#agent-tree", Tree)
        tree.clear()
        tree.root.expand()

        # Agents section
        agents = load_agents()
        agents_node = tree.root.add("[bold #c026d3]⚡ Agents[/]", expand=True)
        for a in agents:
            status_icon = {"dormant": "[#504d78]●[/]", "awakened": "[#00ff88]●[/]", "error": "[#ff2244]●[/]"}.get(a.get("status", "dormant"), "[#504d78]●[/]")
            agents_node.add_leaf(f"{status_icon} [#c8c4e0]{a['name']}[/]", data={"type": "agent", "name": a["name"]})

        # MCPs section
        mcps = load_mcps()
        mcps_node = tree.root.add("[bold #00fff7]◈ MCPs[/]", expand=True)
        for m in mcps:
            mcps_node.add_leaf(f"[#26244a]▸[/] [#c8c4e0]{m['name']}[/]", data={"type": "mcp", "id": m["id"]})

        # Models section
        models = load_models()
        models_node = tree.root.add("[bold #8b5cf6]▣ Models[/]", expand=True)
        for m in models:
            models_node.add_leaf(f"[#26244a]▸[/] [#c8c4e0]{m['name']}[/]", data={"type": "model", "id": m["id"]})

    # ── Console Logging ──────────────────────────────────────

    def log_console(self, msg: str) -> None:
        console = self.query_one("#console-log", RichLog)
        now = datetime.datetime.now().strftime("%H:%M:%S")
        console.write(Text.from_markup(f"[#26244a]{now}[/] {msg}"))

    def log_mind(self, msg: str) -> None:
        mind = self.query_one("#mind-log", RichLog)
        now = datetime.datetime.now().strftime("%H:%M:%S")
        mind.write(Text.from_markup(f"[#26244a]{now}[/] {msg}"))

    def log_git(self, msg: str) -> None:
        git_log = self.query_one("#git-log", RichLog)
        git_log.write(Text.from_markup(msg))

    # ── Git Panel ────────────────────────────────────────────

    @work(thread=True)
    def refresh_git_panel(self) -> None:
        git_log = self.query_one("#git-log", RichLog)
        git_log.clear()

        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            if branch.returncode == 0:
                branch_name = branch.stdout.strip()
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup(f"[bold #8b5cf6]⎇ {branch_name}[/]")
                )

                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True, text=True, timeout=5
                )
                changed = len([l for l in status.stdout.strip().split("\n") if l.strip()])
                if changed:
                    self.app.call_from_thread(
                        git_log.write,
                        Text.from_markup(f"[#f59e0b]{changed} file(s) changed[/]")
                    )
                else:
                    self.app.call_from_thread(
                        git_log.write,
                        Text.from_markup("[#00ff88]✓ working tree clean[/]")
                    )

                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup(f"\n[#504d78]{'─' * 30}[/]")
                )
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup("[bold #504d78]RECENT COMMITS[/]")
                )

                log = subprocess.run(
                    ["git", "log", "--oneline", "-8", "--pretty=format:%h %s"],
                    capture_output=True, text=True, timeout=5
                )
                if log.returncode == 0:
                    for line in log.stdout.strip().split("\n")[:8]:
                        if line.strip():
                            parts = line.split(" ", 1)
                            sha = parts[0] if parts else ""
                            msg = parts[1] if len(parts) > 1 else ""
                            self.app.call_from_thread(
                                git_log.write,
                                Text.from_markup(f"[#8b5cf6]{sha}[/] [#c8c4e0]{msg[:28]}[/]")
                            )
            else:
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup("[#504d78]Not a git repository[/]")
                )
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup("[#504d78]Run [bold #00fff7]git init[/bold #00fff7] to start[/]")
                )
        except Exception as e:
            self.app.call_from_thread(
                git_log.write,
                Text.from_markup(f"[#ff2244]Git error: {e}[/]")
            )

    # ── Agent Execution ──────────────────────────────────────

    def run_agent(self, agent: dict) -> None:
        name = agent["name"]
        model = agent.get("model", "unknown")
        self.log_console(f"[bold #00ff88]▶ MANIFESTING[/] [#00fff7]{name}[/] [#504d78]on {model}[/]")
        self.log_mind(f"[#00ff88]AWAKEN[/] {name} channeling will")
        self.log_mind(f"[#504d78]       [/] model: {model}")

        # Update agent status
        agents = load_agents()
        for a in agents:
            if a["name"] == name:
                a["status"] = "awakened"
        save_agents(agents)
        self.refresh_agent_tree()

        # Simulate agent work
        self.simulate_agent(agent)

    @work(thread=True)
    def simulate_agent(self, agent: dict) -> None:
        """Simulate agent activity for demo purposes."""
        import time
        name = agent["name"]
        steps = [
            f"[#00fff7]{name}[/] [#504d78]Channeling will...[/]",
            f"[#00fff7]{name}[/] [#504d78]Loading incantation ({len(agent.get('incantation', ''))} chars)[/]",
            f"[#00fff7]{name}[/] [#504d78]Binding to model endpoint...[/]",
            f"[#00fff7]{name}[/] [#00ff88]⚡ Awakened — streaming response[/]",
        ]
        for step in steps:
            time.sleep(0.5)
            self.app.call_from_thread(self.log_console, step)

        # Mark dormant
        time.sleep(0.5)
        agents = load_agents()
        for a in agents:
            if a["name"] == name:
                a["status"] = "dormant"
        save_agents(agents)
        self.app.call_from_thread(self.refresh_agent_tree)
        self.app.call_from_thread(
            self.log_mind,
            f"[#f59e0b]DONE[/] {name} returned to dormancy"
        )

    # ── Command Processing ───────────────────────────────────

    @on(Input.Submitted, "#command-input")
    def on_command(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return

        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""

        self.log_console(f"[bold #c026d3]◬[/] [#00fff7]{escape(cmd)}[/]")

        parts = cmd.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "help":
            self.cmd_help()
        elif command in ("agents", "ls"):
            self.cmd_list_agents()
        elif command == "mcps":
            self.cmd_list_mcps()
        elif command == "models":
            self.cmd_list_models()
        elif command in ("run", "manifest", "awaken") and args:
            self.cmd_run_agent(args[0])
        elif command in ("new", "manifest"):
            if args and args[0] == "mcp":
                self.action_bind_mcp()
            else:
                self.action_manifest_agent()
        elif command in ("bind",) and args:
            self.action_bind_mcp()
        elif command == "inspect" and args:
            self.cmd_inspect(args[0])
        elif command in ("delete", "banish") and args:
            self.cmd_delete_agent(args[0])
        elif command == "export" and args:
            self.cmd_export(args[0])
        elif command == "clear":
            self.action_clear_console()
        elif command == "git" and args:
            self.cmd_git(args)
        elif command == "status":
            self.cmd_status()
        elif command == "ascii":
            console = self.query_one("#console-log", RichLog)
            console.write(Text.from_markup(LOGO))
        else:
            self.log_console(f"[#ff2244]Unknown command:[/] [#c8c4e0]{escape(cmd)}[/]")
            self.log_console(f"[#504d78]Type [bold #c026d3]help[/bold #c026d3] for available commands[/]")

    def cmd_help(self) -> None:
        help_text = f"""
[bold #c026d3]◬ ANIMYST COMMANDS ◬[/]
[#504d78]{'─' * 44}[/]
[bold #00fff7]agents[/]         [#c8c4e0]List all configured agents[/]
[bold #00fff7]mcps[/]           [#c8c4e0]List all MCP servers[/]
[bold #00fff7]models[/]         [#c8c4e0]List available models[/]
[bold #00fff7]manifest[/]       [#c8c4e0]Manifest a new agent[/]
[bold #00fff7]bind mcp[/]       [#c8c4e0]Bind a new MCP server[/]
[bold #00fff7]awaken <n>[/]   [#c8c4e0]Awaken an agent[/]
[bold #00fff7]inspect <n>[/]  [#c8c4e0]View agent configuration[/]
[bold #00fff7]banish <n>[/]   [#c8c4e0]Banish an agent[/]
[bold #00fff7]export <n>[/]   [#c8c4e0]Export agent config as JSON[/]
[bold #00fff7]git <cmd>[/]      [#c8c4e0]Run git commands[/]
[bold #00fff7]status[/]         [#c8c4e0]System status overview[/]
[bold #00fff7]clear[/]          [#c8c4e0]Clear console[/]
[bold #00fff7]ascii[/]          [#c8c4e0]Show animyst logo[/]
[#504d78]{'─' * 44}[/]
[#504d78]Shortcuts: Ctrl+N manifest │ Ctrl+M bind mcp[/]
[#504d78]           Ctrl+G git      │ Ctrl+L clear[/]"""
        self.log_console(help_text)

    def cmd_list_agents(self) -> None:
        agents = load_agents()
        if not agents:
            self.log_console("[#504d78]No agents manifested. Create one with [bold #c026d3]manifest[/bold #c026d3][/]")
            return
        self.log_console("[bold #c026d3]◬ AGENTS[/]")
        for a in agents:
            status_icon = {"dormant": "[#504d78]●[/]", "awakened": "[#00ff88]●[/]", "error": "[#ff2244]●[/]"}.get(a.get("status", "dormant"), "[#504d78]●[/]")
            model_short = a.get("model", "?")[:20]
            self.log_console(f"  {status_icon} [bold #00fff7]{a['name']:<16}[/] [#504d78]{model_short}[/]")

    def cmd_list_mcps(self) -> None:
        mcps = load_mcps()
        self.log_console("[bold #00fff7]◈ BOUND MCP SERVERS[/]")
        for m in mcps:
            self.log_console(f"  [#26244a]▸[/] [bold #c8c4e0]{m['name']:<16}[/] [#504d78]{m.get('type', 'stdio')}[/]")

    def cmd_list_models(self) -> None:
        models = load_models()
        self.log_console("[bold #8b5cf6]▣ MODELS[/]")
        for m in models:
            self.log_console(f"  [#26244a]▸[/] [bold #c8c4e0]{m['name']:<24}[/] [#504d78]{m.get('provider', '?')}[/]")

    def cmd_run_agent(self, name: str) -> None:
        agents = load_agents()
        agent = next((a for a in agents if a["name"].lower() == name.lower()), None)
        if agent:
            self.run_agent(agent)
        else:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")

    def cmd_inspect(self, name: str) -> None:
        agents = load_agents()
        agent = next((a for a in agents if a["name"].lower() == name.lower()), None)
        if agent:
            self.push_screen(AgentDetailModal(agent))
        else:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")

    def cmd_delete_agent(self, name: str) -> None:
        agents = load_agents()
        original_len = len(agents)
        agents = [a for a in agents if a["name"].lower() != name.lower()]
        if len(agents) < original_len:
            save_agents(agents)
            self.refresh_agent_tree()
            self.log_console(f"[#ff2244]✕ Agent '{escape(name)}' banished[/]")
            self.log_mind(f"[#ff2244]BANISH[/] {name} removed")
        else:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")

    def cmd_export(self, name: str) -> None:
        agents = load_agents()
        agent = next((a for a in agents if a["name"].lower() == name.lower()), None)
        if agent:
            export_path = Path.cwd() / f"{agent['name']}_agent.json"
            export_path.write_text(json.dumps(agent, indent=2))
            self.log_console(f"[#00ff88]✓ Exported to {export_path}[/]")
            self.log_mind(f"[#00ff88]EXPORT[/] {name} → {export_path.name}")
        else:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")

    @work(thread=True)
    def cmd_git(self, args: list[str]) -> None:
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True, text=True, timeout=15
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                for line in output.split("\n"):
                    self.app.call_from_thread(
                        self.log_console,
                        f"[#c8c4e0]{escape(line)}[/]"
                    )
            self.app.call_from_thread(self.refresh_git_panel)
        except Exception as e:
            self.app.call_from_thread(
                self.log_console,
                f"[#ff2244]Git error: {e}[/]"
            )

    def cmd_status(self) -> None:
        agents = load_agents()
        mcps = load_mcps()
        models = load_models()
        awakened = sum(1 for a in agents if a.get("status") == "awakened")
        self.log_console(f"""
[bold #c026d3]◬ ANIMYST STATUS ◬[/]
[#504d78]{'─' * 30}[/]
[#00fff7]Agents:[/]  [#c8c4e0]{len(agents)} manifested, {awakened} awakened[/]
[#00fff7]MCPs:[/]    [#c8c4e0]{len(mcps)} bound[/]
[#00fff7]Models:[/]  [#c8c4e0]{len(models)} available[/]
[#00fff7]Config:[/]  [#c8c4e0]{ANIMYST_DIR}[/]
""")

    # ── Actions ──────────────────────────────────────────────

    def action_manifest_agent(self) -> None:
        def on_result(result: Optional[dict]) -> None:
            if result:
                agents = load_agents()
                if any(a["name"].lower() == result["name"].lower() for a in agents):
                    self.log_console(f"[#ff2244]Agent '{result['name']}' already exists[/]")
                    return
                agents.append(result)
                save_agents(agents)
                self.refresh_agent_tree()
                self.log_console(f"[#00ff88]⚡ Agent '{result['name']}' manifested[/]")
                self.log_mind(f"[#00ff88]MANIFEST[/] {result['name']}")
                self.log_mind(f"[#504d78]         [/] model: {result['model'][:30]}")

        self.push_screen(ManifestAgentModal(), callback=on_result)

    def action_bind_mcp(self) -> None:
        def on_result(result: Optional[dict]) -> None:
            if result:
                mcps = load_mcps()
                if any(m["id"] == result["id"] for m in mcps):
                    self.log_console(f"[#ff2244]MCP '{result['name']}' already bound[/]")
                    return
                mcps.append(result)
                save_mcps(mcps)
                self.refresh_agent_tree()
                self.log_console(f"[#00ff88]◈ MCP '{result['name']}' bound[/]")
                self.log_mind(f"[#00ff88]BIND[/] MCP: {result['name']}")

        self.push_screen(BindMCPModal(), callback=on_result)

    def action_git_status(self) -> None:
        self.cmd_git(["status", "--short"])
        self.refresh_git_panel()

    def action_refresh(self) -> None:
        self.refresh_agent_tree()
        self.refresh_git_panel()
        self.log_console("[#00fff7]↻ Refreshed[/]")

    def action_clear_console(self) -> None:
        console = self.query_one("#console-log", RichLog)
        console.clear()
        self.log_console("[#504d78]Console cleared[/]")

    # ── Event Handlers ───────────────────────────────────────

    @on(Button.Pressed, "#btn-new-agent")
    def on_new_agent_btn(self) -> None:
        self.action_manifest_agent()

    @on(Button.Pressed, "#btn-new-mcp")
    def on_new_mcp_btn(self) -> None:
        self.action_bind_mcp()

    @on(Button.Pressed, "#btn-settings")
    def on_settings_btn(self) -> None:
        self.log_console(f"[#504d78]Config directory: {ANIMYST_DIR}[/]")
        self.cmd_status()

    @on(Button.Pressed, "#btn-push")
    def on_push_btn(self) -> None:
        self.cmd_git(["push"])
        self.log_mind("[#8b5cf6]GIT [/] Push initiated")

    @on(Button.Pressed, "#btn-pr")
    def on_pr_btn(self) -> None:
        self.log_console("[#8b5cf6]Creating PR...[/]")
        self.cmd_git(["log", "--oneline", "-1"])
        self.log_mind("[#8b5cf6]GIT [/] PR creation requested")

    @on(Button.Pressed, "#btn-diff")
    def on_diff_btn(self) -> None:
        self.cmd_git(["diff", "--stat"])

    @on(Tree.NodeSelected, "#agent-tree")
    def on_tree_select(self, event: Tree.NodeSelected) -> None:
        node = event.node
        if node.data and isinstance(node.data, dict):
            if node.data.get("type") == "agent":
                agents = load_agents()
                agent = next(
                    (a for a in agents if a["name"] == node.data["name"]),
                    None,
                )
                if agent:
                    self.push_screen(AgentDetailModal(agent))
            elif node.data.get("type") == "mcp":
                mcps = load_mcps()
                mcp = next(
                    (m for m in mcps if m["id"] == node.data["id"]),
                    None,
                )
                if mcp:
                    self.log_console(
                        f"[bold #00fff7]◈ MCP: {mcp['name']}[/]\n"
                        f"  [#c026d3]Type:[/]    [#c8c4e0]{mcp.get('type', 'stdio')}[/]\n"
                        f"  [#c026d3]Command:[/] [#c8c4e0]{mcp.get('command', 'N/A')}[/]"
                    )


def main():
    """Entry point for animyst CLI."""
    app = AnimystApp()
    app.run()


if __name__ == "__main__":
    main()
