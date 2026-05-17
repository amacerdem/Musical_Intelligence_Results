#!/usr/bin/env bash
# Phase 05.4 — Cross-subject voxelwise routing-ablation (ds003720).
#
# Modes:
#   default                Audit mode: verify pre-computed C17_*.csv outputs vs paper.
#                          Wall: <1 s. No external data needed.
#
#   --raw-rerun            Full-pipeline mode: re-derive C17_deney_*.csv from raw BIDS
#                          using vendored Cycle 17 scripts.
#                          REQUIRES:
#                            - ds003720 BIDS at datasets/neuroimaging/ds003720/
#                              (fetch via _infra/download_datasets.sh --datasets ds003720)
#                            - fmriprep-preprocessed BOLD outputs (user provides)
#                            - Stimulus audio for 25 song clips (Daly et al. 2020)
#                          Wall: ~2 hours (encoding + ridge LOSO + CKA on N=4 QC-pass)
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
    echo "[phase05_4] raw-rerun mode: regenerating C17_deney_*.csv"
    C17_DIR="$VREPRO_ROOT/datasets/paper-anchors/voxelwise-encoding"
    CKPT_BOLD="$C17_DIR/ckpt_bold"

    if [ ! -d "$C17_DIR" ] || [ ! -f "$C17_DIR/C17_deney_2_ridge_loso.py" ]; then
        echo "[phase05_4] ERROR: Cycle 17 scripts not vendored at $C17_DIR"
        echo "          Run: bash _infra/vendor_paper_capture.sh"
        exit 1
    fi

    if [ -d "$CKPT_BOLD" ] && [ "$(ls "$CKPT_BOLD"/*.npy 2>/dev/null | wc -l | tr -d ' ')" -ge 4 ]; then
        echo "[phase05_4] using vendored ckpt_bold ($CKPT_BOLD, $(ls "$CKPT_BOLD"/*.npy | wc -l | tr -d ' ') BOLD .npy files)"
        cd "$C17_DIR"
        echo "[phase05_4] [1/3] C17_deney_2_ridge_loso.py — ridge LOSO held-out r"
        python3 C17_deney_2_ridge_loso.py 2>&1 | tail -3 || { echo "Failed"; cd "$PHASE_DIR"; exit 1; }
        echo "[phase05_4] [2/3] C17_deney_1_shuffle_null_cross_subject.py — shuffle null"
        python3 C17_deney_1_shuffle_null_cross_subject.py 2>&1 | tail -3 || { echo "Failed"; cd "$PHASE_DIR"; exit 1; }
        echo "[phase05_4] [3/3] C17_deney_3b_cka_vs_bold.py — CKA (optional)"
        python3 C17_deney_3b_cka_vs_bold.py 2>&1 | tail -3 || echo "[phase05_4] CKA optional, skipped"
        cd "$PHASE_DIR"
        echo "[phase05_4] Cycle 17 pipeline complete. C17_*.csv re-derived."
    else
        # Fallback: raw BIDS + fmriprep (advanced)
        BIDS="$VREPRO_ROOT/datasets/neuroimaging/ds003720"
        if [ ! -d "$BIDS" ]; then
            echo "[phase05_4] ERROR: vendored ckpt_bold missing AND raw BIDS not found"
            echo "          Vendored expected at: $CKPT_BOLD"
            echo "          OR fetch raw BIDS: bash _infra/download_datasets.sh --datasets ds003720"
            exit 1
        fi
        echo "[phase05_4] BIDS path raw-rerun (advanced) — see RAW_RERUN.md"
        exit 1
    fi
fi

# Audit mode: verify CSVs against paper headlines (always runs)
echo "[phase05_4] audit mode: verifying C17_*.csv vs paper claims"
python3 code/run_phase05_4.py
