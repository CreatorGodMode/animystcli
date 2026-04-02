"""Shared UI text and formatting helpers."""

from __future__ import annotations

from rich.markup import escape

from animyst.domain import HistorySummary

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


def status_icon(status: str) -> str:
    return {
        "dormant": "[#504d78]●[/]",
        "awakened": "[#00ff88]●[/]",
        "error": "[#ff2244]●[/]",
    }.get(status, "[#504d78]●[/]")


def status_color(status: str) -> str:
    return {
        "dormant": "#504d78",
        "awakened": "#00ff88",
        "error": "#ff2244",
    }.get(status, "#504d78")


def help_text() -> str:
    return """
[bold #c026d3]◬ ANIMYST COMMANDS ◬[/]
[#504d78]────────────────────────────────────────────[/]
[bold #00fff7]agents[/]         [#c8c4e0]List all configured agents[/]
[bold #00fff7]mcps[/]           [#c8c4e0]List all MCP servers[/]
[bold #00fff7]models[/]         [#c8c4e0]List available models[/]
[bold #00fff7]manifest[/]       [#c8c4e0]Manifest a new agent[/]
[bold #00fff7]bind mcp[/]       [#c8c4e0]Bind a new MCP server[/]
[bold #00fff7]check mcp <n>[/]  [#c8c4e0]Run a basic MCP health check[/]
[bold #00fff7]awaken <n>[/]     [#c8c4e0]Awaken an agent[/]
[bold #00fff7]inspect mcp <n>[/][#c8c4e0]View MCP details[/]
[bold #00fff7]inspect <n>[/]    [#c8c4e0]View agent configuration[/]
[bold #00fff7]banish <n>[/]     [#c8c4e0]Banish an agent[/]
[bold #00fff7]export <n>[/]     [#c8c4e0]Export agent config as JSON[/]
[bold #00fff7]git <cmd>[/]      [#c8c4e0]Run git commands[/]
[bold #00fff7]status[/]         [#c8c4e0]System status overview[/]
[bold #00fff7]clear[/]          [#c8c4e0]Clear console[/]
[bold #00fff7]ascii[/]          [#c8c4e0]Show animyst logo[/]
[#504d78]────────────────────────────────────────────[/]
[#504d78]Shortcuts: Ctrl+N manifest │ Ctrl+G git[/]
[#504d78]           Ctrl+L clear    │ Ctrl+R refresh[/]
[#504d78]Settings:  Click ⚙ Settings to add API keys[/]
""".strip()


def chat_help_text() -> str:
    return """
[bold #c026d3]◬ CHAT MODE COMMANDS ◬[/]
[#504d78]────────────────────────────────────────────[/]
[#c8c4e0]Type messages to chat with the agent.[/]
[#c8c4e0]Prefix with [bold #c026d3]/[/bold #c026d3] for commands:[/]
[#504d78]────────────────────────────────────────────[/]
[bold #00fff7]/sleep[/]         [#c8c4e0]Exit chat mode (agent → dormant)[/]
[bold #00fff7]/history[/]       [#c8c4e0]Show persisted conversation stats[/]
[bold #00fff7]/clear[/]         [#c8c4e0]Clear console output[/]
[bold #00fff7]/help[/]          [#c8c4e0]Show this help[/]
[bold #00fff7]/<command>[/]     [#c8c4e0]Run any animyst command[/]
[#504d78]────────────────────────────────────────────[/]
""".strip()


def format_status(agent_count: int, awakened_count: int, mcp_count: int, model_count: int, config_path: str) -> str:
    return f"""
[bold #c026d3]◬ ANIMYST STATUS ◬[/]
[#504d78]──────────────────────────────[/]
[#00fff7]Agents:[/]  [#c8c4e0]{agent_count} manifested, {awakened_count} awakened[/]
[#00fff7]MCPs:[/]    [#c8c4e0]{mcp_count} bound[/]
[#00fff7]Models:[/]  [#c8c4e0]{model_count} available[/]
[#00fff7]Config:[/]  [#c8c4e0]{escape(config_path)}[/]
""".strip()


def format_history_summary(summary: HistorySummary) -> str:
    if not summary.session_count:
        return "[#504d78]No persisted history yet[/]"
    updated = summary.last_updated or "unknown"
    return (
        f"[#00fff7]History:[/] [#c8c4e0]{summary.turn_count} turn(s), "
        f"{summary.message_count} message(s), {summary.session_count} session(s)[/] "
        f"[#504d78]updated {escape(updated)}[/]"
    )


def format_mcp_detail(mcp: dict[str, str]) -> str:
    health_status = mcp.get("health_status", "unknown")
    health_color = {
        "healthy": "#00ff88",
        "error": "#ff2244",
        "unknown": "#504d78",
    }.get(health_status, "#504d78")
    health_detail = mcp.get("last_error") or mcp.get("health_detail") or "not checked"
    target_label = "Command" if mcp.get("type", "stdio") == "stdio" else "URL"
    target_value = mcp.get("command") or mcp.get("url") or "N/A"
    checked = mcp.get("last_checked") or "never"
    return (
        f"[bold #00fff7]◈ MCP: {escape(mcp['name'])}[/]\n"
        f"  [#c026d3]Type:[/]    [#c8c4e0]{escape(mcp.get('type', 'stdio'))}[/]\n"
        f"  [#c026d3]{target_label}:[/] [#c8c4e0]{escape(target_value)}[/]\n"
        f"  [#c026d3]Health:[/]  [{health_color}]{escape(health_status.upper())}[/]\n"
        f"  [#c026d3]Checked:[/] [#c8c4e0]{escape(checked)}[/]\n"
        f"  [#c026d3]Detail:[/]  [#c8c4e0]{escape(str(health_detail))}[/]"
    )
