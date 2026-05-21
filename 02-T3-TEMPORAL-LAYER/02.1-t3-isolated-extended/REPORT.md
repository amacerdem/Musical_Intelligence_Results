# T³ Isolated Validation — Run Report

- **Started:**  2026-05-20T15:14:36
- **Finished:** 2026-05-20T15:14:45
- **Headline:** ❌ FAIL

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **Pin** | ✅ PASS | 7 passed in 0.41s | Engine SHA + H³ registry integrity |
| **L1** | ❌ FAIL | 20 errors in 0.03s | Per-tuple (r,h,m,ℓ) formula re-implementation, bit-identical to engine |
| **L2** | ⚪ EMPTY | (no test files — audit artefacts only) | Statelessness: no self._ema / hidden state across frames |
| **L3** | ❌ FAIL | 7 errors in 0.02s | Bit-identicality across run/seed/thread axes |
| **L4** | ❌ FAIL | 125 errors in 0.17s | Range, shape, no-NaN, dataclass guarantees on H3Output |
| **L5** | ❌ FAIL | 21 errors in 0.03s | Pathological-input robustness (silence, single-frame, post-warm-up) |
| **L6** | ❌ FAIL | 22 errors in 0.04s | 24 morphs × 3 laws correctness via analytical anchors |
| **L7** | ⚪ EMPTY | (no test files — audit artefacts only) | Demand-driven sparsity & embarrassingly parallel staging |
| **L8** | ⚪ EMPTY | (no test files — audit artefacts only) | 32 horizons log-coverage, 4 perceptual bands |
| **L9** | ⚪ EMPTY | (no test files — audit artefacts only) | Constant provenance audit (zero-calibration) |
| **L10** | ⚪ EMPTY | (no test files — audit artefacts only) | Cross-implementation cross-validation |
| **L11** | ⚪ EMPTY | (no test files — audit artefacts only) | Anti-feature / hidden-state probes |
| **L12** | ⚪ EMPTY | (no test files — audit artefacts only) | API contract; H3Output frozen, H3DemandSpec slot-restricted |
| **L13** | ❌ FAIL | 5 errors in 0.04s | T³-stage real-time-factor & memory budget |

## Engine pin

Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

