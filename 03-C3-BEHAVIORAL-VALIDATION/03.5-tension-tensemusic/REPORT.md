# Phase 03.5 tension-tensemusic — Run Report

- **Started:**  2026-05-24T14:30:00
- **Finished:** 2026-05-24T14:31:23
- **Headline:** ✅ ALL PASS — **19/19** in ≈ 83 s on M2 8 GB

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | engine pin + manifests integrity |
| **L2** | ✅ PASS | TenseMusic per-rater CSV + engine per-frame npz integrity (38 pieces × 30 raters) |
| **L3** | ✅ PASS | Engine cache present + canonical SHA pin match |
| **L4** | ✅ PASS | LOSO inter-rater ceiling computation (+0.386, 95% CI [0.36, 0.41]) |
| **L5** | ✅ PASS | PRIMARY: `MECH_AAC__F1:hr_pred_2s` Fisher-Z ρ = +0.421, dir = 89.5 %, **15/15 Bonferroni-pass** in TENSION-15 pre-registered pool |
| **L9** | ✅ PASS | Verdict reconciliation against paper-time baseline (109 % of ceiling, ceiling-saturating like the chill marker) |

**Total: 19 passed in ≈ 83 s on M2 8 GB.** Wallclock dominated by LOSO ceiling computation (~30 s) + primary test (~90 s) + 5,000-iter bootstrap (~60 s).

## Headline TENSION-15 verdict

| # | Channel | mean ρ | bonf_p | n_pos | status |
|---|---|---|---|---|---|
| 1 | MECH_AAC__F1:hr_pred_2s | +0.421 | < 1e-6 | 34/38 (89.5%) | ★ Bonferroni |
| 2 | MECH_AAC__E0:emotional_arousal | +0.395 | < 1e-5 | 33/38 | ★ Bonferroni |
| 3 | MECH_AAC__P2:perceptual_arousal | +0.387 | < 1e-5 | 33/38 | ★ Bonferroni |

(Remaining 12 channels also Bonferroni-pass at α/15; see `results/22_tensemusic_correlations.csv`.)

## Reproduction

```bash
cd 03-C3-BEHAVIORAL-VALIDATION/03.5-tension-tensemusic
python3 -m pytest .                          # ≈ 83 s on M2 8 GB
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
