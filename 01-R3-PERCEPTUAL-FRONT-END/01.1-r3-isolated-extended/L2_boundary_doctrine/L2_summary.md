# L2 — Boundary Doctrine — Summary

**Engine pin:** `318eb2f5…` · **Total tests:** 24 PASS / 24 (100 %)

L2 quantifies the engine's compliance with the **five inclusion rules** of
the R³ Boundary Doctrine (paper §Boundary doctrine). Each rule moves from
a textual claim to a runnable probe.

---

## Per-rule scorecard

| Rule | Description | Test file | Tests | Verdict |
|------|-------------|-----------|-------|---------|
| **R1** Frame locality       | Output at frame t depends only on t±2 mel frames on Tier-0 dims | [test_l2_1_frame_locality.py](test_l2_1_frame_locality.py) | 8 | ✅ 8/8 PASS |
| **R2** No listener model    | No `listener` / `culture` / `expectation` parameters; output is invariant to listener-proxy env vars | [test_l2_2_no_listener_model.py](test_l2_2_no_listener_model.py) | 4 | ✅ 4/4 PASS |
| **R3** No cross-domain binding | Each group consumes only declared dependencies; Stage-2 deps are narrow | [test_l2_3_group_isolation.py](test_l2_3_group_isolation.py) | 6 | ✅ 6/6 PASS |
| **R4** No prediction        | Truncating the input at frame T leaves earlier frames bit-identical (modulo declared edge cases) | [test_l2_4_no_prediction.py](test_l2_4_no_prediction.py) | 5 | ✅ 5/5 PASS |
| **R5** Deterministic        | Three back-to-back runs on the same audio produce bit-identical output (full coverage in L3) | [test_l2_5_determinism_marker.py](test_l2_5_determinism_marker.py) | 1 | ✅ 1/1 PASS |
| **Total** |  |  | **24** | **✅ 24/24** |

## R1 (frame locality) — what's pinned

- 79 Tier-0 dims × 5 perturbation distances (k ∈ {3, 5, 10, 50, 100}) at frame `t = 200`: all bit-identical at frame `t` after perturbation at `t+k`. **5/5 PASS.**
- Symmetric backward probe: perturbation at `t−10` also leaves frame `t` bit-identical. ✅
- Perturbation at `t±2` is **allowed** to change frame `t` (Rule 1 admits ±2 neighbours, e.g. `tonal_stability` uses 5-frame avg_pool). Test verifies the ±2 perturbation is *handled* (no NaN, output in range), not bit-identical.

## R2 (no listener model) — what's pinned

- `R3Extractor.extract` signature has no listener / user / culture / expectation / history / memory / context / session / subject / personality parameter (substring scan).
- No discovered group's `compute*` methods or instance attributes carry listener-proxy state.
- Sweeping `LANG / LC_ALL / USER / USERNAME / TZ` env vars leaves R³ output bit-identical.

## R3 (no cross-domain binding) — what's pinned

- Every group declares a `DEPENDENCIES` tuple.
- All 7 Stage-1 groups declare `DEPENDENCIES = ()` — they consume only `mel`/`audio`.
- The 2 Stage-2 groups declare exactly their documented dependencies:
  - `rhythm_groove → ('energy',)`
  - `harmony      → ('pitch_chroma',)`
- No group module imports another group module (would create a runtime binding outside the declared DAG).
- **Dynamic dep narrowness probe:**
  - Group G's `compute_with_deps` reads only `energy[:, :, 4]` (`onset_strength`); zeroing other channels of energy leaves G output bit-identical. ✅
  - Group H's `compute_with_deps` reads only `pitch_chroma[:, :, :12]` (the 12-bin chroma); zeroing dims 12–15 (pitch_height, pc_entropy, salience, inharmonicity_index) leaves H output bit-identical. ✅

## R4 (no prediction) — what's pinned and disclosed

- Truncating the mel/audio at `T_trunc ∈ {344, 600, 1000}` leaves all **77 strictly-Rule-1 dims** bit-identical for frames `t < T_trunc − 12`.
- The `−12` margin is the inherited reach of **torchaudio's `center=True` STFT** with `n_fft=4096` (Group A consonance, Group C warmth/sharpness): ±2048 audio samples ≈ ±8 mel frames, so we conservatively skip 12 frames at the truncation tail.
- **Disclosed quirks (pinned):**
  - **dim 92 `fluctuation_strength`** is set by alias to `modulation_4Hz` (dim 86, Tier-1 zero). It inherits Tier-1 truncation behaviour even though it's not in the warmup registry. Documented in L1's `K_modulation.md` and excluded from R4's strict-bit-identity set.
  - **dims 8 `velocity_A`, 9 `acceleration_A`** normalise their per-frame derivatives by the **clip-level mean amplitude** (`b_energy/group.py:32, 39`). This is a deliberate scale-invariance trade-off; it makes velocity / acceleration magnitudes comparable across clips, at the cost of formal Rule-1 frame-locality. Truncation produces ε-deltas of ~5 × 10⁻⁶. Pinned at `0 < |Δ| < 10⁻⁴` so any future engine change to per-window or zero normalisation trips the test.

## R5 (deterministic) — marker only here

L2.5 plants a single sanity-grade fingerprint (3 back-to-back same-audio
runs bit-identical). Full cross-axis determinism (cross-process,
cross-thread, cross-OS, cross-HW, cross-torch-version) is **L3**'s job.

---

## Disclosed boundary-doctrine quirks (full pinning index)

| Dim(s) | Quirk | Disclosed in | Pinned by |
|--------|-------|--------------|-----------|
| 92 (`fluctuation_strength`)   | Aliased to dim 86 (`modulation_4Hz`, Tier-1 zero) — inherits Tier-1 truncation behaviour despite not being in warmup registry | L1 K_modulation.md | L1 `test_fluctuation_strength_equals_modulation_4hz`, L2.4 `ALIASED_TO_WARMUP` exclusion |
| 8 (`velocity_A`), 9 (`acceleration_A`) | Clip-level mean-amplitude normalisation breaks formal Rule-1 frame-locality with ε-truncation deltas | L2.4 | L2.4 `test_velocity_accel_clip_norm_disclosed` |

These quirks are part of R³'s engineering trade-offs — disclosed openly,
not papered over. Each pin auto-trips on a future engine change so
disclosures stay synchronised with code.
