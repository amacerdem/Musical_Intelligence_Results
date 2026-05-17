# L1 — Group B Energy (dims 07–11) — Spec Compliance Report

**Engine pin:** `318eb2f5…` (SHA-256 aggregate `482ade45…`)
**Test file:** [test_b_energy.py](test_b_energy.py)

---

## Group B spec sources

| Dim | Name             | Range | Engine formula                                                       |
|-----|------------------|-------|----------------------------------------------------------------------|
| 07  | `amplitude`      | [0,1] | `sigmoid(8·(rms_log_mel − 0.25))` — Stevens-style absolute-RMS gate |
| 08  | `velocity_A`     | [0,1] | `sigmoid(8·diff1 / mean_rms)` — first derivative, scale-invariant   |
| 09  | `acceleration_A` | [0,1] | `sigmoid(12·diff2 / mean_rms)` — second derivative                  |
| 10  | `loudness`       | [0,1] | `sigmoid(6·(amp^0.3 − 0.5))` — Stevens 1957 power-law (γ ≈ 0.3)     |
| 11  | `onset_strength` | [0,1] | `sigmoid(12·(HWR_flux/N − 0.3))` — half-wave-rectified spectral flux |

Code anchor: [Musical_Intelligence/ear/r3/groups/b_energy/group.py](../../../../Musical_Intelligence/ear/r3/groups/b_energy/group.py)

---

## Test inventory (26 tests, all PASS)

### Range & well-definedness — 10 tests (5 dims × 2 invariants)

| # | Test                                                | Coverage                              | Verdict |
|---|-----------------------------------------------------|---------------------------------------|---------|
| 01 | `test_dim_in_unit_interval_across_eight_stimuli`   | 5 dims × 8 families = 40 frame checks | ✅ PASS |
| 02 | `test_dim_well_defined_on_silence`                  | 5 dims, no NaN/Inf on silence         | ✅ PASS |

### Canonical-name agreement — 5 tests

| # | Test                                              | Coverage                          | Verdict |
|---|---------------------------------------------------|-----------------------------------|---------|
| 03 | `test_dim_index_matches_canonical_name`          | Index ↔ name vs `_infra/dims.py` | ✅ PASS |

### Boundary-frame identities — 3 tests

The engine enforces the following at clip boundaries (stateless design):

| # | Identity                                    | Expected value                      | Verdict |
|---|---------------------------------------------|-------------------------------------|---------|
| 04 | `velocity_A[t=0] = sigmoid(diff1=0)`       | `0.500` ± 1e-6                     | ✅ PASS |
| 05 | `acceleration_A[t=0,1] = sigmoid(diff2=0)` | `0.500` ± 1e-6                     | ✅ PASS |
| 06 | `onset_strength[t=0] = sigmoid(-3.6)`      | `0.0266` ± 1e-3                    | ✅ PASS |

These ensure no hidden initial-state leakage at frame 0.

### Behavioural fingerprints — 7 tests

| # | Stimulus → expected behaviour                                              | Threshold                          | Verdict |
|---|----------------------------------------------------------------------------|------------------------------------|---------|
| 07 | Silence → amplitude at sigmoid(-2)                                          | median ≈ 0.119, tol 5e-3           | ✅ PASS |
| 08 | Silence → loudness at sigmoid(-3)                                           | median ≈ 0.047, tol 5e-3           | ✅ PASS |
| 09 | Pure A4 has higher amplitude than silence                                   | strict ordering                    | ✅ PASS |
| 10 | Pure A4 has higher loudness than silence                                    | strict ordering                    | ✅ PASS |
| 11 | Tone burst (silence → tone) → onset spike at burst start                    | burst_max > 2× silence baseline    | ✅ PASS |
| 12 | Constant-amp tone steady-state → velocity ≈ 0.5 (no derivative)             | tol 0.02                           | ✅ PASS |
| 13 | Constant-amp tone steady-state → acceleration ≈ 0.5 (no curvature)          | tol 0.02                           | ✅ PASS |

### Determinism — 1 test

| # | Test                                              | Coverage                          | Verdict |
|---|---------------------------------------------------|-----------------------------------|---------|
| 14 | `test_group_b_bit_identical_across_runs`         | Same audio → bit-identical 5-D    | ✅ PASS |

---

## Verdict

**Group B: 26/26 spec-compliance checks PASS.** The five energy dims behave
exactly as their documented sigmoid-normalised RMS / flux / derivative
formulas demand, with correct boundary-frame zero-init and steady-state
neutrality on constant-amplitude inputs.

**Note on the impulse stimulus.** A Dirac at `t=0` produces only a *falling*
mel-bin transition after the engine's frame-0 boundary, so HWR onset stays
at its silence baseline; the onset fingerprint is therefore tested with a
silence-→-tone burst stimulus, which is the engine's documented "rising
edge" detection target. Using a Dirac at `t=0` to test onset would test the
*opposite* of what the formula computes — this is a known stimulus-design
nuance, not an engine deficiency.

**Out of scope here.** Loudness perception against ISO 226 / Pulse, onset
agreement with annotated boundaries, groove perception — those are
downstream-cognition tests living in `R3_Success_in_System/`. Independent
re-implementation of Stevens 1957 power-law lives in L10.
