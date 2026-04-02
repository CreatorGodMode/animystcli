# Animyst Next Steps Ralph Loop

This loop replaces the completed refactor plan and focuses on the next product and automation milestones for Animyst.

## Objectives

- ship real MCP binding and basic health checks
- deepen conversation history UX beyond simple resume and summary counts
- add Textual integration coverage around core app flows
- harden `ralph.sh` for repeatable status, reset, PR, and release workflows
- finish with a release-quality documentation and packaging pass

## Phase Order

1. `00-baseline`
2. `10-mcp-binding`
3. `20-history-ux`
4. `30-textual-tests`
5. `40-ralph-hardening`
6. `50-release-pass`

## Success Criteria

- MCP binding is enabled from both the command console and the left-panel action
- bound MCPs can be persisted, listed, inspected, and checked for basic health
- agents can browse prior session metadata and start a fresh session intentionally
- the app has Textual integration tests for key command and modal flows
- Ralph loop status can be reset and inspected without manual file cleanup
- docs, versioning, and release notes are aligned with the shipped behavior

