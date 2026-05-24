# Phase 05.6 cross-dataset-region-prediction — Run Report

- **Started:**  2026-05-24T14:34:00
- **Finished:** 2026-05-24T14:34:00
- **Headline:** ✅ ALL PASS — **23/23** in ≈ 0.03 s on M2 8 GB (cache-anchored)

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 5 passed | Engine SHA + paper-baseline structural checks |
| **L4** | ✅ PASS | 4 passed | C1 mi_feature_mean paradigm-invariance Pearson r > 0.99 + C2 mi_feature_variance > 0.95 |
| **L5** | ✅ PASS | 5 passed | B directional trend (encoder cross-paradigm) + A paradigm-specific (BOLD ceiling) + 3-way separation contract |
| **L9** | ✅ PASS | 9 passed | Per-axis verdict reconciliation against paper baseline |

**Total: 23 passed in ≈ 0.03 s.** Pure cache-anchored statistical reads against `paper_time_baseline.json`; no per-frame engine invocation at test time.

## Headline cross-dataset fMRI consistency (ds002725 N=17 ↔ ds003720 N=4)

| Axis | Metric | Value | Significance |
|---|---|---|---|
| **C1** | MI mean\|RAM\| paradigm-invariance | Pearson **+0.998**, Spearman **+0.988** | p < 0.001 (5,000-permutation label-shuffle null) |
| **C2** | MI variance paradigm-invariance | Pearson **+0.968**, Spearman **+0.952** | p < 0.001 |
| **B** | MI encoder cross-paradigm | Pearson +0.237 | directional trend, n.s. |
| **A** | BOLD ceiling cross-paradigm | Pearson −0.161 | paradigm-specific, n.s. |

**Three-way framing:** Engine paradigm-invariant (C1 + C2) + Encoder transfers directionally (B) + Brain response paradigm-specific (A). The frozen region-routing prior produces a stable, dataset-invariant anatomical fingerprint at the engine-output level; no claim is made of paradigm-invariant empirical brain activity.

## Reproduction

```bash
cd 05-FMRI-BRAIN-GROUNDING/05.6-cross-dataset-region-prediction
python3 -m pytest .                          # ≈ 0.03 s on M2 8 GB
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
