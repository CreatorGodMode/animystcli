# Animyst Autonomous Refactor Plan

Animyst is being refactored from a single large Textual app into a modular agent workbench with:

- repository-backed persistence
- explicit services for agent lifecycle and chat sessions
- persisted conversation history per agent
- testable command parsing and storage logic
- a Ralph loop kit for replayable automation

## Phase Order

1. `00-bootstrap`
2. `01-domain-storage`
3. `02-commands-services`
4. `03-history`
5. `04-ui-split`
6. `05-verify-docs`

## Success Criteria

- `animyst/app.py` is a thin UI shell
- agent/session/history logic lives outside the UI layer
- `awaken <name>` resumes persisted history
- `/history` reports persisted conversation stats
- non-UI behavior is covered by automated tests
- the Ralph task and prompt files are sufficient for an autonomous Codex loop

