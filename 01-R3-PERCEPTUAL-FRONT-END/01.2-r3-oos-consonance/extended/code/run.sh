#!/usr/bin/env bash
# Phase 6 extended single entry point — R³ extended OOS consonance battery.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 6 extended start: $(date -Iseconds)"
"$PY" code/run_extended.py
echo "[run.sh] phase 6 extended done:  $(date -Iseconds)"
