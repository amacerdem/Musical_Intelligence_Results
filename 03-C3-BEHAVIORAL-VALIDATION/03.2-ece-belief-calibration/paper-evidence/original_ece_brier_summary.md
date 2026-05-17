# T-R3-08 Phase B — ECE + Brier Summary

**Generated:** 2026-04-23 01:52:19
**Songs:** [1034, 1508, 1777, 1896, 1923] (DEAM, seed=42, id>1000)
**Warm-up frames dropped per song:** 16
**Bins:** 10 equal-frequency

## Per-belief calibration

| Belief | N (post-warmup) | mean π_pred | mean y | **ECE** | Brier | ECE (marginal) | ECE (uniform) |
|---|---:|---:|---:|---:|---:|---:|---:|
| harmonic_stability | 25,760 | 0.847 | 0.816 | **0.091** | 0.024 | 0.000 | 0.316 |
| pitch_prominence | 25,760 | 0.960 | 0.877 | **0.082** | 0.014 | 0.000 | 0.377 |
| pitch_identity | 25,760 | 0.906 | 0.750 | **0.156** | 0.032 | 0.000 | 0.250 |
| timbral_character | 25,760 | 0.997 | 0.886 | **0.111** | 0.013 | 0.000 | 0.386 |
| prediction_hierarchy | 25,760 | 0.985 | 0.884 | **0.101** | 0.013 | 0.000 | 0.384 |
| prediction_accuracy | 25,760 | 1.000 | 0.979 | **0.021** | 0.001 | 0.000 | 0.479 |
| sequence_match | 25,760 | 0.996 | 0.916 | **0.080** | 0.008 | 0.000 | 0.416 |
| information_content | 25,760 | 0.996 | 0.947 | **0.049** | 0.004 | 0.000 | 0.447 |

## Pooled (8 beliefs × 5 songs)

- **Pooled ECE:** 0.079
- **Pooled Brier:** 0.014
- **N frames pooled:** 206,080
- **mean π_pred (pooled):** 0.961
- **mean y (pooled):** 0.882

## Verdict against Q-R3-08 thresholds

- ECE < 0.10  → CLOSED (Bayesian label defensible)
- 0.10 ≤ ECE < 0.20 → CLOSED-AT-RUNG-3 (softened language)
- ECE ≥ 0.20 → HONEST-CONCESSION (GT-0041 relabel)

**Pooled-ECE verdict:** CLOSED

