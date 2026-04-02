# Phase 40: Ralph Hardening

## Goal

Make the Ralph wrapper easier to reuse for future work without manual bookkeeping.

## In Scope

- live status reporting
- status reset
- optional PR and merge helpers
- stronger log markers for phase outcomes

## Required Behavior

- `./ralph.sh status` prints each phase and its current state from the log files
- `./ralph.sh clear-status` removes prior phase log files for a clean run
- each phase log records `running`, `completed`, or `failed`
- add optional helpers for `open-pr` and `merge-pr` gated behind existing GitHub auth
- update docs so the next engineer can run the full loop without re-discovering commands

## Verification

- `./ralph.sh status`
- `./ralph.sh clear-status`
- `python3 -m pytest`

