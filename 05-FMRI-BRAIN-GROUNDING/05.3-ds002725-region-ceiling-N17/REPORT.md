# 05.3-ds002725-region-ceiling-N17 — Run Report

- **Started:**  2026-05-20T15:15:12
- **Finished:** 2026-05-20T15:15:12
- **Headline:** ⛔ ABORTED at L1 engine-pin gate

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ❌ FAIL | 5 errors in 0.02s | Engine SHA aggregate integrity + paper-baseline structural checks |

## Paper-time baseline (positive evidence only)

**Four NEW positive evidence axes** added to V-Reproduction:
1. Stage 3 ds002725 N=17 LOSO per-region ceiling: 15/21 stimulus-driven, top putamen +0.442, amygdala +0.383, MGB +0.346
2. Stage 4 Mendelssohn-window MI encoder: **16/21 ceiling-saturating** (11 AT_CEILING + 5 EXCEEDS), max A1_HG +0.509
3. Mendelssohn pilot paradox resolved: BOLD reliability (full-scan +0.383) vs encoder fidelity (Mendelssohn-window +0.012) separable
4. Cross-paradigm bridge ds002725 ↔ ds003720: 1 STRONG (STG) + 5 MIXED (IFG/OFC/MGB/hypothalamus/insula)

See `_infra/manifests/paper_time_baseline.json` for full locked numbers.

