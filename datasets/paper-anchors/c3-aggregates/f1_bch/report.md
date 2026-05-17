# C3 F1 BCH -- Gold Standard Scientific Validation Report
# Brainstem Consonance Hierarchy (Relay, depth 0, SPU, 16D)

**Date:** 2026-04-01
**Pipeline:** R3(97D) -> H3(48 demands) -> BCH(16D) -> 4 beliefs
**Statistics:** Bootstrap CI (10K), permutation null (5K), BH-FDR, Cohen's f2, post-hoc power

---

## 1. Scientific Story

BCH (Brainstem Consonance Hierarchy) is a depth-0 Relay in
F1 (Sensory Processing). It transforms R3/H3 features through 48 H3
temporal demands into a 16D output across processing layers:

```
E-layer [0:4]  Extraction  -> ['E0:nps', 'E1:harmonicity', 'E2:hierarchy', 'E3:ffr_behavior']
M-layer [4:8]  Memory  -> ['M0:consonance_memory', 'M1:pitch_memory', 'M2:tonal_memory', 'M3:spectral_memory']
P-layer [8:12]  Present  -> ['P0:consonance_signal', 'P1:template_match', 'P2:neural_pitch', 'P3:tonal_context']
F-layer [12:16]  Forecast  -> ['F0:consonance_forecast', 'F1:pitch_forecast', 'F2:tonal_forecast', 'F3:interval_forecast']
```

**4 beliefs** read BCH output:
- **harmonic_stability**
- **interval_quality**
- **harmonic_template_match**
- **consonance_trajectory**

**Evidence tier:** alpha
**Confidence:** (0.85, 0.95)

### Citations

- Plomp (1965): Critical bandwidth roughness model [foundational]
- Sethares (1993): Roughness from spectral peaks [foundational]
- Helmholtz (1863): Integer ratio consonance theory [foundational]
- Stumpf (1890): Tonal fusion theory [foundational]
- Bidelman (2009): FFR pitch salience correlates with consonance [r=0.81]
- Bidelman (2013): Harmonicity > roughness as consonance predictor [r=0.84]
- Bidelman (2011): AN population predicts hierarchy [6/6 ordering]
- McDermott (2010): Harmonicity preference = consonance preference [r=0.71]
- Tramo (2001): Brainstem-cortex consonance pathway [lesion study]
- Krumhansl (1990): Key profiles and tonal hierarchies [r=0.97]
- Parncutt (1989): Virtual pitch salience model [foundational]
- Cousineau (2015): FFR-behavior drops for natural stimuli [r=ns for natural]

---

## 2. Bowling 2018 Cross-Domain (N=13)

### All Dims x Bowling

| Dimension | rho | p | p(perm) | 95% CI | Pearson r | f2 | Power | Sig |
|-----------|-----|---|---------|--------|-----------|-----|-------|-----|
| E0:nps | +0.033 | 0.9149 | 0.9174 | [-0.627, +0.627] | +0.144 | 0.001 | 0.05 | ns |
| E1:harmonicity | +0.896 | 0.0000 | 0.0000 | [+0.584, +0.994] | +0.823 | 4.053 | 1.00 | *** |
| E2:hierarchy | +0.929 | 0.0000 | 0.0000 | [+0.654, +1.000] | +0.779 | 6.259 | 1.00 | *** |
| E3:ffr_behavior | +0.896 | 0.0000 | 0.0000 | [+0.584, +0.994] | +0.821 | 4.053 | 1.00 | *** |
| M0:consonance_memory | +0.835 | 0.0004 | 0.0010 | [+0.413, +0.983] | +0.772 | 2.306 | 1.00 | *** |
| M1:pitch_memory | +0.907 | 0.0000 | 0.0000 | [+0.609, +1.000] | +0.856 | 4.615 | 1.00 | *** |
| M2:tonal_memory | +0.786 | 0.0015 | 0.0028 | [+0.360, +0.966] | +0.795 | 1.613 | 1.00 | ** |
| M3:spectral_memory | +0.808 | 0.0008 | 0.0020 | [+0.391, +0.971] | +0.740 | 1.877 | 1.00 | *** |
| P0:consonance_signal | +0.896 | 0.0000 | 0.0000 | [+0.581, +0.994] | +0.798 | 4.053 | 1.00 | *** |
| P1:template_match | +0.780 | 0.0017 | 0.0030 | [+0.277, +0.978] | +0.831 | 1.556 | 1.00 | ** |
| P2:neural_pitch | +0.868 | 0.0001 | 0.0002 | [+0.487, +1.000] | +0.840 | 3.059 | 1.00 | *** |
| P3:tonal_context | +0.786 | 0.0015 | 0.0028 | [+0.360, +0.966] | +0.795 | 1.613 | 1.00 | ** |
| F0:consonance_forecast | +0.956 | 0.0000 | 0.0000 | [+0.787, +1.000] | +0.903 | 10.631 | 1.00 | *** |
| F1:pitch_forecast | +0.912 | 0.0000 | 0.0000 | [+0.610, +1.000] | +0.846 | 4.949 | 1.00 | *** |
| F2:tonal_forecast | +0.786 | 0.0015 | 0.0028 | [+0.360, +0.966] | +0.795 | 1.613 | 1.00 | ** |
| F3:interval_forecast | +0.885 | 0.0001 | 0.0002 | [+0.542, +0.989] | +0.855 | 3.599 | 1.00 | *** |

