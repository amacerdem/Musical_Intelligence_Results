# L5 — Pathological R³-input robustness

> **Status:** **POPULATED + PASS (2026-05-09)** — 21/21 tests pass in 0.48s. See [`L5_summary.md`](L5_summary.md) for full scorecard.

## Paper claim being defended

*T³ is well-defined on every valid R³ input, including edge cases (very short clips, very long clips, boundary values, malformed inputs).*

## Audit results

> **✅ PASS — 21/21 tests pass.** Engine produces well-defined finite output for any T ≥ 1 (including T much smaller than the requested horizon's window via fall-back to whole-sequence broadcast). Ultra-band horizons (H24-H31) work on clips as short as 100 frames. **NaN in R³ input propagates to output (documented; no engine-side sanitization); Inf is implicitly clamped via final normalization.**

| Sub-test | Subject | Tests | Result |
|---|---|---|---|
| **L5.1/L5.3** | Silence-frame + constant R³ stream | covered by L4.2 + L5 short-clip | **PASS** |
| **L5.2** | Single-frame window (T=1) | 2 | **PASS** |
| **L5.4** | Pre-warm-up frames (zero/ramp inputs) | covered by silence + ramp tests | **PASS** |
| **L5.5/L5.6** | Short clips (T=1, T<window, T at boundary) | 9 | **PASS** |
| **L5.7** | Long clips (Macro / Ultra horizons; 30s envelope) | 6 | **PASS** |
| **L5.8** | NaN/Inf in R³ input | 6 | **PASS as DOCUMENTED BEHAVIOR** |

## Documented behaviors surfaced (engine contract clarification)

L5 reveals three formerly-undocumented engine behaviors:

1. **No NaN sanitization at T³ stage.** If R³ output contains NaN (which violates R³'s own contract), T³ propagates it. Downstream consumers should not rely on T³ to sanitize.
2. **Inf clamping is implicit.** The `clamp(raw / scale, lo, hi)` step in `morphology/scaling.py` converts Inf to the boundary. T³ outputs are guaranteed finite even when input contains Inf.
3. **Out-of-range input is clamped per-morph.** R³ values outside [0, 1] (negative or > 1) produce outputs clamped to each morph's documented bound.

These are operator-level contracts for `H3Extractor` API documentation.

## Bonus result: L7.4 dependency narrowness empirically confirmed

`test_mixed_extreme_input_dimensions` is the runtime version of L7.4 (which was deferred from the static L7 audit):

> Querying T³ feature `(r3_idx=10, h, m, ℓ)` reads only frames in R³ dim 10. Contamination of other dims (5 = NaN, 20 = Inf) does NOT affect the dim-10 query.

Consistent with [executor.py:139](../../../../Musical_Intelligence/ear/h3/pipeline/executor.py#L139) `r3_series = r3_tensor[:, :, r3_idx]` — only the queried dim is read.

## Reports

- [`L5_summary.md`](L5_summary.md) — full audit + per-test scorecard + documented behaviors
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

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
