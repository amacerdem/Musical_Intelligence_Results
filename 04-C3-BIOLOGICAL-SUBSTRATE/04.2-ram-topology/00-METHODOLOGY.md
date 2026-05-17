# Phase 04.2 — RAM Topology — Methodology (LOCKED 2026-05-07)

**Section:** 04 — C³ Biological Substrate
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1. Scope

Phase 04.2 reproduces 5 RAM-topology paper anchors (paper §Additional architectural-signature evidence + Table tab:fmri):

- 28/31 fMRI peaks ≤10mm in MNI152 across 7 studies (N=104)
- p<0.0001 under Null-1 centroid-relocation (10K perms)
- p<0.0001 under Null-2 label-shuffle (10K perms)
- 26/29 no-proxy robustness (paper line 1322)
- 28 matches stable across 8/10/12 mm radii (paper Methods §Coord match)

## 2. Reproduction strategy

V3 audit-anchored against the V2 T-R1-08 preserved permutation-null artefacts (vendored under `datasets/paper-anchors/ram-topology/`):

1. `literature_coords_32.csv` — 31-row coord-eligible subset (1 atlas-centroid-proxy pre-excluded by filename convention)
2. `permutation_null_results.csv` — observed 28/31 @ 10mm under both nulls + per-radius rows
3. `permutation_null_results_no_proxy.csv` — 26/29 robustness without the atlas-proxy row
4. `match_table_by_radius.csv` — per-row distances @ 8/10/12 mm

The verification reads the headline `(observed, n_tests, p_value)` triple at radius=10mm + Null-1 and Null-2 designs, then iterates across {8, 10, 12} mm to confirm the radius-robust claim.

## 3. Per-claim paper values + tolerances

| Claim ID | Paper value | Source | Tolerance |
|---|---|---|---|
| C-RAM-COORD-28-31 | 28/31 @ ≤10mm | permutation_null_results.csv | exact_match (numerator + denominator) |
| C-RAM-NULL-1-CENTROID | p<0.0001 centroid-relocation | permutation_null_results.csv | p < 1e-3 |
| C-RAM-NULL-2-LABEL | p<0.0001 label-shuffle | permutation_null_results.csv | p < 1e-3 |
| C-RAM-NO-PROXY-26-29 | 26/29 no-proxy robustness | permutation_null_results_no_proxy.csv | exact_match |
| C-RAM-RADIUS-ROBUST | 28 at 8/10/12 mm | permutation_null_results.csv | exact_match all three radii |

## 4. Forbidden moves

- Modifying the published peak coordinate list to chase a higher match count.
- Re-running permutation nulls with different random seeds and selecting the "best" p-value.
