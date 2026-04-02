#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${ROOT_DIR}/.codex/ralph-logs"
RALPH_BIN="${RALPH_BIN:-ralph}"
RALPH_CMD="${RALPH_CMD:-$RALPH_BIN loop}"
RUN_PUSH="${RUN_PUSH:-0}"

PHASES=(
  "00-bootstrap"
  "01-domain-storage"
  "02-commands-services"
  "03-history"
  "04-ui-split"
  "05-verify-docs"
)

mkdir -p "${LOG_DIR}"

phase_task() {
  echo "${ROOT_DIR}/docs/ralph-tasks/$1.md"
}

phase_prompt() {
  echo "${ROOT_DIR}/docs/ralph-prompts/$1.md"
}

run_phase() {
  local phase="$1"
  local task_file
  local prompt_file
  local log_file

  task_file="$(phase_task "${phase}")"
  prompt_file="$(phase_prompt "${phase}")"
  log_file="${LOG_DIR}/${phase}.log"

  if [[ ! -f "${task_file}" || ! -f "${prompt_file}" ]]; then
    echo "Missing Ralph files for phase ${phase}" >&2
    exit 1
  fi

  echo "==> Running ${phase}"
  echo "Task: ${task_file}"
  echo "Prompt: ${prompt_file}"
  echo "Log: ${log_file}"

  {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] phase=${phase}"
    echo "task=${task_file}"
    echo "prompt=${prompt_file}"
  } >> "${log_file}"

  if ! command -v "${RALPH_BIN}" >/dev/null 2>&1; then
    echo "Ralph binary '${RALPH_BIN}' not found." | tee -a "${log_file}"
    echo "Set RALPH_BIN or RALPH_CMD, then rerun." | tee -a "${log_file}"
    exit 1
  fi

  # shellcheck disable=SC2086
  ${RALPH_CMD} --task "${task_file}" --prompt-file "${prompt_file}" | tee -a "${log_file}"
}

run_all() {
  local phase
  for phase in "${PHASES[@]}"; do
    run_phase "${phase}"
  done
}

verify() {
  python3 -m pytest
  git status --short
  if [[ "${RUN_PUSH}" == "1" ]]; then
    git push
  fi
}

usage() {
  cat <<'EOF'
Usage:
  ./ralph.sh bootstrap
  ./ralph.sh run <phase>
  ./ralph.sh resume <phase>
  ./ralph.sh run-all
  ./ralph.sh verify

Environment:
  RALPH_BIN   Ralph executable name (default: ralph)
  RALPH_CMD   Full Ralph command prefix (default: "$RALPH_BIN loop")
  RUN_PUSH    Set to 1 to allow git push during verify
EOF
}

case "${1:-}" in
  bootstrap)
    run_phase "00-bootstrap"
    ;;
  run)
    [[ -n "${2:-}" ]] || { usage; exit 1; }
    run_phase "${2}"
    ;;
  resume)
    [[ -n "${2:-}" ]] || { usage; exit 1; }
    run_phase "${2}"
    ;;
  run-all)
    run_all
    ;;
  verify)
    verify
    ;;
  *)
    usage
    exit 1
    ;;
esac
