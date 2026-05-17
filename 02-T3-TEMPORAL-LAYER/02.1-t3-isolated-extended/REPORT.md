# T³ Isolated Validation — Run Report

- **Started:**  2026-05-11T11:50:30
- **Finished:** 2026-05-11T11:50:49
- **Headline:** ✅ ALL PASS

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **Pin** | ✅ PASS | 7 passed in 0.54s | Engine SHA + H³ registry integrity |
| **L1** | ✅ PASS | 20 passed in 0.08s | Per-tuple (r,h,m,ℓ) formula re-implementation, bit-identical to engine |
| **L2** | ⚪ EMPTY | (no test files — audit artefacts only) | Statelessness: no self._ema / hidden state across frames |
| **L3** | ✅ PASS | 7 passed in 3.61s | Bit-identicality across run/seed/thread axes |
| **L4** | ✅ PASS | 125 passed in 0.97s | Range, shape, no-NaN, dataclass guarantees on H3Output |
| **L5** | ✅ PASS | 21 passed in 0.14s | Pathological-input robustness (silence, single-frame, post-warm-up) |
| **L6** | ✅ PASS | 22 passed in 0.10s | 24 morphs × 3 laws correctness via analytical anchors |
| **L7** | ⚪ EMPTY | (no test files — audit artefacts only) | Demand-driven sparsity & embarrassingly parallel staging |
| **L8** | ⚪ EMPTY | (no test files — audit artefacts only) | 32 horizons log-coverage, 4 perceptual bands |
| **L9** | ⚪ EMPTY | (no test files — audit artefacts only) | Constant provenance audit (zero-calibration) |
| **L10** | ⚪ EMPTY | (no test files — audit artefacts only) | Cross-implementation cross-validation |
| **L11** | ⚪ EMPTY | (no test files — audit artefacts only) | Anti-feature / hidden-state probes |
| **L12** | ⚪ EMPTY | (no test files — audit artefacts only) | API contract; H3Output frozen, H3DemandSpec slot-restricted |
| **L13** | ✅ PASS | 5 passed in 0.68s | T³-stage real-time-factor & memory budget |

## Engine pin

Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

