# L6 — Operator correctness: summary scorecard

**Date:** 2026-05-09
**Audit method:** Runtime pytest tests against `H3Extractor.extract()` on synthetic R³ feature streams with analytically-known temporal structure. Anchors empirically measured against engine HEAD (SHA `482ade45...`, pin commit `318eb2f5...`).
**Engine pin:** verified at session start (autouse `_pin_integrity` fixture)

## Headline

> **✅ PASS — 22/22 morph and law tests pass in 0.49s. M0, M2, M8, M14, M18 reproduce their analytically-expected behavior on canonical stimuli. L0 (memory) is bit-identically strictly causal: a perturbation at frames `t ≥ T_split` cannot affect any output at `t < T_split`. L1 (forward) and L2 (integration) differ from L0 in the documented direction.**

Plus 2 migrated experiments (`phase_lag_32rate/`, `wilson_cowan/`) provide the kernel-level operator anchors against the Doelling 2019 oscillator-class paradigm.

## Per-test scorecard

### Morph anchors — `test_morph_anchors.py` (15 tests, all PASS)

| Class | Test | Anchor |
|---|---|---|
| **M0 value** | `test_constant_07_returns_07` | constant 0.7 → output exactly 0.7 |
| | `test_silence_returns_zero` | silence → 0 |
| | `test_linear_ramp_midpoint_near_05` | ramp 0→1 → midpoint ≈ 0.498 (attention-weighted) |
| **M2 std** | `test_constant_returns_zero` | constant → exactly 0 |
| | `test_silence_returns_zero` | silence → exactly 0 |
| | `test_ramp_std_positive` | ramp → 0.001 < std < 0.05 (small but positive) |
| **M8 velocity** | `test_constant_returns_zero` | constant → exactly 0 |
| | `test_silence_returns_zero` | silence → exactly 0 |
| | `test_positive_ramp_returns_positive` | ramp → > 0 |
| **M14 periodicity** | `test_silence_returns_zero` | silence → exactly 0 |
| | `test_constant_near_zero` | constant → < 0.05 |
| | `test_sinusoid_peak_at_matching_horizon` | 4Hz sinusoid: H3 (4 frames, sub-period) → near 0; H7 (43 frames, period match) → > 0.85; monotone increase H3→H5→H7 |
| **M18 trend** | `test_constant_returns_zero` | constant → exactly 0 |
| | `test_silence_returns_zero` | silence → exactly 0 |
| | `test_positive_ramp_returns_positive` | ramp → strongly positive (saturates near 1.0) |

### Law direction — `test_law_direction.py` (7 tests, all PASS)

| Class | Test | Anchor |
|---|---|---|
| **L0 memory** | `test_L0_unaffected_by_future_perturbation_H5` | At H5 (window=8), L0 at t∈{50,100,150,195,199} is **bit-identical** between unperturbed and perturbed-at-200 streams |
| | `test_L0_unaffected_at_larger_horizon_H10` | At H10 (window=69), same bit-identicality at t∈{100,150,175,195,199} |
| **L1 forward** | `test_L1_affected_by_future_perturbation_H5` | At H5, L1 at t∈{195,197,199} **DIFFERS** between A and B (window crosses split) |
| | `test_L1_unaffected_when_window_fully_before_split` | At H5, L1 at t∈{50,100,150,190} is bit-identical (window does not reach split) |
| **L2 integration** | `test_L2_affected_when_symmetric_window_reaches_split` | At H5, L2 at t∈{197,199} differs (symmetric window crosses split) |
| | `test_L2_unaffected_when_symmetric_window_fully_before_split` | At H5, L2 at t∈{50,100,150,190} is bit-identical |
| **Sign-asymmetry** | `test_L0_lt_L1_on_positive_ramp` | At H7 midpoint of positive ramp, L0 (past mean) < L1 (future mean) |

## Migrated kernel-level evidence

| Experiment | Subject |
|---|---|
| **`phase_lag_32rate/`** | 32-rate phase-lag sweep (cross-rate PCM = 0.9606); 28/32 rates valid; corresponds to L6.kernel.32rate |
| **`wilson_cowan/`** | Wilson-Cowan E-I population vs T³ kernel comparison at Doelling 2019's 6 rates; corresponds to L6.kernel.WC |

These were migrated from `experiments/` during the 2026-05-09 R³-template restructuring.

## L6.law.L0 — bit-identical strict causality (PARTICULARLY LOAD-BEARING)

The strongest result of L6 is the **runtime empirical confirmation that L0 (memory) is strictly causal**:

```
At H5 (window=8 frames), perturbation at T_split=200:
  t_check=50, 100, 150, 195, 199:
    L0 output bit-identical between perturbed and unperturbed streams
    (max-abs-diff = 0.0)
```

This is the structural property the T³ paper §sec:sparsity invokes when claiming the law distribution (49.4% L0 / 3.1% L1 / 47.5% L2) is consistent with active-inference / predictive-coding's prediction of "no future-window observations". L0's strict causality means cognition can read past evidence without leaking future information; a system that needs to anticipate must do so via L1's forward window or via belief-cycle prediction, not via L0's read.

The bit-identical result complements the **L2.1 AST audit** (zero non-init self-assigns) and the **L11.3 + L11.6 static checks** (no PRNG, no env-var reads): together, they establish that determinism is structural, and L0's causality is empirically verified at the operator level.

## Reports

- [`L6_summary.md`](L6_summary.md) — this scorecard
- [`test_morph_anchors.py`](test_morph_anchors.py) — 15 morph anchor tests
- [`test_law_direction.py`](test_law_direction.py) — 7 law direction tests

## Reproducibility

Run tests:
```bash
cd T3-Paper/T3_Isolated_Validation
pytest L6_operator_correctness/ -v
```

Engine pin verified at session start; if engine drifts from `482ade45...`, session halts with clear message.

## Coverage gap (deferred to future expansion)

- M3 (median), M4 (max), M5 (range): Level/Dispersion morphs not yet anchored
- M6 (skewness), M7 (kurtosis): Shape morphs not yet anchored
- M9–M13 (velocity_*, acceleration_*): not yet anchored individually
- M15 (smoothness), M16 (curvature), M17 (shape_period), M19 (stability): not yet anchored
- M20 (entropy), M21 (zero_crossings), M22 (peaks), M23 (symmetry): not yet anchored

5 morphs of 24 are anchored (M0, M2, M8, M14, M18) — covers the core operators that feed C³'s Bayesian belief precision update (M14 + M18 are documented load-bearing inputs at master Eq.~`belief-update`). The remaining 19 morphs follow the same pattern; expansion is mechanical.

## Headline (production-grade form)

When all 24 morphs are anchored:

> **L6 PASS — N/N:** all 24 morphs reproduce analytical expectations on canonical stimuli; all 3 laws verified bit-identically against future-perturbation probes; kernel-level oscillator-class commitment validated via Doelling 2019 paradigm and Wilson-Cowan analytical comparison.
