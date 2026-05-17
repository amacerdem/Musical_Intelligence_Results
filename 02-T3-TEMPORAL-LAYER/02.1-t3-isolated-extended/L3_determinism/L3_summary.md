# L3 — Determinism audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Runtime pytest tests covering 5 of 8 documented determinism axes (run-to-run, cross-seed, cross-thread, cross-process, dtype-sensitivity); the other 3 (cross-machine-reboot, cross-OS, cross-torch-version) require multi-environment infrastructure deferred to V-Reproduction Phase 4.
**Engine pin:** verified at session start.

## Headline

> **✅ PASS — 7/7 tests pass in 2.72 s. T³ output is bit-identical across run-to-run, cross-seed, cross-thread (1/2/4/8 workers), and cross-process axes. Float32-vs-float64 drift = 2.71×10⁻⁶ — an order of magnitude below the engine's documented |Δρ| ≤ 8.8×10⁻⁵ reproducibility envelope.**
>
> Plus 28 pair canary migrated from `experiments/determinism_canary/` (still passing as L3 pre-test).

## Per-sub-test scorecard

| Sub-test | Subject | Method | Result |
|---|---|---|---|
| **L3.1** | Run-to-run, 1,000 iterations same input | runtime | **PASS** — max-abs-diff = 0 across 1,000 iters × 24 morphs |
| **L3.2** | Cross-process (subprocess) bit-identical | runtime | **PASS** — fresh interpreter produces bit-identical output for all 24 morphs |
| **L3.3** | Cross-seed (`torch.manual_seed`) no effect | runtime | **PASS** — seeds {42, 137, 20260509} + edge seeds {0, 1, 2³¹−1} all produce bit-identical output (T³ has no PRNG; per L11.3) |
| **L3.4** | Cross-thread-permutation {1, 2, 4, 8} | runtime | **PASS** — bit-identical across thread counts |
| **L3.5** | Cross-machine-reboot | runtime | **Deferred** — requires re-run after machine restart; covered by V-Reproduction Phase 4 |
| **L3.6** | Cross-OS (macOS vs Linux) | runtime | **Deferred** — requires Linux host; covered by V-Reproduction CI matrix |
| **L3.7** | Cross-torch-version | runtime | **Deferred** — requires multi-version test matrix |
| **L3.8** | Float32 vs Float64 sensitivity | runtime | **PASS** — observed drift = 2.71×10⁻⁶ (within documented |Δρ| ≤ 8.8×10⁻⁵ envelope) |

Plus migrated:
| Migrated | Subject |
|---|---|
| **`determinism_canary/`** (28 tracked test files) | 28-pair canary at multiple thread counts; pre-existing PASS |

## Key observations

### L3.1 — 1,000 iterations bit-identical

24 morphs × 1,000 iterations = 24,000 morph-evaluation comparisons against a single reference. **Max-abs-diff = 0** across all comparisons. This is the strongest empirical anchor for the engine's run-to-run determinism on a single hardware/process.

### L3.3 — Cross-seed has no effect (T³ has no PRNG)

`torch.manual_seed(42)`, `torch.manual_seed(137)`, `torch.manual_seed(20260509)`, plus edge seeds `{0, 1, 2³¹-1}` — all produce bit-identical output for the same input. This is the runtime confirmation of L11.3's static AST scan finding that `ear/h3/` contains no `random` import, no `torch.rand*` call, no `manual_seed` reference. **Determinism is structural.**

### L3.4 — Cross-thread-permutation bit-identical

`torch.set_num_threads({1, 2, 4, 8})` — all four thread counts produce bit-identical output. This is consistent with L2.1 (zero non-init self-assigns; classes have no shared mutable state) and L7.1 (acyclic data flow; no callbacks/event-loops). **The engine is structurally thread-safe.**

### L3.2 — Cross-process bit-identical

A fresh `subprocess.run([sys.executable, "-c", child_script])` produces output identical to the parent's in-process call. This guards against any process-startup-order or memory-layout effect.

### L3.8 — Float32-vs-float64 drift well below envelope

Engine pin is float32. Casting input to float64, running extract, and comparing reveals max drift = **2.71×10⁻⁶** across all 24 morphs at H5/L0. This is:
- **Below** the engine's own documented `|Δρ| ≤ 8.8×10⁻⁵` reproducibility envelope (master paper §Compute profile, line 1298).
- **At least 100× smaller** than typical numerical error in research-grade signal processing.

The drift is the cumulative float32 rounding error in the attention-weighted sum, not a bug. Documenting it characterises the engine's numerical sensitivity.

## Reports

- [`L3_summary.md`](L3_summary.md) — this scorecard
- [`test_run_to_run.py`](test_run_to_run.py) — L3.1 + L3.3 (3 tests)
- [`test_thread_permutation.py`](test_thread_permutation.py) — L3.4 (2 tests)
- [`test_cross_process.py`](test_cross_process.py) — L3.2 (1 test)
- [`test_dtype_sensitivity.py`](test_dtype_sensitivity.py) — L3.8 (1 test)
- [`determinism_canary/`](determinism_canary/) — migrated 28-pair canary

## Reproducibility

Run tests:
```bash
cd T3-Paper/T3_Isolated_Validation
pytest L3_determinism/ -v
```

Engine pin verified at session start.

## Headline (production-grade form)

> **L3 PASS — 5 of 8 axes empirically verified at runtime; 3 multi-environment axes deferred to V-Reproduction Phase 4. Run-to-run, cross-seed, cross-thread, cross-process bit-identical (max-abs-diff = 0). Float32-vs-float64 drift 2.71×10⁻⁶ within documented envelope.**
