# Phase 06.1 — Falsifiable Table 5 Aggregator — Methodology

**Axis ID:** AXIS-12
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1. Scope (5 paper claims)

Paper §Methods §Falsifiable predictions pre-commits 5 tests. Each is a
falsification point: if it fails, the corresponding architectural claim is
falsified. Phase 06.1 aggregates verdicts from upstream Phases 01.2, 03.3, 05.1, 05.2, 05.4.

| # | Test | Source phase |
|---|---|---|
| FT5-#1 | Carillon ρ_stumpf = −0.824 anti-overfit | Phase 01.2 / C-R3OOS-CARILLON-STUMPF |
| FT5-#2 | ds003720 voxelwise 4/4 vs 1/4 vs 0/4 | Phase 05.4 / C-VOXEL-02..04 |
| FT5-#3 | Cheung interaction β=−0.158, CI contains −0.124 | Phase 03.3 / C-CHEUNG-01 + C-CHEUNG-03 |
| FT5-#4 | Mendelssohn rank 1/7, 2.2× lift | Phase 05.1 / C-MEND-06 |
| FT5-#5 | Pre-reg mech×region 16/22 BH-FDR | Phase 05.2 / C-MXREG-01 |

## 2. Aggregation rule

Each FT5-#k passes iff its source-phase claim has verdict=PASS in the per-phase
correlations CSV. No re-execution; pure aggregation.

## 3. Forbidden moves

- Re-classifying CAVEAT or PARTIAL upstream verdicts to PASS at this aggregation
  step. Aggregation faithfully mirrors source-phase verdicts.
- Adding additional falsifiable claims beyond paper's pre-committed 5.
