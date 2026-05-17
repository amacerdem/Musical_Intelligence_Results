# 05.6-cross-dataset-region-prediction — Run Report

- **Started:**  2026-05-17T17:27:02
- **Finished:** 2026-05-17T17:27:07
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 5 passed in 2.92s | Engine SHA + paper-baseline structural |
| **L4** | ✅ PASS | 3 passed in 0.09s | C1+C2 paradigm-invariance within tolerance |
| **L5** | ✅ PASS | 3 passed in 0.10s | B directional trend + A paradigm-specific + 3-way separation |
| **L9** | ✅ PASS | 4 passed in 0.15s | Verdict + companion V-Repros untouched |

## Paper-time baseline

**Cross-dataset fMRI consistency (ds002725 N=17 ↔ ds003720 N=4):**
- C1 MI mean|RAM| paradigm-invariance: **Pearson +0.998, Spearman +0.988**, p<0.001
- C2 MI variance paradigm-invariance:  **Pearson +0.968, Spearman +0.952**, p<0.001
- B  MI encoder cross-paradigm: Pearson +0.237 (directional trend, n.s.)
- A  BOLD ceiling cross-paradigm: Pearson −0.161 (paradigm-specific, n.s.)

**Three-way framing:** Engine paradigm-invariant + Encoder transfers directionally + Brain response paradigm-specific.

