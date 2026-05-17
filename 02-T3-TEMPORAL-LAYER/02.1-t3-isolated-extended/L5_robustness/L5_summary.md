# L5 — Robustness audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Runtime pytest tests against `H3Extractor.extract()` for short clips, long clips (Macro/Ultra horizons), and input-extreme behavior (NaN, Inf, out-of-range R³ values).
**Engine pin:** verified at session start (autouse `_pin_integrity` fixture)

## Headline

> **✅ PASS — 21/21 tests pass in 0.48 s.** Engine produces well-defined finite output for any T ≥ 1, including T much smaller than the requested horizon's window (fall-back to whole-sequence broadcast). Ultra-band horizons (H24-H31) work on clips as short as 100 frames. **NaN in R³ input propagates to output (documented; no engine-side sanitization); Inf in R³ input is implicitly clamped via final normalization.**
>
> **Bonus result:** L7.4 dependency narrowness is empirically confirmed at runtime — contamination at dim 5 does NOT leak to a dim-10 query.

## Per-sub-test scorecard

| Sub-test | Subject | Tests | Result |
|---|---|---|---|
| **L5.5/L5.6** | Short clips (T=1, T<window, T at boundary, sub-Macro, sub-Ultra) | 9 | **PASS** |
| **L5.7** | Long clips (Macro full window, multi-window; Ultra fall-back; MAX_DURATION_S envelope) | 6 | **PASS** |
| **L5.8** | Input extremes (NaN propagates, Inf clamped, out-of-range clamped, dim isolation) | 6 | **PASS** |

## Test coverage detail

### Short clips — `test_short_clips.py` (9 tests)

| Test | Anchor |
|---|---|
| `test_T1_single_frame_returns_shape_1` | T=1, H5 window=8: returns (1,1) with input value preserved |
| `test_T_at_horizon_boundary` | T=8, H5 window=8: returns (1,8), all values 0.5 |
| `test_T_smaller_than_horizon_window` | T=4 < window=8: returns (1,4), constant preserved |
| `test_T_smaller_than_largest_requested_horizon_macro` | T=200, H16=172 frames: works (T > window) |
| `test_T_smaller_than_macro_horizon_window` | T=50, H16=172: T<<window, fall-back works |
| `test_T_smaller_than_ultra_horizon_window` | T=100, H24=6,202: T<<<window, fall-back works |
| `test_T_at_largest_horizon_minus_one` | T=171, H16=172: T = window-1, fall-back |
| `test_T1_silence` | T=1, silence: M0=0, M2=0 well-defined |
| `test_short_clip_all_morphs_no_nan` | T=4, all 24 morphs at H5: no NaN/Inf |

### Long clips — `test_long_clips.py` (6 tests)

| Test | Anchor |
|---|---|
| `test_macro_horizon_full_window` | T=200, H16=172: full Macro window |
| `test_macro_horizon_multi_window` | T=600, H16/H17/H18: multiple Macro windows |
| `test_ultra_horizon_short_subwindow` | T=1000 << H24=6202: fall-back to single value broadcast |
| `test_ultra_horizon_full_window_H24` | T=8000 > H24=6202: both fall-back and steady-state available |
| `test_max_duration_envelope_30s` | T=5165 ≈ 30s: H16-H22 all produce finite |
| `test_ultra_band_all_horizons_short_clip` | T=200, H24-H31: all 8 Ultra horizons fall back to whole-sequence |

### Input extremes — `test_input_extremes.py` (6 tests, all PASS as documented behavior)

| Test | DOCUMENTED BEHAVIOR |
|---|---|
| `test_nan_in_input_propagates_to_output` | **NaN propagates.** Engine has no input sanitization at T³ stage. Upstream R³ contract is "no NaN"; if violated, T³ propagates without error. |
| `test_inf_in_input_clamped_via_normalization` | **Inf is clamped to bounds.** The final `clamp(raw / scale, lo, hi)` normalization step converts Inf to the boundary value (0 or 1 unsigned; -1 or 1 signed). Output is finite. |
| `test_negative_input_clamped` | R³ value -0.5: M0 (unsigned) clamps to [0, 1]. |
| `test_above_unit_input_clamped` | R³ value 2.5: M0 clamps to [0, 1]. |
| `test_input_at_exact_boundaries_zero_and_one` | All 24 morphs survive R³ values 0.0 and 1.0 without overflow. |
| `test_mixed_extreme_input_dimensions` | dim 5 = NaN, dim 20 = Inf, query dim 10: **dim 10 output is uncontaminated** (L7.4 dependency narrowness empirically confirmed). |

## Documented behaviors (engine contract clarification)

L5 surfaces three formerly-undocumented engine behaviors:

1. **No NaN sanitization at T³ stage.** If R³ output contains NaN (which violates R³'s own contract), T³ propagates it. Downstream consumers should not rely on T³ to sanitize.

2. **Inf clamping is implicit.** The `clamp(raw / scale, lo, hi)` step in `morphology/scaling.py` converts Inf to the boundary. T³ outputs are guaranteed finite even when the input contains Inf.

3. **Out-of-range input is clamped per-morph.** R³ values outside [0, 1] (negative or > 1) produce outputs clamped to each morph's documented bound. T³ does not raise; it normalises silently.

These three behaviors are **operator-level contracts** that should be referenced from the T³ paper's `H3Extractor` API documentation and from `T3_Isolated_Validation/L12_api/`.

## Bonus: L7.4 dependency narrowness — empirical confirmation

`test_mixed_extreme_input_dimensions` is the runtime version of L7.4 (which was deferred):

> Querying T³ feature `(r3_idx=10, h, m, ℓ)` reads only frames in R³ dim 10. Contamination of other dims (5 = NaN, 20 = Inf) does not affect the dim-10 query.

This is consistent with the executor.py:139 line `r3_series = r3_tensor[:, :, r3_idx]` — only the queried dim is read.

## Reports

- [`L5_summary.md`](L5_summary.md) — this scorecard
- [`test_short_clips.py`](test_short_clips.py) — 9 short-clip tests
- [`test_long_clips.py`](test_long_clips.py) — 6 long-clip tests
- [`test_input_extremes.py`](test_input_extremes.py) — 6 input-extreme tests

## Reproducibility

Run tests:
```bash
cd T3-Paper/T3_Isolated_Validation
pytest L5_robustness/ -v
```

Engine pin verified at session start.

## Headline (production-grade form)

> **L5 PASS — 21/21:** engine well-defined for any T ≥ 1; Ultra-band horizons work on clips of any size via fall-back; documented behaviors for input extremes (NaN propagates; Inf clamped; out-of-range clamped); dependency narrowness empirically verified at runtime.
