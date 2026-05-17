#!/bin/bash
# Phase 1 single entry-point — Architectural Cardinalities.
# Reads V2 T-R1-10-R3-04 paper-anchor classifier output.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Phase 1: Architectural Cardinalities ==="
python3 code/run_phase1.py

echo ""
echo "=== Done. Verdict at results/01_cardinalities_correlations.csv ==="
