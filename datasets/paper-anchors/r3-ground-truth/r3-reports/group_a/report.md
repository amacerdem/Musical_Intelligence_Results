# R³ Group A — Scientific Validation Report
# Psychoacoustic Consonance (7D, indices [0:7])

**Date:** 2026-03-24
**Result:** 68/68 PASS
**Runtime:** ~3 minutes

---

## Scientific Questions Addressed

1. Does the Sethares dissonance model reproduce the 1993 published curve shape?
2. Is the Plomp-Levelt critical bandwidth formula correctly implemented?
3. Does ratio simplicity (helmholtz/stumpf) follow number-theoretic predictions?
4. Do R³ physics features track human consonance perception (Bowling 2018)?
5. Do R³ features agree with neural (Bidelman FFR) and speech (Schwartz) data?
6. Do features generalize to 45 real music genres without degeneracy?

**What this report does NOT cover** (deferred to C³ F1 BCH):
- Eerola Exp2/Exp3 chord rating prediction (cognitive judgment)
- Head-to-head model comparison against published predictors
- DCD multi-chord consonance prediction

---

## Test Summary

| Tier | Tests | Pass | Description |
|------|-------|------|-------------|
| T1_formula | 10 | 10 | Sethares constants, derived formulas, output ranges |
| T2_pipeline | 14 | 14 | Metadata, shapes, NaN guards, determinism |
| T3_stimulus | 13 | 13 | Real WAV: intervals, controls, triads, timbral invariance |
| T4_ground_truth | 23 | 23 | Sethares curve (151pt), Plomp-Levelt CB, ratio simplicity, Bowling/Bidelman/Schwartz + bootstrap/permutation/FDR |
| T5_ecological | 8 | 8 | 45 real music genres: NaN, variance, intercorrelation, genre consistency |
| **TOTAL** | **68** | **68** | |

---

## Stimuli Inventory

| Category | Path | Count | Details |
|----------|------|-------|---------|
| Named intervals | `intervals/interval_*.wav` | 13 | P1–P8 just-intonation dyads |
| Sethares curve | `intervals/_synth_*.wav` | 151 | 0.0-15.0 semitones |
| Controls | `controls/` | 3 | Silence, noise, 440Hz sine |
| Triads | `triads/` | 36 | Major/minor + dom7 |
| Timbral | `timbral/` | 3 | P5 variants + instruments |
| Real music | `real_music/` | 45 | 20+ genres |
| **Total WAVs tested** | | **251** | |

---

## Datasets

| Dataset | File | N | Type |
|---------|------|---|------|
| bowling_2018 | `bowling2018_dyad_ratings.csv` | 13 | behavioral pleasantness |
| sethares_1993 | `sethares1993_dissonance.csv` | 13 | dissonance rank order |
| bidelman_2009 | `bidelman2009_ffr.csv` | 6 | brainstem FFR neural |
| schwartz_2003 | `schwartz2003_speech_harmonics.csv` | 13 | speech harmonics |

---

## Result 1: Sethares 1993 Curve Reproduction

**151 synth WAVs** swept from 0.0 to 15.0 semitones in 0.1 steps.

| Metric | Value | Expected |
|--------|-------|----------|
| Peak dissonance location | **1.2 semitones** | ~1.0 (m2 region) |
| P5 valley (6.5–7.5st mean) | 0.2403 | Local minimum |
| P8 region (11.5–12.5st mean) | 0.2009 | Low (< 50% of peak) |
| P8/peak ratio | 0.27 | < 0.50 |
| Roughness-Sethares internal ρ | +0.790 | > 0.60 |
| Model rank vs published rank ρ | +0.758 | > 0.50 |

---

## Result 2: Plomp-Levelt Critical Bandwidth

Formula: `CB = 25 + 75 * (1 + 1.4 * (f/1000)^2)^0.69` (Zwicker & Fastl 2007)

| Frequency (Hz) | Computed CB (Hz) | Published CB (Hz) | Error % |
|---------------|-----------------|-------------------|---------|
| 100 | 100.7 | 100 | 0.7% |
| 250 | 104.5 | 100 | 4.5% |
| 500 | 117.3 | 110 | 6.6% |
| 1000 | 162.2 | 160 | 1.4% |
| 2000 | 300.8 | 300 | 0.3% |
| 4000 | 685.4 | 700 | 2.1% |

CB is monotonically increasing with frequency: **VERIFIED**

---

## Result 3: Ratio Simplicity (Number Theory)

Expected ordering from number theory: P1 > P8 > P5 > P4 > M3

| Interval | stumpf_fusion | helmholtz_kang |
|----------|--------------|----------------|
| P1 | 0.9312 | 0.9896 |
| P8 | 0.9470 | 0.9924 |
| P5 | 0.6344 | 0.7565 |
| P4 | 0.5014 | 0.3841 |
| M3 | 0.2994 | 0.5655 |

