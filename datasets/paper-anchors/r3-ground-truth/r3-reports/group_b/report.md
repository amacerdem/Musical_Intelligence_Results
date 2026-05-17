# R³ Group B — Scientific Validation Report
# Energy (5D, indices [7:12])

**Date:** 2026-03-24
**Result:** 48/48 PASS
**WAV files tested:** 62
**Bugs found & fixed:** 3

---

## Scientific Questions

1. Does loudness follow Stevens' power law (exponent 0.3)?
2. Does amplitude correctly rank 6 dynamics levels (pp→ff)?
3. Does onset detection produce periodic peaks matching BPM?
4. Does velocity encode temporal dynamics direction?
5. Are amplitude and loudness monotonically related?

---

## Test Summary

| Tier | Tests | Pass | Description |
|------|-------|------|-------------|
| T1_formula | 10 | 10 | Stevens exponent, velocity/accel sigmoid, output ranges |
| T2_pipeline | 10 | 10 | Metadata, shapes, NaN, determinism |
| T3_stimulus | 12 | 12 | 6 dynamics + crescendo/decrescendo/sforzando + click onset + controls |
| T4_ground_truth | 9 | 9 | Stevens law, dynamics rank+permutation, click BPM, velocity direction, cross-feature consistency |
| T5_ecological | 5 | 5 | 45 genres: NaN, range, variance, genre ordering |
| **TOTAL** | **48** | **48** | |

---

## Bugs Found and Fixed

- **B-001:** Per-file max-norm destroyed cross-file amplitude ordering → Fix: `sigmoid(8*(x-0.25))` [FIXED]
- **B-002:** sigmoid(5*diff) compressed acceleration → Fix: `Normalized by mean amplitude, scale=12` [FIXED]
- **B-003:** onset max-norm broke cross-file comparison → Fix: `sigmoid(12*(x/N-0.3))` [FIXED]

---

## Result 1: Dynamics Amplitude Ordering

Amplitude vs dynamics rank (pp=1, ff=6): **ρ = +1.000**, 95% CI [+1.000, +1.000], permutation p = 0.0030

| Dynamic | amplitude | velocity | accel | loudness | onset |
|---------|-----------|----------|-------|----------|-------|
| dynamics_pp.wav | 0.3876 | 0.5002 | 0.4984 | 0.6596 | 0.0266 |
| dynamics_p.wav | 0.4556 | 0.5001 | 0.4990 | 0.7004 | 0.0266 |
| dynamics_mp.wav | 0.4902 | 0.5001 | 0.4993 | 0.7181 | 0.0266 |
| dynamics_mf.wav | 0.5124 | 0.5001 | 0.4995 | 0.7286 | 0.0266 |
| dynamics_f.wav | 0.5257 | 0.5001 | 0.4996 | 0.7347 | 0.0267 |
| dynamics_ff.wav | 0.5352 | 0.5001 | 0.4996 | 0.7389 | 0.0267 |

---

## Result 2: Click Track BPM Detection

| Expected BPM | Measured BPM | Peaks Detected |
|-------------|-------------|----------------|
| 100 | 99.9 | 3 |
| 120 | 120.2 | 3 |
| 140 | 139.7 | 4 |
| 160 | 159.0 | 5 |
| 180 | 179.8 | 5 |

---

## Result 3: Velocity Direction

- Crescendo mean velocity: **0.5049** (> 0.5 = rising)
- Decrescendo mean velocity: **0.4952** (< 0.5 = falling)

---

## Result 4: Amplitude-Loudness Consistency

Spearman ρ across all dynamics + control stimuli: **+1.000**

---

## Ecological (45 Genres)

