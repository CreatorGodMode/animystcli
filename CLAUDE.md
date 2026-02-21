# ANIMYST — Project Conventions

## Identity
- **Name:** ANIMYST
- **Sigil:** ◬ (open triangle eye)
- **Tagline:** "breathe life into code"
- **Domain:** animystlab.com
- **License:** MIT

## Language System (Manifestation Metaphor)
ANIMYST uses ritualistic language — never use generic terms in UI, logs, or code comments:

| Generic          | ANIMYST          |
|------------------|------------------|
| Create agent     | **Manifest** agent |
| Running          | **Awakened**     |
| Idle             | **Dormant**      |
| Delete           | **Banish**       |
| System prompt    | **Incantation**  |
| Register MCP     | **Bind** MCP     |
| Initializing     | **Channeling will** |

## Color Palette
- **Primary (fuchsia-violet):** `#c026d3` — sigil, headings, primary actions
- **Secondary (cyan):** `#00fff7` — data, active states, command text
- **Accent (blood red):** `#ff1744` — power, urgency (sparingly)
- **Purple:** `#8b5cf6` — git UI, secondary elements
- **Amber:** `#f59e0b` — warnings, cost indicators
- **Green:** `#00ff88` — success, live/awakened states
- **Error red:** `#ff2244` — errors, banish actions
- **Void black:** `#06050c` — main background
- **Deep:** `#0a091a` — panel backgrounds
- **Surface:** `#12102a` — elevated surfaces
- **Border:** `#1a1738` — panel borders
- **Muted:** `#26244a` — subtle elements
- **Dim:** `#504d78` — secondary text
- **Text:** `#c8c4e0` — body text

## Architecture
- **Python 3.10+** with type hints
- **Textual 1.0+** for TUI framework
- **Rich 13.0+** for terminal formatting
- **GitPython 3.1+** for git integration
- **Build system:** Hatchling

### Entry Point
`animyst` command → `animyst.app:main` (via pyproject.toml console_scripts)

### Data Storage
All config lives in `~/.animyst/`:
- `agents.json` — agent configurations
- `mcps.json` — bound MCP server registry
- `models.json` — available model definitions

### Repo Structure
```
animystcli/
├── animyst/
│   ├── __init__.py        # Package init, version string
│   ├── __main__.py        # CLI entry (python -m animyst)
│   ├── app.py             # Main TUI app — all widgets, modals, commands
│   └── cyberpunk.tcss     # Textual CSS theme
├── docs/
│   └── index.html         # Interactive HTML preview for GitHub Pages
├── .gitignore
├── CLAUDE.md              # This file
├── LICENSE                # MIT
├── pyproject.toml
└── README.md
```

### TUI Layout (4-panel)
```
┌──────────────┬──────────────────────────┬──────────────────┐
│  REGISTRY    │     CONSOLE              │   GIT            │
│  (left)      │     (center)             │   (top-right)    │
│  - Agents    │     - REPL + logs        │   - branch/diff  │
│  - MCPs      │     - command input      │   - commits      │
│  - Models    │                          ├──────────────────┤
│  - Actions   │                          │   AGENT MIND     │
│              │                          │   (bottom-right) │
└──────────────┴──────────────────────────┴──────────────────┘
```

## CLI Commands
- `animyst manifest <name>` — create/run agent
- `animyst awaken <name>` — run agent
- `animyst banish <name>` — delete agent
- `animyst bind <mcp>` — register MCP server
- `animyst inspect <name>` — view agent details
- `animyst export <name>` — export config as JSON

## Code Style
- Python type hints throughout
- Black formatting
- Textual CSS for all styling (cyberpunk.tcss)
- Rich markup for console output (not ANSI codes)
- Always run tests after changes

## Key Patterns
- `load_json()` / `save_json()` for all file I/O
- `log_console()`, `log_mind()`, `log_git()` for panel output
- `@work(thread=True)` for blocking operations (git, agent simulation)
- `call_from_thread()` for UI updates from worker threads
- Modal screens for agent manifest, MCP bind, agent inspect
