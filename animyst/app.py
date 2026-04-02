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

import datetime
import subprocess
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input, RichLog, Static, Tree

from animyst.commands import CommandDispatcher
from animyst.domain import ConversationSession
from animyst.llm import stream_chat
from animyst.services import AgentService, ChatService
from animyst.storage import (
    ANIMYST_DIR,
    AgentRepository,
    HistoryRepository,
    McpRepository,
    ModelRepository,
    SettingsRepository,
    ensure_animyst_dir,
)
from animyst.ui import (
    AgentDetailModal,
    LOGO,
    ManifestAgentModal,
    SettingsModal,
    WELCOME_MSG,
    chat_help_text,
    format_history_summary,
    format_mcp_detail,
    format_status,
    help_text,
    status_icon,
)


class AnimystApp(App):
    """ANIMYST — Breathe Life Into Code."""

    TITLE = "ANIMYST"
    SUB_TITLE = "Agent Development Environment"
    CSS_PATH = "cyberpunk.tcss"

    BINDINGS = [
        Binding("ctrl+n", "manifest_agent", "Manifest", show=True),
        Binding("ctrl+g", "git_status", "Git", show=True),
        Binding("ctrl+r", "refresh", "Refresh", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear_console", "Clear", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.agent_repository = AgentRepository()
        self.mcp_repository = McpRepository()
        self.model_repository = ModelRepository()
        self.settings_repository = SettingsRepository()
        self.history_repository = HistoryRepository()
        self.agent_service = AgentService(self.agent_repository, self.history_repository)
        self.chat_service = ChatService(self.history_repository, self.model_repository)
        self.command_dispatcher = CommandDispatcher()
        self.active_agent: dict | None = None
        self.active_session: ConversationSession | None = None
        self.is_streaming = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Static(" ◬ ANIMYST", id="logo")
            yield Static("v0.1.0 │ breathe life into code", id="header-status")

        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Static(" ◬ REGISTRY", id="panel-title-agents")
                yield Tree("animyst", id="agent-tree")
                with Vertical(id="left-actions"):
                    yield Button("⚡ Manifest Agent", id="btn-new-agent", classes="action-btn")
                    yield Button("◈ Bind MCP (soon)", id="btn-new-mcp", classes="action-btn", disabled=True)
                    yield Button("⚙ Settings", id="btn-settings", classes="action-btn")

            with Vertical(id="center-panel"):
                yield Static(" ◬ CONSOLE", id="console-title")
                yield RichLog(highlight=True, markup=True, id="console-log")
                with Horizontal(id="input-bar"):
                    yield Static(" animyst › ", id="prompt-label")
                    yield Input(placeholder="type a command...", id="command-input")

            with Vertical(id="right-panel"):
                with Vertical(id="git-panel"):
                    yield Static(" ◬ GIT", id="panel-title-git")
                    yield RichLog(highlight=True, markup=True, id="git-log")
                    with Horizontal(id="git-actions"):
                        yield Button("PUSH", id="btn-push", classes="git-btn")
                        yield Button("PR", id="btn-pr", classes="git-btn")
                        yield Button("DIFF", id="btn-diff", classes="git-btn")

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
        self.log_mind("[#00fff7]SYS [/] Animyst initialized")
        self.log_mind(f"[#504d78]SYS [/] Config: {ANIMYST_DIR}")
        self.log_mind("[#504d78]SYS [/] The ether is listening")
        self.query_one("#command-input", Input).focus()

    def refresh_agent_tree(self) -> None:
        tree = self.query_one("#agent-tree", Tree)
        tree.clear()
        tree.root.expand()

        agents_node = tree.root.add("[bold #c026d3]⚡ Agents[/]", expand=True)
        for agent in self.agent_service.list_agents():
            agents_node.add_leaf(
                f"{status_icon(agent.get('status', 'dormant'))} [#c8c4e0]{agent['name']}[/]",
                data={"type": "agent", "name": agent["name"]},
            )

        mcps_node = tree.root.add("[bold #00fff7]◈ MCPs[/]", expand=True)
        for mcp in self.mcp_repository.list_mcps():
            mcps_node.add_leaf(
                f"[#26244a]▸[/] [#c8c4e0]{mcp['name']}[/]",
                data={"type": "mcp", "id": mcp["id"]},
            )

        models_node = tree.root.add("[bold #8b5cf6]▣ Models[/]", expand=True)
        for model in self.model_repository.list_models():
            models_node.add_leaf(
                f"[#26244a]▸[/] [#c8c4e0]{model['name']}[/]",
                data={"type": "model", "id": model["id"]},
            )

    def log_console(self, msg: str) -> None:
        console = self.query_one("#console-log", RichLog)
        now = datetime.datetime.now().strftime("%H:%M:%S")
        console.write(Text.from_markup(f"[#26244a]{now}[/] {msg}"))

    def log_mind(self, msg: str) -> None:
        mind = self.query_one("#mind-log", RichLog)
        now = datetime.datetime.now().strftime("%H:%M:%S")
        mind.write(Text.from_markup(f"[#26244a]{now}[/] {msg}"))

    @work(thread=True)
    def refresh_git_panel(self) -> None:
        git_log = self.query_one("#git-log", RichLog)
        git_log.clear()

        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if branch.returncode != 0:
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup("[#504d78]Not a git repository[/]"),
                )
                self.app.call_from_thread(
                    git_log.write,
                    Text.from_markup("[#504d78]Run [bold #00fff7]git init[/bold #00fff7] to start[/]"),
                )
                return

            branch_name = branch.stdout.strip()
            self.app.call_from_thread(
                git_log.write,
                Text.from_markup(f"[bold #8b5cf6]⎇ {branch_name}[/]"),
            )

            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            changed = len([line for line in status.stdout.strip().split("\n") if line.strip()])
            status_text = "[#00ff88]✓ working tree clean[/]" if not changed else f"[#f59e0b]{changed} file(s) changed[/]"
            self.app.call_from_thread(git_log.write, Text.from_markup(status_text))
            self.app.call_from_thread(git_log.write, Text.from_markup("\n[#504d78]──────────────────────────────[/]"))
            self.app.call_from_thread(git_log.write, Text.from_markup("[bold #504d78]RECENT COMMITS[/]"))

            log = subprocess.run(
                ["git", "log", "--oneline", "-8", "--pretty=format:%h %s"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if log.returncode == 0:
                for line in log.stdout.strip().split("\n")[:8]:
                    if not line.strip():
                        continue
                    sha, _, message = line.partition(" ")
                    self.app.call_from_thread(
                        git_log.write,
                        Text.from_markup(f"[#8b5cf6]{sha}[/] [#c8c4e0]{message[:28]}[/]"),
                    )
        except Exception as error:
            self.app.call_from_thread(
                git_log.write,
                Text.from_markup(f"[#ff2244]Git error: {escape(str(error))}[/]"),
            )

    def run_agent(self, agent: dict) -> None:
        name = agent["name"]
        model = agent.get("model", "unknown")
        self.agent_service.set_status(name, "awakened")
        self.refresh_agent_tree()
        self.active_agent = agent
        self.active_session, resumed = self.chat_service.start_session(name)
        self.is_streaming = False

        self.log_console(f"[bold #00ff88]▶ AWAKENING[/] [#00fff7]{name}[/] [#504d78]on {model}[/]")
        self.log_console("[#504d78]Chat mode active. Type messages to converse.[/]")
        self.log_console("[#504d78]Use [bold #c026d3]/sleep[/bold #c026d3] to exit chat, [bold #c026d3]/help[/bold #c026d3] for commands.[/]")
        if resumed and self.active_session.message_count:
            self.log_console(
                f"[#00fff7]Resumed history:[/] [#c8c4e0]{self.active_session.turn_count} turn(s), "
                f"{self.active_session.message_count} message(s)[/]"
            )
        self.log_mind(f"[#00ff88]AWAKEN[/] {name} channeling will")
        self.log_mind(f"[#504d78]       [/] model: {model}")

        prompt_label = self.query_one("#prompt-label", Static)
        prompt_label.update(f" {name} › ")
        command_input = self.query_one("#command-input", Input)
        command_input.placeholder = "send a message..."

    def send_chat_message(self, msg: str) -> None:
        if not self.active_agent or not self.active_session:
            return
        self.active_session = self.chat_service.append_user_message(self.active_session, msg)
        self.log_console(f"[bold #00fff7]YOU ›[/] [#c8c4e0]{escape(msg)}[/]")
        self.is_streaming = True
        self.stream_agent_response()

    @work(thread=True)
    def stream_agent_response(self) -> None:
        import time

        if not self.active_agent or not self.active_session:
            self.is_streaming = False
            return

        agent = self.active_agent
        session = self.active_session
        name = agent["name"]
        model_id = agent.get("model", "claude-sonnet-4-5-20250929")
        provider = self.chat_service.resolve_provider(model_id)
        console = self.query_one("#console-log", RichLog)
        full_response = ""
        line_buffer = ""
        last_flush = time.monotonic()

        self.app.call_from_thread(
            self.log_mind,
            f"[#00fff7]STREAM[/] {name} → {provider}/{model_id[:30]}",
        )
        self.app.call_from_thread(
            console.write,
            Text.from_markup(f"[bold #c026d3]{name} ›[/] "),
        )

        for event in stream_chat(
            messages=session.to_llm_messages(),
            model=model_id,
            provider=provider,
            system=agent.get("incantation", "You are a helpful assistant."),
            temperature=agent.get("temperature", 0.7),
            max_tokens=agent.get("max_tokens", 4096),
        ):
            if event.type == "text":
                full_response += event.content
                line_buffer += event.content
                now = time.monotonic()

                if "\n" in line_buffer:
                    lines = line_buffer.split("\n")
                    for line in lines[:-1]:
                        self.app.call_from_thread(
                            console.write,
                            Text.from_markup(f"[#c8c4e0]{escape(line)}[/]"),
                        )
                    line_buffer = lines[-1]
                    last_flush = now
                elif now - last_flush > 0.08 and line_buffer:
                    self.app.call_from_thread(
                        console.write,
                        Text.from_markup(f"[#c8c4e0]{escape(line_buffer)}[/]"),
                    )
                    line_buffer = ""
                    last_flush = now

            elif event.type == "error":
                self.agent_service.set_status(name, "error")
                self.app.call_from_thread(self.refresh_agent_tree)
                self.app.call_from_thread(
                    self.log_console,
                    f"[#ff2244]ERROR:[/] [#c8c4e0]{escape(event.content)}[/]",
                )
                self.app.call_from_thread(
                    self.log_mind,
                    f"[#ff2244]ERROR[/] {escape(event.content[:60])}",
                )
                self.is_streaming = False
                return

            elif event.type == "done":
                if line_buffer:
                    self.app.call_from_thread(
                        console.write,
                        Text.from_markup(f"[#c8c4e0]{escape(line_buffer)}[/]"),
                    )

                if full_response:
                    self.active_session = self.chat_service.complete_assistant_message(
                        session,
                        full_response,
                        event.usage,
                    )
                elif event.usage:
                    self.active_session = self.chat_service.record_usage(session, event.usage)

                if event.usage:
                    inp = event.usage.get("input_tokens", 0)
                    out = event.usage.get("output_tokens", 0)
                    self.app.call_from_thread(
                        self.log_mind,
                        f"[#f59e0b]USAGE[/] ↑{inp} ↓{out} tokens",
                    )

                turns = self.active_session.turn_count if self.active_session else session.turn_count
                self.app.call_from_thread(
                    self.log_mind,
                    f"[#00ff88]DONE[/] {name} response complete ({turns} turns)",
                )

        self.is_streaming = False

    def exit_chat_mode(self) -> None:
        if not self.active_agent:
            return

        name = self.active_agent["name"]
        turns = self.active_session.turn_count if self.active_session else 0
        self.agent_service.set_status(name, "dormant")
        self.refresh_agent_tree()

        if self.active_session:
            self.chat_service.end_session(self.active_session)

        self.active_agent = None
        self.active_session = None
        self.is_streaming = False

        prompt_label = self.query_one("#prompt-label", Static)
        prompt_label.update(" animyst › ")
        command_input = self.query_one("#command-input", Input)
        command_input.placeholder = "type a command..."

        self.log_console(f"[#504d78]{name} returned to dormancy ({turns} turns)[/]")
        self.log_mind(f"[#f59e0b]SLEEP[/] {name} → dormant ({turns} turns)")

    @on(Input.Submitted, "#command-input")
    def on_command(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return

        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""

        if self.is_streaming:
            self.notify("Agent is still responding...", severity="warning")
            return

        if self.active_agent:
            if cmd.startswith("/"):
                raw = cmd[1:].strip()
                subcmd = raw.split()[0].lower() if raw.split() else ""

                if subcmd == "sleep":
                    self.exit_chat_mode()
                elif subcmd == "history":
                    summary = self.agent_service.history_summary(self.active_agent["name"])
                    self.log_console(format_history_summary(summary))
                elif subcmd == "clear":
                    self.action_clear_console()
                elif subcmd == "help":
                    self.cmd_chat_help()
                else:
                    self.log_console(f"[bold #c026d3]◬[/] [#00fff7]{escape(raw)}[/]")
                    self._process_command(raw)
                return

            self.send_chat_message(cmd)
            return

        self.log_console(f"[bold #c026d3]◬[/] [#00fff7]{escape(cmd)}[/]")
        self._process_command(cmd)

    def _process_command(self, cmd: str) -> None:
        action = self.command_dispatcher.dispatch(cmd)

        if action.kind == "noop":
            return
        if action.kind == "help":
            self.cmd_help()
        elif action.kind == "list_agents":
            self.cmd_list_agents()
        elif action.kind == "list_mcps":
            self.cmd_list_mcps()
        elif action.kind == "list_models":
            self.cmd_list_models()
        elif action.kind == "run_agent":
            self.cmd_run_agent(action.args[0])
        elif action.kind == "manifest_agent":
            self.action_manifest_agent()
        elif action.kind == "bind_mcp_info":
            self.log_console("[#f59e0b]◈ MCP binding coming in v0.2[/]")
        elif action.kind == "inspect_agent":
            self.cmd_inspect(action.args[0])
        elif action.kind == "delete_agent":
            self.cmd_delete_agent(action.args[0])
        elif action.kind == "export_agent":
            self.cmd_export(action.args[0])
        elif action.kind == "clear_console":
            self.action_clear_console()
        elif action.kind == "git":
            self.cmd_git(action.args)
        elif action.kind == "status":
            self.cmd_status()
        elif action.kind == "ascii":
            self.query_one("#console-log", RichLog).write(Text.from_markup(LOGO))
        else:
            command_name = action.payload.get("command", cmd)
            self.log_console(f"[#ff2244]Unknown command:[/] [#c8c4e0]{escape(command_name)}[/]")
            self.log_console("[#504d78]Type [bold #c026d3]help[/bold #c026d3] for available commands[/]")

    def cmd_help(self) -> None:
        self.log_console(help_text())

    def cmd_chat_help(self) -> None:
        self.log_console(chat_help_text())

    def cmd_list_agents(self) -> None:
        agents = self.agent_service.list_agents()
        if not agents:
            self.log_console("[#504d78]No agents manifested. Create one with [bold #c026d3]manifest[/bold #c026d3][/]")
            return
        self.log_console("[bold #c026d3]◬ AGENTS[/]")
        for agent in agents:
            self.log_console(
                f"  {status_icon(agent.get('status', 'dormant'))} "
                f"[bold #00fff7]{agent['name']:<16}[/] [#504d78]{agent.get('model', '?')[:20]}[/]"
            )

    def cmd_list_mcps(self) -> None:
        self.log_console("[bold #00fff7]◈ BOUND MCP SERVERS[/]")
        for mcp in self.mcp_repository.list_mcps():
            self.log_console(
                f"  [#26244a]▸[/] [bold #c8c4e0]{mcp['name']:<16}[/] [#504d78]{mcp.get('type', 'stdio')}[/]"
            )

    def cmd_list_models(self) -> None:
        self.log_console("[bold #8b5cf6]▣ MODELS[/]")
        for model in self.model_repository.list_models():
            self.log_console(
                f"  [#26244a]▸[/] [bold #c8c4e0]{model['name']:<24}[/] [#504d78]{model.get('provider', '?')}[/]"
            )

    def cmd_run_agent(self, name: str) -> None:
        agent = self.agent_service.get_agent(name)
        if not agent:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")
            return
        self.run_agent(agent)

    def _history_line_for_agent(self, agent_name: str) -> str:
        summary = self.agent_service.history_summary(agent_name)
        if not summary.session_count:
            return "[#504d78]none[/]"
        updated = summary.last_updated or "unknown"
        return (
            f"[#c8c4e0]{summary.turn_count} turns across {summary.session_count} session(s)[/] "
            f"[#504d78]updated {escape(updated)}[/]"
        )

    def cmd_inspect(self, name: str) -> None:
        agent = self.agent_service.get_agent(name)
        if not agent:
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")
            return
        self.push_screen(
            AgentDetailModal(
                agent=agent,
                model_repository=self.model_repository,
                history_line=self._history_line_for_agent(agent["name"]),
                on_delete=self.cmd_delete_agent,
                on_awaken=self.run_agent,
            )
        )

    def cmd_delete_agent(self, name: str) -> None:
        if not self.agent_service.delete_agent(name):
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")
            return
        self.refresh_agent_tree()
        self.log_console(f"[#ff2244]✕ Agent '{escape(name)}' banished[/]")
        self.log_mind(f"[#ff2244]BANISH[/] {name} removed")

    def cmd_export(self, name: str) -> None:
        export_path = Path.cwd() / f"{name}_agent.json"
        if not self.agent_service.export_agent(name, export_path):
            self.log_console(f"[#ff2244]Agent '{escape(name)}' not found[/]")
            return
        self.log_console(f"[#00ff88]✓ Exported to {export_path}[/]")
        self.log_mind(f"[#00ff88]EXPORT[/] {name} → {export_path.name}")

    @work(thread=True)
    def cmd_git(self, args: list[str]) -> None:
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=15,
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                for line in output.split("\n"):
                    self.app.call_from_thread(
                        self.log_console,
                        f"[#c8c4e0]{escape(line)}[/]",
                    )
            self.app.call_from_thread(self.refresh_git_panel)
        except Exception as error:
            self.app.call_from_thread(
                self.log_console,
                f"[#ff2244]Git error: {escape(str(error))}[/]",
            )

    def cmd_status(self) -> None:
        agents = self.agent_service.list_agents()
        awakened = sum(1 for agent in agents if agent.get("status") == "awakened")
        self.log_console(
            format_status(
                agent_count=len(agents),
                awakened_count=awakened,
                mcp_count=len(self.mcp_repository.list_mcps()),
                model_count=len(self.model_repository.list_models()),
                config_path=str(ANIMYST_DIR),
            )
        )

    def action_manifest_agent(self) -> None:
        def on_result(result: dict | None) -> None:
            if not result:
                return
            if not self.agent_service.create_agent(result):
                self.log_console(f"[#ff2244]Agent '{result['name']}' already exists[/]")
                return
            self.refresh_agent_tree()
            self.log_console(f"[#00ff88]⚡ Agent '{result['name']}' manifested[/]")
            self.log_mind(f"[#00ff88]MANIFEST[/] {result['name']}")
            self.log_mind(f"[#504d78]         [/] model: {result['model'][:30]}")

        self.push_screen(ManifestAgentModal(self.model_repository), callback=on_result)

    def action_bind_mcp(self) -> None:
        self.notify("MCP binding coming in v0.2", severity="information")

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

    @on(Button.Pressed, "#btn-new-agent")
    def on_new_agent_btn(self) -> None:
        self.action_manifest_agent()

    @on(Button.Pressed, "#btn-new-mcp")
    def on_new_mcp_btn(self) -> None:
        self.notify("MCP binding coming in v0.2", severity="information")

    @on(Button.Pressed, "#btn-settings")
    def on_settings_btn(self) -> None:
        self.push_screen(SettingsModal(self.settings_repository))

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
        if not node.data or not isinstance(node.data, dict):
            return

        if node.data.get("type") == "agent":
            self.cmd_inspect(node.data["name"])
        elif node.data.get("type") == "mcp":
            mcp = next(
                (item for item in self.mcp_repository.list_mcps() if item["id"] == node.data["id"]),
                None,
            )
            if mcp:
                self.log_console(format_mcp_detail(mcp))


def main() -> None:
    """Entry point for animyst CLI."""
    app = AnimystApp()
    app.run()


if __name__ == "__main__":
    main()
