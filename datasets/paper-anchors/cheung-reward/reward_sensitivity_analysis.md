# Reward Formula Sensitivity Analysis — Supplementary

**Generated:** 2026-04-01 17:44

## Method
Reward formula weights (W_S=1.5, W_D=0.8, W_E=0.5, W_M=-0.6) perturbed by ±30% 
simultaneously across 1,000 random configurations. Input: 36 Core beliefs × 100 frames 
with realistic PE, precision, salience distributions.

## Results

| Metric | Value |
|--------|-------|
| Baseline reward (mean) | 2.1238 |
| Perturbed reward (mean ± std) | 2.1073 ± 0.3181 |
| Coefficient of Variation | 15.1% |
| Rank-order Spearman ρ (mean) | 0.9991 |
| Rank-order ρ (min) | 0.9950 |
| All ρ > 0.90 | 100/100 |
| All ρ > 0.95 | 100/100 |

## Interpretation
The reward formula is **robust to ±30% weight perturbation**: rank-order correlation 
with baseline exceeds ρ=0.999 on average, with minimum ρ=0.995. 
This means the relative ordering of frames by reward is preserved regardless of exact 
weight values — confirming that the 6 hand-specified-disclosed reward weights capture 
qualitative structure rather than being finely optimized or calibrated to specific values.
