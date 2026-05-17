# 22-h8-tensemusic-tension-prediction — Run Report

- **Started:**  2026-05-13T14:52:49
- **Finished:** 2026-05-13T14:54:13
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 3 passed in 0.35s | Engine SHA aggregate integrity |
| **L4** | ✅ PASS | 1 passed, 38 warnings in 2.45s | LOSO inter-rater ceiling +0.386 [0.36, 0.41] reproduction |
| **L5** | ✅ PASS | 4 passed in 80.48s (0:01:20) | PRIMARY — TENSION-15 lag-aware Spearman + Bonferroni |

## Paper-time baseline

See `_infra/manifests/paper_time_baseline.json` for locked numbers.
Top: `MECH_AAC__F1:hr_pred_2s` ρ=+0.421, dir=89.5 %, 15/15 Bonferroni, 109 % of ceiling.

