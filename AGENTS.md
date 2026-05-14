# Repository Guidelines

This file is the contributor guide for `animystcli`. For end-user docs see `README.md`. For project conventions and architecture see `CLAUDE.md`.

## Project Structure
Core code lives in `animyst/`:
- `cli.py` — argparse + dispatch for the `animyst` subcommands
- `rites.py` — registry, summon, attach, stop, banish (lifecycle + state)
- `watcher.py` — Textual `animyst watch` tracker
- `prompt_template.md` — the Ralph-protocol prompt the agent runs against (the actual product value)
- `settings_template.json` — Claude Code deny rules shipped into every rite
- `loop.sh` — bash loop driver that calls `claude -p` in iteration

Tests go under `tests/`. Per-release artifacts (wheels, sdist) build into `dist/` and are gitignored.

## Build, Test, and Development Commands
- `python3.12 -m venv .venv && source .venv/bin/activate` — create/activate the venv (use the absolute Homebrew path `/opt/homebrew/bin/python3.12` if your system `python3.12` shadows to a newer version)
- `pip install -e .` — install in editable mode
- `animyst --version` — verify the CLI is wired
- `animyst summon "test description"` — full end-to-end run (spawns a tmux session calling `claude -p`)
- `python -m build` — build sdist + wheel (install `build` first)
- `python -m animyst` — alternate launch path

## Runtime Requirements
- Python 3.10+
- `claude` CLI on PATH ([Claude Code](https://claude.com/claude-code), signed in)
- `tmux`
- `git`

## Coding Style
- Python 3.10+, 4-space indentation, type hints on new/changed code
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- Keep user-facing language aligned with the ritual vocabulary (`summon`, `awaken`, `dormant`, `banish` — see `CLAUDE.md`)
- Textual styling lives inline in `watcher.py` as a `CSS = """..."""` block; no separate `.tcss` file

## Testing
There is currently no automated test suite. For functional changes:
- Add `pytest` tests under `tests/` using `test_*.py` naming when introducing testable logic. Start with pure functions (slug derivation, prompt rendering, registry CRUD).
- For end-to-end verification, run `animyst summon "<smoke description>" --cap 2` in a throwaway directory and observe.

Manual verification steps go in PR descriptions until a CI suite exists.

## Commit & Pull Request Guidelines
- Commit subjects: short, imperative, no conventional-commit prefix. Match existing style (e.g. `Add v0.2.0 rite framework CLI`, `Rewrite README around the v0.2 rite framework`).
- One concern per commit. Use the body to explain "why."
- Never add `Co-Authored-By: Claude` or other AI co-authorship trailers.
- PR descriptions should include: summary of behavior change, manual test notes (commands run + outcomes), and screenshots/asciinema if you changed `animyst watch` or anything else visible.

## Security & Configuration
- Never commit `.env*`, API tokens, or anything from `~/.animyst/`
- Never commit personal rite directories — they may contain experimental or unfinished work
- The rite `.claude/settings.json` deny rules are a hard wall; don't relax them without a real reason
- `.envrc` (direnv) is gitignored — keep PyPI tokens and similar there
