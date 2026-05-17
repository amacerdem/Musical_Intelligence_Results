# Phase 05.1 — Provenance

## Source artefacts (read-only)

### V2 GT-0016 cross-subject extension (preserved)
- `Science/V2/results/GT-0016-cross-subject/cross_subject_summary.json`
- `Science/V2/results/GT-0016-cross-subject/cross_subject_headtohead.csv`
- `Science/V2/results/GT-0016-cross-subject/supplementary_posthoc_max_r.csv`
- `Science/V2/results/GT-0016-cross-subject/cross_subject_report.md`

### V2 fig1_reinforcement (sub-08 paper-time TR 556)
- `Science/V2/results/fig1_reinforcement/sub08_mendelssohn_smoke.csv` — Method A + Method B per-region

### V2 deneyler rescore (Mendelssohn piece-specificity)
- `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/open-validation/R1/v9.5.6-ds002725-deneyler-rescore.md` — rank 1/7 + 2.2× lift documentation

### Paper anchor
- §Single-subject pilot scope + §Limitations Single-subject pilot
- Figure 1a caption (paper text)
- §Methods §fMRI Method A/B

## Reproduction strategy

V2 ran the analyses end-to-end on engine HEAD `318eb2f5`. Phase 05.1 reads
preserved CSVs/JSON and verifies 6 paper claims. No engine re-execution.

## Derived artefacts

- `results/05.1_mendelssohn_correlations.csv`
- `results/05.1_mendelssohn_manifest.json`
