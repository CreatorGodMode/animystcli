# Phase 01: Domain And Storage

## Goal

Extract typed models, shared paths, JSON helpers, and repositories out of the Textual app.

## In Scope

- agent/session/history dataclasses
- config paths and JSON utilities
- repositories for agents, MCPs, models, settings, and history

## Checklist

- keep current file formats backward-compatible
- preserve default models and MCPs
- move settings persistence out of `llm.py`
- add repository tests

## Verification

- `python3 -m pytest tests/test_repositories.py`
- `python3 -m py_compile animyst/domain/models.py animyst/storage/repositories.py animyst/llm.py`

