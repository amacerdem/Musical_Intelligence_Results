# R³ Group H — Scientific Validation Report
# Harmony & Tonality (12D, indices [51:63])

**Date:** 2026-03-24
**Result:** 32 PASS, 1 XFAIL / 33 total
**Stimuli:** 12 major + 12 minor scales, 8 cadences, 45 genres
**Dataset:** Krumhansl & Kessler 1982 (24 key profiles embedded)

---

## Scientific Questions

1. Does key_clarity discriminate tonal from atonal content (Krumhansl profiles)?
2. Does Tonnetz preserve circle-of-fifths geometry?
3. Does diatonicity track number of active pitch classes?
4. Does harmonic_change detect chord transitions in cadences?
5. Do key profiles work across all 12 major and 12 minor keys?

---

## Test Summary

| Tier | Total | Pass | XFail | Description |
|------|-------|------|-------|-------------|
| T1_formula | 12 | 12 | 0 | Key profiles (24×12, unit norm), Tonnetz geometry, diatonicity formula |
| T2_pipeline | 10 | 10 | 0 | Metadata, shapes, NaN, determinism |
| T4_ground_truth | 11 | 10 | 1 | 12 major keys clarity+bootstrap, minor keys, Tonnetz fifths, cadences, diatonicity 48 scales |
| T5_ecological | 3 | 3 | 0 | 45 genres NaN, clarity variance, classical > average |
| **TOTAL** | **33** | **32** | **1** | |

## Known Weakness

### H-W01: Mel-based chroma too smooth for harmonic_change [MEDIUM]
All cadences show harmonic_change ~0.003, same as steady scales. Mel frame resolution insufficient for chord boundary detection.
**Fix:** Use STFT-based chroma (CQT) or increase mel hop resolution.

---

## Result 1: Key Clarity across 12 Major Scales

Mean key_clarity: **0.4888**, 95% CI [0.4482, 0.5293]

| Key | key_clarity | diatonicity | tonal_stability |
|-----|------------|-------------|----------------|
| C | 0.3991 | 0.6377 | 0.3984 |
| Cs | 0.3821 | 0.6991 | 0.3815 |
| D | 0.4224 | 0.7165 | 0.4217 |
| Ds | 0.4341 | 0.7287 | 0.4334 |
| E | 0.4512 | 0.7681 | 0.4503 |
| F | 0.4753 | 0.7362 | 0.4744 |
| Fs | 0.4867 | 0.8203 | 0.4857 |
| G | 0.5189 | 0.8272 | 0.5179 |
| Gs | 0.5402 | 0.8586 | 0.5391 |
| A | 0.5629 | 0.8835 | 0.5617 |
| As | 0.5897 | 0.8904 | 0.5885 |
| B | 0.6025 | 0.9130 | 0.6012 |

## Result 2: Tonnetz Circle of Fifths

- C-G (fifth) distance: **0.0457**
- C-F# (tritone) distance: **0.0834**
- Fifth < tritone: **YES**

## Result 3: Cadences

| Cadence | key_clarity | harmonic_change | tonal_stability |
|---------|------------|----------------|----------------|
| cadence_authentic_I_IV_V_I | 0.3188 | 0.0031 | 0.3183 |
| cadence_chromatic_approach | 0.3079 | 0.0031 | 0.3074 |
| cadence_circle_of_fifths | 0.3123 | 0.0031 | 0.3118 |
| cadence_deceptive_I_IV_V_vi | 0.3225 | 0.0032 | 0.3220 |
| cadence_half_I_ii_V | 0.3239 | 0.0031 | 0.3234 |
| cadence_interrupted_V_bVI | 0.3319 | 0.0030 | 0.3315 |
| cadence_perfect_V7_I | 0.3252 | 0.0030 | 0.3248 |
| cadence_plagal_I_IV_I | 0.3195 | 0.0030 | 0.3190 |

**Note:** harmonic_change ~0.003 for all cadences — H-W01 weakness.

## Ecological (45 Genres)

| Genre | key_clarity | diatonicity | tonal_stability |
|-------|------------|-------------|----------------|
| african_polyrhythm | 0.102 | 0.881 | 0.095 |
| ambient_pad | 0.282 | 0.188 | 0.282 |
| celtic | 0.360 | 0.635 | 0.359 |
| chillout | 0.328 | 0.398 | 0.328 |
| cinematic_epic | 0.280 | 0.327 | 0.279 |
| cinematic_tension | 0.268 | 0.402 | 0.267 |
| classical_chamber | 0.367 | 0.287 | 0.367 |
| classical_choir | 0.387 | 0.514 | 0.387 |
| classical_orchestral | 0.275 | 0.282 | 0.274 |
| classical_piano | 0.321 | 0.439 | 0.319 |
| classical_strings | 0.354 | 0.376 | 0.354 |
| country | 0.354 | 0.625 | 0.353 |
| dnb | 0.351 | 0.443 | 0.350 |
| east_asian_pentatonic | 0.607 | 0.919 | 0.606 |
| edm_house | 0.209 | 0.015 | 0.208 |
| electronic_glitch | 0.701 | 0.899 | 0.698 |
| flamenco | 0.496 | 0.875 | 0.495 |
| funk | 0.053 | 0.383 | 0.049 |
| gamelan | 0.339 | 0.694 | 0.338 |
| gospel | 0.315 | 0.424 | 0.314 |
| hiphop_beat | 0.704 | 0.971 | 0.702 |
| indian_raga | 0.227 | 0.225 | 0.226 |
| indie_folk | 0.237 | 0.444 | 0.236 |
| jazz_ballad | 0.451 | 0.680 | 0.451 |
| jazz_bossa | 0.374 | 0.252 | 0.373 |
| jazz_fusion | 0.105 | 0.129 | 0.100 |
| jazz_modal | 0.516 | 0.732 | 0.515 |
| jazz_swing | 0.086 | 0.105 | 0.082 |
| latin_salsa | 0.253 | 0.186 | 0.253 |
| lofi_hiphop | 0.113 | 0.000 | 0.113 |
| metal | 0.148 | 0.001 | 0.148 |
| middle_eastern | 0.207 | 0.166 | 0.206 |
| new_age_meditation | 0.114 | 0.014 | 0.114 |
| pop_ballad | 0.432 | 0.608 | 0.432 |
| pop_synth | 0.421 | 0.792 | 0.421 |
| reggae | 0.593 | 0.935 | 0.592 |
| rock_blues | 0.533 | 0.682 | 0.532 |
| rock_power | 0.130 | 0.000 | 0.130 |
| social_anti_hook | 0.270 | 0.662 | 0.266 |
| social_call_response | 0.348 | 0.842 | 0.346 |
| social_catchy_hook | 0.419 | 0.738 | 0.418 |
| social_ensemble_polyphonic | 0.242 | 0.300 | 0.241 |
| social_ensemble_unison | 0.214 | 0.386 | 0.214 |
| soul_rnb | 0.263 | 0.325 | 0.261 |
| techno_minimal | 0.573 | 0.889 | 0.570 |

## Files

| File | Purpose |
|------|---------|
| `validation/r3/group_h/test_formula.py` | T1: 12 tests (key profiles, Tonnetz, diatonicity) |
| `validation/r3/group_h/test_pipeline.py` | T2: 10 tests |
| `validation/r3/group_h/test_ground_truth.py` | T4: 11 tests (Krumhansl, Tonnetz fifths, cadences, 48 scales) |
| `validation/r3/group_h/test_ecological.py` | T5: 3 tests (45 genres) |
| `results/r3/group_h/report.json` | Machine-readable |
| `results/r3/group_h/report.md` | This report |