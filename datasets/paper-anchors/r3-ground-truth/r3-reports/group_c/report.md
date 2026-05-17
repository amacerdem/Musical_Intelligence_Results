# R³ Group C — Scientific Validation Report
# Timbre (9D, indices [12:21])

**Date:** 2026-03-24
**Result:** 36 PASS, 4 XFAIL / 40 total
**Instruments tested:** 20 (audio path: STFT warmth/sharpness)
**Dataset:** Grey 1977 / McAdams 1995 (15 matched)

---

## Bug Fixed

### C-F01: Added compute_from_audio() STFT path for warmth/sharpness
Warmth now uses STFT low-freq (<1kHz) dominance instead of mel bottom-quarter ratio. Sharpness uses Zwicker-weighted high-freq (>3kHz) emphasis.
**Impact:** Warmth-sharpness anti-correlation improved: ρ=-0.11 → ρ=-0.53 (PASS). C-W03 resolved.

## Known Weaknesses (3)

### C-W01: Warmth does not predict perceptual warmth [HIGH]
STFT warmth (low-freq dominance) correlates ρ=0.40 (p=0.14) with Grey 1977. Perceptual warmth is multidimensional — spectral envelope shape, harmonic structure, temporal envelope. Single spectral feature insufficient.
**Status:** OPEN — requires multi-feature model or learned mapping

### C-W02: Sharpness does not predict perceptual brightness [HIGH]
STFT sharpness correlates ρ=0.19 (p=0.50) with Grey 1977 brightness. Zwicker sharpness weighting helps direction but magnitude insufficient.
**Status:** OPEN

### C-W03: Warmth-sharpness anti-correlation weak (mel path) [MEDIUM]
Mel-only path: ρ=-0.11. Audio path: ρ=-0.53.
**Status:** PARTIALLY FIXED — audio path ρ=-0.53, mel path still weak

---

## Grey 1977 Correlations (audio path)

- **Warmth vs Grey warmth:** ρ = +0.402 (p=0.1373) — NOT significant
- **Sharpness vs Grey brightness:** ρ = +0.188 (p=0.5026)
- **Warmth↔sharpness internal:** ρ = -0.525 (IMPROVED from −0.11 → −0.53)
- **Matched instruments:** 15/17

### All Features vs Grey 1977 Warmth

| Feature | ρ vs warmth | p |
|---------|------------|---|
| warmth | +0.402 | 0.1373 ns |
| sharpness | -0.193 | 0.4907 ns |
| tonalness | -0.220 | 0.4311 ns |
| clarity | -0.338 | 0.2182 ns |
| spectral_smoothness | +0.272 | 0.3273 ns |
| spectral_autocorrelation | +0.415 | 0.1243 ns |
| tristimulus1 | +0.168 | 0.5495 ns |
| tristimulus2 | -0.105 | 0.7084 ns |
| tristimulus3 | -0.288 | 0.2983 ns |

---

## Instrument Timbre Profiles (20 WAVs, audio path)

