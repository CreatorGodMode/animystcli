# Phase 00: Baseline

## Goal

Reset the Ralph loop state, verify the current repo baseline, and prepare a clean starting point for feature work.

## In Scope

- clear prior Ralph status logs
- inspect repo status and branch state
- verify tests pass before feature work begins
- confirm the app can be smoke-tested with `ANIMYST_DIR=.animyst-dev`

## Checklist

- run `./ralph.sh clear-status`
- inspect `git status --short`
- run `python3 -m pytest`
- if dependencies are present, launch `ANIMYST_DIR=.animyst-dev .venv/bin/python -m animyst`
- prepare commit message: `Reset Ralph loop baseline for next steps`

## Verification

- `./ralph.sh status`
- `python3 -m pytest`
- `git status --short`

