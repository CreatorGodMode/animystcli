# Phase 20: History UX

## Goal

Expand persisted conversation history into a usable session workflow.

## In Scope

- command-mode history browsing
- explicit fresh-session behavior in chat mode
- richer inspect metadata for prior sessions

## Required Behavior

- add `history <agent>` to list saved sessions newest-first with session id, updated time, turns, and message count
- add `/new` in chat mode to end the current session and start a fresh one for the active agent
- keep `/history` in chat mode, but make it show current session details plus recent saved sessions
- update inspect to show total sessions, total turns, and last updated metadata
- malformed history files must still fail safe and create a clean session

## Verification

- `python3 -m pytest`
- manual smoke test:
  - awaken an agent
  - chat once
  - run `/history`
  - run `/new`
  - run `history <agent>`