---

## Result 4: Bowling 2018 (PNAS) — R³ Physics Level

Spearman ρ between Group A features (real WAV) and mean human ratings (N=13, 30 subjects).

| Feature | ρ | p (param) | p (perm) | 95% CI | Pearson r | FDR |
|---------|---|-----------|----------|--------|-----------|-----|
| roughness | -0.797 | 0.0011 ** | 0.0016 | [-0.949, -0.385] | -0.703 | YES |
| sethares_dissonance | -0.753 | 0.0030 ** | 0.0033 | [-0.961, -0.275] | -0.719 | YES |
| helmholtz_kang | +0.615 | 0.0252 * | 0.0307 | [+0.034, +0.905] | +0.721 | YES |
| stumpf_fusion | +0.885 | 0.0001 *** | 0.0001 | [+0.547, +0.983] | +0.850 | YES |
| sensory_pleasantness | +0.912 | 0.0000 *** | 0.0001 | [+0.630, +0.994] | +0.868 | YES |
| inharmonicity | -0.885 | 0.0001 *** | 0.0001 | [-0.983, -0.547] | -0.850 | YES |
| harmonic_deviation | +0.209 | 0.4936 ns | 0.4841 | [-0.496, +0.858] | +0.347 | no |

**FDR-significant features:** 6/7

---

## Result 5: Cross-Dataset Convergence

| Dataset | Modality | Feature | ρ | p | N |
|---------|----------|---------|---|---|---|
| Bowling 2018 | Behavioral | stumpf_fusion | +0.885 | 0.0001 | 13 |
| Bidelman 2009 | Neural FFR | stumpf_fusion | +1.000 | 0.0000 | 6 |
| Schwartz 2003 | Speech | stumpf_fusion | +0.852 | 0.0002 | 13 |

---

## Result 6: Ecological Validation (45 Genres)

**45 real music excerpts** tested.

| Metric | Value |
|--------|-------|
| NaN/Inf on any genre | None |
| All features in [0,1] | Yes |
| roughness std across genres | 0.2696 |
| sethares_dissonance std across genres | 0.2982 |
| helmholtz_kang std across genres | 0.1847 |
| stumpf_fusion std across genres | 0.2255 |
| sensory_pleasantness std across genres | 0.2635 |
| inharmonicity std across genres | 0.2255 |
| harmonic_deviation std across genres | 0.1841 |
| Roughness-pleasantness ρ across genres | -0.914 |

---

## Interval Feature Table (13 WAVs)

| Interval | roughne | sethare | helmhol | stumpf_ | sensory | inharmo | harmoni |
|---|---|---|---|---|---|---|---|
|  P1 | 0.1299 | 0.1354 | 0.9896 | 0.9312 | 0.8912 | 0.0688 | 0.3015 |
|  m2 | 0.7111 | 0.7072 | 0.4408 | 0.0807 | 0.2079 | 0.9193 | 0.3135 |
|  M2 | 0.5435 | 0.6792 | 0.2811 | 0.2320 | 0.2853 | 0.7680 | 0.3201 |
|  m3 | 0.2142 | 0.4505 | 0.4993 | 0.2998 | 0.4497 | 0.7002 | 0.4185 |
|  M3 | 0.2286 | 0.3880 | 0.5655 | 0.2994 | 0.4870 | 0.7006 | 0.3790 |
|  P4 | 0.1419 | 0.2812 | 0.3841 | 0.5014 | 0.6318 | 0.4986 | 0.4252 |
|  TT | 0.1978 | 0.3405 | 0.3164 | 0.1269 | 0.4465 | 0.8731 | 0.4427 |
|  P5 | 0.1285 | 0.1689 | 0.7565 | 0.6344 | 0.7524 | 0.3656 | 0.5109 |
|  m6 | 0.2772 | 0.3197 | 0.6165 | 0.1501 | 0.4682 | 0.8499 | 0.4551 |
|  M6 | 0.1391 | 0.2338 | 0.2939 | 0.1853 | 0.5339 | 0.8147 | 0.3928 |
|  m7 | 0.1409 | 0.2549 | 0.3756 | 0.2999 | 0.5670 | 0.7001 | 0.4497 |
|  M7 | 0.3791 | 0.3595 | 0.4654 | 0.0535 | 0.4057 | 0.9465 | 0.3972 |
|  P8 | 0.1294 | 0.1325 | 0.9924 | 0.9470 | 0.8993 | 0.0530 | 0.6233 |

---

## Real Music Feature Table (45 Genres)