**15/16 dimensions significant at p<0.05**

### All Beliefs x Bowling

| Belief | rho | p | p(perm) | 95% CI | Pearson r | FDR |
|--------|-----|---|---------|--------|-----------|-----|
| harmonic_stability | +0.945 | 0.0000 | 0.0000 | [+0.727, +1.000] | +0.888 | PASS |
| interval_quality | +0.929 | 0.0000 | 0.0000 | [+0.654, +1.000] | +0.779 | PASS |
| harmonic_template_match | +0.780 | 0.0017 | 0.0030 | [+0.277, +0.978] | +0.831 | PASS |
| consonance_trajectory | +0.956 | 0.0000 | 0.0000 | [+0.787, +1.000] | +0.903 | PASS |

**4/4 beliefs pass BH-FDR**

---

## 3. Emotion Stimuli Validation

### Happy (N=2)

- **emotion_happy_1**: F3:interval_forecast=0.813, M1:pitch_memory=0.792, P0:consonance_signal=0.770
  - harmonic_stability = 0.7513
  - interval_quality = 0.7343
  - harmonic_template_match = 0.7319
  - consonance_trajectory = 0.5473
- **emotion_happy_2**: F3:interval_forecast=0.791, E2:hierarchy=0.787, P0:consonance_signal=0.754
  - harmonic_stability = 0.7391
  - interval_quality = 0.7873
  - harmonic_template_match = 0.6815
  - consonance_trajectory = 0.5340

### Sad (N=2)

- **emotion_sad_1**: M1:pitch_memory=0.828, P0:consonance_signal=0.719, P1:template_match=0.706
  - harmonic_stability = 0.6970
  - interval_quality = 0.6286
  - harmonic_template_match = 0.7058
  - consonance_trajectory = 0.4316
- **emotion_sad_2**: M1:pitch_memory=0.770, M3:spectral_memory=0.564, P2:neural_pitch=0.535
  - harmonic_stability = 0.3384
  - interval_quality = 0.1855
  - harmonic_template_match = 0.4934
  - consonance_trajectory = 0.2266

### Calm (N=2)

- **emotion_calm_1**: M1:pitch_memory=0.785, P0:consonance_signal=0.571, P2:neural_pitch=0.564
  - harmonic_stability = 0.4508
  - interval_quality = 0.1530
  - harmonic_template_match = 0.4483
  - consonance_trajectory = 0.3387
- **emotion_calm_2**: M1:pitch_memory=0.797, P0:consonance_signal=0.640, M0:consonance_memory=0.612
  - harmonic_stability = 0.5381
  - interval_quality = 0.2655
  - harmonic_template_match = 0.5491
  - consonance_trajectory = 0.3795

### Angry (N=2)

- **emotion_angry_1**: M1:pitch_memory=0.725, F3:interval_forecast=0.506, P2:neural_pitch=0.498
  - harmonic_stability = 0.3252
  - interval_quality = 0.1031
  - harmonic_template_match = 0.3623
  - consonance_trajectory = 0.2469
- **emotion_angry_2**: M1:pitch_memory=0.808, F3:interval_forecast=0.633, P2:neural_pitch=0.603
  - harmonic_stability = 0.4840
  - interval_quality = 0.4087
  - harmonic_template_match = 0.5776
  - consonance_trajectory = 0.3384

### Chills (N=4)

- **chills_appoggiatura_chain**: F3:interval_forecast=0.655, P0:consonance_signal=0.650, E2:hierarchy=0.629
  - harmonic_stability = 0.6295
  - interval_quality = 0.6287
  - harmonic_template_match = 0.5964
  - consonance_trajectory = 0.4249
