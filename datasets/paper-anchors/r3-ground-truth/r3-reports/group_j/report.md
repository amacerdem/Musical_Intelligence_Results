# R³ Group J — Scientific Validation Report
# Timbre Extended (20D, indices [63:83])

**Date:** 2026-03-24
**Result:** 48/48 PASS
**Instruments tested:** 20
**MFCC discrimination:** 166/190 pairs too similar (cosine > 0.99)
**Mean MFCC cosine similarity:** 0.9945

---

## Scientific Questions

1. Do MFCCs discriminate instrument timbres (cosine similarity < 0.99)?
2. Does DCT-II matrix correctly compute cepstral coefficients?
3. Do spectral contrast bands capture peak-valley structure?
4. Are 7 octave sub-bands correctly defined?

---

## Instrument MFCC Profiles (13 MFCCs)

| Instrument | mfcc1 | mfcc2 | mfcc3 | mfcc4 | mfcc5 | mfcc6 | mfcc7 | mfcc8 | mfcc9 | mfcc10 | mfcc11 | mfcc12 | mfcc13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| instrument_bass_guitar_E2 | 0.698 | 0.482 | 0.450 | 0.461 | 0.468 | 0.470 | 0.487 | 0.512 | 0.530 | 0.517 | 0.493 | 0.489 | 0.488 |
| instrument_cello_C3 | 0.726 | 0.562 | 0.509 | 0.455 | 0.433 | 0.458 | 0.499 | 0.518 | 0.490 | 0.435 | 0.395 | 0.399 | 0.443 |
| instrument_clarinet_Bb3 | 0.611 | 0.507 | 0.478 | 0.494 | 0.520 | 0.506 | 0.470 | 0.465 | 0.493 | 0.485 | 0.424 | 0.375 | 0.382 |
| instrument_flute_C5 | 0.573 | 0.507 | 0.473 | 0.453 | 0.457 | 0.478 | 0.489 | 0.479 | 0.467 | 0.483 | 0.529 | 0.583 | 0.608 |
| instrument_glockenspiel_C6 | 0.513 | 0.496 | 0.489 | 0.486 | 0.489 | 0.501 | 0.521 | 0.537 | 0.529 | 0.481 | 0.439 | 0.456 | 0.505 |
| instrument_guitar_E3 | 0.611 | 0.495 | 0.482 | 0.496 | 0.503 | 0.495 | 0.488 | 0.499 | 0.513 | 0.500 | 0.473 | 0.463 | 0.475 |
| instrument_harpsichord_C4 | 0.563 | 0.499 | 0.487 | 0.485 | 0.488 | 0.490 | 0.487 | 0.485 | 0.496 | 0.499 | 0.491 | 0.478 | 0.469 |
| instrument_marimba_C4 | 0.524 | 0.507 | 0.504 | 0.501 | 0.499 | 0.495 | 0.492 | 0.488 | 0.483 | 0.478 | 0.474 | 0.468 | 0.461 |
| instrument_oboe_A4 | 0.572 | 0.447 | 0.494 | 0.508 | 0.431 | 0.468 | 0.495 | 0.427 | 0.469 | 0.507 | 0.450 | 0.515 | 0.587 |
| instrument_organ_A4 | 0.598 | 0.466 | 0.440 | 0.491 | 0.510 | 0.465 | 0.449 | 0.483 | 0.491 | 0.472 | 0.486 | 0.512 | 0.521 |
| instrument_piano_C2 | 0.646 | 0.564 | 0.568 | 0.556 | 0.538 | 0.512 | 0.487 | 0.465 | 0.455 | 0.458 | 0.471 | 0.491 | 0.511 |
| instrument_piano_C4 | 0.602 | 0.519 | 0.486 | 0.462 | 0.463 | 0.485 | 0.496 | 0.480 | 0.448 | 0.431 | 0.442 | 0.468 | 0.480 |
| instrument_synth_pad_C4 | 0.585 | 0.533 | 0.525 | 0.504 | 0.476 | 0.448 | 0.425 | 0.411 | 0.415 | 0.434 | 0.459 | 0.482 | 0.495 |
| instrument_synth_saw_C4 | 0.480 | 0.478 | 0.491 | 0.485 | 0.470 | 0.468 | 0.464 | 0.462 | 0.453 | 0.442 | 0.433 | 0.441 | 0.447 |
| instrument_synth_square_C4 | 0.442 | 0.496 | 0.505 | 0.498 | 0.493 | 0.494 | 0.490 | 0.480 | 0.464 | 0.440 | 0.415 | 0.400 | 0.373 |
| instrument_trumpet_C4 | 0.669 | 0.504 | 0.441 | 0.443 | 0.488 | 0.503 | 0.461 | 0.423 | 0.447 | 0.485 | 0.466 | 0.411 | 0.411 |
| instrument_tubular_bell_C4 | 0.554 | 0.515 | 0.508 | 0.501 | 0.495 | 0.488 | 0.481 | 0.474 | 0.465 | 0.456 | 0.448 | 0.433 | 0.414 |
| instrument_vibraphone_A4 | 0.529 | 0.505 | 0.500 | 0.494 | 0.485 | 0.479 | 0.473 | 0.466 | 0.465 | 0.471 | 0.486 | 0.519 | 0.563 |
| instrument_violin_A4 | 0.597 | 0.476 | 0.454 | 0.492 | 0.494 | 0.445 | 0.440 | 0.488 | 0.486 | 0.444 | 0.471 | 0.548 | 0.562 |
| instrument_violin_vibrato | 0.596 | 0.476 | 0.454 | 0.492 | 0.494 | 0.445 | 0.441 | 0.488 | 0.486 | 0.444 | 0.471 | 0.547 | 0.562 |

