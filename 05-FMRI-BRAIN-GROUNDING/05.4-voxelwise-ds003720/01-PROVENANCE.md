# Phase 05.4 — Provenance

## Source artefacts (read-only)

### Cycle 17 ds003720 encoding pipeline (preserved)
- `Science/Bold-fMRI/ds003720/06_encoding/C17_deney_1_shuffle_null_results.csv` — per-subject × per-encoder shuffle-null pass at q<0.05
- `Science/Bold-fMRI/ds003720/06_encoding/C17_deney_2_ridge_loso.csv` — per-subject × per-encoder Ridge 5-fold held-out top-5% r
- `Science/Bold-fMRI/ds003720/06_encoding/C17_deney_3b_cka_vs_bold.csv` — per-subject × per-encoder CKA encoder vs BOLD

### V6 A3 banded-ridge variance partitioning (preserved)
- `Science/V6/results/A3_per_subject.csv` — 4 subjects × MI-unique / MERT-unique / shared R² with 95% CI
- `Science/V6/results/A3_summary.json` — composite verdict + n_ci_excludes_0
- `Science/V6/code/A3_banded_ridge/run_banded_ridge.py` — pipeline script

### V2 paper-anchor tex
- `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/Divan-Draft/versions/main-v9.5.7-cycle-17-ds003720.tex` — paper claim source for MI=0.165, MI-naive=0.084, Random-26=0.090, Random-768=0.121, CLAP-512=0.138, MERT-768=0.221, CKA(MI-full, MI-naive)=0.994

### Phase 0.5 dependency
- ds003720 mi_compatible=True, n_alignment_qualified=4 (≥4 required entry condition)

### Paper anchor (canonical)
- §Additional architectural-signature evidence + §Discussion (Musical-Intelligence-corrected-evidence.tex)

## Reproduction strategy

V2 + V6 ran the analyses end-to-end on engine HEAD `318eb2f5` (frozen). Phase 05.4
reads preserved CSVs/JSON and computes Fisher-z mean held-out r per encoder
across 4 subjects. No engine re-execution required (engine bit-determinism
re-confirmed by Phases 0/2/6/7/8/9 canaries).

## Derived artefacts

- `results/05.4_voxelwise_correlations.csv` — 11-row claim verdict
- `results/05.4_voxelwise_manifest.json`
