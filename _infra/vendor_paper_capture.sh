#!/usr/bin/env bash
# Vendor paper-time anchors from parent Science/ tree into V-Reproduction.
# Run once by the maintainer (Amaç) to bootstrap the self-contained
# V-Repro snapshot.
#
# After running, V-Reproduction is independent of the parent Science/
# tree for paper-time anchors. Phase scripts find them at
# `V-Repro/datasets/paper-anchors/<scientific-purpose>/`.
#
# Layout (organised by scientific purpose, NOT by lab cycle name):
#
#   paper-anchors/
#     r3-ground-truth/         R³ DEV stimulus + per-group reports
#     c3-aggregates/           F1-F8 mech pass rates + F3 dim-level
#     bb-fdr/                  Paper-wide 1,496-test BB-FDR registry
#     mech-region/             ds002725 22-pair encoding + V3 pipeline
#     voxelwise-encoding/      ds003720 Cycle 17 routing-ablation
#     cross-cultural/          V4 + V5 anchor reproduction
#     ece-calibration/         ECE 0.079 + Brier 10.8× capture
#     voxelwise-A3/            V6 A3 banded-ridge variance partitioning
#     cheung-reward/           Cheung 2019 emergent reward
#     cardinality/             16,191 numeric constants AST inventory
#     ram-topology/            RAM 28/31 paper-anchor
#     mendelssohn-pilot/       sub-08 illustrative + cross-subject N=17
#     r3-oos/                  R³ OOS Stumpf-relabel + Carillon
#     neurochemicals/          Pharma 11/11 + reward sensitivity
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VREPRO_ROOT="$(cd "$HERE/.." && pwd)"
SCIENCE_ROOT="$(cd "$VREPRO_ROOT/.." && pwd)"
ANCH="$VREPRO_ROOT/datasets/paper-anchors"

# Source paths in parent Science/
S_V1="$SCIENCE_ROOT/V1"
S_V2="$SCIENCE_ROOT/V2"
S_V3="$SCIENCE_ROOT/V3"
S_V4="$SCIENCE_ROOT/V4"
S_V5="$SCIENCE_ROOT/V5"
S_V6="$SCIENCE_ROOT/V6"
S_BOLD="$SCIENCE_ROOT/Bold-fMRI"
S_TR2="$S_V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase"

echo "[vendor] paper-anchors → $ANCH"
mkdir -p "$ANCH"

# ─── r3-ground-truth ────────────────────────────────────────────────
echo "[vendor] r3-ground-truth (V1 r3 per-group reports + intervals + Bowling)"
mkdir -p "$ANCH/r3-ground-truth/r3-reports" "$ANCH/r3-ground-truth/intervals"
rsync -a --exclude="__pycache__" "$S_V1/results/r3/" "$ANCH/r3-ground-truth/r3-reports/"
rsync -a "$S_V1/stimuli/intervals/" "$ANCH/r3-ground-truth/intervals/"

# ─── c3-aggregates ──────────────────────────────────────────────────
echo "[vendor] c3-aggregates (F1-F8 paper headlines + F3 dim-level)"
mkdir -p "$ANCH/c3-aggregates"
rsync -a --exclude="__pycache__" "$S_V1/results/All_Results/" "$ANCH/c3-aggregates/All_Results/"
rsync -a --exclude="__pycache__" "$S_V1/results/f1/bch/" "$ANCH/c3-aggregates/f1_bch/"
rsync -a --exclude="__pycache__" "$S_V2/results/GT-0019/" "$ANCH/c3-aggregates/GT-0019/"

# ─── bb-fdr ─────────────────────────────────────────────────────────
echo "[vendor] bb-fdr (paper-wide 1,496-test registry)"
mkdir -p "$ANCH/bb-fdr"
rsync -a --exclude="__pycache__" "$S_V2/results/GT-0006/" "$ANCH/bb-fdr/"

# ─── mech-region (Phase 11 + V3 pipeline + 692 MB mech_features + 1.1 MB BOLD) ─
echo "[vendor] mech-region (V3 + Bold-fMRI exp-02 + ckpt + mech_features 692 MB)"
mkdir -p "$ANCH/mech-region/v3-results" "$ANCH/mech-region/v3-code"
rsync -a --exclude="__pycache__" "$S_V3/results/" "$ANCH/mech-region/v3-results/"
rsync -a --exclude="__pycache__" --exclude=".pytest_cache" "$S_V3/code/" "$ANCH/mech-region/v3-code/"
if [ -d "$S_V3/V3-comprehensive" ]; then
    mkdir -p "$ANCH/mech-region/v3-comprehensive"
    rsync -a --exclude="__pycache__" --exclude=".pytest_cache" \
        --exclude="*.nii.gz" --exclude="*.nii" \
        "$S_V3/V3-comprehensive/" "$ANCH/mech-region/v3-comprehensive/"