## Spectral Contrast (7 bands)

| Instrument | band1 | band2 | band3 | band4 | band5 | band6 | band7 |
|---|---|---|---|---|---|---|---|
| instrument_bass_guitar_E2 | 0.031 | 0.029 | 0.038 | 0.032 | 0.038 | 0.018 | 0.004 |
| instrument_cello_C3 | 0.015 | 0.023 | 0.075 | 0.043 | 0.055 | 0.000 | 0.000 |
| instrument_clarinet_Bb3 | 0.000 | 0.020 | 0.099 | 0.069 | 0.067 | 0.000 | 0.000 |
| instrument_flute_C5 | 0.000 | 0.000 | 0.001 | 0.091 | 0.065 | 0.000 | 0.000 |
| instrument_glockenspiel_C6 | 0.000 | 0.000 | 0.000 | 0.002 | 0.037 | 0.004 | 0.003 |
| instrument_guitar_E3 | 0.038 | 0.064 | 0.055 | 0.057 | 0.036 | 0.010 | 0.002 |
| instrument_harpsichord_C4 | 0.019 | 0.000 | 0.052 | 0.050 | 0.033 | 0.004 | 0.001 |
| instrument_marimba_C4 | 0.000 | 0.000 | 0.042 | 0.016 | 0.006 | 0.001 | 0.000 |
| instrument_oboe_A4 | 0.000 | 0.000 | 0.030 | 0.092 | 0.072 | 0.057 | 0.000 |
| instrument_organ_A4 | 0.000 | 0.000 | 0.014 | 0.093 | 0.095 | 0.032 | 0.000 |
| instrument_piano_C2 | 0.082 | 0.017 | 0.019 | 0.049 | 0.000 | 0.000 | 0.000 |
| instrument_piano_C4 | 0.000 | 0.001 | 0.081 | 0.065 | 0.048 | 0.000 | 0.000 |
| instrument_synth_pad_C4 | 0.000 | 0.002 | 0.099 | 0.086 | 0.000 | 0.000 | 0.000 |
| instrument_synth_saw_C4 | 0.002 | 0.006 | 0.092 | 0.074 | 0.055 | 0.016 | 0.002 |
| instrument_synth_square_C4 | 0.005 | 0.010 | 0.091 | 0.067 | 0.055 | 0.035 | 0.008 |
| instrument_trumpet_C4 | 0.000 | 0.001 | 0.099 | 0.092 | 0.079 | 0.000 | 0.000 |
| instrument_tubular_bell_C4 | 0.000 | 0.001 | 0.084 | 0.040 | 0.013 | 0.002 | 0.000 |
| instrument_vibraphone_A4 | 0.000 | 0.000 | 0.007 | 0.061 | 0.014 | 0.003 | 0.000 |
| instrument_violin_A4 | 0.000 | 0.000 | 0.030 | 0.092 | 0.072 | 0.020 | 0.000 |
| instrument_violin_vibrato | 0.000 | 0.000 | 0.030 | 0.092 | 0.072 | 0.020 | 0.000 |

## Ecological (45 Genres)

