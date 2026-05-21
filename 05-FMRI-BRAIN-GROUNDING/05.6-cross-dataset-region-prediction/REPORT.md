# 05.6-cross-dataset-region-prediction — Run Report

- **Started:**  2026-05-20T15:15:13
- **Finished:** 2026-05-20T15:15:13
- **Headline:** ⛔ ABORTED at L1 engine-pin gate

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ❌ FAIL | 5 errors in 0.01s | Engine SHA + paper-baseline structural |

## Paper-time baseline

**Cross-dataset fMRI consistency (ds002725 N=17 ↔ ds003720 N=4):**
- C1 MI mean|RAM| paradigm-invariance: **Pearson +0.998, Spearman +0.988**, p<0.001
- C2 MI variance paradigm-invariance:  **Pearson +0.968, Spearman +0.952**, p<0.001
- B  MI encoder cross-paradigm: Pearson +0.237 (directional trend, n.s.)
- A  BOLD ceiling cross-paradigm: Pearson −0.161 (paradigm-specific, n.s.)

**Three-way framing:** Engine paradigm-invariant + Encoder transfers directionally + Brain response paradigm-specific.

