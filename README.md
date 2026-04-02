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

**A local-first terminal workspace for building and running AI agents**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-00fff7?style=flat-square&logo=python&logoColor=00fff7)](https://python.org)
[![Textual](https://img.shields.io/badge/framework-Textual-c026d3?style=flat-square)](https://textual.textualize.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square)](LICENSE)

*Manifest agents. Bind MCPs. Resume real conversations. Stay in the terminal.*

[animystlab.com](https://animystlab.com)

</div>

---

## What is Animyst?

Animyst is a **local-first terminal app for building and running AI agents**.

It gives you a place to define named agents, choose their models, write their incantations, bind MCP servers, store provider settings, and resume conversations without bouncing between scripts, config folders, and separate chat tabs.

Animyst sits in a practical middle ground. It is more structured than ad hoc API calls or one-off prompts, but lighter than a hosted orchestration platform. Your agents and settings live as files under `~/.animyst/`, so the setup stays inspectable, portable, and close to your actual development workflow.

It is still early, and that is part of the honest story here. Animyst is not pretending to be a full remote control plane yet. What it already is, though, is a real terminal workspace for people who want to shape how an agent is configured before they ask it to work.

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

**⚡ Agent manifesting** — Create named agents with a model, incantation, temperature, token limits, and bound MCPs. Agent definitions are stored as JSON in `~/.animyst/`.

**🔮 Live model streaming** — Chat with Anthropic, OpenAI, and Google models from inside the TUI, with streamed responses and per-response usage reporting.

**🕰 Persistent conversation history** — Awaken an agent, talk to it, exit, and come back later. Animyst saves session history under `~/.animyst/history/` and resumes the latest conversation automatically.

**◈ MCP registration and checks** — Bind MCP servers with command-based or URL-based transports, persist their config, and run basic health checks from the console.

**🔑 Provider settings management** — Save API keys and preferences for supported model providers with restricted file permissions.

**⎇ Git context in view** — See branch status, changed files, and recent commits without leaving the app, so the agent workflow stays connected to the repo you are actually changing.

**⌨ Command-first workflow** — Manage agents, MCPs, models, chat sessions, and git actions through a built-in command console with keyboard shortcuts and inspectable output.

**◬ Agent activity visibility** — Follow manifestations, awakenings, exports, checks, and other app activity from the side panels instead of guessing what happened behind the scenes.

**🌆 A deliberate terminal interface** — Animyst leans into a strong visual identity, but the design is there to support clarity and flow, not to hide the fact that this is still a working developer tool.

## Install

```bash
pip install animyst
animyst
```

Or install from source:

```bash
git clone https://github.com/CreatorGodMode/animystcli.git
cd animystcli
pip install -e .
animyst
```

## Quick Start

```bash
# Launch animyst
animyst

# Inside the console:
help              # See all commands
manifest          # Manifest a new agent (or Ctrl+N)
bind mcp          # Bind a new MCP server
check mcp github  # Run a basic MCP health check
inspect mcp github # View stored MCP details
agents            # List all agents
awaken scout      # Awaken an agent
inspect scout     # View agent configuration
banish scout      # Remove an agent
export scout      # Export agent config as JSON
git status        # Run git commands
status            # System overview
```

To smoke-test in a local sandbox without writing to `~/.animyst`, set a workspace-local config directory:

```bash
ANIMYST_DIR=.animyst-dev animyst
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
├── history/       # Per-agent conversation sessions
├── mcps.json      # Bound MCP server registry
├── models.json    # Available model definitions
└── settings.json  # API keys and preferences (0600 perms)
```

Animyst uses a file-based config system. Agent configs are portable JSON files that can be version-controlled, shared, and composed into pipelines.

Internally, the app is now organized as a thin Textual shell over dedicated modules for:

- typed domain models in `animyst/domain/`
- repository-backed persistence in `animyst/storage/`
- lifecycle and chat orchestration in `animyst/services/`
- command parsing and dispatch in `animyst/commands/`
- modal and formatting helpers in `animyst/ui/`

Current repo layout:

```text
animyst/
├── app.py                 # Textual app shell and event wiring
├── llm.py                 # Provider streaming and settings access
├── commands/              # Command parsing and dispatch
├── domain/                # Agent and conversation models
├── services/              # Agent lifecycle and chat orchestration
├── storage/               # Paths, JSON helpers, repositories
└── ui/                    # Modals and shared formatting
```

## Conversation History

When you awaken an agent, Animyst resumes the latest saved session for that agent automatically.

- sessions are stored under `~/.animyst/history/`
- `/history` shows persisted session and turn counts while chat mode is active
- `inspect <name>` surfaces history metadata for that agent
- malformed history files fail safe and start a clean session instead of crashing the app

## Ralph Loop Kit

The previous refactor loop has been cleared. The current Ralph loop now targets the next product milestones: MCP binding, history UX, Textual tests, Ralph hardening, and release cleanup.
Phase `10-mcp-binding` is already implemented in the repo, so the next active milestone is session history UX.

Use the included Ralph loop wrapper to run the new phase sequence:

```bash
./ralph.sh run-all
```

Useful commands:

```bash
./ralph.sh bootstrap
./ralph.sh status
./ralph.sh clear-status
./ralph.sh run 10-mcp-binding
./ralph.sh resume 20-history-ux
./ralph.sh verify
```

Supporting files:

- `docs/implementation-plan.md`
- `docs/automation-approvals.md`
- `docs/ralph-status.md`
- `docs/ralph-tasks/`
- `docs/ralph-prompts/`

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

## Current State

What is already working in the repo today:

- [x] Live agent execution with streaming output
- [x] Persistent per-agent conversation history
- [x] Modular architecture for storage, services, commands, and UI
- [x] Ralph loop automation scaffolding for autonomous implementation work
- [x] MCP binding with persistence and basic health checks

What we plan to improve next:

- [ ] Richer history UX for browsing past sessions and transcripts
- [ ] Deeper MCP runtime integration and more useful health diagnostics
- [ ] Textual integration tests for real command and modal flows
- [ ] Harder-to-break Ralph automation with stronger resume and PR workflows
- [ ] Release polish, changelog discipline, and better public-facing assets
- [ ] Cost tracking per agent run
- [ ] Import and export for reusable agent packs

## License

MIT

---

<div align="center">

Created by [Abhi](https://github.com/CreatorGodMode) at [Animyst Lab](https://animystlab.com)

</div>
