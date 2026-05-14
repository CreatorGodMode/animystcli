"""ANIMYST CLI — `animyst` entry point."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from animyst import __version__
from animyst.rites import (
    attach,
    banish,
    list_rites,
    rite_state,
    stop,
    summon,
)


SIGIL = "◬"


def _elapsed_human(started_iso: str | None) -> str:
    if not started_iso:
        return "?"
    try:
        started = datetime.fromisoformat(started_iso.replace("Z", "+00:00"))
    except ValueError:
        return "?"
    delta = datetime.now(timezone.utc) - started
    s = int(delta.total_seconds())
    if s < 90:
        return f"{s}s"
    m = s // 60
    if m < 90:
        return f"{m}m"
    h = m / 60
    return f"{h:.1f}h"


def _status_icon(state: dict) -> str:
    if state.get("session_alive"):
        return "⊙"
    if state.get("status") == "dormant":
        return "⊘"
    if state.get("status") == "blocked":
        return "⚠"
    return "○"


def print_status(slug: str | None = None) -> None:
    rites = list_rites()
    if not rites:
        print(
            f"{SIGIL} ANIMYST — no rites yet.\n"
            f'  Run `animyst summon "<description>"` to begin.'
        )
        return

    if slug:
        s = rite_state(slug)
        if not s:
            sys.stderr.write(f"⊗ Unknown rite: {slug}\n")
            sys.exit(1)
        icon = _status_icon(s)
        print(f"{SIGIL} {slug}")
        print(f"  {icon} {s.get('status', '?')}")
        print(f"  Phase: {s.get('phase', '?')}/{s.get('total_phases_estimate') or '?'}")
        print(f"  Task:  {s.get('current_task', '')}")
        print(f"  Path:  {s.get('path', '')}")
        print(f"  Last:  {s.get('last_commit', '(no commits)')}")
        if s.get("blocker"):
            print(f"  ⚠ Blocker: {s['blocker']}")
        return

    print(f"{SIGIL} ANIMYST — active rites\n")
    for r in rites:
        s = rite_state(r["slug"]) or {}
        icon = _status_icon(s)
        elapsed = _elapsed_human(s.get("started_at"))
        phase = s.get("phase", "?")
        total = s.get("total_phases_estimate") or "?"
        task = (s.get("current_task") or "")[:55]
        last = s.get("last_commit") or "(no commits)"
        print(f"  {r['slug']}")
        print(f"    {icon} {s.get('status', '?')}    phase {phase}/{total}    {elapsed} elapsed")
        print(f"    task: {task}")
        print(f"    last: {last}")
        print(f"    path: {r['path']}")
        if s.get("blocker"):
            print(f"    ⚠ blocker: {s['blocker']}")
        print()
    print(f'  Run `animyst attach <slug>` to peek inside a session.')
    print(f'  Run `animyst watch` for live tracker.')
    print(f'  Run `animyst summon "<description>"` to start a new rite.')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="animyst",
        description=f"{SIGIL} ANIMYST — breathe life into code via autonomous rites.",
    )
    parser.add_argument("--version", action="version", version=f"animyst {__version__}")

    sub = parser.add_subparsers(dest="cmd")

    p_summon = sub.add_parser("summon", help="Create a new rite or iterate an existing one")
    p_summon.add_argument("description", help="What you want to build (or change)")
    p_summon.add_argument("--cap", type=int, default=15, help="Max loop iterations (default 15)")

    p_status = sub.add_parser("status", help="Show all rites (or details for one)")
    p_status.add_argument("slug", nargs="?", help="Specific rite slug")

    p_attach = sub.add_parser("attach", help="tmux attach to a rite session")
    p_attach.add_argument("slug", nargs="?", help="Rite slug (defaults to the only live one)")

    sub.add_parser("watch", help="Open the Textual tracker")

    p_stop = sub.add_parser("stop", help="Kill a rite's tmux session (keeps the directory)")
    p_stop.add_argument("slug", nargs="?", help="Rite slug (omit to stop all)")

    p_banish = sub.add_parser("banish", help="Delete a rite directory and registry entry")
    p_banish.add_argument("slug", help="Rite slug")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    cmd = args.cmd

    if cmd is None:
        print_status()
        return

    if cmd == "summon":
        summon(args.description, max_iter=args.cap)
    elif cmd == "status":
        print_status(args.slug)
    elif cmd == "attach":
        attach(args.slug)
    elif cmd == "watch":
        from animyst.watcher import run_watcher

        run_watcher()
    elif cmd == "stop":
        stop(args.slug)
    elif cmd == "banish":
        banish(args.slug)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
