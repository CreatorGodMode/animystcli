"""Rite registry, lifecycle, and state aggregation."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

ANIMYST_DIR = Path(os.environ.get("ANIMYST_DIR", Path.home() / ".animyst"))
REGISTRY_PATH = ANIMYST_DIR / "rites.json"

_STOP_WORDS = {
    "a", "an", "the", "for", "of", "to", "with", "and", "or", "in", "on",
    "at", "by", "from", "as", "is", "are", "be", "this", "that", "my",
    "your", "our", "their", "its", "it", "i", "we", "you", "they",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slugify(description: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", description.lower())
    keep = [t for t in tokens if t not in _STOP_WORDS][:4]
    if not keep:
        keep = ["rite", datetime.now().strftime("%Y%m%d%H%M")]
    return "-".join(keep)


def _ensure_registry() -> None:
    ANIMYST_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text(json.dumps({"rites": []}, indent=2))


def _load_registry() -> dict[str, Any]:
    _ensure_registry()
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except json.JSONDecodeError:
        return {"rites": []}


def _save_registry(reg: dict[str, Any]) -> None:
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2))


def _register_rite(slug: str, path: Path, description: str) -> None:
    reg = _load_registry()
    entry = {
        "slug": slug,
        "path": str(path),
        "description": description,
        "created_at": _now_iso(),
    }
    reg["rites"] = [r for r in reg.get("rites", []) if r["slug"] != slug]
    reg["rites"].append(entry)
    _save_registry(reg)


def list_rites() -> list[dict[str, Any]]:
    return _load_registry().get("rites", [])


def get_rite(slug: str) -> dict[str, Any] | None:
    for r in list_rites():
        if r["slug"] == slug:
            return r
    return None


def tmux_session_name(slug: str) -> str:
    return f"animyst-{slug}"


def session_alive(slug: str) -> bool:
    r = subprocess.run(
        ["tmux", "has-session", "-t", tmux_session_name(slug)],
        capture_output=True,
    )
    return r.returncode == 0


def rite_state(slug: str) -> dict[str, Any] | None:
    r = get_rite(slug)
    if not r:
        return None
    path = Path(r["path"])
    state_file = path / ".animyst" / "rite.json"
    state: dict[str, Any] = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
        except json.JSONDecodeError:
            pass
    state["session_alive"] = session_alive(slug)
    state["path"] = str(path)
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "log", "-1", "--format=%h %s"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        state["last_commit"] = out
    except (subprocess.CalledProcessError, FileNotFoundError):
        state["last_commit"] = ""
    try:
        n = subprocess.check_output(
            ["git", "-C", str(path), "rev-list", "--count", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        state["commit_count"] = int(n)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        state["commit_count"] = 0
    return state


def _require_tool(name: str) -> None:
    if shutil.which(name) is None:
        sys.stderr.write(f"⊗ ANIMYST requires `{name}` on PATH.\n")
        sys.exit(2)


def _resource_text(name: str) -> str:
    return files("animyst").joinpath(name).read_text()


def _resource_path(name: str) -> Path:
    with files("animyst").joinpath(name) as p:
        return Path(str(p))


def _render_rite_md(slug: str, description: str, path: Path, started_at: str) -> str:
    tpl = _resource_text("prompt_template.md")
    return (
        tpl.replace("{{slug}}", slug)
        .replace("{{description}}", description)
        .replace("{{path}}", str(path))
        .replace("{{started_at}}", started_at)
    )


def _start_loop_session(slug: str, rite_dir: Path, max_iter: int) -> None:
    _require_tool("tmux")
    _require_tool("claude")
    session = tmux_session_name(slug)
    subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)
    loop_path = _resource_path("loop.sh")
    cmd = f"bash {loop_path} {rite_dir} {max_iter}"
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session, "-c", str(rite_dir), cmd],
        check=True,
    )


def summon(description: str, max_iter: int = 15) -> None:
    _require_tool("git")
    _require_tool("tmux")
    _require_tool("claude")

    cwd = Path.cwd()

    # Iteration mode: already inside a rite?
    if (cwd / "RITE.md").exists() and (cwd / "WHAT_CHANGED.md").exists():
        _iterate(cwd, description, max_iter)
        return

    slug = _slugify(description)
    target = cwd / slug
    if target.exists():
        sys.stderr.write(
            f"⊗ {target} already exists. Pick a different description or `cd` elsewhere.\n"
        )
        sys.exit(1)

    print(f"◬ Channeling intent for: {slug}")
    target.mkdir(parents=True)

    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    if not subprocess.run(["git", "config", "user.email"], capture_output=True).stdout.strip():
        subprocess.run(["git", "config", "user.email", "rite@animyst.local"], cwd=target)
        subprocess.run(["git", "config", "user.name", "ANIMYST"], cwd=target)

    (target / ".claude").mkdir()
    (target / ".claude" / "settings.json").write_text(_resource_text("settings_template.json"))

    (target / ".animyst").mkdir()
    now = _now_iso()
    rite_data = {
        "slug": slug,
        "description": description,
        "phase": 0,
        "total_phases_estimate": None,
        "current_task": "Awaiting first iteration",
        "status": "awakened",
        "started_at": now,
        "last_commit_at": None,
        "blocker": None,
    }
    (target / ".animyst" / "rite.json").write_text(json.dumps(rite_data, indent=2))

    (target / "RITE.md").write_text(_render_rite_md(slug, description, target, now))

    subprocess.run(
        ["git", "add", "RITE.md", ".claude/settings.json", ".animyst/rite.json"],
        cwd=target,
        check=True,
    )
    subprocess.run(["git", "commit", "-q", "-m", "chore: scaffold rite"], cwd=target, check=True)

    _register_rite(slug, target, description)
    _start_loop_session(slug, target, max_iter)

    print(f"  → Working directory: {target}")
    print(f"  → tmux session:      animyst-{slug}")
    print(f"  → Awakened. Track with `animyst` or `animyst attach {slug}`.")


def _iterate(rite_dir: Path, description: str, max_iter: int) -> None:
    state_file = rite_dir / ".animyst" / "rite.json"
    state = json.loads(state_file.read_text())
    slug = state["slug"]
    started_at = state.get("started_at") or _now_iso()

    (rite_dir / "RITE.md").write_text(_render_rite_md(slug, description, rite_dir, started_at))

    state["description"] = description
    state["status"] = "awakened"
    state["current_task"] = "Awaiting iteration on new request"
    state["blocker"] = None
    state_file.write_text(json.dumps(state, indent=2))

    subprocess.run(
        ["git", "add", "RITE.md", ".animyst/rite.json"], cwd=rite_dir, check=True
    )
    short = description[:60].replace('"', "'")
    subprocess.run(
        ["git", "commit", "-q", "-m", f"chore: iterate rite — {short}"],
        cwd=rite_dir,
        check=True,
    )

    _start_loop_session(slug, rite_dir, max_iter)
    print(f"◬ Iterating: {slug}")
    print(f"  → New mission: {description}")
    print(f"  → tmux session: animyst-{slug}")


def attach(slug: str | None = None) -> None:
    _require_tool("tmux")
    if slug is None:
        alive = [r for r in list_rites() if session_alive(r["slug"])]
        if len(alive) == 1:
            slug = alive[0]["slug"]
        elif not alive:
            print("⊘ No live rite sessions.")
            return
        else:
            print("Specify a slug. Active rites:")
            for r in alive:
                print(f"  {r['slug']}")
            return
    if not session_alive(slug):
        sys.stderr.write(f"⊗ No live session for {slug}.\n")
        sys.exit(1)
    os.execvp("tmux", ["tmux", "attach-session", "-t", tmux_session_name(slug)])


def stop(slug: str | None = None) -> None:
    _require_tool("tmux")
    if slug is None:
        any_alive = False
        for r in list_rites():
            if session_alive(r["slug"]):
                any_alive = True
                _stop_one(r["slug"])
        if not any_alive:
            print("⊘ No live sessions.")
        return
    _stop_one(slug)


def _stop_one(slug: str) -> None:
    session = tmux_session_name(slug)
    r = subprocess.run(["tmux", "kill-session", "-t", session], capture_output=True)
    if r.returncode == 0:
        print(f"⊘ Stopped {session}")
    else:
        print(f"  (no live session for {slug})")


def banish(slug: str) -> None:
    r = get_rite(slug)
    if not r:
        sys.stderr.write(f"⊗ Unknown rite: {slug}\n")
        sys.exit(1)
    print("⚠ This will delete:")
    print(f"  Directory:       {r['path']}")
    print(f"  Registry entry:  {slug}")
    try:
        confirm = input(f"Type {slug!r} to confirm: ")
    except EOFError:
        confirm = ""
    if confirm != slug:
        print("Cancelled.")
        return
    subprocess.run(
        ["tmux", "kill-session", "-t", tmux_session_name(slug)], capture_output=True
    )
    shutil.rmtree(r["path"], ignore_errors=True)
    reg = _load_registry()
    reg["rites"] = [x for x in reg["rites"] if x["slug"] != slug]
    _save_registry(reg)
    print(f"⊘ Banished {slug}.")
