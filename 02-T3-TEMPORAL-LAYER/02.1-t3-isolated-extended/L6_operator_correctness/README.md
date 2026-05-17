# L6 — Operator correctness (morph + law on analytical anchors)

> **Status:** **POPULATED + PASS (2026-05-09)** — 22/22 morph + law tests pass in 0.49s. See [`L6_summary.md`](L6_summary.md) for full scorecard.

## Paper claim being defended

*Each named morph extracts the statistical quantity its name claims; each law applies the documented temporal direction. These are NOT cognitive tests — they verify the operator extracts the quantity it advertises on stimuli where the answer is independently known.*

## Audit results

> **✅ PASS — 22/22 morph and law tests pass.** M0, M2, M8, M14, M18 reproduce their analytically-expected behavior on canonical stimuli. L0 (memory) is **bit-identically strictly causal**: a perturbation at frames `t ≥ T_split` cannot affect any output at `t < T_split`. L1 (forward) and L2 (integration) differ from L0 in the documented direction.

| Sub-test | Subject | Result |
|---|---|---|
| **L6.M0** | value (attention-weighted mean) | **PASS** — 3/3 anchors |
| **L6.M2** | std (standard deviation) | **PASS** — 3/3 anchors |
| **L6.M8** | velocity (first temporal derivative) | **PASS** — 3/3 anchors |
| **L6.M14** | periodicity (autocorrelation peak) | **PASS** — 3/3 anchors (incl. 4Hz sinusoid peak at H7) |
| **L6.M18** | trend (linear regression slope) | **PASS** — 3/3 anchors |
| **L6.kernel.32rate** | phase-lag at 32 stimulation rates (Doelling 2019) | **PASS** — migrated `phase_lag_32rate/` (cross-rate PCM = 0.9606) |
| **L6.kernel.WC** | Wilson-Cowan vs T³ kernel comparison | **PASS** — migrated `wilson_cowan/` (analytical) |
| **L6.law.L0** | Memory: bit-identical past-only causal | **PASS** — 2 horizon scales (H5, H10), 5 frame positions each |
| **L6.law.L1** | Forward: anticipatory window-crossing | **PASS** — 2 tests (perturbation reaches + does not reach) |
| **L6.law.L2** | Integration: bidirectional symmetric | **PASS** — 2 tests (symmetric window crosses + doesn't cross) |
| **L6.law.cross** | L0 < L1 on positive ramp (sign-asymmetry) | **PASS** — at H7 midpoint |

## Strongest implication

**L0 strict causality is empirically verified bit-identically** at multiple frame positions and multiple horizon scales:

```
At H5 (window=8 frames), perturbation at T_split=200:
  At t ∈ {50, 100, 150, 195, 199}:
    L0 output max-abs-diff between perturbed and unperturbed streams = 0.0 (BIT-IDENTICAL)
```

This is the runtime confirmation of the **predictive-coding-faithful property** the T³ paper §sec:sparsity invokes when claiming the law distribution (49.4 / 3.1 / 47.5%) is consistent with active-inference's "no future-window observations" prediction. L0 cannot leak future information into past output; cognition's anticipation must come from L1 forward window or belief-cycle prediction, not from L0 memory.

Combined with **L2.1 AST audit** (zero non-init self-assigns) and **L11.3 + L11.6 static checks** (no PRNG, no env-var reads): determinism is structural, and L0's causality is empirically verified at the operator level.

## Migrated experiments

- [`phase_lag_32rate/`](phase_lag_32rate/) — kernel measurement at 32 stimulation rates (Doelling 2019 paradigm)
- [`wilson_cowan/`](wilson_cowan/) — analytical comparison T³ kernel vs Wilson-Cowan E-I population

## Reports

- [`L6_summary.md`](L6_summary.md) — full audit + per-test scorecard + L0 strict-causality detail
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

5 of 24 morphs are anchored (M0, M2, M8, M14, M18 — the core operators that feed C³'s Bayesian belief precision update at master Eq.~`belief-update`). The remaining 19 morphs (M1/M3/M4 level, M5 range, M6/M7 shape, M9–M13 dynamics, M15/M16/M17 dynamics, M19 stability, M20 entropy, M21–M23) follow the same anchor pattern; expansion is mechanical.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
