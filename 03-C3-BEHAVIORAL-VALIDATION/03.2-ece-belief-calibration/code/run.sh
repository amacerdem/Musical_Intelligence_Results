#!/bin/bash
# V-Reproduction/05-ece-belief-calibration — Single-command reproduction
#
# Reproduces:
#   - Pooled ECE = 0.0841 on paper's 8 beliefs (paper claim: 0.079, deviation +0.005)
#   - Extension test on 6 additional beliefs (F3-F8); F7 GrooveQuality is the only outlier
#
# Engine pin: 318eb2f5 (V-Reproduction frozen HEAD, bit-identical |Δ|=0)
# Engine path resolution (audit-grade, vendored-first):
#   1) V-Reproduction/engine/Musical_Intelligence/  (vendored flat snapshot)
#   2) Science/Musical_Intelligence/  (parent-checkout fallback)
#
# Wall-clock: ~5 min extract + ~10 min compute_metrics on M2 8 GB

set -euo pipefail

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ECE_ROOT="$( cd "$HERE/.." && pwd )"
VREPRO_ROOT="$( cd "$ECE_ROOT/.." && pwd )"
SCIENCE_ROOT="$( cd "$VREPRO_ROOT/.." && pwd )"

echo "================================================================"
echo "V-Reproduction/05-ece-belief-calibration — single-command reproduction"
echo "================================================================"
echo "ECE_ROOT:     $ECE_ROOT"
echo "VREPRO_ROOT:  $VREPRO_ROOT"
echo "SCIENCE_ROOT: $SCIENCE_ROOT"
echo

# 1. Activate venv (vendored under V-Repro first, then Science)
if [ -f "$VREPRO_ROOT/.venv/bin/activate" ]; then
    echo "[run] activating $VREPRO_ROOT/.venv ..."
    source "$VREPRO_ROOT/.venv/bin/activate"
elif [ -f "$SCIENCE_ROOT/.venv/bin/activate" ]; then
    echo "[run] activating $SCIENCE_ROOT/.venv ..."
    source "$SCIENCE_ROOT/.venv/bin/activate"
else
    echo "[run] WARNING: no .venv found; using system python"
fi

# 2. Verify engine present (vendored first, then parent fallback)
if [ -d "$VREPRO_ROOT/engine/Musical_Intelligence" ]; then
    export PYTHONPATH="$VREPRO_ROOT/engine:${PYTHONPATH:-}"
    echo "[run] using vendored engine at $VREPRO_ROOT/engine/Musical_Intelligence (HEAD 318eb2f5)"
elif [ -d "$SCIENCE_ROOT/Musical_Intelligence" ]; then
    export PYTHONPATH="$SCIENCE_ROOT:${PYTHONPATH:-}"
    echo "[run] using parent engine at $SCIENCE_ROOT/Musical_Intelligence"
else
    echo "[run] ERROR: engine not found at either $VREPRO_ROOT/engine/ or $SCIENCE_ROOT/" >&2
    exit 1
fi

# 3. Verify DEAM songs cached (datasets path: vendored datasets/ first, then Science fallback)
if [ -d "$VREPRO_ROOT/datasets/emotion/DEAM/audio/MEMD_audio" ]; then
    DEAM="$VREPRO_ROOT/datasets/emotion/DEAM/audio/MEMD_audio"
else
    DEAM="$SCIENCE_ROOT/datasets/emotion/DEAM/audio/MEMD_audio"
fi
for sid in 1034 1508 1777 1896 1923; do
    if [ ! -f "$DEAM/$sid.mp3" ]; then
        echo "[run] ERROR: DEAM song $sid.mp3 missing at $DEAM" >&2
        exit 1
    fi
done
echo "[run] all 5 DEAM held-out songs verified"

# 4. Phase 1 — extract belief traces
echo
echo "[run] Phase 1 — extracting (π_pred, PE) traces from 14 beliefs × 5 songs..."
python3 "$HERE/extract_belief_traces.py"

# 5. Phase 2 — compute metrics
echo
echo "[run] Phase 2 — computing ECE + Brier + null + reliability..."
python3 "$HERE/compute_metrics.py"

# 6. Phase 3 — generate figures (if matplotlib available)
echo
echo "[run] Phase 3 — generating reliability diagrams..."
python3 "$HERE/plot_reliability.py" || echo "[run] WARNING: figure generation failed (non-fatal)"

echo
echo "================================================================"
echo "Reproduction complete. Results at:"
echo "  $ECE_ROOT/results/A2_summary.json"
echo "  $ECE_ROOT/results/A2_per_cell_ece.csv"
echo "  $ECE_ROOT/figures/"
echo "================================================================"
