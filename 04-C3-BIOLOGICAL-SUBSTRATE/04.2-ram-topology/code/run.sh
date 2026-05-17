#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 04.2 start: $(date -Iseconds)"
"$PY" code/run_phase04_2.py
echo "[run.sh] phase 04.2 done:  $(date -Iseconds)"