- **chills_climactic_build**: M1:pitch_memory=0.779, P0:consonance_signal=0.606, M0:consonance_memory=0.599
  - harmonic_stability = 0.5032
  - interval_quality = 0.3050
  - harmonic_template_match = 0.4636
  - consonance_trajectory = 0.3967
- **chills_gap_reentry**: M1:pitch_memory=0.742, P0:consonance_signal=0.621, M0:consonance_memory=0.588
  - harmonic_stability = 0.5253
  - interval_quality = 0.3077
  - harmonic_template_match = 0.5111
  - consonance_trajectory = 0.3838
- **chills_harmonic_surprise**: M1:pitch_memory=0.796, P2:neural_pitch=0.578, F3:interval_forecast=0.551
  - harmonic_stability = 0.4142
  - interval_quality = 0.2026
  - harmonic_template_match = 0.4564
  - consonance_trajectory = 0.3349

### Tension (N=5)

- **tension_appoggiatura**: M1:pitch_memory=0.770, P2:neural_pitch=0.569, F1:pitch_forecast=0.530
  - harmonic_stability = 0.3759
  - interval_quality = 0.2224
  - harmonic_template_match = 0.4126
  - consonance_trajectory = 0.2864
- **tension_resolution_delay0ms**: P0:consonance_signal=0.646, F3:interval_forecast=0.607, M0:consonance_memory=0.607
  - harmonic_stability = 0.5710
  - interval_quality = 0.5018
  - harmonic_template_match = 0.4926
  - consonance_trajectory = 0.4211
- **tension_resolution_delay1000ms**: P0:consonance_signal=0.653, F3:interval_forecast=0.626, M0:consonance_memory=0.612
  - harmonic_stability = 0.5780
  - interval_quality = 0.5051
  - harmonic_template_match = 0.5015
  - consonance_trajectory = 0.4180
- **tension_resolution_delay250ms**: P0:consonance_signal=0.652, F3:interval_forecast=0.616, M0:consonance_memory=0.612
  - harmonic_stability = 0.5762
  - interval_quality = 0.5001
  - harmonic_template_match = 0.5015
  - consonance_trajectory = 0.4209
- **tension_resolution_delay500ms**: P0:consonance_signal=0.651, F3:interval_forecast=0.616, M0:consonance_memory=0.611
  - harmonic_stability = 0.5758
  - interval_quality = 0.4998
  - harmonic_template_match = 0.5016
  - consonance_trajectory = 0.4206

### Dynamics (N=9)

- **dynamics_crescendo**: M1:pitch_memory=0.878, E2:hierarchy=0.791, F3:interval_forecast=0.713
  - harmonic_stability = 0.6853
  - interval_quality = 0.7910
  - harmonic_template_match = 0.6141
  - consonance_trajectory = 0.4586
- **dynamics_decrescendo**: M1:pitch_memory=0.878, E2:hierarchy=0.792, F3:interval_forecast=0.712
  - harmonic_stability = 0.6859
  - interval_quality = 0.7924
  - harmonic_template_match = 0.6141
  - consonance_trajectory = 0.4570
- **dynamics_f**: M1:pitch_memory=0.859, P1:template_match=0.777, E2:hierarchy=0.774
  - harmonic_stability = 0.7613
  - interval_quality = 0.7735
  - harmonic_template_match = 0.7771
  - consonance_trajectory = 0.5058
- **dynamics_ff**: M1:pitch_memory=0.857, P1:template_match=0.773, E2:hierarchy=0.768
  - harmonic_stability = 0.7582
  - interval_quality = 0.7684
  - harmonic_template_match = 0.7733
  - consonance_trajectory = 0.5022
- **dynamics_mf**: M1:pitch_memory=0.861, P1:template_match=0.781, E2:hierarchy=0.779
  - harmonic_stability = 0.7648
  - interval_quality = 0.7789
  - harmonic_template_match = 0.7814
  - consonance_trajectory = 0.5101
- **dynamics_mp**: M1:pitch_memory=0.866, P1:template_match=0.787, E2:hierarchy=0.784
  - harmonic_stability = 0.7691
  - interval_quality = 0.7844
  - harmonic_template_match = 0.7868
  - consonance_trajectory = 0.5161
- **dynamics_p**: M1:pitch_memory=0.869, P1:template_match=0.793, E2:hierarchy=0.789
  - harmonic_stability = 0.7738
  - interval_quality = 0.7888
  - harmonic_template_match = 0.7928
  - consonance_trajectory = 0.5234
- **dynamics_pp**: M1:pitch_memory=0.875, P1:template_match=0.799, E2:hierarchy=0.794
  - harmonic_stability = 0.7794
  - interval_quality = 0.7937
  - harmonic_template_match = 0.7986
  - consonance_trajectory = 0.5313
