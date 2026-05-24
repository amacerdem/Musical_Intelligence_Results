# Phase 05.3 ds002725-region-ceiling-N17 — Run Report

- **Started:**  2026-05-24T14:33:00
- **Finished:** 2026-05-24T14:33:01
- **Headline:** ✅ ALL PASS — **27/27** in ≈ 0.2 s on M2 8 GB (cache-anchored)

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 5 passed | Engine SHA aggregate integrity + paper-baseline structural checks |
| **L4** | ✅ PASS | 3 passed | Stage 3 ds002725 N=17 LOSO per-region ceiling reproduction (15/21 stimulus-driven) |
| **L5** | ✅ PASS | 4 passed | Stage 4 Mendelssohn-window MI encoder + saturation verdict (16/21 ceiling-saturating) |
| **L6** | ✅ PASS | 3 passed | Stage 9 cross-paradigm bridge ds002725 ↔ ds003720 (1 STRONG + 5 MIXED) |
| **L9** | ✅ PASS | 12 passed | All four paper-headline numbers locked + per-axis reconciliation |

**Total: 27 passed in ≈ 0.2 s.** All cache-anchored against pre-computed `paper_time_baseline.json`; no per-frame engine invocation required at test time.

## Positive evidence axes verified

1. **Stage 3 ds002725 N=17 LOSO per-region ceiling:** 15/21 stimulus-driven, top putamen +0.442, amygdala +0.383, MGB +0.346
2. **Stage 4 Mendelssohn-window MI encoder:** 16/21 ceiling-saturating (11 AT_CEILING + 5 EXCEEDS), max A1_HG +0.509
3. **Mendelssohn pilot paradox resolved:** BOLD reliability (full-scan +0.383) vs encoder fidelity (Mendelssohn-window +0.012) separable
4. **Cross-paradigm bridge ds002725 ↔ ds003720:** 1 STRONG (STG) + 5 MIXED (IFG/OFC/MGB/hypothalamus/insula)

## Reproduction

```bash
cd 05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17
python3 -m pytest .                          # ≈ 0.2 s on M2 8 GB
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
