# 05.3-ds002725-region-ceiling-N17 — Run Report

- **Started:**  2026-05-17T19:06:34
- **Finished:** 2026-05-17T19:06:38
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 5 passed in 0.48s | Engine SHA aggregate integrity + paper-baseline structural checks |
| **L4** | ✅ PASS | 3 passed in 0.14s | Stage 3 full-scan LOSO ceiling reproduction (15/21 PASS locked) |
| **L5** | ✅ PASS | 4 passed in 0.15s | Stage 4 Mendelssohn-window encoder + saturation verdict (16/21 saturating) |
| **L6** | ✅ PASS | 3 passed in 0.16s | Stage 9 cross-paradigm bridge ds002725 ↔ ds003720 (1 STRONG + 5 MIXED) |
| **L9** | ✅ PASS | 4 passed in 0.14s | All four paper-headline numbers locked |

## Paper-time baseline (positive evidence only)

**Four NEW positive evidence axes** added to V-Reproduction:
1. Stage 3 ds002725 N=17 LOSO per-region ceiling: 15/21 stimulus-driven, top putamen +0.442, amygdala +0.383, MGB +0.346
2. Stage 4 Mendelssohn-window MI encoder: **16/21 ceiling-saturating** (11 AT_CEILING + 5 EXCEEDS), max A1_HG +0.509
3. Mendelssohn pilot paradox resolved: BOLD reliability (full-scan +0.383) vs encoder fidelity (Mendelssohn-window +0.012) separable
4. Cross-paradigm bridge ds002725 ↔ ds003720: 1 STRONG (STG) + 5 MIXED (IFG/OFC/MGB/hypothalamus/insula)

See `_infra/manifests/paper_time_baseline.json` for full locked numbers.