- **dynamics_sforzando**: M1:pitch_memory=0.886, E2:hierarchy=0.785, F3:interval_forecast=0.718
  - harmonic_stability = 0.6858
  - interval_quality = 0.7848
  - harmonic_template_match = 0.6158
  - consonance_trajectory = 0.4683

---

## 4. Ecological Validation: Real Music

**N = 45 genres**

| Genre | E0:nps | E1:harmonicity | E2:hierarchy |
|-------|---|---|---|
| african_polyrhythm | 0.123 | 0.691 | 0.784 |
| ambient_pad | 0.476 | 0.146 | 0.398 |
| celtic | 0.466 | 0.229 | 0.673 |
| chillout | 0.492 | 0.130 | 0.241 |
| cinematic_epic | 0.476 | 0.094 | 0.249 |
| cinematic_tension | 0.486 | 0.086 | 0.195 |
| classical_chamber | 0.464 | 0.170 | 0.428 |
| classical_choir | 0.482 | 0.156 | 0.354 |
| classical_orchestral | 0.480 | 0.072 | 0.172 |
| classical_piano | 0.424 | 0.224 | 0.446 |
| classical_strings | 0.465 | 0.204 | 0.660 |
| country | 0.388 | 0.286 | 0.635 |
| dnb | 0.467 | 0.156 | 0.493 |
| east_asian_pentatonic | 0.516 | 0.273 | 0.754 |
| edm_house | 0.436 | 0.098 | 0.203 |
| electronic_glitch | 0.542 | 0.316 | 0.718 |
| flamenco | 0.482 | 0.314 | 0.733 |
| funk | 0.066 | 0.374 | 0.422 |
| gamelan | 0.466 | 0.278 | 0.696 |
| gospel | 0.485 | 0.144 | 0.384 |
| hiphop_beat | 0.550 | 0.322 | 0.760 |
| indian_raga | 0.474 | 0.075 | 0.179 |
| indie_folk | 0.351 | 0.262 | 0.469 |
| jazz_ballad | 0.467 | 0.281 | 0.633 |
| jazz_bossa | 0.481 | 0.174 | 0.662 |
| jazz_fusion | 0.207 | 0.193 | 0.220 |
| jazz_modal | 0.496 | 0.210 | 0.568 |
| jazz_swing | 0.131 | 0.160 | 0.225 |
| latin_salsa | 0.485 | 0.105 | 0.219 |
| lofi_hiphop | 0.263 | 0.187 | 0.299 |
| metal | 0.323 | 0.120 | 0.148 |
| middle_eastern | 0.469 | 0.074 | 0.181 |
| new_age_meditation | 0.197 | 0.191 | 0.376 |
| pop_ballad | 0.469 | 0.269 | 0.755 |
| pop_synth | 0.496 | 0.211 | 0.706 |
| reggae | 0.542 | 0.320 | 0.763 |
| rock_blues | 0.486 | 0.229 | 0.615 |
| rock_power | 0.271 | 0.129 | 0.159 |
| social_anti_hook | 0.310 | 0.418 | 0.614 |
| social_call_response | 0.390 | 0.394 | 0.715 |
| social_catchy_hook | 0.467 | 0.282 | 0.677 |
| social_ensemble_polyphonic | 0.486 | 0.072 | 0.166 |
| social_ensemble_unison | 0.507 | 0.066 | 0.154 |
| soul_rnb | 0.480 | 0.082 | 0.200 |
| techno_minimal | 0.531 | 0.311 | 0.696 |

---

## 5. Dimension-Level Output (13 Intervals)

