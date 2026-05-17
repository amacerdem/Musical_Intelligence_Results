# Phase 04.2 — Provenance / Chain of Custody

## Source artefacts (read-only)

### Engine
- HEAD: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- This phase is CSV-anchored — verifies pre-computed V2 T-R1-08 permutation-null statistics, no live engine run

### Paper anchor
- §Additional architectural-signature evidence (Musical-Intelligence-corrected-evidence.tex) — `28/31 (90.3%) ≤10mm under two independent permutation nulls (p<0.0001 each), 26/29 no-proxy robustness, radii 8/10/12 mm`
- Methods §Coord match — radius-stability rationale

### V2 stored RAM permutation-null artefacts (T-R1-08)
- `literature_coords_32.csv` — 31-row coord-eligible literature peak set
- `permutation_null_results.csv` — observed/n_tests/p_value × {null_design, radius_mm}
- `permutation_null_results_no_proxy.csv` — 26/29 robustness without atlas-proxy row
- `match_table_by_radius.csv` — per-row distance @ 8/10/12 mm

All four are vendored under `datasets/paper-anchors/ram-topology/`. Original V2 path: `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R1-08/`.

## Reproduction strategy

Direct CSV-anchored verification: read the headline rows from `permutation_null_results.csv` at radius=10mm under both Null-1 (centroid-relocation) and Null-2 (label-shuffle) designs; iterate {8, 10, 12} mm for radius-stability; cross-check no-proxy table for the 26/29 robustness row.

## Derived artefacts (this phase produces)

- `results/04.2_ram_topology_correlations.csv` — 5 claim-level rows
- `results/04.2_ram_topology_manifest.json`
- `results/peak_match_per_row.csv` — auxiliary per-row distance dump (carried forward from V2 audit)
