#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 7 start: $(date -Iseconds)"
"$PY" code/run_phase7.py
echo "[run.sh] phase 7 done:  $(date -Iseconds)"
