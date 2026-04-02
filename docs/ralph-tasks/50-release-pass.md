# Phase 50: Release Pass

## Goal

Wrap the loop with release-quality docs, packaging cleanup, and publication steps.

## In Scope

- sync README, HTML preview, and maintainer docs with shipped behavior
- review versioning impact
- run final verification
- open and merge the PR if configured

## Required Behavior

- update docs/screenshots/text to match MCP binding and history UX
- decide whether the scope warrants a version bump and apply it consistently if so
- run the full test suite and at least one smoke test from the repo-local virtualenv
- if GitHub auth is available and publishing is enabled, push, open the PR, and merge it

## Verification

- `python3 -m pytest`
- `git status --short`
- `./ralph.sh status`

