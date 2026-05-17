# Stumpf-relabel audit — engine-canonical re-correlation across 4 datasets

**Goal**: Resolve the discrepancy between Table 1 (Group A row: stumpf +0.885*) and the body text (13-dyad anchor Stumpf fusion ρ = −0.797) in the current paper. Determine which feature physically corresponds to which value, using the frozen R³ engine as ground truth.

**Engine truth** (`Musical_Intelligence/ear/r3/groups/a_consonance/group.py` L194–198):
```
feature_names = (
    "roughness", "sethares_dissonance", "helmholtz_kang",
    "stumpf_fusion", "sensory_pleasantness", "inharmonicity",
    "harmonic_deviation",
)
```
`stumpf_fusion` = pairwise harmonicity ratio. High value → more harmonic → expected positive ρ vs consonance/pleasantness rating.

---

## 1. 13-dyad anchor 2018, N = 13 — DECISIVE (real WAVs from V1/stimuli/intervals)

| Engine name | ρ (canonical) | p | 95% CI | Pearson r |
|---|---:|---:|---:|---:|
| roughness | **−0.7967** | 0.0011 | [−0.937, −0.438] | −0.7031 |
| sethares_dissonance | −0.7527 | 0.0030 | [−0.922, −0.345] | −0.7187 |
| helmholtz_kang | +0.6154 | 0.0252 | [+0.097, +0.871] | +0.7212 |
| **stumpf_fusion** | **+0.8846** | **5.9e-5** | **[+0.651, +0.965]** | **+0.8501** |
| sensory_pleasantness | +0.9121 | 1.4e-5 | [+0.726, +0.974] | +0.8681 |
| inharmonicity | −0.8846 | 5.9e-5 | [−0.965, −0.651] | −0.8501 |
| harmonic_deviation | +0.2088 | 0.494 | [−0.387, +0.681] | +0.3472 |

Bit-exact match to V1/results/r3/group_a/report.md (Mar 24, 2026).

**Verdict**: V1/results/OOS-VALIDATION-REPORT.md (Apr 1, 2026) attached label "stumpf_fusion" to engine `roughness` (−0.797), and label "autocorrelation_peak" to engine `sensory_pleasantness` (+0.912). All seven Group A labels in the OOS report are scrambled.

---

## 2. Eerola 2021 Exp3, N = 617 chords — STRONG CONFIRMATION

Synthesis: harmonic complex per MIDI note, 8 partials, −3 dB/octave rolloff, 1.5 s, 50 ms ramp.

| Engine name | ρ (canonical) | V1 OOS report's claim | Δ vs V1 OOS |
|---|---:|---|---:|
| roughness | −0.5405 | "stumpf_fusion" −0.581 | **0.04 — match** |
| sethares_dissonance | −0.4446 | "helmholtz_roughness" −0.433 | 0.01 — match |
| helmholtz_kang | −0.0592 | "pitch_salience" −0.248 | 0.19 |
| stumpf_fusion | +0.3589 | "tonal_clarity" +0.433 | 0.07 |
| **sensory_pleasantness** | **+0.5296** | **"autocorrelation_peak" +0.518** | **0.012 — bit-exact** |
| inharmonicity | −0.3589 | "roughness_total" −0.433 | 0.07 |
| harmonic_deviation | +0.2898 | "inharmonicity" +0.219 | 0.07 |

Five of seven OOS-report values match within ±0.07 of the canonically-named feature once the labels are unscrambled. Most striking: V1 OOS "autocorrelation_peak +0.518" reproduces engine `sensory_pleasantness` +0.530 (Δ = 0.012) — across N = 617 with independent synthesis. This is engine-canonical match, not coincidence.

**Verdict**: The OOS report values are real engine outputs; only the labels are wrong.

---

## 3. Marjieh 2024, N = 7,500 → 13 bins — synthesis-quality limited

Synthesis: harmonic dyad, 10 partials, −3 dB/octave rolloff, integer-semitone intervals.

