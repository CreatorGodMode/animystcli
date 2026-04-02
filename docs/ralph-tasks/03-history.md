# Phase 03: Persistent History

## Goal

Persist all chat turns and restore the latest session when an agent is awakened again.

## In Scope

- per-agent history files under `~/.animyst/history/`
- session resume behavior
- history summary reporting
- inspect metadata updates

## Checklist

- append user and assistant turns as they occur
- preserve history on chat exit and error paths
- show persisted counts in `/history`
- surface summary metadata in inspect

## Verification

- `python3 -m pytest tests/test_repositories.py tests/test_chat_service.py`

