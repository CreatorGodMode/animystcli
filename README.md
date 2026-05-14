# ◬ ANIMYST

<div align="center">

```
 █████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗████████╗
██╔══██╗████╗  ██║██║████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝
███████║██╔██╗ ██║██║██╔████╔██║ ╚████╔╝ ███████╗   ██║
██╔══██║██║╚██╗██║██║██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║
██║  ██║██║ ╚████║██║██║ ╚═╝ ██║   ██║   ███████║   ██║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝
```

**Describe what you want. Walk away. Come back to a working repo.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-00fff7?style=flat-square&logo=python&logoColor=00fff7)](https://python.org)
[![Textual](https://img.shields.io/badge/tracker-Textual-c026d3?style=flat-square)](https://textual.textualize.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square)](LICENSE)

*Autonomous build rites. Local-first. Open source.*

[animystlab.com](https://animystlab.com)

</div>

---

## What is ANIMYST?

ANIMYST is a local-first CLI that turns plain-English descriptions into working code.

You describe what you want to build. ANIMYST scaffolds the repository, runs Claude Code in a multi-iteration loop until the build is done, and tracks state across tmux + git + filesystem so you can walk away and come back.

Each build is called a **rite**. A rite is one description → one worktree → one autonomous loop → one shippable commit log.

ANIMYST sits in a deliberate position. It is **not** a hosted AI coding tool — there is no proprietary backend, no telemetry, no per-token billing. It runs locally, uses your existing Claude Code subscription, and produces a real git repository you can push anywhere. It is built for people who want to ship without typing the code themselves.

```
$ animyst summon "Landing page for GroundFloor Coffee. Warm orange #E8743B.
> Three tiers: Single Origin $24/mo, Roaster's Choice $32/mo, Curator $48/mo.
> Hero: 'Coffee from people who care'. Email signup. Mobile-first."

◬ Channeling intent for: landing-page-groundfloor-coffee
  → Working directory: ./landing-page-groundfloor-coffee/
  → tmux session:      animyst-landing-page-groundfloor-coffee
  → Awakened. Track with `animyst` or `animyst attach`.

# 25 minutes later …

$ animyst
◬ ANIMYST — active rites

  landing-page-groundfloor-coffee
    ⊘ dormant     phase 7/7    25m elapsed
    task: Wrote a README and marked the rite complete
    last: ae79539 docs: add README and mark rite complete
```

## How it works

1. **Summon.** `animyst summon "<description>"` creates a directory, runs `git init`, drops a vetted `RITE.md` (the autonomous-build prompt) and `.claude/settings.json` (the safety deny rules), and starts a build loop in a detached tmux session.
2. **Walk away.** Each loop iteration: read context, pick the next single coherent task, implement it, verify the build passes, commit explicit paths with a conventional commit message, append a plain-English summary to `WHAT_CHANGED.md`. Loops until done — or until the agent surfaces a blocker that needs you.
3. **Come back.** `animyst` prints a status board. `animyst watch` opens a Textual tracker. `animyst attach <slug>` drops you into the tmux session to peek at live output.
4. **Iterate.** `cd` into the rite directory and run `animyst summon "<change request>"` again. The prompt detects an existing `WHAT_CHANGED.md` and treats the new description as a change to the existing repo, not a fresh build.

## Install

```bash
pip install animyst
```

Or from source:

```bash
git clone https://github.com/CreatorGodMode/animystcli.git
cd animystcli
pip install -e .
```

Requirements:

- **Python 3.10+**
- **[Claude Code](https://claude.com/claude-code)** installed and signed in (`claude --version` should work). ANIMYST invokes `claude -p` in headless mode for each loop iteration, so your existing subscription is the auth.
- **tmux** — built-in on macOS; `apt install tmux` / `brew install tmux` elsewhere.
- **git**

## Quickstart

```bash
$ cd ~/Code

$ animyst summon "Single-page portfolio site for a freelance illustrator.
> Earth-tone palette (#3a2e1c base, #d4a574 accent). Hero with name and
> tagline. Gallery grid of project cards (placeholder for 8). About blurb.
> Contact email form. Mobile-first."

$ animyst                       # status at a glance
$ animyst watch                 # Textual live tracker
$ animyst attach <slug>         # tmux attach into the running session
$ animyst stop <slug>           # kill the session (keeps the directory)
$ animyst banish <slug>         # delete the directory + registry entry
```

To iterate on an existing rite:

```bash
$ cd ./single-page-portfolio-freelance-illustrator
$ animyst summon "Make the accent warmer, more terracotta (#c46a3b).
> Add a 'currently booking' callout next to the contact form."
```

## Commands

| Command | What it does |
|---|---|
| `animyst summon "<description>"` | Create a new rite, or iterate from inside an existing one |
| `animyst` | Status board for all rites |
| `animyst status [<slug>]` | Same, or detailed view for one rite |
| `animyst attach [<slug>]` | tmux attach to a rite's session (defaults to the only live one) |
| `animyst watch` | Open the Textual tracker |
| `animyst stop [<slug>]` | Kill a rite's tmux session (keeps the directory) |
| `animyst banish <slug>` | Delete a rite directory and registry entry (confirmation required) |

Use `--cap N` with `summon` to change the max loop iterations (default 15).

## Architecture

```
~/.animyst/rites.json               global rite registry

<rite-directory>/                   one per rite
├── RITE.md                         the prompt (auto-generated from your description)
├── WHAT_CHANGED.md                 plain-English log, updated each iteration
├── .animyst/
│   ├── rite.json                   current state (phase, status, blocker)
│   └── logs/iter-NN.log            per-iteration claude output
├── .claude/settings.json           deny rules — the safety wall
└── <the actual project files>      what you wanted built
```

Everything is local. No telemetry, no hosted runs, no proprietary backend. The rite directory is a normal git repository — push to GitHub, deploy on Vercel, do whatever you would with any other project.

The Textual tracker (`animyst watch`) reads the registry + tmux state + each rite's `rite.json` + `WHAT_CHANGED.md` to render a live cross-rite view. No daemon. No IPC. Just filesystem + tmux + git.

## The Ralph protocol, productized

ANIMYST is a productized version of the Ralph protocol — a battle-tested pattern for autonomous, multi-iteration agent builds where a hand-authored 250-650 line spec encodes mission, file allow/deny lists, commit cycle, retry budget, failure protocol, and completion criteria. The pattern works. The bottleneck for adoption was authoring the spec.

ANIMYST collapses that. It ships a vetted, parameterized prompt template and static deny rules. Your description fills in the mission. The rest is the same Ralph protocol that has shipped real work in production repositories, now packaged behind one command.

## Safety

Every rite gets a `.claude/settings.json` that denies, at the Claude Code permission layer:

- `git push`, `gh pr create`, all remote git operations
- `git add -A`, `git add .`, `git add --all` (forces explicit-path staging)
- `git commit --amend`, `git reset --hard`, `git rebase`, `git checkout <branch>`
- Global package installs (`npm i -g`, `pip install --user`, `yarn global`)
- Reads/writes of `.env*` and any file named `*secrets*`
- Piped-shell installs (`curl … | sh`, `wget … | bash`)
- `sudo`, `chmod 777`, `rm -rf /…`

Validated by an adversarial probe: eight forbidden operations attempted in isolation, eight blocked, zero slipped through.

These rules are the hard wall. The prompt template ALSO repeats them as guidance, but the harness enforces independently — belt and suspenders.

## Language

ANIMYST uses ritualistic terminology deliberately to distinguish itself:

| Generic | ANIMYST |
|---|---|
| Create | **Summon** |
| Running | **Awakened** |
| Completed | **Dormant** |
| Blocked | **⚠ Blocked** |
| Delete | **Banish** |
| Build | **Rite** |

## Tech stack

- **Python 3.10+** — Async-native, type-hinted
- **[Textual](https://textual.textualize.io)** — TUI tracker
- **[Rich](https://rich.readthedocs.io)** — Terminal formatting
- **tmux** — Long-running session manager for unattended loops
- **[Claude Code](https://claude.com/claude-code)** — Executor agent (subscription auth, no API tokens charged)
- **git** — State and history surface

## What's next

- **Codex CLI** as an alternative agent adapter (parity with `claude -p`)
- **`animyst deploy`** — one-command push to GitHub + Vercel for the standard archetypes
- **More archetypes** beyond Next.js: Python scripts, Expo apps, FastAPI services
- **Pause-and-ask flow** — agent surfaces blockers as plain-English questions, user resolves via `animyst ask`
- **Hardened iteration mode** — better diffs for change-request-style re-runs

## License

MIT

---

<div align="center">

Created by [Abhi](https://github.com/CreatorGodMode) at [Animyst Lab](https://animystlab.com)

</div>
