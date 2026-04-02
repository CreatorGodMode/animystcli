# Automation Approval Checklist

These are the commands the autonomous flow is expected to need. Approve them up front when possible so the loop can continue without waiting.

## Likely approvals

- `python3 -m pip install -e .`
- `python3 -m pytest`
- `git add <scoped files>`
- `git commit -m <message>`

## Optional approvals

- `git push`
- any package install required for local smoke tests if the base environment is missing Textual

## Approval posture

- Stay sandboxed by default
- escalate only when a blocked command is required to verify or finish the phase
- do not request destructive approvals