| Instrument | warmth | sharp | tonal | clarity | smooth | autocr | t1 | t2 | t3 |
|------------|--------|-------|-------|---------|--------|--------|-----|-----|-----|
| instrument_bass_guitar_E2 | 0.217 | 0.335 | 0.026 | 0.275 | 0.741 | 0.911 | 0.664 | 0.311 | 0.025 |
| instrument_cello_C3 | 0.751 | 0.144 | 0.047 | 0.156 | 0.597 | 0.854 | 1.000 | 0.000 | 0.000 |
| instrument_clarinet_Bb3 | 0.515 | 0.143 | 0.076 | 0.230 | 0.304 | 0.746 | 0.674 | 0.326 | 0.000 |
| instrument_flute_C5 | 0.290 | 0.144 | 0.126 | 0.223 | 0.315 | 0.751 | 0.797 | 0.203 | 0.000 |
| instrument_glockenspiel_C6 | 0.015 | 0.284 | 0.340 | 0.310 | 0.111 | 0.672 | 0.810 | 0.168 | 0.022 |
| instrument_guitar_E3 | 0.417 | 0.245 | 0.052 | 0.232 | 0.226 | 0.623 | 0.736 | 0.251 | 0.013 |
| instrument_harpsichord_C4 | 0.427 | 0.237 | 0.089 | 0.213 | 0.094 | 0.627 | 0.815 | 0.174 | 0.011 |
| instrument_marimba_C4 | 0.770 | 0.519 | 0.345 | 0.108 | 0.176 | 0.722 | 0.984 | 0.016 | 0.000 |
| instrument_oboe_A4 | 0.190 | 0.550 | 0.047 | 0.391 | 0.150 | 0.542 | 0.390 | 0.587 | 0.023 |
| instrument_organ_A4 | 0.076 | 0.298 | 0.062 | 0.320 | 0.160 | 0.606 | 0.501 | 0.499 | 0.000 |
| instrument_piano_C2 | 0.858 | 0.146 | 0.071 | 0.075 | 0.795 | 0.944 | 1.000 | 0.000 | 0.000 |
| instrument_piano_C4 | 0.572 | 0.148 | 0.081 | 0.190 | 0.263 | 0.723 | 0.910 | 0.090 | 0.000 |
| instrument_synth_pad_C4 | 0.858 | 0.145 | 0.136 | 0.116 | 0.467 | 0.854 | 1.000 | 0.000 | 0.000 |
| instrument_synth_saw_C4 | 0.071 | 1.000 | 0.020 | 0.511 | 0.687 | 0.475 | 0.293 | 0.363 | 0.343 |
| instrument_synth_square_C4 | 0.099 | 1.000 | 0.023 | 0.540 | 0.641 | 0.582 | 0.273 | 0.328 | 0.399 |
| instrument_trumpet_C4 | 0.307 | 0.144 | 0.050 | 0.239 | 0.248 | 0.659 | 0.713 | 0.287 | 0.000 |
| instrument_tubular_bell_C4 | 0.795 | 0.163 | 0.190 | 0.139 | 0.307 | 0.785 | 0.966 | 0.034 | 0.000 |
| instrument_vibraphone_A4 | 0.717 | 0.217 | 0.290 | 0.170 | 0.234 | 0.748 | 0.947 | 0.053 | 0.000 |
| instrument_violin_A4 | 0.288 | 0.236 | 0.067 | 0.306 | 0.191 | 0.633 | 0.549 | 0.451 | 0.000 |
| instrument_violin_vibrato | 0.288 | 0.236 | 0.067 | 0.306 | 0.191 | 0.633 | 0.549 | 0.451 | 0.000 |

---

## Ecological (45 Genres, audio path)

