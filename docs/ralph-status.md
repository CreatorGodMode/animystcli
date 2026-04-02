# Ralph Loop Status

The previous refactor loop has been cleared. This board tracks the next-step loop for Animyst after the architecture refactor and MCP binding rollout.

## Current Loop

- `00-baseline` — complete
- `10-mcp-binding` — complete
- `20-history-ux` — next
- `30-textual-tests` — pending
- `40-ralph-hardening` — pending
- `50-release-pass` — pending

## Runtime Source Of Truth

- `./ralph.sh status` prints the live phase state from `.codex/ralph-logs/`
- `./ralph.sh clear-status` resets the live phase logs for a fresh run
- this file is the human-readable public status board for the current loop
