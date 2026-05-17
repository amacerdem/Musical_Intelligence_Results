#!/bin/bash
# Phase 00.3 — Compute Profile cache-anchored verdict.
# The original 15-run benchmark + latency + memory + determinism + aggregate
# scripts are preserved in code/ for transparency but the entry point reads
# the cached manifest produced at engine SHA 318eb2f5... on 2026-05-06.
# Hardware-tier CAVEAT verdicts (C-COMPUTE-01..05) are paper-disclosed
# limitations; only C-COMPUTE-06 determinism is PASS.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Phase 00.3: Compute Profile ==="
python3 code/run_phase00_3.py

echo ""
echo "=== Done. Verdict at results/00.3_compute_profile_correlations.csv ==="
