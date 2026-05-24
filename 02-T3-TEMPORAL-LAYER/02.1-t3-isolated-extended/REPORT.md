# T³ Isolated Validation — Run Report

- **Started:**  2026-05-24T18:02:00
- **Finished:** 2026-05-24T18:02:04
- **Headline:** ✅ ALL PASS (207/207) — live-engine BUILD mode
- **Reviewer cache-mode:** ✅ ALL PASS (207/207) in ≈ 0.5 s

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **Pin** | ✅ PASS | 7 passed | Engine SHA-256 aggregate integrity + H³ registry integrity |
| **L1** | ✅ PASS | 18 passed | Per-tuple (r3_idx, horizon, morph, law) formula re-implementation, bit-identical to engine + attention kernel within float32 epsilon (≤ 1 ULP) |
| **L2** | ✅ PASS | 17 passed | Statelessness: AST audit (no `self._ema`), window-purity, embarrassingly-parallel equivalence, no R³ frame-state leakage |
| **L3** | ✅ PASS | 15 passed | Bit-identicality across run/seed/thread/process axes (cross-process via subprocess re-execution) |
| **L4** | ✅ PASS | 33 passed | Range, shape, no-NaN, dataclass guarantees on H3Output (per-tuple bounds across 24 morphs × 32 horizons) |
| **L5** | ✅ PASS | 21 passed | Pathological-input robustness (silence, single-frame, post-warm-up, edge cases) |
| **L6** | ✅ PASS | 22 passed | 24 morphs × 3 laws (memory/forward/integration) correctness via analytical anchors (constant, ramp, sinusoid, silence) |
| **L7** | ✅ PASS | 11 passed | Demand-driven sparsity (~644 mech-only / ~8,600 full registry of 223,488 theoretical) + embarrassingly-parallel staging |
| **L8** | ✅ PASS | 14 passed | 32 horizons log-coverage (H0 = 5.8 ms → H31 = 981 s) across 4 perceptual bands (Micro / Meso / Macro / Ultra) |
| **L9** | ✅ PASS | 18 passed | Constant provenance audit (zero-calibration): ATTENTION_DECAY=3.0, HORIZON_FRAMES, MORPH_SCALE, LAW_NAMES |
| **L10** | ✅ PASS | 7 passed | Cross-implementation: attention kernel exp(−3·(1−p)) re-impl matches torch within float32 epsilon |
| **L11** | ✅ PASS | 5 passed | Anti-features (no hidden state, no caching, no engine-state mutation) |
| **L12** | ✅ PASS | 14 passed | API contract: H3Extractor.extract() signature, H3Output frozen dataclass, H3DemandSpec slot-restricted |
| **L13** | ✅ PASS | 5 passed | T³-stage real-time-factor + memory budget on M2 |

**Total: 207 passed** in either mode (≈ 4 s live BUILD on M2 8 GB; ≈ 0.5 s reviewer cache mode).

## Headline

> **T³ delivers what it claims to deliver: 207 / 207 pytest tests PASS in both reviewer cache mode (oracle + engine_facts substrate) and live-engine BUILD mode against the canonical engine SHA-pin `318eb2f5…`. The attention kernel exhibits the specification's ~20× newest-to-oldest weighting (exp(3) = 20.09); the three causal laws (memory, forward, integration) produce clearly differentiated outputs on constant, ramp, and silence input; statelessness preserved across all per-tuple paths.**

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

## Reproduction

```bash
# Reviewer cache mode (no engine source needed)
python3 -m pytest .                          # ≈ 0.5 s, 207/207 PASS

# Live-engine BUILD mode (rebuilds the oracle + facts manifest)
MI_BUILD_ORACLE=1 python3 -m pytest .        # ≈ 4 s on M2 8 GB, 207/207 PASS
```

## Layer-completion history

The 2026-05-24 cache-substrate landing also added pytest runtime tests for layers L2, L7, L8, L9, L10, L11, L12 that were originally documentation-only. All seven layers are now green; per-layer coverage is documented in their respective L*_summary.md files.
