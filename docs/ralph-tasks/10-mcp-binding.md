# Phase 10: MCP Binding

## Goal

Turn MCP binding from placeholder UX into a usable feature with persistence and basic health checks.

## In Scope

- enable the left-panel bind action and `bind mcp` flow
- persist newly bound MCPs to `mcps.json`
- support `stdio`, `sse`, and `http` MCP definitions
- add basic health validation and surface the result in lists and inspect views

## Required Behavior

- `bind mcp` opens the bind modal instead of showing a placeholder message
- the Bind MCP button is enabled
- `mcps` lists each MCP with type and last known health state
- `check mcp <name>` runs a basic health check:
  - `stdio`: verify the executable prefix resolves on `PATH`
  - `http` and `sse`: issue a lightweight GET request and record the HTTP result
- MCP inspect output shows command or URL plus the last check result and timestamp

## Verification

- `python3 -m pytest`
- `ANIMYST_DIR=.animyst-dev .venv/bin/python -m animyst`

