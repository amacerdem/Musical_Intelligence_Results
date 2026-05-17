# _infra — Test fixtures, stimuli, engine pin

> **Status:** **POPULATED + PIN VERIFIED (2026-05-09)**. 7/7 sanity tests PASS at commit time.

## Layout

```
_infra/
├── __init__.py
├── sha_utils.py               ← engine-tree SHA-256 aggregator (verbatim from R3)
├── stimuli.py                 ← analytical R³ feature-stream generators for T³ testing
├── test_pin_integrity.py      ← session-start sanity checks (engine pin + H3 import + smoke)
├── audit_scripts/             ← static-analysis audit scripts (L2, L7, L8, L9, L11, L12)
│   ├── h3_anti_features_audit.py
│   ├── h3_api_audit.py
│   ├── h3_constants_audit.py
│   ├── h3_horizon_audit.py
│   ├── h3_pipeline_audit.py
│   └── h3_statelessness_audit.py
└── manifests/
    └── engine_pin.json        ← pinned commit + SHA-256 aggregate

(One level up: `T3_Isolated_Validation/conftest.py` — root pytest fixtures)
```

## How fixtures wire up

The pytest discovery order is:

1. `T3_Isolated_Validation/conftest.py` is auto-discovered when running pytest from this directory.
2. The conftest's session-start `_pin_integrity` fixture (autouse) computes the SHA-256 aggregate of all `.py` files under `Musical_Intelligence/` and asserts it matches `engine_pin.json:content_aggregate_sha256`.
3. **If the engine drifts, the entire session halts at start** with a clear message. This guards against running tests against an unintended engine.
4. Per-test fixtures: `h3` (H3Extractor instance, session-scope), `h3_extract` (callable wrapper), `stim` (stimuli module shortcut), `engine_pin` (parsed manifest), `project_root` (Path).

## Stimulus library (`stimuli.py`)

R³ feature-stream generators for testing T³ in isolation. All return `Tensor` of shape `(B, T, 97)`, values in `[0, 1]`, deterministic.

| Generator | Purpose |
|---|---|
| `stim_constant(value, T, B, r3_dim)` | All-value (or single-dim) R³ stream — for L6.M0 mean, L6.M2 std (= 0), L6.M8 velocity (= 0) |
| `stim_silence(T, B)` | All-zero R³ stream — edge case for every morph |
| `stim_linear_ramp(start, end, T, B, r3_dim)` | Linearly-increasing — L6.M8 velocity (= constant), L6.M18 trend (= positive slope) |
| `stim_step(low, high, step_at, T, B, r3_dim)` | Step function — L6.M22 peak count, L6.M18 trend |
| `stim_sinusoid(freq_hz, amp, dc, T, B, r3_dim, phase_rad)` | Sinusoid at known frequency — L6.M14 periodicity peak at horizon ≈ FRAME_RATE/freq_hz |
| `stim_am_modulated(carrier_dc, mod_freq_hz, mod_depth, T, B, r3_dim)` | AM-modulated wrapper around `stim_sinusoid` |
| `stim_impulse(impulse_at, height, baseline, T, B, r3_dim)` | Single-frame Dirac — L6.M22 peak count = 1 |
| `stim_single_dim_only(values, r3_dim, B)` | Wrap arbitrary 1-D series at one R³ dim, zero others |

Demand factories:
| Factory | Returns |
|---|---|
| `demand_single(r3_idx, horizon, morph, law)` | 1-tuple set |
| `demand_all_morphs_one_horizon(r3_idx, horizon, law)` | 24-tuple set |
| `demand_all_horizons_one_morph(r3_idx, morph, law)` | 32-tuple set |
| `demand_all_laws_one_tuple(r3_idx, horizon, morph)` | 3-tuple set |

## Pin manifest (`manifests/engine_pin.json`)

Identical to `R3-Paper/R3_Isolated_Validation/_infra/manifests/engine_pin.json` (the engine is shared between R³ and T³ companion validations). Pinned commit: `318eb2f5...` (canonical paper-validated engine, 2026-05-08). SHA-256 aggregate: `482ade45...`.

To re-pin after engine update:

```bash
# Compute new aggregate
find Musical_Intelligence -type f -name '*.py' -not -path '*/__pycache__/*' \
  | sort | xargs shasum -a 256 | awk '{print $1}' | shasum -a 256 | awk '{print $1}'

# Update content_aggregate_sha256 in manifests/engine_pin.json
```

## Sanity test results (`pytest _infra/test_pin_integrity.py`)

7/7 PASS at infra commit time (2026-05-09):

```
test_engine_sha_aggregate_matches_pin       PASSED  [ 14%]
test_h3_extractor_imports                   PASSED  [ 28%]
test_h3_constants_import_and_match_spec     PASSED  [ 42%]
test_h3_extract_empty_demand_returns_empty  PASSED  [ 57%]
test_h3_extract_single_tuple_runs           PASSED  [ 71%]
test_h3_extract_twice_bit_identical         PASSED  [ 85%]   ← empirical L2.4 / L12.6 confirmation
test_h3_output_is_frozen_dataclass          PASSED  [100%]
```

Each test guards a different invariant:
- **engine SHA aggregate** — engine is at the pinned commit
- **H3Extractor + H3Output imports** — public API resolves
- **Constants spec match** — N_HORIZONS=32, N_MORPHS=24, N_LAWS=3, ATTENTION_DECAY=3.0, etc.
- **Empty-demand path** — `extract({}, set())` returns empty `H3Output`
- **Single-tuple smoke** — `extract` runs end-to-end on synthetic sinusoid; output shape `(1, 512)`, no NaN/Inf
- **Determinism smoke** — two consecutive `extract` calls produce bit-identical output (max-abs-diff = 0)
- **H3Output frozen** — `dataclass(frozen=True)` enforced; assignment raises `FrozenInstanceError`

## Audit-script catalogue (`audit_scripts/`)

Static-analysis scripts that produced the L2, L7, L8, L9, L11, L12 audit reports. All byte-deterministic against the engine source; re-run any of them to verify the corresponding layer:

| Script | Layer | Output |
|---|---|---|
| `h3_statelessness_audit.py` | L2 | `L2_statelessness/L2.1_ast_audit.{md,json}` |
| `h3_pipeline_audit.py` | L7 | `L7_pipeline_dag/L7_audit.json` |
| `h3_horizon_audit.py` | L8 | `L8_horizon_scale/L8_audit.json` |
| `h3_constants_audit.py` | L9 | `L9_constants/L9.1_inventory.{md,json}` |
| `h3_anti_features_audit.py` | L11 | `L11_anti_features/L11_audit.json` |
| `h3_api_audit.py` | L12 | `L12_api/L12_audit.json` |

Each script is self-contained and can be re-run independently.

## Engine pin

All tests run against engine HEAD per `manifests/engine_pin.json`. Pin-drift detection halts the session at start.

## Source-of-truth links

- Engine source: `Musical_Intelligence/ear/h3/`
- Engine pin: `manifests/engine_pin.json`
- R³ counterpart: `R3-Paper/R3_Isolated_Validation/_infra/` (this T³ infra is structurally parallel)
