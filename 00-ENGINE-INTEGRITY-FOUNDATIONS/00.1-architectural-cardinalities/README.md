# Phase 1 — Architectural Cardinalities

**Status:** Closed 2026-05-07 (paper-anchor v2)
**Verdict:** 5 / 5 PASS
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

This phase reproduces the architectural inventory of the engine
against the paper-anchor capture: numeric-constant total and the
five-bucket provenance partition (LITERATURE, STRUCTURAL, NULL,
CALIB, HAND-TUNED).

## Quick reference

| Claim | Paper | Reproduced | Tolerance | Verdict |
|---|---|---|---|---|
| C-CARD-09-V2 | 16,191 numeric constants total | 16,222 | abs ≤ 50 (0.3 %) | PASS |
| C-CARD-11-STRICT | LITERATURE bucket ≈ 5,534 | 5,449 | abs ≤ 200 (4 %) | PASS |
| C-CARD-12-STRICT | STRUCTURAL bucket ≈ 4,212 | 4,210 | abs ≤ 200 (5 %) | PASS |
| C-CARD-13-STRICT | NULL bucket ≈ 1,381 | 1,381 | exact | PASS |
| C-CARD-14-STRICT | CALIB bucket ≈ 246 | 247 | abs ≤ 50 (20 %) | PASS |

Aggregate: 5 / 5 PASS.

## How to run

```bash
bash code/run.sh
```

The phase reads the AST inventory CSV from the paper-anchor capture
and verifies the bucket counts against paper headlines.

## Output

- `results/01_cardinalities_correlations.csv` — per-claim verdicts
- `results/01_cardinalities_manifest.json` — machine-readable manifest

## Reading order

1. `00-METHODOLOGY.md` — operationalisation and per-claim tolerance
2. `01-PROVENANCE.md` — paper-line anchors and code anchors
3. `02-RESULTS.md` — full diagnosis and per-claim verdict table
4. `04-INTEGRATION-LOG.md` — iteration history
