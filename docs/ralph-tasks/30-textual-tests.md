# Phase 30: Textual Tests

## Goal

Add integration-style Textual tests around the current app shell so core UI flows are protected.

## In Scope

- command input and dispatch
- modal open/close flows
- chat mode transitions
- history and MCP UI touchpoints introduced in this loop

## Required Coverage

- launching the app and showing initial chrome
- `help` and `status` command rendering
- manifest modal open/close behavior
- bind MCP modal open and submit behavior
- awaken entering chat mode and returning to command mode
- history command rendering from a seeded repo-local `ANIMYST_DIR`

## Verification

- `python3 -m pytest`

