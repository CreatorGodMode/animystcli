# ANIMYST — Project Conventions

## Identity
- **Name:** ANIMYST
- **Sigil:** ◬ (open triangle eye)
- **Tagline:** "Describe what you want. Walk away. Come back to a working repo."
- **Domain:** animystlab.com
- **License:** MIT

## What ANIMYST is
A local-first CLI that turns plain-English descriptions into working code. The user runs `animyst summon "<description>"` and walks away; ANIMYST scaffolds a fresh repo, runs `claude -p` in a multi-iteration loop until done (the "rite"), and tracks state across tmux + git + a local registry.

Each build is a **rite**. A rite is: one description → one directory → one autonomous loop → one shippable commit log.

## Language System (Ritual Vocabulary)
ANIMYST uses ritualistic language deliberately — never use generic terms in user-facing output or docs:

| Generic        | ANIMYST          |
|----------------|------------------|
| Create         | **Summon**       |
| Running        | **Awakened**     |
| Completed      | **Dormant**      |
| Blocked        | **⚠ Blocked**    |
| Delete         | **Banish**       |
| Build artifact | **Rite**         |
| Intent prompt  | **RITE.md**      |

## Color Palette (used by the Textual tracker's inline CSS)
- **Primary (fuchsia-violet):** `#c026d3` — sigil, headings, primary actions
- **Secondary (cyan):** `#00fff7` — data, active states
- **Accent (blood red):** `#ff1744` — power, urgency (sparingly)
- **Purple:** `#8b5cf6` — secondary elements
- **Amber:** `#f59e0b` — warnings (blocked rites)
- **Green:** `#00ff88` — awakened/success
- **Void black:** `#06050c` — main background
- **Deep:** `#0a091a` — panel backgrounds
- **Border:** `#1a1738` — panel borders
- **Dim:** `#504d78` — dormant/secondary text
- **Text:** `#c8c4e0` — body text

## Architecture
- **Python 3.10+** with type hints
- **Textual** for the `animyst watch` tracker
- **Rich** for terminal formatting
- **Build system:** Hatchling
- **Entry point:** `animyst.cli:main` (via pyproject.toml `console_scripts`)
- **Agent execution:** `claude -p` subprocess via the Claude Code CLI — uses the user's existing subscription, never the Anthropic API directly

### Repo structure
```
animystcli/
├── animyst/
│   ├── __init__.py            # package init + version string
│   ├── __main__.py            # `python -m animyst` entry
│   ├── cli.py                 # argparse + subcommand dispatch
│   ├── rites.py               # registry, summon, attach, stop, banish
│   ├── watcher.py             # Textual `animyst watch` tracker
│   ├── prompt_template.md     # the vetted Ralph prompt (the product)
│   ├── settings_template.json # Claude Code deny rules
│   └── loop.sh                # bash loop driver, runs inside tmux
├── .github/                   # issue + PR templates
├── tests/                     # currently empty; for future v0.2+ tests
├── CHANGELOG.md
├── CLAUDE.md                  # this file
├── AGENTS.md                  # contributor guide
├── LICENSE                    # MIT
├── pyproject.toml
└── README.md
```

### State surface (per rite)
```
~/.animyst/rites.json                # global rite registry

<rite-directory>/                    # one per rite, user's chosen parent dir
├── RITE.md                          # generated prompt (template + description)
├── WHAT_CHANGED.md                  # plain-English running log
├── .animyst/
│   ├── rite.json                    # current state (phase, status, blocker)
│   └── logs/iter-NN.log             # per-iteration claude output
├── .claude/settings.json            # deny rules — the safety wall
└── <the project files>              # what was actually built
```

`ANIMYST_DIR` overrides `~/.animyst` for tests/sandboxing.

## CLI Surface
- `animyst summon "<description>"` — create a new rite, or iterate from inside an existing one
- `animyst` — status board for all rites
- `animyst status [<slug>]` — same, or detailed view for one rite
- `animyst attach [<slug>]` — tmux attach to a rite's session
- `animyst watch` — open the Textual tracker
- `animyst stop [<slug>]` — kill a rite's tmux session (keeps the directory)
- `animyst banish <slug>` — delete a rite's directory and registry entry (confirmation required)

`--cap N` on `summon` changes max loop iterations (default 15).

## Code Style
- Python type hints throughout
- 4-space indentation, snake_case functions/vars, PascalCase classes
- Match the project's brief imperative commit style: e.g. `Add v0.2.0 rite framework CLI`, `Rewrite README around the v0.2 rite framework`. No conventional-commit prefix. No `Co-Authored-By: Claude` trailer.

## Key Patterns
- The product value lives in `prompt_template.md` and `settings_template.json` — the CLI is a thin shipping vehicle around them
- `loop.sh` is the canonical executor: bash `while` loop calling `claude -p` headless until `RITE_COMPLETE` sentinel
- State is read-only aggregation: tmux session liveness + git log + `rite.json` + `WHAT_CHANGED.md`. No daemons, no IPC.
- Per-rite `.claude/settings.json` is the hard safety wall — deny rules block `git push`, `git add -A`, `.env` reads, global installs, etc. The prompt repeats these as guidance but enforcement is at the harness layer
- Use `subprocess.run(..., check=True)` for git/tmux calls in `rites.py`; let `_require_tool()` fail fast if `git`/`tmux`/`claude` is missing
- Textual: keep CSS inline in `watcher.py` (not in a `.tcss` file) — small enough that the indirection isn't worth it
- When adding/changing the prompt template, validate against the reference Ralph specs the user maintains in sibling repos (e.g. `svarna-llm-ralph/ralph-prompt.md`) — those are the empirical ground truth for what works

## Testing
- `tests/` is currently empty. v0.2 ships with extensive manual validation (a single-iteration smoke test, an adversarial safety probe of the deny rules, and a 6-iteration end-to-end convergence run) but no automated pytest suite yet.
- When adding tests, target the pure parts first: `_slugify()`, registry CRUD, prompt template rendering. The loop/tmux/claude integration paths are harder to unit-test.
