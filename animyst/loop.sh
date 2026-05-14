#!/usr/bin/env bash
# loop.sh — ANIMYST rite loop driver
# Usage: loop.sh <rite-dir> [max-iter]
# Runs `claude -p` in a loop until RITE_COMPLETE or max iterations.

set -euo pipefail

RITE_DIR="${1:-$PWD}"
MAX_ITER="${2:-15}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-2}"

if [[ ! -f "$RITE_DIR/RITE.md" ]]; then
  echo "Error: no RITE.md in $RITE_DIR" >&2
  exit 2
fi

cd "$RITE_DIR"
mkdir -p .animyst/logs

DRIVER_PROMPT="Read RITE.md in the current directory. Execute exactly ONE iteration as described in 'Each loop iteration'. Stop after that one iteration — do not loop yourself."

echo "◬ ANIMYST loop awakening for: $RITE_DIR"
echo "  Cap: $MAX_ITER iterations"
echo

for i in $(seq 1 "$MAX_ITER"); do
  PADDED=$(printf '%02d' "$i")
  LOG_FILE=".animyst/logs/iter-${PADDED}.log"

  echo "==> Iteration $i / $MAX_ITER at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  set +e
  claude -p "$DRIVER_PROMPT" \
    --allowedTools "Edit,Write,Bash,Read,Glob,Grep" \
    > "$LOG_FILE" 2>&1
  EXIT=$?
  set -e

  echo "    exit=$EXIT  log=$LOG_FILE"

  if grep -q "RITE_COMPLETE" "$LOG_FILE"; then
    echo
    echo "◬ RITE_COMPLETE on iteration $i. Dormant."
    exit 0
  fi

  if [[ $EXIT -ne 0 ]]; then
    echo "    iteration exited non-zero. Last 20 lines:"
    tail -20 "$LOG_FILE" | sed 's/^/    /'
    echo "    continuing to next iteration."
  fi

  sleep "$SLEEP_BETWEEN"
done

echo
echo "⚠ Hit max iterations ($MAX_ITER) without RITE_COMPLETE."
exit 1
