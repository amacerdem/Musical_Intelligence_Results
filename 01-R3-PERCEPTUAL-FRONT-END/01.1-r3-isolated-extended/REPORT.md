# R³ Isolated Validation — Run Report

- **Started:**  2026-05-11T11:30:13
- **Finished:** 2026-05-11T11:32:23
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **Pin** | ✅ PASS | 5 passed in 0.75s | Engine SHA + dim registry integrity |
| **L1** | ✅ PASS | 362 passed in 9.30s | Per-dim spec compliance (97 dims × 8 stimuli) |
| **L2** | ✅ PASS | 24 passed in 1.65s | Boundary-doctrine probes (5 inclusion rules) |
| **L3** | ✅ PASS | 13 passed in 12.09s | Bit-identicality across run/seed/thread/HW/OS axes |
| **L4** | ✅ PASS | 10 passed in 67.62s (0:01:07) | Range, shape, no-NaN, dataclass guarantees |
| **L5** | ✅ PASS | 33 passed in 1.82s | Pathological-input robustness |
| **L6** | ✅ PASS | 18 passed in 3.55s | Group-internal physical correctness |
| **L7** | ✅ PASS | 10 passed in 0.21s | DAG & staging correctness |
| **L8** | ✅ PASS | 11 passed in 0.35s | Warm-up tier disclosure |
| **L9** | ✅ PASS | 14 passed in 0.16s | Constant provenance audit (zero-calibration) |
| **L10** | ✅ PASS | 9 passed in 0.13s | Cross-implementation cross-validation |
| **L11** | ✅ PASS | 8 passed in 0.64s | Anti-feature / hidden-state probes |
| **L12** | ✅ PASS | 9 passed in 0.33s | API contract & immutability |
| **L13** | ✅ PASS | 5 passed in 8.90s | Real-time-factor & memory budget |

## Engine pin

Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

