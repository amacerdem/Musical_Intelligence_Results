# 05.5-ds003720-region-ceiling-N4 — Run Report

- **Started:**  2026-05-17T19:06:38
- **Finished:** 2026-05-17T19:06:41
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 4 passed in 0.14s | Engine SHA + paper-baseline structural checks |
| **L4** | ✅ PASS | 2 passed in 0.13s | Per-region ceiling matches paper baseline |
| **L5** | ✅ PASS | 2 passed in 0.14s | Saturation verdict distribution within tolerance |
| **L9** | ✅ PASS | 3 passed in 0.13s | Verdict reconciliation + V-Repro 12 untouched |

## Paper-time baseline

Companion to V-Repro 12 (paper-canonical voxelwise). This package adds per-region
cross-subject LOSO ceiling on ds003720 N=4 at cycle-17 26-region BOLD scale.

**Top regions:** hippocampus +0.354, dlPFC +0.319, AG +0.243, IFG +0.233, PMC +0.193.
**N pass floor+q05 (non-brainstem):** 16/21.
**MI encoder saturation:** 5/21 (scale mismatch: cycle-17 per-clip vs ceiling per-TR).