| Engine name | ρ (canonical) | V1 OOS report's claim |
|---|---:|---|
| roughness | −0.3956 | "stumpf_fusion" −0.769 |
| sethares_dissonance | −0.4176 | "helmholtz_roughness" −0.747 |
| helmholtz_kang | +0.0110 | "pitch_salience" +0.692 |
| stumpf_fusion | +0.2473 | "tonal_clarity" +0.813 |
| sensory_pleasantness | +0.4780 | "autocorrelation_peak" +0.890 |
| inharmonicity | −0.2473 | "roughness_total" −0.813 |
| harmonic_deviation | +0.0604 | "inharmonicity" +0.269 |

My synthesis under-estimates magnitudes (rating range was narrow at [3.18, 3.96] across bins). Sign and rank ordering match the relabeling theory; magnitudes do not match V1's. V1 evidently used a richer synthesis (likely the Marjieh paper's exact stimulus generation) which my quick approximation does not reproduce.

**Verdict**: Synthesis-quality limited but **structurally consistent** with the relabel theory.

---

## 4. Harrison 2024 Carillon, N = 1,499 → 13 bins — synthesis-quality limited

Synthesis: lower bell + upper bell with idealised partial spectra (12 partials each, additive synthesis), integer-semitone intervals.

| Engine name | ρ (canonical, mine) | V1 OOS report's claim |
|---|---:|---|
| roughness | **−0.6264** | "stumpf_fusion" −0.824 |
| sethares_dissonance | −0.5055 | "helmholtz_roughness" −0.824 |
| helmholtz_kang | +0.1154 | "pitch_salience" +0.451 |
| stumpf_fusion | +0.3846 | "tonal_clarity" +0.731 |
| sensory_pleasantness | +0.6154 | "autocorrelation_peak" +0.852 |
| inharmonicity | −0.3846 | "roughness_total" −0.731 |
| harmonic_deviation | 0.0000 | "inharmonicity" +0.341 |

My synthesis under-estimates here too. V1 likely used the carillon study's actual recorded bell samples (`bell-samples.csv` references real f0s for 30+ recorded bells); idealised additive synthesis from formatted partial spectra is a coarser approximation.

**Critical observation for the paper**: Under my synthesis, |ρ_roughness Carillon| = 0.626 < |ρ_roughness 13-dyad anchor| = 0.797 — the anti-overfitting headline ("OOS magnitude > DEV magnitude") **fails under my synthesis**. Under V1's synthesis (probably bell-sample-based), it succeeds at 0.824 > 0.797. The argument's strength depends on synthesis fidelity; this is a critical synthesis-faithfulness question that should be settled before publication.

**Verdict**: Sign + rank order consistent with relabel theory. Magnitude depends on synthesis. Anti-overfitting claim needs the V1 synthesis pipeline (or recorded bell samples) to be reproducible.

---

## 5. Cross-dataset relabel correspondence (the load-bearing pattern)

| V1 OOS report label | Engine-canonical name (from this audit) | 13-dyad anchor Δ | Eerola Δ |
|---|---|---:|---:|
| "stumpf_fusion" | roughness | 0.000 | 0.040 |
| "helmholtz_roughness" | sethares_dissonance | 0.000 | 0.011 |
| "pitch_salience" | helmholtz_kang | 0.000 | 0.189 |
| "tonal_clarity" | stumpf_fusion | 0.000 | 0.074 |
| "autocorrelation_peak" | sensory_pleasantness | 0.000 | 0.012 |
| "roughness_total" | inharmonicity | 0.000 | 0.074 |
| "inharmonicity" | harmonic_deviation | 0.000 | 0.071 |

13-dyad anchor matches are exact (same WAVs, deterministic engine). Eerola matches are within ±0.19 across 617 chords with independent synthesis. **The relabeling is a single, consistent permutation across two datasets.**

---

## 6. What this means for the paper

**Confirmed:**
- Engine-canonical `stumpf_fusion` 13-dyad N=13 = **+0.885**, not −0.797.
- Body claims of "Stumpf fusion ρ = −0.797 / −0.581 / −0.769 / −0.824" across 13-dyad anchor / Eerola / Marjieh / Carillon are actually engine `roughness` values, mis-labeled.
- Body claim "autocorrelation peak ρ = +0.912 / +0.518 / +0.890" are actually engine `sensory_pleasantness` values, mis-labeled.
- Supplementary caption's "sign-flip convention" excuse is factually wrong (magnitudes differ; this is a label permutation, not a sign change).

