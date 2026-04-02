# Ralph Loop Approval Checklist

These are the commands the next-step loop is expected to need. Approve them early when possible so the loop can continue without repeated pauses.

## Likely approvals

- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`
- `python3 -m pytest`
- `.venv/bin/python -m pytest`
- `ANIMYST_DIR=.animyst-dev .venv/bin/python -m animyst`
- `git add <scoped files>`
- `git commit -m <message>`
- `git push -u origin <branch>`
- `gh pr create ...`
- `gh pr merge ...`

## Optional approvals

- `git fetch origin main`
- `gh pr view ...`
- `gh pr list ...`

## Approval posture

- stay sandboxed by default
- escalate only when a blocked step is required to verify, publish, or merge work
- prefer repo-local virtualenvs and `ANIMYST_DIR=.animyst-dev` for smoke tests
- do not request destructive approvals