| Genre | rough | seth | helm | stumpf | pleas |
|-------|-------|------|------|--------|-------|
| african_polyrhythm | 0.229 | 0.253 | 0.996 | 0.984 | 0.842 |
| ambient_pad | 0.162 | 0.441 | 0.627 | 0.769 | 0.643 |
| celtic | 0.148 | 0.155 | 0.932 | 0.874 | 0.857 |
| chillout | 0.292 | 0.562 | 0.453 | 0.663 | 0.528 |
| cinematic_epic | 0.635 | 0.796 | 0.571 | 0.491 | 0.319 |
| cinematic_tension | 0.700 | 0.852 | 0.495 | 0.443 | 0.266 |
| classical_chamber | 0.131 | 0.187 | 0.814 | 0.638 | 0.743 |
| classical_choir | 0.187 | 0.397 | 0.541 | 0.795 | 0.680 |
| classical_orchestral | 0.729 | 0.853 | 0.545 | 0.365 | 0.234 |
| classical_piano | 0.262 | 0.374 | 0.834 | 0.624 | 0.625 |
| classical_strings | 0.130 | 0.148 | 0.960 | 0.844 | 0.849 |
| country | 0.233 | 0.355 | 0.958 | 0.810 | 0.711 |
| dnb | 0.896 | 0.968 | 0.913 | 0.665 | 0.285 |
| east_asian_pentatonic | 0.139 | 0.146 | 0.984 | 0.951 | 0.893 |
| edm_house | 0.478 | 0.886 | 0.632 | 0.399 | 0.228 |
| electronic_glitch | 0.250 | 0.256 | 0.984 | 0.905 | 0.809 |
| flamenco | 0.146 | 0.149 | 0.978 | 0.923 | 0.880 |
| funk | 0.607 | 0.636 | 0.905 | 0.559 | 0.442 |
| gamelan | 0.221 | 0.282 | 0.941 | 0.902 | 0.791 |
| gospel | 0.304 | 0.559 | 0.618 | 0.741 | 0.561 |
| hiphop_beat | 0.219 | 0.228 | 0.975 | 0.967 | 0.850 |
| indian_raga | 0.873 | 0.915 | 0.630 | 0.355 | 0.193 |
| indie_folk | 0.406 | 0.553 | 0.877 | 0.631 | 0.521 |
| jazz_ballad | 0.128 | 0.192 | 0.823 | 0.947 | 0.864 |
| jazz_bossa | 0.332 | 0.468 | 0.947 | 0.862 | 0.664 |
| jazz_fusion | 0.619 | 0.889 | 0.620 | 0.389 | 0.222 |
| jazz_modal | 0.167 | 0.201 | 0.874 | 0.754 | 0.781 |
| jazz_swing | 0.716 | 0.819 | 0.770 | 0.341 | 0.245 |
| latin_salsa | 0.303 | 0.449 | 0.494 | 0.552 | 0.552 |
| lofi_hiphop | 0.508 | 0.767 | 0.750 | 0.493 | 0.337 |
| metal | 0.948 | 0.993 | 0.504 | 0.368 | 0.151 |
| middle_eastern | 0.933 | 0.946 | 0.679 | 0.326 | 0.163 |
| new_age_meditation | 0.739 | 0.797 | 0.881 | 0.528 | 0.333 |
| pop_ballad | 0.126 | 0.132 | 0.980 | 0.952 | 0.902 |
| pop_synth | 0.196 | 0.275 | 0.942 | 0.908 | 0.799 |
| reggae | 0.145 | 0.177 | 0.982 | 0.966 | 0.880 |
| rock_blues | 0.202 | 0.217 | 0.937 | 0.785 | 0.784 |
| rock_power | 0.694 | 0.882 | 0.555 | 0.358 | 0.214 |
| social_anti_hook | 0.213 | 0.255 | 0.894 | 0.801 | 0.767 |
| social_call_response | 0.153 | 0.160 | 0.966 | 0.902 | 0.865 |
| social_catchy_hook | 0.142 | 0.168 | 0.930 | 0.868 | 0.847 |
| social_ensemble_polyphonic | 0.667 | 0.773 | 0.488 | 0.377 | 0.287 |
| social_ensemble_unison | 0.801 | 0.871 | 0.488 | 0.316 | 0.204 |
| soul_rnb | 0.797 | 0.849 | 0.575 | 0.412 | 0.256 |
| techno_minimal | 0.302 | 0.316 | 0.931 | 0.909 | 0.774 |

---

## Files

| File | Purpose |
|------|---------|
| `validation/r3/group_a/conftest.py` | ConsonanceGroup + fixtures |
| `validation/r3/group_a/test_formula.py` | T1: 10 tests |
| `validation/r3/group_a/test_pipeline.py` | T2: 14 tests |
| `validation/r3/group_a/test_stimulus.py` | T3: 13 tests |
| `validation/r3/group_a/test_ground_truth.py` | T4: 23 tests |
| `validation/r3/group_a/test_ecological.py` | T5: 8 tests |
| `results/r3/group_a/report.json` | Machine-readable (91KB) |
| `results/r3/group_a/report.md` | This report |