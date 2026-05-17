#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 10 start: $(date -Iseconds)"
"$PY" code/run_phase10.py
echo "[run.sh] phase 10 done:  $(date -Iseconds)"
