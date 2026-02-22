# ◬ ANIMYST

<div align="center">

```
 █████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗████████╗
██╔══██╗████╗  ██║██║████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝
███████║██╔██╗ ██║██║██╔████╔██║ ╚████╔╝ ███████╗   ██║
██╔══██║██║╚██╗██║██║██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║
██║  ██║██║ ╚████║██║██║ ╚═╝ ██║   ██║   ███████║   ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝
```

**Breathe Life Into Code**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-00fff7?style=flat-square&logo=python&logoColor=00fff7)](https://python.org)
[![Textual](https://img.shields.io/badge/framework-Textual-c026d3?style=flat-square)](https://textual.textualize.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square)](LICENSE)

*Manifest agents. Bind MCPs. Ship code. All from your terminal.*

[animystlab.com](https://animystlab.com)

</div>

---

## What is Animyst?

Animyst is an **agent development environment** for the terminal. A  TUI for building, configuring, and managing AI agents — not just running them.

Unlike tools that act as session managers for existing coding agents, Animyst lets you **define** custom agents from scratch — choosing models, attaching MCP servers, writing incantations (system prompts), and composing multi-agent workflows.

Think of it as the difference between Spotify (playing music) and Ableton (creating music).

```
┌──────────────┬────────────────────────────────┬──────────────────┐
│  REGISTRY    │        CONSOLE                 │   GIT            │
│              │                                │                  │
│ ⚡ Agents    │  animyst › manifest scout       │  ⎇ main          │
│  ● scout     │  [scout] Channeling will...    │  2 files changed │
│  ● coder     │  [scout] Loading incantation   │                  │
│ ◈ MCPs       │  [scout] ⚡ Awakened            │  a3f2d manifest  │
│  ▸ GitHub    │                                │  b1c4e bind mcp  │
│  ▸ Filesystem│                                ├──────────────────┤
│ ▣ Models     │                                │   AGENT MIND     │
│  ▸ Sonnet 4.5│                                │                  │
│  ▸ Opus 4.5  │                                │  AWAKEN scout    │
│              │  animyst › _                   │  MANIFEST coder  │
└──────────────┴────────────────────────────────┴──────────────────┘
```

## Features

**⚡ Agent Manifest** — Define agents with custom incantations, model selection, temperature, and token limits. All configs stored as JSON in `~/.animyst/`.

**◈ MCP Binding** *(coming in v0.2)* — Register and manage Model Context Protocol servers (filesystem, GitHub, Slack, custom APIs). Bind them to agents with a keystroke.

**⎇ Git Integration** — Built-in git panel showing branch, changed files, recent commits. Quick actions for push, PR, and diff without leaving the TUI.

**◬ Agent Mind** — Real-time feed of all agent operations — manifestations, awakenings, banishments, exports. Your mission control.

**⌨ Command Console** — Full REPL with commands for managing agents, MCPs, models, and git operations. Keyboard shortcuts included.

**🌆 Cyberpunk Theme** — Fuchsia-violet, electric cyan, and deep purple on void black. Because dev tools should look as good as they work.

## Install

```bash
# Clone the repo
git clone https://github.com/CreatorGodMode/animystcli.git
cd animystcli

# Install with pip
pip install -e .

# Run
animyst
```

Or install directly:

```bash
pip install animyst
```

## Quick Start

```bash
# Launch animyst
animyst

# Inside the console:
help              # See all commands
manifest          # Manifest a new agent (or Ctrl+N)
bind mcp          # Bind a new MCP server (coming in v0.2)
agents            # List all agents
awaken scout      # Awaken an agent
inspect scout     # View agent configuration
banish scout      # Remove an agent
export scout      # Export agent config as JSON
git status        # Run git commands
status            # System overview
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+N` | Manifest new agent |
| `Ctrl+G` | Git status |
| `Ctrl+R` | Refresh all panels |
| `Ctrl+L` | Clear console |
| `Ctrl+Q` | Quit |

## Architecture

```
~/.animyst/
├── agents.json    # Agent configurations
├── mcps.json      # Bound MCP server registry
└── models.json    # Available model definitions
```

Animyst uses a file-based config system. Agent configs are portable JSON files that can be version-controlled, shared, and composed into pipelines.

## Agent Config Format

```json
{
  "name": "scout",
  "model": "claude-sonnet-4-5-20250929",
  "incantation": "You are a research agent that finds and summarizes information.",
  "mcps": ["web-search", "filesystem"],
  "temperature": 0.7,
  "max_tokens": 4096,
  "status": "dormant"
}
```

## Language

Animyst uses intentional language to distinguish itself:

| Generic | Animyst |
|---------|---------|
| Create agent | **Manifest** agent |
| Running | **Awakened** |
| Idle | **Dormant** |
| Delete | **Banish** |
| System prompt | **Incantation** |
| Register MCP | **Bind** MCP |

## Tech Stack

- **[Textual](https://textual.textualize.io)** — Python TUI framework with CSS-like styling
- **[Rich](https://rich.readthedocs.io)** — Terminal formatting and markup
- **[GitPython](https://gitpython.readthedocs.io)** — Git integration
- **[Anthropic SDK](https://docs.anthropic.com)** — Claude model integration
- **[OpenAI SDK](https://platform.openai.com/docs)** — GPT model integration
- **[Google GenAI SDK](https://ai.google.dev)** — Gemini model integration
- **Python 3.10+** — Async-native, type-hinted

## Roadmap

- [x] Live agent execution with streaming output
- [ ] MCP server connection & health checking
- [ ] Multi-agent pipeline composer
- [ ] Agent conversation history
- [ ] Akira-style telemetry HUD in Agent Mind panel
- [ ] Plugin system for custom panels
- [ ] Remote agent deployment
- [ ] Cost tracking per agent run
- [ ] Import/export agent packs

## License

MIT

---

<div align="center">

*Built with ◬ by [Abhi](https://github.com/CreatorGodMode) — CEO @ [Famished.ai](https://famished.ai) [Animystlab.com](https://animystlab.com)*

</div>
