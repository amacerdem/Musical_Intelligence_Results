# Phase 06.1 — Provenance

## Source artefacts (read-only V-Reproduction phases)

- `Science/V-Reproduction/06-r3-oos-consonance/results/06_r3_oos_correlations.csv`
- `Science/V-Reproduction/10-cheung-emergent-reward/results/10_cheung_correlations.csv`
- `Science/V-Reproduction/11-mech-region-encoding/results/11_mech_region_correlations.csv`
- `Science/V-Reproduction/12-voxelwise-ds003720/results/12_voxelwise_correlations.csv`
- `Science/V-Reproduction/13-mendelssohn-pilot/results/13_mendelssohn_correlations.csv`

## Paper anchor

- §Methods §Falsifiable predictions (Musical-Intelligence-corrected-evidence.tex)
- Table 5 (paper)

## Reproduction strategy

Pure aggregation. Reads upstream phase CSVs, looks up the specific claim_id
referenced by each Falsifiable Table 5 row, mirrors verdict. No engine call.

## Derived artefacts

- `results/06.1_falsifiable_table5_correlations.csv` — 5-row aggregated table
- `results/06.1_falsifiable_table5_manifest.json`
