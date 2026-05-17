# Top-20 HAND-TUNED free-parameter groups (engine-only)

Total engine HAND-TUNED rows: **495**

| Rank | Name pattern | Count | Distinct values | File spread | Example |
|------|-------------|-------|-----------------|-------------|----------|
| 1 | `\<expr-L\>` | 134 | 13 (0.02, 0.05, 0.1…) | 48 files | `pnh/conflict_assessment.py:14` |
| 2 | `TAU` | 51 | 17 (0.25, 0.3, 0.35…) | 51 files | `bch/harmonic_stability.py:45` |
| 3 | `\<cmp-threshold\>` | 43 | 6 (1e-08, 2, 3…) | 9 files | `morphology/batch.py:36` |
| 4 | `_W_TREND` | 37 | 3 (0.03, 0.04, 0.05) | 37 files | `bch/harmonic_stability.py:33` |
| 5 | `_W_CTX` | 37 | 3 (0.02, 0.03, 0.04) | 37 files | `bch/harmonic_stability.py:35` |
| 6 | `\<expr-R\>` | 30 | 9 (0.1, 10.0, 1000.0…) | 20 files | `pnh/consonance_preference.py:23` |
| 7 | `_W_PERIOD` | 27 | 3 (0.03, 0.04, 0.05) | 27 files | `bch/harmonic_stability.py:34` |
| 8 | `BASELINE` | 15 | 2 (0.4, 0.5) | 15 files | `pnh/consonance_preference.py:16` |
| 9 | `h3_features.get.arg0` | 14 | 3 ([0, 8, 18, 0], [21, 3, 8, 0], [60, 8, 18, 0]) | 13 files | `pnh/consonance_preference.py:23` |
| 10 | `PRECISION_H3_TUPLES` | 13 | 5 ([[0, 8, 2, 0], [4, 8, 2, 0], [3, 8, 2, 0]], [[4, 8, 2, 0], [60, 8, 2, 0], [21, 8, 2, 0]], [[60, 8, 2, 0], [17, 8, 2, 0], [21, 8, 2, 0]]…) | 13 files | `pnh/consonance_preference.py:18` |
| 11 | `sigma.clamp.min` | 4 | 1 (1e-08) | 2 files | `morphology/batch.py:73` |
| 12 | `range.arg0` | 4 | 1 (2) | 2 files | `morphology/batch.py:210` |
| 13 | `_SENSORY_PLEAS` | 3 | 1 (4) | 3 files | `miaa/extraction.py:12` |
| 14 | `h3.arg0` | 3 | 3 (18, 19, 20) | 1 files | `miaa/extraction.py:31` |
| 15 | `h3.arg1` | 3 | 1 (2) | 1 files | `miaa/extraction.py:31` |
| 16 | `h3.arg3` | 3 | 1 (2) | 1 files | `miaa/extraction.py:31` |
| 17 | `_SPECTRAL_AUTO` | 2 | 1 (17) | 2 files | `miaa/extraction.py:13` |
| 18 | `_KEY_CLARITY` | 2 | 1 (51) | 2 files | `miaa/extraction.py:14` |
| 19 | `_TONAL_STABILITY` | 2 | 1 (60) | 2 files | `miaa/extraction.py:15` |
| 20 | `_INHARM` | 2 | 1 (5) | 2 files | `miaa/extraction.py:16` |

## Named free-parameter groups (the R3 concession list)

All the following are set by the authors without a cited source:

- **`TAU`** — per-belief temporal decay; 51 values across 51 beliefs; range 0.25-0.95
- **`_W_TREND`** — per-belief trend weight (M18 morphology coefficient); 37 beliefs; range 0.03-0.05
- **`_W_CTX`** — per-belief context weight (cross-belief context); 37 beliefs; range 0.02-0.04
- **`_W_PERIOD`** — per-belief period weight (M14 morphology coefficient); 27 beliefs; range 0.03-0.05
- **`BASELINE`** — per-belief prior; 15 beliefs; values {0.4, 0.5}
- **`W_SURPRISE=1.5`** — reward Eq(1) surprise weight (brain/reward.py)
- **`W_RESOLUTION=0.8`** — reward Eq(1) resolution weight
- **`W_EXPLORATION=0.5`** — reward Eq(1) exploration weight
- **`W_MONOTONY=-0.6`** — reward Eq(1) monotony penalty
- **`PRECISION_SCALE=12.0`** — Bayesian precision sigmoid scale
- **`eta`** — familiarity modulator multiplier; multiple per-belief instances
- **`PRECISION_H3_TUPLES`** — per-belief H3 demand tuple selection (13 beliefs)

**Honest framing for the paper:** the reward-formula weights were admitted as hand-tuned in the v1 submission (count: 7). The AST walk exposes that the hand-tuned surface extends to per-belief temporal parameters (TAU, _W_TREND, _W_CTX, _W_PERIOD) across Core + Anticipation beliefs — ~150 additional constants — plus in-expression mixer literals in files whose module docstrings do not carry a literature anchor (~250 more). Total ≈ 495 engine HAND-TUNED constants. The sensitivity analysis in V1/results covers only the 4 reward-formula weights (±30% → ρ>0.995 rank-preservation). A larger sensitivity sweep over TAU / _W_TREND / _W_CTX / _W_PERIOD is scoped as a follow-up compute ticket but is not required for closure of this disclosure ticket.
