# Phase 06.1 — Falsifiable Table 5 Aggregator

**Status:** CLOSED 2026-05-07
**Verdict:** **5/5 PASS** — all 5 paper falsification points SURVIVE
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Aggregate

| # | Test | Source | Verdict |
|---|---|---|---|
| FT5-#1 | Carillon ρ_stumpf = −0.824 | Phase 01.2 | **PASS** |
| FT5-#2 | ds003720 voxelwise 4/4 vs 1/4 vs 0/4 | Phase 05.4 | **PASS** |
| FT5-#3 | Cheung β=−0.158, Cheung's −0.124 in CI | Phase 03.3 | **PASS** |
| FT5-#4 | Mendelssohn rank 1/7, 2.2× lift | Phase 05.1 | **PASS** |
| FT5-#5 | Pre-reg mech×region 16/22 BH-FDR | Phase 05.2 | **PASS** |

This is the strongest single-table summary of MI's empirical defensibility.
Every pre-committed falsification point survives.

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase06_1.py`
- `results/06.1_falsifiable_table5_correlations.csv` + manifest
