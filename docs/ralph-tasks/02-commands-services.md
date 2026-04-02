# Phase 02: Commands And Services

## Goal

Move command normalization, agent lifecycle, and chat session orchestration into testable modules.

## In Scope

- command parser and dispatcher
- agent service
- chat service
- `app.py` rewiring to consume the new interfaces

## Checklist

- preserve existing commands
- keep command mode and chat mode behavior aligned
- ensure the app no longer owns repository details directly

## Verification

- `python3 -m pytest tests/test_commands.py tests/test_chat_service.py`
- `python3 -m py_compile animyst/commands/parser.py animyst/commands/dispatcher.py animyst/services/agent_service.py animyst/services/chat_service.py animyst/app.py`

