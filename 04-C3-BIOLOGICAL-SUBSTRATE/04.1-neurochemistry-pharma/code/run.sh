#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 04.1 start: $(date -Iseconds)"
"$PY" code/run_phase04_1.py
echo "[run.sh] phase 04.1 done:  $(date -Iseconds)"