| Genre | ampl | vel | accel | loud | onset |
|-------|------|-----|-------|------|-------|
| african_polyrhythm | 0.168 | 0.479 | 0.487 | 0.172 | 0.028 |
| ambient_pad | 0.522 | 0.499 | 0.500 | 0.693 | 0.027 |
| celtic | 0.538 | 0.500 | 0.497 | 0.738 | 0.029 |
| chillout | 0.456 | 0.500 | 0.500 | 0.699 | 0.027 |
| cinematic_epic | 0.437 | 0.500 | 0.500 | 0.683 | 0.028 |
| cinematic_tension | 0.502 | 0.500 | 0.500 | 0.719 | 0.027 |
| classical_chamber | 0.637 | 0.500 | 0.500 | 0.780 | 0.027 |
| classical_choir | 0.567 | 0.500 | 0.500 | 0.753 | 0.027 |
| classical_orchestral | 0.494 | 0.500 | 0.499 | 0.716 | 0.029 |
| classical_piano | 0.415 | 0.495 | 0.499 | 0.603 | 0.027 |
| classical_strings | 0.615 | 0.500 | 0.500 | 0.771 | 0.027 |
| country | 0.289 | 0.484 | 0.498 | 0.447 | 0.028 |
| dnb | 0.215 | 0.497 | 0.492 | 0.446 | 0.028 |
| east_asian_pentatonic | 0.338 | 0.500 | 0.498 | 0.599 | 0.027 |
| edm_house | 0.318 | 0.499 | 0.500 | 0.597 | 0.028 |
| electronic_glitch | 0.277 | 0.500 | 0.498 | 0.555 | 0.027 |
| flamenco | 0.305 | 0.477 | 0.498 | 0.542 | 0.029 |
| funk | 0.567 | 0.479 | 0.468 | 0.534 | 0.041 |
| gamelan | 0.281 | 0.491 | 0.498 | 0.509 | 0.027 |
| gospel | 0.418 | 0.500 | 0.500 | 0.632 | 0.027 |
| hiphop_beat | 0.284 | 0.498 | 0.499 | 0.567 | 0.027 |
| indian_raga | 0.592 | 0.500 | 0.496 | 0.759 | 0.031 |
| indie_folk | 0.368 | 0.489 | 0.498 | 0.526 | 0.028 |
| jazz_ballad | 0.594 | 0.500 | 0.500 | 0.763 | 0.027 |
| jazz_bossa | 0.269 | 0.499 | 0.499 | 0.474 | 0.027 |
| jazz_fusion | 0.648 | 0.495 | 0.490 | 0.698 | 0.033 |
| jazz_modal | 0.436 | 0.500 | 0.499 | 0.664 | 0.027 |
| jazz_swing | 0.731 | 0.485 | 0.490 | 0.744 | 0.035 |
| latin_salsa | 0.490 | 0.499 | 0.500 | 0.717 | 0.027 |
| lofi_hiphop | 0.551 | 0.500 | 0.500 | 0.743 | 0.029 |
| metal | 0.567 | 0.500 | 0.494 | 0.752 | 0.031 |
| middle_eastern | 0.645 | 0.500 | 0.491 | 0.779 | 0.033 |
| new_age_meditation | 0.599 | 0.500 | 0.500 | 0.743 | 0.030 |
| pop_ballad | 0.543 | 0.500 | 0.500 | 0.742 | 0.027 |
| pop_synth | 0.373 | 0.500 | 0.497 | 0.638 | 0.028 |
| reggae | 0.322 | 0.497 | 0.498 | 0.604 | 0.027 |
| rock_blues | 0.429 | 0.492 | 0.498 | 0.670 | 0.029 |
| rock_power | 0.648 | 0.500 | 0.500 | 0.784 | 0.029 |
| social_anti_hook | 0.349 | 0.499 | 0.490 | 0.472 | 0.028 |
| social_call_response | 0.422 | 0.499 | 0.496 | 0.597 | 0.028 |
| social_catchy_hook | 0.519 | 0.500 | 0.498 | 0.730 | 0.029 |
| social_ensemble_polyphonic | 0.478 | 0.500 | 0.499 | 0.711 | 0.028 |
| social_ensemble_unison | 0.381 | 0.500 | 0.499 | 0.650 | 0.027 |
| soul_rnb | 0.533 | 0.500 | 0.496 | 0.734 | 0.030 |
| techno_minimal | 0.277 | 0.500 | 0.497 | 0.553 | 0.028 |

---

## Files

| File | Purpose |
|------|---------|
| `Musical_Intelligence/ear/r3/groups/b_energy/group.py` | **MODIFIED** — sigmoid normalization |
| `validation/r3/group_b/test_formula.py` | T1: 10 tests |
| `validation/r3/group_b/test_pipeline.py` | T2: 10 tests |
| `validation/r3/group_b/test_stimulus.py` | T3: 12 tests |
| `validation/r3/group_b/test_ground_truth.py` | T4: 9 tests (Stevens, rank+permutation, BPM, velocity, consistency) |
| `validation/r3/group_b/test_ecological.py` | T5: 5 tests |
| `results/r3/group_b/report.json` | Machine-readable |
| `results/r3/group_b/report.md` | This report |