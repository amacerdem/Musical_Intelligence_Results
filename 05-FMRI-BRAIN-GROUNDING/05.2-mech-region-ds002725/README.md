# Phase 05.2 — Pre-Registered Mechanism × Region Encoding (ds002725)

**Status:** CLOSED 2026-05-07
**Verdict:** 11 PASS / 1 CAVEAT / 0 FAIL across 12 paper claims
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Summary

22 target × 22 random mechanism×region encoding analysis on ds002725
(N=17 alignment-qualified subjects). 16/22 target pairs survive BH-FDR
at q<0.05. Effect-size separation +0.105 vs 2×SE 0.048 → POSITIVE verdict
per pre-registered decision rule (frozen 2026-05-03 18:29).

Per-pair anchors paper-exact: PNH→A1_HG +0.334, BCH→A1_HG +0.317,
CDEM→MGB +0.315. F-function pass-rate breakdown: F1 5/5, F2 4/4,
F4 2/2, F8 1/1. F3→ACC null preserved (function-separation prediction).

## Single CAVEAT

C-MXREG-10 L3 cross-subject BH-FDR target_reject: paper claims 34/147,
V3 preserved comprehensive_summary stores 59. Numerator-direction and
verdict (POSITIVE) consistent; denominator-filter ambiguity logged as
paper revision item R9.

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase05_2.py`
- `results/05.2_mech_region_correlations.csv` + manifest