fi
# Phase 11 raw-rerun intermediate: 26-region BOLD checkpoints (1.1 MB)
if [ -d "$S_BOLD/exp-02-cross-subject-17" ]; then
    mkdir -p "$ANCH/mech-region/bold-26region"
    rsync -a "$S_BOLD/exp-02-cross-subject-17/" "$ANCH/mech-region/bold-26region/"
fi
# Phase 11 raw-rerun: pre-extracted MI features (692 MB)
if [ -d "$S_V3/data" ]; then
    mkdir -p "$ANCH/mech-region/data"
    rsync -a --exclude="__pycache__" "$S_V3/data/" "$ANCH/mech-region/data/"
fi

# ─── voxelwise-encoding (Phase 12) ──────────────────────────────────
echo "[vendor] voxelwise-encoding (Cycle 17 ds003720 + RunPod ckpt_bold)"
mkdir -p "$ANCH/voxelwise-encoding"
if [ -d "$S_BOLD/ds003720/06_encoding" ]; then
    rsync -a "$S_BOLD/ds003720/06_encoding/" "$ANCH/voxelwise-encoding/"
fi
if [ -d "$S_TR2/T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold" ]; then
    mkdir -p "$ANCH/voxelwise-encoding/ckpt_bold"
    rsync -a "$S_TR2/T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold/" \
        "$ANCH/voxelwise-encoding/ckpt_bold/"
fi

# ─── cross-cultural (Phase 14) ──────────────────────────────────────
echo "[vendor] cross-cultural (V4 NHS + Hindustani + Mridangam + V5 Pakistan/bonang)"
mkdir -p "$ANCH/cross-cultural/v4" "$ANCH/cross-cultural/v5"
rsync -a --exclude="__pycache__" "$S_V4/results/" "$ANCH/cross-cultural/v4/"
rsync -a --exclude="__pycache__" "$S_V5/results/" "$ANCH/cross-cultural/v5/"

# ─── ece-calibration + voxelwise-A3 (Phase 5 + 12) ──────────────────
echo "[vendor] ece-calibration (V6 A2 ECE + paper-evidence) + voxelwise-A3 (V6 A3)"
mkdir -p "$ANCH/ece-calibration" "$ANCH/voxelwise-A3"
# V6 A2 (ECE) artefacts → ece-calibration; V6 A3 (voxelwise) → voxelwise-A3
for f in "$S_V6/results"/A2_*; do
    [ -e "$f" ] && cp -r "$f" "$ANCH/ece-calibration/"
done
for f in "$S_V6/results"/A3_*; do
    [ -e "$f" ] && cp -r "$f" "$ANCH/voxelwise-A3/"
done

# ─── cheung-reward (Phase 10) ───────────────────────────────────────
echo "[vendor] cheung-reward (V2 T-R2-04 + V1 reward_sensitivity)"
mkdir -p "$ANCH/cheung-reward"
if [ -d "$S_TR2/T-R2-04" ]; then
    rsync -a --exclude="__pycache__" "$S_TR2/T-R2-04/" "$ANCH/cheung-reward/"
fi
[ -f "$S_V1/results/reward_sensitivity_analysis.md" ] && \
    cp "$S_V1/results/reward_sensitivity_analysis.md" "$ANCH/cheung-reward/"

# ─── cardinality (Phase 1) ──────────────────────────────────────────
echo "[vendor] cardinality (V2 T-R1-10-R3-04 16,191 constants)"
mkdir -p "$ANCH/cardinality"
if [ -d "$S_TR2/T-R1-10-R3-04" ]; then
    rsync -a --exclude="__pycache__" "$S_TR2/T-R1-10-R3-04/" "$ANCH/cardinality/"
fi

# ─── ram-topology (Phase 9) ─────────────────────────────────────────
echo "[vendor] ram-topology (V2 T-R1-08 28/31 paper-anchor)"
mkdir -p "$ANCH/ram-topology"
if [ -d "$S_TR2/T-R1-08" ]; then
    rsync -a --exclude="__pycache__" "$S_TR2/T-R1-08/" "$ANCH/ram-topology/"
fi