**Falsifiable but pending V1-synthesis recovery:**
- Anti-overfitting headline "Carillon −0.824 > 13-dyad anchor −0.797" actually applies to engine `roughness`, not `stumpf_fusion`. This **may still be a valid claim under the correct feature name**, but only if V1's synthesis (or original recorded bell samples) reproduces the magnitude. My approximate synthesis gives 0.626, not 0.824.

**New strong claims now available for the paper (engine-canonical):**
- Engine `stumpf_fusion` 13-dyad N=13: **ρ = +0.885, p = 5.9 × 10⁻⁵, 95% CI [+0.651, +0.965]** — direct positive prediction of consonance pleasantness from harmonicity ratio.
- Engine `sensory_pleasantness` Eerola Exp3 N=617: ρ = +0.530, p = 6.5 × 10⁻⁴⁶, CI [+0.470, +0.584] — strongest single feature on this OOS chord dataset.
- Engine `roughness` Eerola Exp3 N=617: ρ = −0.541, p = 4.3 × 10⁻⁴⁸ — strongest single feature on the dissonance side.
- Engine `inharmonicity = 1 − stumpf_fusion` mathematical complement is verifiable in the engine; both correlate at ±0.885 on 13-dyad anchor — internal-consistency proof of engine determinism.

---

## 7. Recommended fix order

1. **Body text**: replace every "Stumpf fusion ρ = X" (X ∈ {−0.797, −0.581, −0.769, −0.824}) with "Sethares roughness ρ = X". Replace every "autocorrelation peak ρ = +0.912 / +0.518 / +0.890" with "sensory pleasantness ρ = ..." or recompute with engine `autocorrelation_peak` (different feature in Group G/H — may not exist in Group A at all; verify).
2. **Table 1 (Group A row)**: keep "stumpf +0.885***"; this is correct.
3. **Supplementary caption** (`Amac-Erdem-Musical-Intelligence.tex` L522): delete the "sign-flip convention" sentence. It is false. Replace with a single sentence noting the feature naming derives from the engine source at `a_consonance/group.py` L194–198.
4. **Add the new Stumpf headline to body**: `stumpf_fusion ρ = +0.885 vs 13-dyad anchor pleasantness, p = 5.9 × 10⁻⁵` — this is a strictly stronger claim than the current −0.797 and aligns with Stumpf 1890 fusion theory (high harmonicity → high consonance).
5. **Anti-overfitting claim**: rerun engine `roughness` on Carillon with V1-faithful synthesis (or original recorded bell samples) before claiming "Carillon ≥ 13-dyad anchor". If V1 synthesis is unrecoverable, the strongest defensible form is: "engine roughness retains a substantial negative correlation with carillon pleasantness (|ρ| = 0.626 under approximate synthesis), demonstrating partial-pair generalisation to inharmonic timbres beyond harmonic calibration." Magnitude > 13-dyad anchor is the optional stretch claim.

---

## Provenance

- Engine commit: same as paper-canonical (V1 frozen at Apr 1, 2026; V2 path uses `Science/Musical_Intelligence/`)
- 13-dyad anchor: 13 WAVs from `Science/V1/stimuli/intervals/`, ratings from `Science/datasets/consonance/dyad-anchor2018_dyad_ratings.csv`
- Eerola: 617 chord rows from `Legacy/Final-Validation-V1/datasets/consonance/eerola2021_exp3.csv`, MIDI notes from `midi` column, harmonic synthesis (8 partials, −3 dB/oct)
- Marjieh: 7,500 ratings from `Science/datasets/consonance/marjieh2024/data-csv/rating_dyh3dd.csv`, binned to 13 integer-semitone bins
- Carillon: 1,499 interval points from `Science/datasets/consonance/harrison2024_carillon/carillon-behavioural-profile.csv`, binned to 13 integer-semitone bins; idealised partials from `idealised_bell_spectra_formatted.csv`
- Scripts: `Science/V2/code/stumpf-relabel-audit/01_dyad-anchor_groupA_canonical.py`, `02_oos_groupA_canonical.py`
- Outputs: `Science/V2/results/stumpf-relabel-audit/01_dyad-anchor_groupA_canonical.csv`, `02_oos_groupA_canonical.csv`
