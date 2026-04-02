# Phase 04: UI Split

## Goal

Reduce `app.py` to a UI shell and move reusable modal/formatting code into dedicated UI modules.

## In Scope

- modal classes
- formatting helpers
- tree label and detail rendering helpers

## Checklist

- keep current theme and language
- avoid behavior regressions
- add comments only where the new boundaries are non-obvious

## Verification

- `python3 -m py_compile animyst/ui/modals.py animyst/ui/formatting.py animyst/app.py`