| Genre | mfcc1 | mfcc2 | mfcc3 | contrast1 | contrast4 | contrast7 |
|-------|-------|-------|-------|-----------|-----------|-----------|
| african_polyrhythm | 0.519 | 0.506 | 0.504 | 0.007 | 0.004 | 0.000 |
| ambient_pad | 0.643 | 0.560 | 0.556 | 0.002 | 0.075 | 0.000 |
| celtic | 0.641 | 0.528 | 0.497 | 0.073 | 0.080 | 0.000 |
| chillout | 0.604 | 0.545 | 0.545 | 0.003 | 0.043 | 0.000 |
| cinematic_epic | 0.634 | 0.556 | 0.554 | 0.043 | 0.045 | 0.000 |
| cinematic_tension | 0.643 | 0.558 | 0.553 | 0.046 | 0.073 | 0.000 |
| classical_chamber | 0.674 | 0.515 | 0.460 | 0.000 | 0.085 | 0.000 |
| classical_choir | 0.643 | 0.556 | 0.547 | 0.003 | 0.085 | 0.000 |
| classical_orchestral | 0.650 | 0.553 | 0.534 | 0.075 | 0.036 | 0.000 |
| classical_piano | 0.609 | 0.508 | 0.472 | 0.000 | 0.053 | 0.000 |
| classical_strings | 0.686 | 0.537 | 0.487 | 0.004 | 0.077 | 0.000 |
| country | 0.547 | 0.501 | 0.491 | 0.024 | 0.034 | 0.001 |
| dnb | 0.534 | 0.516 | 0.517 | 0.021 | 0.006 | 0.001 |
| east_asian_pentatonic | 0.560 | 0.511 | 0.500 | 0.001 | 0.040 | 0.000 |
| edm_house | 0.591 | 0.533 | 0.530 | 0.044 | 0.020 | 0.001 |
| electronic_glitch | 0.537 | 0.511 | 0.520 | 0.019 | 0.003 | 0.000 |
| flamenco | 0.534 | 0.498 | 0.493 | 0.040 | 0.042 | 0.002 |
| funk | 0.504 | 0.468 | 0.515 | 0.014 | 0.019 | 0.022 |
| gamelan | 0.549 | 0.512 | 0.505 | 0.000 | 0.039 | 0.000 |
| gospel | 0.601 | 0.543 | 0.542 | 0.001 | 0.049 | 0.000 |
| hiphop_beat | 0.538 | 0.520 | 0.526 | 0.022 | 0.000 | 0.000 |
| indian_raga | 0.684 | 0.550 | 0.514 | 0.010 | 0.029 | 0.000 |
| indie_folk | 0.582 | 0.504 | 0.488 | 0.026 | 0.037 | 0.001 |
| jazz_ballad | 0.641 | 0.513 | 0.484 | 0.000 | 0.084 | 0.000 |
| jazz_bossa | 0.542 | 0.519 | 0.514 | 0.000 | 0.040 | 0.001 |
| jazz_fusion | 0.604 | 0.525 | 0.514 | 0.059 | 0.013 | 0.006 |
| jazz_modal | 0.594 | 0.508 | 0.499 | 0.002 | 0.044 | 0.000 |
| jazz_swing | 0.607 | 0.444 | 0.495 | 0.032 | 0.032 | 0.015 |
| latin_salsa | 0.618 | 0.542 | 0.528 | 0.000 | 0.084 | 0.000 |
| lofi_hiphop | 0.475 | 0.534 | 0.521 | 0.006 | 0.053 | 0.010 |
| metal | 0.652 | 0.534 | 0.530 | 0.017 | 0.023 | 0.004 |
| middle_eastern | 0.707 | 0.534 | 0.481 | 0.008 | 0.025 | 0.000 |
| new_age_meditation | 0.433 | 0.515 | 0.498 | 0.009 | 0.031 | 0.011 |
| pop_ballad | 0.633 | 0.519 | 0.489 | 0.006 | 0.078 | 0.000 |
| pop_synth | 0.580 | 0.525 | 0.513 | 0.003 | 0.039 | 0.000 |
| reggae | 0.552 | 0.525 | 0.530 | 0.089 | 0.004 | 0.000 |
| rock_blues | 0.569 | 0.514 | 0.524 | 0.082 | 0.024 | 0.002 |
| rock_power | 0.632 | 0.519 | 0.515 | 0.058 | 0.036 | 0.005 |
| social_anti_hook | 0.572 | 0.503 | 0.488 | 0.001 | 0.041 | 0.000 |
| social_call_response | 0.574 | 0.493 | 0.471 | 0.000 | 0.070 | 0.000 |
| social_catchy_hook | 0.609 | 0.497 | 0.458 | 0.000 | 0.082 | 0.000 |
| social_ensemble_polyphonic | 0.623 | 0.547 | 0.536 | 0.006 | 0.078 | 0.000 |
| social_ensemble_unison | 0.579 | 0.530 | 0.522 | 0.000 | 0.072 | 0.000 |
| soul_rnb | 0.653 | 0.554 | 0.538 | 0.009 | 0.044 | 0.000 |
| techno_minimal | 0.539 | 0.519 | 0.523 | 0.062 | 0.001 | 0.001 |

## Files

| File | Purpose |
|------|---------|
| `validation/r3/group_j/test_formula.py` | T1: 17 tests (DCT matrix, MFCC scales, contrast bands) |
| `validation/r3/group_j/test_pipeline.py` | T2: 15 tests |
| `validation/r3/group_j/test_stimulus.py` | T3: 10 tests (20 instruments, MFCC discrimination) |
| `validation/r3/group_j/test_ecological.py` | T5: 7 tests (45 genres) |
| `results/r3/group_j/report.json` | Machine-readable |
| `results/r3/group_j/report.md` | This report |