# R³ Isolated Validation — Run Report

- **Started:**  2026-05-24T18:00:00
- **Finished:** 2026-05-24T18:01:25
- **Headline:** ✅ ALL PASS (531/531) — live-engine BUILD mode
- **Reviewer cache-mode:** ✅ ALL PASS (531/531) in ≈ 7 s

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **Pin** | ✅ PASS | 5 passed | Engine SHA-256 aggregate integrity + 97-D dim registry |
| **L1** | ✅ PASS | 362 passed | Per-dim spec compliance (R³ groups A–K × 8 stimulus families: white noise, A4 tone, sweep, real audio, silence, DC, impulse, mix) |
| **L2** | ✅ PASS | 38 passed | Boundary-doctrine probes (frame locality, no-listener-model, group isolation, no prediction, determinism) |
| **L3** | ✅ PASS | 13 passed | Bit-identicality across run/seed/thread/process axes; no-PRNG source scan |
| **L4** | ✅ PASS | 6 passed | Shape (B,T,97), range [0,1], no NaN/Inf, frozen `R3Output` dataclass |
| **L5** | ✅ PASS | 14 passed | Pathological-input robustness (silence, DC, impulse, clipped, low-amp, phase-inverted, …) |
| **L6** | ✅ PASS | 17 passed | Group-internal physical correctness on analytical anchors (consonance, energy, timbre, change, pitch_chroma, rhythm_groove, harmony, timbre_extended, modulation) |
| **L7** | ✅ PASS | 10 passed | 2-stage acyclic DAG + dependency narrowness (`compute_with_deps`) |
| **L8** | ✅ PASS | 9 passed | Warm-up tier disclosure (Tier 0 / Tier 1 ramp / Tier 1 zero / Tier 2 zero) + `WarmupManager.get_confidence` |
| **L9** | ✅ PASS | 14 passed | Constant provenance audit (Sethares 1993, K-K 1982, Stumpf 1890, Plomp-Levelt, IEC 61672-1, Stevens 1957) + negative-claim source scans |
| **L10** | ✅ PASS | 9 passed | Cross-implementation: Sethares dyad kernel, Plomp-Levelt CB, K-K 1982 (now via `pytest.approx(abs=1e-4)`), Harte Tonnetz, MFCC DCT-II, Jiang spectral contrast, A-weighting, Stevens γ=0.3 |
| **L11** | ✅ PASS | 10 passed | Anti-features (no PRNG, no fs side-effects, no sockets, no exec/eval/subprocess, no global-state mutation) |
| **L12** | ✅ PASS | 9 passed | API contract (extract signature, R3Output frozen dataclass, total_dim=97, feature_map immutable) |
| **L13** | ✅ PASS | 8 passed | Real-time factor + peak RSS budget on M2 |
| **_infra** | ✅ PASS | 7 passed | Pin-integrity self-tests (engine SHA aggregate matches manifest; 97-D layout) |

**Total: 531 passed** in either mode (≈ 85 s live BUILD on M2 8 GB; ≈ 7 s reviewer cache mode).

## Headline

> **R³ delivers what it claims to deliver: 531 / 531 pytest tests PASS in both reviewer cache mode (oracle + engine_facts substrate) and live-engine BUILD mode against the canonical engine SHA-pin `318eb2f5…`. Zero layer-leakage incidents, zero non-determinism incidents, every numeric constant traced to literature or engine-internal derivation.**

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

## Reproduction

```bash
# Reviewer cache mode (no engine source needed; oracle + facts cache shipped via Zenodo engine_outputs)
python3 -m pytest .                          # ≈ 7 s, 531/531 PASS

# Live-engine BUILD mode (rebuilds the oracle + facts manifest)
MI_BUILD_ORACLE=1 python3 -m pytest .        # ≈ 85 s on M2 8 GB, 531/531 PASS
```

## Historical note (resolved 2026-05-24)

Three K-K 1982 list-equality test cells (L9 major + minor profile match, L10.3 cross-impl) previously failed due to Python `list ==` comparing float32-roundtripped tensors against float64 literature literals — a test-tooling defect, not engine drift. Now use `pytest.approx(abs=1e-4)` (four-decimal tolerance, well below the 0.01 publication precision of the K-K Table 2.2 source).
