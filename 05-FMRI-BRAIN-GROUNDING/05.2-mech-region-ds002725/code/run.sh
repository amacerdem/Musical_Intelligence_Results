#!/usr/bin/env bash
# Phase 05.2 — Mech × Region Encoding (ds002725).
#
# Modes:
#   default                Audit mode: verify pre-computed V3 capture CSVs vs paper.
#                          Wall: <1 s. No external data needed.
#
#   --raw-rerun            Full-pipeline mode: re-derive pair_evidence_ds002725.csv
#                          from raw BIDS using vendored V3 pipeline scripts.
#                          REQUIRES:
#                            - ds002725 BIDS at datasets/neuroimaging/ds002725/
#                              (fetch via _infra/download_datasets.sh --datasets ds002725)
#                            - fmriprep-preprocessed BOLD outputs (user provides)
#                            - Stimulus audio for 7 classical pieces
#                          See RAW_RERUN.md for fmriprep setup steps.
#                          Wall: hours (fmriprep external; encoding ~30 min on M2)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PHASE_DIR="$(cd "$HERE/.." && pwd)"
VREPRO_ROOT="$(cd "$PHASE_DIR/.." && pwd)"
cd "$PHASE_DIR"

MODE="audit"
for arg in "$@"; do
    case "$arg" in
        --raw-rerun) MODE="raw-rerun" ;;
        *) echo "Unknown arg: $arg"; exit 1 ;;
    esac
done

if [ "$MODE" = "raw-rerun" ]; then
    echo "[phase05_2] raw-rerun mode: regenerating pair_evidence_ds002725.csv from V3 pipeline"
    V3_CODE="$VREPRO_ROOT/datasets/paper-anchors/mech-region/v3-code"
    BOLD_26="$VREPRO_ROOT/datasets/paper-anchors/mech-region/bold-26region"
    MI_FEAT="$VREPRO_ROOT/datasets/paper-anchors/mech-region/data"

    # Vendored intermediates check (preferred path: no fmriprep needed)
    if [ -d "$V3_CODE" ] && [ -d "$BOLD_26/checkpoints" ] && [ -d "$MI_FEAT/mech_features" ]; then
        echo "[phase05_2] using vendored intermediates:"
        echo "          BOLD-26region: $BOLD_26/checkpoints ($(ls "$BOLD_26/checkpoints" | wc -l | tr -d ' ') subjects)"
        echo "          MI features:   $MI_FEAT/mech_features ($(du -sh "$MI_FEAT/mech_features" | awk '{print $1}'))"
        echo "[phase05_2] running V3 run_analysis.py..."
        cd "$V3_CODE"
        python3 run_analysis.py \
            --skip-existing 2>/dev/null \
            || { echo "[phase05_2] V3 pipeline failed"; cd "$PHASE_DIR"; exit 1; }
        cd "$PHASE_DIR"
        echo "[phase05_2] V3 pipeline complete. pair_evidence_ds002725.csv re-derived."
    else
        # Fallback path: raw BIDS + fmriprep (advanced users)
        BIDS="$VREPRO_ROOT/datasets/neuroimaging/ds002725"
        if [ ! -d "$BIDS" ]; then
            echo "[phase05_2] ERROR: vendored intermediates missing AND raw BIDS not found"
            echo "          Vendored expected at: $BOLD_26/checkpoints + $MI_FEAT/mech_features"
            echo "          OR fetch raw BIDS: bash _infra/download_datasets.sh --datasets ds002725"
            exit 1
        fi
        if [ ! -d "$BIDS/derivatives/fmriprep" ]; then
            echo "[phase05_2] ERROR: vendored intermediates missing AND fmriprep output not found"
            echo "          See RAW_RERUN.md for fmriprep setup."
            exit 1
        fi
        echo "[phase05_2] BIDS path raw-rerun (advanced) — see RAW_RERUN.md"
        exit 1  # Advanced path requires manual orchestration; not yet automated
    fi
fi

# Audit mode: verify CSV against paper headlines (always runs)
echo "[phase05_2] audit mode: verifying pair_evidence_ds002725.csv vs paper claims"
python3 code/run_phase05_2.py