| Interval | nps | harmon | hierar | ffr_be | conson | pitch_ | tonal_ | spectr | conson | templa | neural | tonal_ | conson | pitch_ | tonal_ | interv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.473 | 0.214 | 0.739 | 0.278 | 0.659 | 0.847 | 0.340 | 0.708 | 0.741 | 0.773 | 0.598 | 0.340 | 0.464 | 0.538 | 0.340 | 0.722 |
| m2 | 0.470 | 0.019 | 0.026 | 0.198 | 0.373 | 0.695 | 0.193 | 0.495 | 0.354 | 0.362 | 0.450 | 0.193 | 0.209 | 0.475 | 0.193 | 0.418 |
| M2 | 0.467 | 0.052 | 0.053 | 0.210 | 0.449 | 0.736 | 0.226 | 0.527 | 0.437 | 0.357 | 0.492 | 0.226 | 0.258 | 0.490 | 0.226 | 0.450 |
| m3 | 0.466 | 0.071 | 0.121 | 0.218 | 0.582 | 0.741 | 0.238 | 0.499 | 0.596 | 0.418 | 0.492 | 0.238 | 0.332 | 0.492 | 0.238 | 0.501 |
| M3 | 0.467 | 0.072 | 0.136 | 0.218 | 0.582 | 0.747 | 0.352 | 0.522 | 0.620 | 0.470 | 0.499 | 0.351 | 0.363 | 0.495 | 0.352 | 0.546 |
| P4 | 0.465 | 0.125 | 0.153 | 0.239 | 0.628 | 0.776 | 0.339 | 0.554 | 0.676 | 0.452 | 0.526 | 0.339 | 0.403 | 0.506 | 0.339 | 0.540 |
| TT | 0.465 | 0.032 | 0.033 | 0.201 | 0.589 | 0.722 | 0.200 | 0.451 | 0.612 | 0.306 | 0.473 | 0.200 | 0.320 | 0.485 | 0.200 | 0.441 |
| P5 | 0.465 | 0.162 | 0.384 | 0.254 | 0.643 | 0.799 | 0.376 | 0.548 | 0.703 | 0.583 | 0.545 | 0.375 | 0.437 | 0.514 | 0.376 | 0.644 |
| m6 | 0.465 | 0.041 | 0.076 | 0.205 | 0.563 | 0.721 | 0.311 | 0.462 | 0.599 | 0.421 | 0.468 | 0.311 | 0.340 | 0.484 | 0.311 | 0.525 |
| M6 | 0.464 | 0.051 | 0.045 | 0.208 | 0.620 | 0.730 | 0.270 | 0.501 | 0.670 | 0.340 | 0.471 | 0.269 | 0.363 | 0.487 | 0.270 | 0.460 |
| m7 | 0.465 | 0.081 | 0.090 | 0.221 | 0.621 | 0.745 | 0.166 | 0.503 | 0.654 | 0.358 | 0.495 | 0.166 | 0.348 | 0.493 | 0.166 | 0.477 |
| M7 | 0.466 | 0.015 | 0.022 | 0.195 | 0.522 | 0.711 | 0.314 | 0.469 | 0.558 | 0.366 | 0.458 | 0.314 | 0.315 | 0.480 | 0.314 | 0.487 |
| P8 | 0.466 | 0.284 | 0.753 | 0.304 | 0.663 | 0.852 | 0.425 | 0.589 | 0.720 | 0.714 | 0.592 | 0.425 | 0.491 | 0.538 | 0.425 | 0.757 |

---

## 6. Region Links

**14 region links documented**

| Dimension | Target Region | Weight | Citation |
|-----------|---------------|--------|----------|
| E0:nps | IC | 0.80 | Bidelman 2009 |
| E1:harmonicity | AN | 0.75 | Bidelman 2013 |
| E2:hierarchy | AN | 0.70 | Bidelman & Heinz 2011 |
| E2:hierarchy | IC | 0.65 | Bidelman & Heinz 2011 |
| E3:ffr_behavior | IC | 0.60 | Bidelman 2009 |
| P0:consonance_signal | MGB | 0.70 | Tramo 2001 |
| P0:consonance_signal | A1_HG | 0.55 | Tramo 2001 |
| P0:consonance_signal | STG | 0.50 | Tramo 2001 |
| P1:template_match | IC | 0.65 | Bidelman 2013 |
| P1:template_match | MGB | 0.55 | Tramo 2001 |
| P2:neural_pitch | IC | 0.75 | Bidelman 2009 |
| P3:tonal_context | MGB | 0.45 | Krumhansl 1990 |
| F0:consonance_forecast | IC | 0.40 | Bidelman 2009 |
| F1:pitch_forecast | IC | 0.40 | Bidelman 2009 |

## 7. Neurochemical Links

**2 neurochemical links**

| Neurochemical | Target Dim | Weight | Citation |
|---------------|-----------|--------|----------|
| serotonin | P0:consonance_signal | 0.30 | Blood & Zatorre 2001 |
| dopamine | P0:consonance_signal | 0.15 | Salimpoor 2011 |

---

## 8. Falsification Criteria & Known Issues

- BCH hierarchy P1>P5>P4>M3>m6>TT should hold for synthetic tones; failure to reproduce = model invalid
- Consonance signal should correlate >0.70 with behavioral consonance ratings for synthetic dyads

### General Limitations

- Static interval WAVs (2s) provide limited temporal context
- Evidence tier: alpha (confidence (0.85, 0.95))
- Bowling N=13 is adequate for depth-0 but not for complex interactions

---

*Report generated 2026-04-01 04:08:05 by f1_complete_validation.py*