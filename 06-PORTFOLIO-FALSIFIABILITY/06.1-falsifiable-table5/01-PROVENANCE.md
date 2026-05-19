# Phase 06.1 — Provenance

## Source artefacts (read-only V-Reproduction phases)

- `01-R3-PERCEPTUAL-FRONT-END/01.2-r3-oos-consonance/results/06_r3_oos_correlations.csv`
- `03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward/results/10_cheung_correlations.csv`
- `05-FMRI-BRAIN-GROUNDING/05.2-mech-region-ds002725/results/11_mech_region_correlations.csv`
- `05-FMRI-BRAIN-GROUNDING/05.4-voxelwise-ds003720/results/12_voxelwise_correlations.csv`
- `05-FMRI-BRAIN-GROUNDING/05.1-mendelssohn-pilot/results/13_mendelssohn_correlations.csv`

## Paper anchor

- §Methods §Falsifiable predictions (Musical-Intelligence-corrected-evidence.tex)
- Table 5 (paper)

## Reproduction strategy

Pure aggregation. Reads upstream phase CSVs, looks up the specific claim_id
referenced by each Falsifiable Table 5 row, mirrors verdict. No engine call.

## Derived artefacts

- `results/06.1_falsifiable_table5_correlations.csv` — 5-row aggregated table
- `results/06.1_falsifiable_table5_manifest.json`
