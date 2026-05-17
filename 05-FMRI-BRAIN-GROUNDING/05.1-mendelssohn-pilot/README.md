# Phase 05.1 — Mendelssohn Single-Subject Pilot (CAVEAT-PRESERVING)

**Status:** CLOSED 2026-05-07
**Verdict:** 5 PASS / 1 PARTIAL / 0 FAIL across 6 paper claims
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Framing

Paper itself flags this as illustrative single-window pilot, NOT population-level.
V-Reproduction preserves both numbers side-by-side: sub-08 paper-time r=+0.59
(illustrative) AND cross-subject N=17 median ρ=−0.022 (window-selection effect
disclosure).

## Headline

| Quantity | Paper | Reproduced |
|---|---|---|
| sub-08 amygdala paper-time r | +0.59 | **+0.5904** |
| Cross-subject N=17 median amygdala ρ | −0.022 | **−0.0223** |
| 95% BCa CI | [−0.154, +0.027] | [−0.154, +0.027] (bit-exact) |
| Mendelssohn piece-rank 1/7, 2.2× lift | rank 1/7 | V2 rescore.md confirms |

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase05_1.py`
- `results/05.1_mendelssohn_correlations.csv` + manifest
