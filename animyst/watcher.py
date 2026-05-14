"""Textual tracker for ANIMYST rites — `animyst watch`."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Static

from animyst.rites import list_rites, rite_state


class WatcherApp(App):
    CSS = """
    Screen { background: #06050c; color: #c8c4e0; }
    Header { background: #0a091a; color: #c026d3; }
    Footer { background: #0a091a; color: #504d78; }
    .panel { border: solid #1a1738; padding: 1; margin: 0 1; }
    .heading { color: #c026d3; text-style: bold; margin-bottom: 1; }
    .oracle { color: #c8c4e0; padding: 1; }
    .alive { color: #00ff88; }
    .dormant { color: #504d78; }
    .blocked { color: #f59e0b; }
    DataTable { background: #0a091a; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    TITLE = "◬ ANIMYST"
    SUB_TITLE = "rite tracker"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(classes="panel"):
                yield Static("◬ RITES", classes="heading")
                yield DataTable(id="rites_table", cursor_type="row", zebra_stripes=True)
            with Vertical(classes="panel"):
                yield Static("ORACLE", classes="heading")
                yield Static(id="oracle_text", classes="oracle")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#rites_table", DataTable)
        table.add_columns("slug", "status", "phase", "current task", "elapsed")
        self.set_interval(2.0, self.refresh_data)
        self.refresh_data()

    def action_refresh(self) -> None:
        self.refresh_data()

    def _format_status(self, state: dict) -> str:
        s = state.get("status", "?")
        if state.get("session_alive"):
            return f"⊙ {s}"
        if s == "dormant":
            return f"⊘ {s}"
        if s == "blocked":
            return f"⚠ {s}"
        return f"○ {s}"

    def _elapsed(self, started_iso) -> str:
        if not started_iso:
            return "?"
        from datetime import datetime, timezone

        try:
            started = datetime.fromisoformat(str(started_iso).replace("Z", "+00:00"))
        except ValueError:
            return "?"
        delta = datetime.now(timezone.utc) - started
        s = int(delta.total_seconds())
        if s < 90:
            return f"{s}s"
        m = s // 60
        if m < 90:
            return f"{m}m"
        return f"{m // 60}h{m % 60:02d}"

    def refresh_data(self) -> None:
        table = self.query_one("#rites_table", DataTable)
        oracle = self.query_one("#oracle_text", Static)

        rites = list_rites()
        if not rites:
            table.clear()
            oracle.update(
                'No rites yet.\n\nRun `animyst summon "<description>"`'
                " in a terminal to start your first rite."
            )
            return

        table.clear()
        for r in rites:
            s = rite_state(r["slug"]) or {}
            table.add_row(
                r["slug"],
                self._format_status(s),
                f"{s.get('phase', '?')}/{s.get('total_phases_estimate') or '?'}",
                (s.get("current_task") or "")[:50],
                self._elapsed(s.get("started_at")),
            )

        # Oracle = focused rite's narrative
        focused_idx = table.cursor_row if table.cursor_row is not None else 0
        if 0 <= focused_idx < len(rites):
            focused = rites[focused_idx]
            self._render_oracle(oracle, focused)

    def _render_oracle(self, oracle: Static, rite: dict) -> None:
        from pathlib import Path

        s = rite_state(rite["slug"]) or {}
        path = Path(rite["path"])
        wc = path / "WHAT_CHANGED.md"
        last_section = ""
        if wc.exists():
            try:
                content = wc.read_text()
                # Last "##" section
                parts = content.split("\n## ")
                if len(parts) > 1:
                    last_section = "## " + parts[-1].strip()
                else:
                    last_section = content.strip()[:600]
            except OSError:
                pass

        lines = [
            f"[bold #c026d3]{rite['slug']}[/]",
            f"[#504d78]{rite['path']}[/]",
            "",
            f"Status:  {self._format_status(s)}",
            f"Phase:   {s.get('phase', '?')}/{s.get('total_phases_estimate') or '?'}",
            f"Task:    {s.get('current_task') or ''}",
            f"Last:    {s.get('last_commit') or '(no commits)'}",
            f"Commits: {s.get('commit_count', 0)}",
        ]
        if s.get("blocker"):
            lines.append(f"[#f59e0b]Blocker: {s['blocker']}[/]")
        if last_section:
            lines.append("")
            lines.append("[#c026d3]Latest narrative:[/]")
            lines.append(last_section[:800])
        oracle.update("\n".join(lines))


def run_watcher() -> None:
    WatcherApp().run()
