#!/bin/bash
# Phase 00.2 — fMRI Eligibility Audit single entry-point.
# Reads cached manifest and emits verdict CSV.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Phase 00.2: fMRI Eligibility Audit ==="
python3 code/run_phase00_2.py

echo ""
echo "=== Done. Verdict at results/00.2_eligibility_correlations.csv ==="