# ─── mendelssohn-pilot (Phase 13) ───────────────────────────────────
echo "[vendor] mendelssohn-pilot (V2 GT-0016 + fig1_reinforcement)"
mkdir -p "$ANCH/mendelssohn-pilot/GT-0016-cross-subject" "$ANCH/mendelssohn-pilot/fig1_reinforcement"
[ -d "$S_V2/results/GT-0016-cross-subject" ] && \
    rsync -a "$S_V2/results/GT-0016-cross-subject/" "$ANCH/mendelssohn-pilot/GT-0016-cross-subject/"
[ -d "$S_V2/results/fig1_reinforcement" ] && \
    rsync -a "$S_V2/results/fig1_reinforcement/" "$ANCH/mendelssohn-pilot/fig1_reinforcement/"

# ─── r3-oos (Phase 6) ───────────────────────────────────────────────
echo "[vendor] r3-oos (V2 stumpf-relabel-audit + Carillon sweep)"
mkdir -p "$ANCH/r3-oos"
if [ -d "$S_V2/results/stumpf-relabel-audit" ]; then
    rsync -a "$S_V2/results/stumpf-relabel-audit/" "$ANCH/r3-oos/"
fi

# ─── neurochemicals (Phase 8) ───────────────────────────────────────
echo "[vendor] neurochemicals (V1 neurochem 132/132 + 11/11 pharma)"
mkdir -p "$ANCH/neurochemicals"
if [ -d "$S_V1/results/neurochemicals" ]; then
    rsync -a "$S_V1/results/neurochemicals/" "$ANCH/neurochemicals/"
fi

# ─── Consonance CSVs (Phase 6 + 7, redistributable public data) ─────
echo "[vendor] datasets/consonance: bowling, eerola, marjieh, harrison-carillon CSVs"
mkdir -p "$VREPRO_ROOT/datasets/consonance/marjieh2024/data-csv"
mkdir -p "$VREPRO_ROOT/datasets/consonance/harrison2024_carillon"
[ -f "$SCIENCE_ROOT/datasets/consonance/bowling2018_dyad_ratings.csv" ] && \
    cp "$SCIENCE_ROOT/datasets/consonance/bowling2018_dyad_ratings.csv" \
       "$VREPRO_ROOT/datasets/consonance/"
[ -f "$SCIENCE_ROOT/datasets/consonance/eerola2021_exp3.csv" ] && \
    cp "$SCIENCE_ROOT/datasets/consonance/eerola2021_exp3.csv" \
       "$VREPRO_ROOT/datasets/consonance/"
if [ -d "$SCIENCE_ROOT/datasets/consonance/marjieh2024/data-csv" ]; then
    rsync -a "$SCIENCE_ROOT/datasets/consonance/marjieh2024/data-csv/" \
        "$VREPRO_ROOT/datasets/consonance/marjieh2024/data-csv/"
fi
if [ -d "$SCIENCE_ROOT/datasets/consonance/harrison2024_carillon" ]; then
    rsync -a "$SCIENCE_ROOT/datasets/consonance/harrison2024_carillon/" \
        "$VREPRO_ROOT/datasets/consonance/harrison2024_carillon/"
fi

# ─── DEAM 5 ECE held-out songs (Phase 5) ────────────────────────────
echo "[vendor] DEAM: 5 specific held-out songs (3.6 MB) — CC-BY-NC-SA"
mkdir -p "$VREPRO_ROOT/datasets/emotion/DEAM/audio/MEMD_audio"
for sid in 1034 1508 1777 1896 1923; do
    SRC="$SCIENCE_ROOT/datasets/emotion/DEAM/audio/MEMD_audio/${sid}.mp3"
    if [ -f "$SRC" ]; then
        cp "$SRC" "$VREPRO_ROOT/datasets/emotion/DEAM/audio/MEMD_audio/"
    fi
done

cat > "$VREPRO_ROOT/datasets/emotion/DEAM/README.md" <<'EOF'
# DEAM dataset (vendored subset)

Vendored: 5 specific held-out songs (1034, 1508, 1777, 1896, 1923) used by
Phase 5 ECE for pooled ECE = 0.079 measurement on N=206,080 frames.

**Source:** DEAM v1 — Aljanaki, Yang, Soleymani 2017, *PLoS ONE*.
**License:** CC BY-NC-SA 4.0 (academic use, attribution required).

For the full DEAM corpus, run `_infra/download_datasets.sh --datasets deam`.
EOF

echo
echo "=================================================================="
echo "Paper anchors vendored (organised by scientific purpose):"
du -sh "$ANCH"/*/ 2>&1 | sort -k1 -h
echo "Total paper-anchors: $(du -sh "$ANCH" | awk '{print $1}')"
echo
echo "Total V-Repro datasets/: $(du -sh "$VREPRO_ROOT/datasets" | awk '{print $1}')"
echo "=================================================================="
