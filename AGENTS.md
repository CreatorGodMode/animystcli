# Repository Guidelines

## Project Structure & Module Organization
Core application code lives in `animyst/`:
- `app.py`: main Textual TUI, command handling, modal flows
- `llm.py`: provider streaming and API key/settings logic
- `cyberpunk.tcss`: shared UI styling
- `__main__.py`: `python -m animyst` entry point

Project documentation is in `README.md` and `docs/index.html`. Build outputs are written to `dist/` and should be treated as generated artifacts.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create/activate local environment.
- `pip install -e .`: install Animyst in editable mode for development.
- `animyst`: launch the CLI/TUI via console script.
- `python -m animyst`: alternate launch path for local debugging.
- `python -m build`: build source/wheel distributions (install `build` first if needed).

## Coding Style & Naming Conventions
Use Python 3.10+ with 4-space indentation and type hints for new/changed code. Follow existing naming:
- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

Keep UI language aligned with project terminology (for example: “manifest”, “awaken”, “banish”, “incantation”). Put Textual styling in `cyberpunk.tcss` rather than inline style strings where practical.

## Testing Guidelines
There is currently no committed automated test suite. For functional changes:
- add focused `pytest` tests under `tests/` using `test_*.py` naming when introducing testable logic
- run manual smoke checks by launching `animyst` and validating key commands (`help`, `manifest`, `awaken`, `inspect`)

Document manual verification steps in your PR until a formal CI test pipeline exists.

## Commit & Pull Request Guidelines
Match the repository’s existing commit style: short, imperative summaries (for example, `Update README for v0.1.0 public release`). Keep commits scoped to one concern.

PRs should include:
- clear summary of behavior changes
- linked issue/task when applicable
- terminal screenshots or GIFs for visible TUI updates
- manual test notes (commands run + outcomes)

## Security & Configuration Tips
Never commit API keys or personal config from `~/.animyst/` (`settings.json`, `agents.json`, etc.). Prefer environment variables for local development secrets and verify file permissions remain restricted for saved settings.