| Genre | warmth | sharp | tonal | clarity | smooth |
|-------|--------|-------|-------|---------|--------|
| african_polyrhythm | 0.250 | 0.290 | 0.030 | 0.029 | 0.945 |
| ambient_pad | 0.846 | 0.189 | 0.069 | 0.095 | 0.676 |
| celtic | 0.488 | 0.319 | 0.076 | 0.177 | 0.472 |
| chillout | 0.855 | 0.169 | 0.100 | 0.091 | 0.734 |
| cinematic_epic | 0.857 | 0.148 | 0.061 | 0.084 | 0.765 |
| cinematic_tension | 0.858 | 0.146 | 0.086 | 0.095 | 0.715 |
| classical_chamber | 0.465 | 0.177 | 0.050 | 0.226 | 0.373 |
| classical_choir | 0.857 | 0.149 | 0.080 | 0.106 | 0.630 |
| classical_orchestral | 0.792 | 0.145 | 0.072 | 0.109 | 0.724 |
| classical_piano | 0.370 | 0.230 | 0.054 | 0.206 | 0.400 |
| classical_strings | 0.608 | 0.178 | 0.052 | 0.188 | 0.360 |
| country | 0.425 | 0.324 | 0.095 | 0.177 | 0.336 |
| dnb | 0.237 | 0.995 | 0.104 | 0.140 | 0.647 |
| east_asian_pentatonic | 0.592 | 0.240 | 0.192 | 0.132 | 0.351 |
| edm_house | 0.402 | 0.990 | 0.059 | 0.183 | 0.768 |
| electronic_glitch | 0.632 | 0.427 | 0.239 | 0.079 | 0.655 |
| flamenco | 0.427 | 0.307 | 0.157 | 0.231 | 0.096 |
| funk | 0.024 | 0.802 | 0.009 | 0.305 | 0.909 |
| gamelan | 0.651 | 0.237 | 0.167 | 0.140 | 0.426 |
| gospel | 0.846 | 0.212 | 0.088 | 0.090 | 0.679 |
| hiphop_beat | 0.808 | 0.251 | 0.249 | 0.032 | 0.681 |
| indian_raga | 0.561 | 0.163 | 0.059 | 0.145 | 0.825 |
| indie_folk | 0.364 | 0.278 | 0.051 | 0.179 | 0.519 |
| jazz_ballad | 0.440 | 0.204 | 0.061 | 0.225 | 0.334 |
| jazz_bossa | 0.745 | 0.430 | 0.116 | 0.141 | 0.436 |
| jazz_fusion | 0.120 | 0.998 | 0.019 | 0.368 | 0.900 |
| jazz_modal | 0.553 | 0.308 | 0.144 | 0.172 | 0.353 |
| jazz_swing | 0.047 | 0.924 | 0.016 | 0.366 | 0.815 |
| latin_salsa | 0.786 | 0.176 | 0.089 | 0.123 | 0.683 |
| lofi_hiphop | 0.066 | 1.000 | 0.025 | 0.528 | 0.793 |
| metal | 0.282 | 1.000 | 0.031 | 0.316 | 0.845 |
| middle_eastern | 0.398 | 0.166 | 0.051 | 0.183 | 0.857 |
| new_age_meditation | 0.039 | 0.999 | 0.023 | 0.550 | 0.779 |
| pop_ballad | 0.543 | 0.166 | 0.065 | 0.203 | 0.279 |
| pop_synth | 0.668 | 0.299 | 0.134 | 0.135 | 0.524 |
| reggae | 0.853 | 0.160 | 0.256 | 0.027 | 0.476 |
| rock_blues | 0.615 | 0.333 | 0.161 | 0.149 | 0.427 |
| rock_power | 0.154 | 1.000 | 0.023 | 0.376 | 0.758 |
| social_anti_hook | 0.268 | 0.448 | 0.046 | 0.176 | 0.576 |
| social_call_response | 0.277 | 0.288 | 0.072 | 0.226 | 0.385 |
| social_catchy_hook | 0.343 | 0.304 | 0.079 | 0.261 | 0.274 |
| social_ensemble_polyphonic | 0.858 | 0.145 | 0.084 | 0.116 | 0.708 |
| social_ensemble_unison | 0.858 | 0.146 | 0.139 | 0.119 | 0.684 |
| soul_rnb | 0.763 | 0.175 | 0.074 | 0.113 | 0.805 |
| techno_minimal | 0.748 | 0.356 | 0.252 | 0.055 | 0.507 |

---

## Files

| File | Purpose |
|------|---------|
| `Musical_Intelligence/ear/r3/groups/c_timbre/group.py` | **MODIFIED** — added compute_from_audio() STFT path |
| `validation/r3/group_c/test_formula.py` | T1: 10 tests |
| `validation/r3/group_c/test_pipeline.py` | T2: 10 tests |
| `validation/r3/group_c/test_stimulus.py` | T3: 7 tests (20 instruments) |
| `validation/r3/group_c/test_ground_truth.py` | T4: 9 tests (4 xfail = remaining weaknesses) |
| `validation/r3/group_c/test_ecological.py` | T5: 5 tests (45 genres) |
| `results/r3/group_c/report.json` | Machine-readable |
| `results/r3/group_c/report.md` | This report |