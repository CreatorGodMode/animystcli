# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2026-05-14

### Changed

- Package short description and embedded long description (README) updated to match the GitHub repo's current branding — drops "Powered by Claude Code" from the tagline and "via Claude Code" from the short description. Technical references to Claude Code in install requirements, architecture, and safety sections are unchanged.

### Notes

- Pure metadata patch over v0.2.0. No code or dependency changes; runtime behavior is identical.

## [0.2.0] - 2026-05-14

ANIMYST pivots from a chat-agent TUI to a CLI for autonomous build rites driven by the Ralph protocol. Describe what you want, walk away, come back to a working repo.

### Added

- New `animyst` CLI surface: `summon`, `status`, `attach`, `watch`, `stop`, `banish`.
- `animyst summon "<description>"` scaffolds a rite directory, writes a vetted `RITE.md` (the Ralph-protocol prompt with the user's description interpolated in) and `.claude/settings.json` (safety deny rules), and starts an autonomous build loop in a detached tmux session.
- `animyst watch` opens a Textual tracker that polls the rite registry + tmux + git + per-rite state files to render a live cross-rite view.
- `loop.sh` — bash loop driver that runs `claude -p` in iteration until the agent prints `RITE_COMPLETE` or the iteration cap is hit (default 15, configurable via `--cap`).
- Global rite registry at `~/.animyst/rites.json` (override via `ANIMYST_DIR`).
- Iteration mode: `animyst summon "<change>"` from inside an existing rite directory treats the description as a change request instead of a fresh build.
- Per-rite `WHAT_CHANGED.md` updated each loop iteration — plain-English review surface for non-developer users.
- Safety wall: 14+ deny rules in the shipped `settings.json` blocking `git push`, `git add -A`, remote git operations, `.env*` reads, global installs, and piped-shell installs. Validated by adversarial probe (8/8 blocked).

### Changed

- Repositioned the entire project around the user story "describe what you want, walk away, come back to a working repo." Target audience is the lightly technical founder, not the developer using AI to type faster.
- Entry point switched from `animyst.app:main` to `animyst.cli:main`.
- README rewritten end-to-end around the v0.2 rite framework.
- `CLAUDE.md` and `AGENTS.md` updated for the new architecture.

### Removed

- The entire v0.1.x chat-agent codebase (~3,500 lines): `app.py`, `llm.py`, `commands/`, `domain/`, `services/`, `storage/`, `ui/`, `cyberpunk.tcss`. v0.2 imports nothing from these.
- Chat-agent tests: `test_chat_service.py`, `test_commands.py`, `test_mcp_service.py`.
- v0.1 build artifacts: `ralph.sh` (superseded by `animyst/loop.sh`), `docs/ralph-prompts/`, `docs/ralph-tasks/`, `docs/automation-approvals.md`, `docs/index.html` (chat-agent HTML preview), `screenshot.svg` (chat-agent screenshot).
- Unused chat-agent dependencies: `anthropic`, `openai`, `google-genai`, `gitpython`. v0.2 uses `claude -p` via subprocess (Claude Code subscription) plus the `git` and `tmux` CLIs.

### Notes

- v0.2 was validated end-to-end with a six-iteration convergence build of a Next.js landing page from a plain-English description. Zero safety violations, all deny rules held, production build green.
- iCloud-sync duplicate files (33 `* 2.py`, `* 2.md`, `* 2.sh`) accumulated in the working tree have also been cleaned out.

## [0.1.1] - 2026-04-02

This release brings Animyst's public repo, product copy, and recent architecture work into sync.

### Added

- Persistent per-agent conversation history with automatic session resume.
- MCP binding with transport-aware persistence and basic health checks.
- Repository-backed storage, service, command, and UI module separation.
- Ralph loop scaffolding for autonomous implementation passes.
- Focused pytest coverage for repositories, chat services, commands, and MCP flows.

### Changed

- Reframed the public README and preview docs around what Animyst actually does today.
- Updated package metadata to match the current local-first terminal workspace positioning.
- Refreshed maintainer and Ralph loop documentation for the current roadmap.

### Notes

- This is a patch release over `v0.1.0` that packages the post-refactor baseline and documentation cleanup.
