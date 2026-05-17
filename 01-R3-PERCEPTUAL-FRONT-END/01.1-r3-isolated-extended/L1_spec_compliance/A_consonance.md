# L1 — Group A Consonance (dims 00–06) — Spec Compliance Report

**Engine pin:** `318eb2f5…` (SHA-256 aggregate `482ade45…`)
**Test file:** [test_a_consonance.py](test_a_consonance.py)
**Run date:** 2026-05-09 (initial green-baseline)

---

## What L1 verifies

L1 confirms that the engine's output **behaves as the documented spec demands**
on eight stimulus families. This is *engine ↔ spec doc* compliance — not
literature re-implementation (that lives in L10) and not direct audio re-impl
(that also lives in L10).

For each dim we verify:

1. **Range** — output ∈ [0, 1] across all 8 L1 stimulus families.
2. **Well-definedness** — finite (no NaN/Inf) on every family, including silence.
3. **Algebraic identities** the engine enforces by construction.
4. **Direction-of-effect fingerprints** documented in the spec.

---

## Group A spec sources

| Dim | Name | Range | Source |
|-----|------|-------|--------|
| 00  | `roughness`            | [0,1] | Plomp-Levelt 1965 + Sethares 1993, weighted by critical bandwidth (Zwicker & Fastl 2007) |
| 01  | `sethares_dissonance`  | [0,1] | Sethares 1993, 2nd ed. — pairwise dissonance, F0-free |
| 02  | `helmholtz_kang`       | [0,1] | Pairwise ratio simplicity (Euler 1739, Helmholtz 1863) on beating pairs |
| 03  | `stumpf_fusion`        | [0,1] | Pairwise harmonicity (Stumpf 1890), k-tier weighted |
| 04  | `sensory_pleasantness` | [0,1] | `0.6·(1 − sethares) + 0.4·stumpf` — engine identity |
| 05  | `inharmonicity`        | [0,1] | `1 − stumpf_fusion` — engine identity |
| 06  | `harmonic_deviation`   | [0,1] | Spectral decay deviation from `1/rank` |

Code anchor: [Musical_Intelligence/ear/r3/groups/a_consonance/group.py](../../../../Musical_Intelligence/ear/r3/groups/a_consonance/group.py)

---

## Test inventory (30 tests, all PASS)

### Range & well-definedness — 14 tests (7 dims × 2 invariants)

| # | Test | Coverage | Verdict |
|---|------|----------|---------|
| 01 | `test_dim_in_unit_interval_across_eight_stimuli[d00..d06]` | 7 dims × 8 stimulus families = 56 frame-mean checks | ✅ PASS |
| 02 | `test_dim_well_defined_on_silence[d00..d06]`              | 7 dims, silence input, no NaN/Inf                 | ✅ PASS |

### Canonical-name agreement — 7 tests

| # | Test | Coverage | Verdict |
|---|------|----------|---------|
| 03 | `test_dim_index_matches_canonical_name[d00..d06]` | Index ↔ name agreement vs `_infra/dims.py` | ✅ PASS |

### Algebraic identities (engine-enforced) — 2 tests, 8 stimuli each

| # | Identity | Tolerance | Verdict |
|---|----------|-----------|---------|
| 04 | `pleasantness ≡ 0.6·(1 − sethares) + 0.4·stumpf` (clipped) | atol=1e-6, all frames, all 8 stimuli | ✅ PASS |
| 05 | `inharmonicity ≡ 1 − stumpf` (clipped)                    | atol=1e-6, all frames, all 8 stimuli | ✅ PASS |

These identities are encoded in
[group.py:133-134](../../../../Musical_Intelligence/ear/r3/groups/a_consonance/group.py#L133-L134)
of the audio compute path. If they break, something fundamental is wrong.

### Behavioural fingerprints — 6 tests

| # | Stimulus → expected behaviour | Threshold | Verdict |
|---|-------------------------------|-----------|---------|
| 06 | Silence → low sethares           | mean < 0.20 | ✅ PASS |
| 07 | Silence → low roughness          | mean < 0.20 | ✅ PASS |
| 08 | Pure A4 (440 Hz) → low sethares  | steady-state median < 0.30 | ✅ PASS |
| 09 | Pure A4 → high stumpf (no beating ⇒ fallback ceiling) | steady-state median > 0.85 | ✅ PASS |
| 10 | Octave dyad (1:2) more pleasant than minor-second (15:16) | strict ordering | ✅ PASS |
| 11 | Octave dyad less dissonant than minor-second              | strict ordering | ✅ PASS |
| 12 | Perfect-fifth dyad (2:3) less inharmonic than white noise | strict ordering | ✅ PASS |

These verify documented direction-of-effect properties, not magnitude
predictions. They do not invoke any cognitive label, listener panel, or
human-rated dataset. They check that the engine implements its named
psychoacoustic intent.

### Determinism — 1 test

| # | Test | Coverage | Verdict |
|---|------|----------|---------|
| 13 | `test_group_a_bit_identical_across_runs` | Same audio → bit-identical Group A output (max-abs-diff = 0) | ✅ PASS |

---

## Verdict

**Group A: 30/30 spec-compliance checks PASS.** The engine's 7-D consonance
output behaves as its documented spec demands across the eight L1 stimulus
families, satisfies both algebraic identities exactly, preserves direction
of effect on documented dyad orderings, and is bit-identical run-to-run.

**Out of scope here.** Cognitive consonance rating corpora (Eerola Exp3,
Marjieh, Harrison Carillon, cross-cultural anchors), BCH / PCCR mech-level
behaviour — these are downstream-system tests and live in `R3_Success_in_System/`.
**Independent literature re-implementation** of Sethares 1993, Plomp-Levelt
1965, Stumpf 1890 lives in L10.
