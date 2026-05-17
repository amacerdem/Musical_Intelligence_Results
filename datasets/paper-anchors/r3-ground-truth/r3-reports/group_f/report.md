# R³ Group F — Scientific Validation Report
# Pitch & Chroma (16D, indices [25:41])

**Date:** 2026-03-24
**Result:** 33/33 PASS
**WAV files tested:** 78
**Dataset:** Krumhansl & Kessler 1982 (12 probe-tone profiles)

---

## Scientific Questions

1. Does chroma correctly identify pitch classes from WAV files?
2. Is pitch_height monotonic with octave (C2 < C3 < C4 < C5 < C6)?
3. Does pitch_class_entropy discriminate tonal from chromatic content?
4. Does mel-based chroma correlate with Krumhansl probe-tone profiles?
5. Does pitch_salience discriminate tonal from noise signals?

---

## Test Summary

| Tier | Total | Pass | Description |
|------|-------|------|-------------|
| T1_formula | 8 | 8 | Chroma normalization, pitch height monotonic, PCE bounds, salience |
| T2_pipeline | 11 | 11 | Metadata, shapes, NaN, determinism |
| T3_stimulus | 5 | 5 | 12 pitch classes, octave series, salience, C major diatonic |
| T4_ground_truth | 5 | 5 | Krumhansl 1982 major/minor + bootstrap CI + 12-scale consistency |
| T5_ecological | 4 | 4 | 45 genres: NaN, chroma, pitch height variance |
| **TOTAL** | **33** | **33** | |

---

## Result 1: Krumhansl Probe-Tone Correlations

Each major scale's chroma (rotated to C-root) vs published major profile.

| Scale | ρ vs Krumhansl | p |
|-------|---------------|---|
| C major | +0.462 | 0.1309 ns |
| Cs major | +0.224 | 0.4845 ns |
| D major | +0.580 | 0.0479 * |
| Ds major | +0.231 | 0.4705 ns |
| E major | +0.294 | 0.3541 ns |
| F major | +0.434 | 0.1591 ns |
| Fs major | +0.315 | 0.3191 ns |
| G major | +0.629 | 0.0283 * |
| Gs major | +0.336 | 0.2861 ns |
| A major | +0.510 | 0.0899 ns |
| As major | +0.476 | 0.1182 ns |
| B major | +0.469 | 0.1245 ns |

**Scales with ρ > 0.40:** 7/12

---

## Result 2: Pitch Height Monotonicity

| Octave | pitch_height |
|--------|-------------|
| pitch_C2 | 0.2697 |
| pitch_C3 | 0.3870 |
| pitch_C4 | 0.4852 |
| pitch_C5 | 0.5876 |
| pitch_C6 | 0.6942 |
| pitch_Cs4 | 0.4966 |

---

## Ecological (45 Genres)

| Genre | pitch_height | PCE | salience |
|-------|-------------|-----|----------|
| african_polyrhythm | 0.077 | 0.228 | 0.245 |
| ambient_pad | 0.361 | 0.978 | 0.998 |
| celtic | 0.428 | 0.911 | 0.975 |
| chillout | 0.355 | 0.961 | 1.000 |
| cinematic_epic | 0.307 | 0.975 | 1.000 |
| cinematic_tension | 0.356 | 0.972 | 1.000 |
| classical_chamber | 0.515 | 0.972 | 0.995 |
| classical_choir | 0.372 | 0.960 | 1.000 |
| classical_orchestral | 0.337 | 0.968 | 1.000 |
| classical_piano | 0.469 | 0.874 | 0.903 |
| classical_strings | 0.471 | 0.965 | 0.995 |
| country | 0.383 | 0.792 | 0.803 |
| dnb | 0.305 | 0.963 | 0.944 |
| east_asian_pentatonic | 0.369 | 0.849 | 0.997 |
| edm_house | 0.404 | 0.990 | 0.913 |
| electronic_glitch | 0.106 | 0.670 | 0.990 |
| flamenco | 0.431 | 0.770 | 0.973 |
| funk | 0.430 | 0.622 | 0.140 |
| gamelan | 0.400 | 0.819 | 0.903 |
| gospel | 0.356 | 0.967 | 1.000 |
| hiphop_beat | 0.025 | 0.655 | 0.990 |
| indian_raga | 0.397 | 0.977 | 0.997 |
| indie_folk | 0.386 | 0.792 | 0.743 |
| jazz_ballad | 0.504 | 0.938 | 0.994 |
| jazz_bossa | 0.423 | 0.968 | 0.979 |
| jazz_fusion | 0.546 | 0.877 | 0.445 |
| jazz_modal | 0.413 | 0.897 | 0.991 |
| jazz_swing | 0.571 | 0.898 | 0.277 |
| latin_salsa | 0.411 | 0.980 | 0.995 |
| lofi_hiphop | 0.708 | 0.997 | 0.563 |
| metal | 0.520 | 0.996 | 0.688 |
| middle_eastern | 0.438 | 0.982 | 0.994 |
| new_age_meditation | 0.728 | 0.997 | 0.418 |
| pop_ballad | 0.474 | 0.934 | 0.998 |
| pop_synth | 0.407 | 0.910 | 0.987 |
| reggae | 0.128 | 0.655 | 1.000 |
| rock_blues | 0.315 | 0.853 | 0.945 |
| rock_power | 0.595 | 0.997 | 0.583 |
| social_anti_hook | 0.358 | 0.622 | 0.656 |
| social_call_response | 0.463 | 0.711 | 0.818 |
| social_catchy_hook | 0.548 | 0.911 | 0.984 |
| social_ensemble_polyphonic | 0.399 | 0.976 | 1.000 |
| social_ensemble_unison | 0.411 | 0.949 | 1.000 |
| soul_rnb | 0.354 | 0.969 | 0.995 |
| techno_minimal | 0.150 | 0.662 | 0.976 |

---

## Files

| File | Purpose |
|------|---------|
| `validation/r3/group_f/test_formula.py` | T1: 8 tests |
| `validation/r3/group_f/test_pipeline.py` | T2: 11 tests |
| `validation/r3/group_f/test_stimulus.py` | T3: 5 tests (12 pitch WAVs + 48 scales) |
| `validation/r3/group_f/test_ground_truth.py` | T4: 5 tests (Krumhansl 1982) |
| `validation/r3/group_f/test_ecological.py` | T5: 4 tests (45 genres) |
| `results/r3/group_f/report.json` | Machine-readable |
| `results/r3/group_f/report.md` | This report |