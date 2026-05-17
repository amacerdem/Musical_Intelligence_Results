#!/usr/bin/env bash
# Phase 05.7.1 canonical runner.
# Status: EXEC-PENDING external audio fetch.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 code/run_phase05_7_1.py
