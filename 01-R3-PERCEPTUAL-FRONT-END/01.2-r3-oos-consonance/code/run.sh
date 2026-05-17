#!/usr/bin/env bash
# Phase 6 single entry point — V-Reproduction R³ OOS consonance.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/.."
PY="${PYTHON:-python3}"
echo "[run.sh] phase 6 start: $(date -Iseconds)"
"$PY" code/run_phase6.py
echo "[run.sh] phase 6 done:  $(date -Iseconds)"
