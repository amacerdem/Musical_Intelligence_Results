# 05.5-ds003720-region-ceiling-N4 — Run Report

- **Started:**  2026-05-20T15:15:13
- **Finished:** 2026-05-20T15:15:13
- **Headline:** ⛔ ABORTED at L1 engine-pin gate

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ❌ FAIL | 4 errors in 0.01s | Engine SHA + paper-baseline structural checks |

## Paper-time baseline

Companion to V-Repro 12 (paper-canonical voxelwise). This package adds per-region
cross-subject LOSO ceiling on ds003720 N=4 at cycle-17 26-region BOLD scale.

**Top regions:** hippocampus +0.354, dlPFC +0.319, AG +0.243, IFG +0.233, PMC +0.193.
**N pass floor+q05 (non-brainstem):** 16/21.
**MI encoder saturation:** 5/21 (scale mismatch: cycle-17 per-clip vs ceiling per-TR).

