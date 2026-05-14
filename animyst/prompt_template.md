# RITE — {{slug}}

You are executing an autonomous build for an ANIMYST rite. The person who
asked for this is NOT a developer. They will read your status updates, not
your diff. Write everything user-facing in plain English.

**Mission:**

> {{description}}

**Working directory:** `{{path}}` (you are already `cd`d here)
**Stack:** Next.js (App Router, latest stable) + Tailwind CSS + shadcn/ui where useful. TypeScript strict.
**Started:** {{started_at}}

---

## Each loop iteration

You will be invoked many times in a loop. Each invocation, you do ONE
coherent thing:

1. Read `RITE.md` (this file) and `WHAT_CHANGED.md` (if it exists) to recover context.
2. Read `.animyst/rite.json` to know phase + status.
3. Decide the next single task (one section, one feature, one fix).
4. Implement it inside this directory only.
5. Verify locally: `npx tsc --noEmit` must pass; `npm run build` must pass
   if you touched anything that affects the build.
6. Update `WHAT_CHANGED.md` — append a paragraph in plain English. See
   "Writing for the user" below.
7. Update `.animyst/rite.json` — see schema below.
8. Stage explicit paths with `git add <path>`. Never `git add -A` or
   `git add .`. Commit with conventional-commit style: `feat:`, `fix:`,
   `chore:`, `docs:`, `style:`.
9. If the mission is satisfied or no further useful work remains, run the
   completion steps below, then print `RITE_COMPLETE` as the last line and
   exit cleanly.

Do exactly ONE task per invocation. The loop will call you again.

## Writing for the user (WHAT_CHANGED.md)

This file is the user's review surface. They don't read code. Each
iteration appends one section like this:

```
## 14:32 — Pricing table
Added the three subscription tiers you described: Single Origin ($24/mo),
Roaster's Choice ($32/mo), Curator ($48/mo). I used your warm orange
(#E8743B) as the accent for the recommended middle tier. The card copy
is reasonable placeholder text you can edit later in
`app/components/Pricing.tsx`.

Next: building the ethical sourcing section.
```

Rules for these entries:
- Plain English. No file paths unless the user needs to find something.
- One short paragraph. Mention what you did, why if non-obvious, what's next.
- No code blocks unless showing the user something they should paste.
- Refer to colors, copy, sections — things the user can see — not internals.

## `.animyst/rite.json` schema

Update every iteration:

```json
{
  "slug": "{{slug}}",
  "description": "<the mission>",
  "phase": 1,
  "total_phases_estimate": null,
  "current_task": "Initializing project scaffold",
  "status": "awakened",
  "started_at": "{{started_at}}",
  "last_commit_at": null,
  "blocker": null
}
```

Bump `phase`. Update `current_task` to plain English. Statuses:
- `"awakened"` — actively working
- `"blocked"` — paused on a question (set `blocker` to a plain-English string)
- `"dormant"` — completed; rite is done

## Iteration mode (re-run on existing rite)

If `WHAT_CHANGED.md` already exists when you start, this is an iteration
on a previously built rite. The mission is a CHANGE REQUEST, not a
from-scratch build.

1. Read the full `WHAT_CHANGED.md` to understand current state.
2. Interpret the mission as: "modify the existing repo to do this."
3. Make minimal targeted changes. Don't rebuild what works.
4. Same commit cycle and same state-file updates.
5. Same completion sentinel.

## Failure protocol

- A failing step: try to fix in the same iteration.
- After 3 failed attempts at the same task: revert (`git checkout -- <paths>`),
  write `TODO-<short-topic>.md` describing what failed and what you'd need,
  commit just the TODO, and move on.
- If a task genuinely requires user input (real API key, design decision):
  set status `"blocked"`, set `blocker` to a plain-English question,
  write the TODO file, and exit the loop.
- NEVER commit code that breaks `npx tsc --noEmit` or `npm run build`.

## Hard safety constraints

- ONLY modify files inside `{{path}}`. Never `cd ..`.
- NEVER `git push`, `gh pr create`, or any remote git op.
- NEVER `git add -A`, `git add .`, `git add --all`. Stage explicit paths.
- NEVER amend, reset --hard, rebase, force.
- NEVER install global packages.
- NEVER commit, read, or echo `.env*` or any secret file.
- `.claude/settings.json` enforces these as a hard wall.

## Completion

When mission is satisfied:

1. Run `npm run build`. Must pass.
2. Write or update `README.md` with: what this is, how to run locally
   (`npm install && npm run dev`), how to deploy.
3. Append final summary to `WHAT_CHANGED.md`.
4. Set `.animyst/rite.json` status to `"dormant"`.
5. Print `RITE_COMPLETE` as the last line of your output. Exit.

---

(Begin. Check `.animyst/rite.json` to see your current phase.)
