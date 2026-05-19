# Phase 03.3 Cheung Emergent Reward — Audio-Native Upgrade
## Pre-Registration (5-angle consolidated, FROZEN 2026-05-16 → CLOSED 2026-05-16)

**STATUS: CLOSED 2026-05-16.** All 5 angles executed under the frozen pre-registration; full results in `02-RESULTS.md` §7. Verdict summary:

| Angle | Pre-registered rule | Verdict |
|---|---|---|
| 1 — Substitution validity | median r ≤ 0.2 → NEGATIVE | NEGATIVE_SUBSTITUTION_INVALID (architectural disambiguation, as expected) |
| 2 — Engine-native M2 | Cheung −0.124 ∈ engine bootstrap CI → POSITIVE | INCONCLUSIVE_BORDERLINE (β same sign, 0.013 outside CI; CV r = 2.13× ceiling) |
| 3 — LOSO ceiling | reproduce paper-anchor 0.2169 ± 0.005 | sanity-PASS (0.21686, \|Δ\|=3.8×10⁻⁵); NEW surprise ceiling +0.4808 |
| 4 — Cross-rhythm consistency | median r ≥ 0.7 → POSITIVE | POSITIVE_RHYTHM_INVARIANT (HTP +0.993, ICEM +0.828) |
| 5 — Per-belief ECE | pooled ECE ≤ 0.10 AND Brier ≥ 5× → POSITIVE | POSITIVE_CHEUNG_CALIBRATED (ECE 0.082, Brier 13.47×) |

No pre-registered rule was modified after observing the data. No forbidden move was used. The pre-registration body below is preserved as-frozen for audit.

---

**Engine SHA:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (canonical, motor-free era)
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Companion:** `02-RESULTS.md` (Phase 10 closure, 2026-05-07), `CHILL_STANDARD_UPGRADE.md` (LOSO discipline, 2026-05-12)
**Data deposit:** Cheung et al. 2024 OSF [`5fk2q`](https://osf.io/5fk2q/) — Cognitive and sensory expectations independently shape musical expectancy and pleasure (Phil Trans B, 2024)

---

## §0 Why this upgrade exists

Phase 10 closure (2026-05-07) reproduced 6 paper claims for the Cheung 2019 IC×ENTROPY interaction by **post-hoc statistical reanalysis** on Cheung's IDyOM-derived columns (no engine call), under the explicit assumption that *"audio for Cheung stimuli was never released"* (`02-RESULTS.md` §3, §5).

On 2026-05-16 a web audit confirmed this assumption is **incorrect**: the Cheung 2024 OSF deposit (5fk2q) released:
- 90 stimulus WAV files (3 rhythm conditions × 30 chord progressions, ~14 MB each, 1.2 GB total)
- 30 chord-pitch metadata text files (TSV: song, onset, pitch1..pitch5 in Hz)
- `data_pleasure_2023.csv` (39,351 trial-level pleasure ratings, 39 subj × 1009 chord-rows) — already used by Phase 10
- `data_surprise_2023.csv` (39,351 trial-level **subjective surprise** ratings, parallel rating to pleasure) — **not yet used**
- `bigram.txt` (Cheung's IDyOM training bigrams)

This upgrade closes Phase 10 §5's deferred future-work item:
> *"An audio-native re-derivation (synthesise Cheung's chord stimuli, run MI R³+H³+C³ pipeline, derive engine's own surprise/uncertainty traces, re-fit M2) would test a stronger architectural claim."*

The upgrade tests **5 orthogonal angles** on the same data, each with a frozen pre-registered decision rule. **No claim from §0–§5 of `02-RESULTS.md` is retracted by this upgrade.** All new findings are additive to the closed Phase 10 baseline.

---

## §1 Data envelope (read-only inputs)

| Asset | Source | Local path | SHA-256 (auditable) |
|---|---|---|---|
| 90 stimulus WAVs (3×30) | OSF 5fk2q `stimuli/stimuli_rhythm{1,2,3}/` | `data/cheung_audio/stimuli_rhythm{1,2,3}/` | per-file in `01-PROVENANCE.md` post-Angle-1 |
| 30 chord-pitch TSVs | OSF 5fk2q `stimuli/pitches/` | `data/cheung_audio/pitches/` | per-file |
| `data_pleasure_2023.csv` | OSF 5fk2q | `Science/datasets/reward/cheung2024/` (already on disk) | inherited from Phase 10 |
| `data_surprise_2023.csv` (NEW) | OSF 5fk2q | `Science/datasets/reward/cheung2024/` (already on disk) | recorded at Angle 3 freeze |
| `bigram.txt` (NEW) | OSF 5fk2q | same | reference for IDyOM context |
| `OSFdata_code.Rmd` | OSF 5fk2q | same | reference; not re-executed |

---

## §2 The five angles

Each angle is a **frozen** pre-registered analysis with a single decision rule. Forbidden moves listed at the end.

### Angle 1 — Audio-native HTP/ICEM ↔ IDyOM substitution validity

**Question:** Does MI's runtime architecture (R³+H³+C³ on raw audio) produce HTP (uncertainty proxy) and ICEM (surprise proxy) channels whose statistical content matches Cheung's IDyOM-derived IC and ENTROPY columns on the same stimuli?

**Pipeline:**
1. Run MI engine (canonical pipeline, `_pipeline.run_full_pipeline`) on 90 Cheung WAVs, single rhythm condition first (rhythm1) → cache per-stimulus mech_HTP[T,4] and mech_ICEM[T,4] as compressed npz.
2. For each of 30 stim_id × rhythm condition: align engine per-frame outputs to chord onsets from `pitches/pitches_merged_wav_stim<NN>.txt` (event-triggered windowed mean over ±200 ms around each onset).
3. Per-stimulus Pearson correlation:
   - `r(MI_HTP_E0, IDyOM_ENTROPY)` across 1009 chord-rows that fall within the 30-stim subset
   - `r(MI_ICEM_E0, IDyOM_IC)` across same
4. Aggregate: median + IQR + 95% bootstrap CI of per-stimulus r distribution across 30 stimuli (rhythm1).

**Frozen decision rule:**
- POSITIVE substitution validity: median r(HTP, ENT) ≥ 0.5 AND median r(ICEM, IC) ≥ 0.5
- NEGATIVE: either median ≤ 0.2
- INCONCLUSIVE: in between

**Channels selected (frozen pre-execution):** HTP.E0 = high_level_lead (~500ms abstract patterns); ICEM.E0 = information_content (explicit IC proxy per source docstring).

**Output artefacts:**
- `data/cheung_audio_outputs/mi_features_rhythm1/<stim_id>.npz` (HTP[T,4], ICEM[T,4], 26-D RAM, 4-D neuro for completeness)
- `results/angle1_correlations.csv` (per-stimulus per-channel-pair r)
- `results/angle1_aggregate.json` (medians, CIs, decision)

### Angle 2 — Engine-native M2/M3 re-fit (architectural emergence direct test)

**Question:** When MI's engine-runtime HTP and ICEM signals replace Cheung's IDyOM IC and ENTROPY in the M2 interaction regression, does the published interaction coefficient β = −0.124 still reproduce inside the bootstrap 95% CI?

**Pre-condition:** Angle 1 must complete (cached engine features available). This test is independent of Angle 1's verdict — even if substitution validity is NEGATIVE, the engine-native re-fit is the direct architectural emergence test.

**Pipeline:**
1. For each of 1009 chord-rows in `data_pleasure_2023.csv`: extract MI's HTP and ICEM windowed mean at the corresponding chord onset (event-triggered, ±200 ms) from rhythm1 cache.
2. Z-score MI_HTP_z and MI_ICEM_z per chord-row.
3. Fit two regression models (statsmodels OLS, seed=42):
   - **M2_engine:** `rating ~ MI_HTP_z + MI_ICEM_z + MI_HTP_z:MI_ICEM_z + controls` (controls = valence, arousal, dissonance, spectralcentroid, spectralcomplexity, Leman6)
   - **M3_engine:** MI Eq.5 closed-form with MI_HTP and MI_ICEM as inputs (instead of Cheung's IDyOM IC/ENT)
4. Bootstrap 5000 iterations (resample chord-rows with replacement) → β(MI_HTP × MI_ICEM) 95% CI
5. Held-out 5-fold leave-songs-out CV: per-fold M2_engine + M3_engine held-out Pearson r vs pleasure ratings.

**Frozen decision rule:**
- POSITIVE for architectural emergence: Cheung's published β = −0.124 lies inside bootstrap 95% CI of β(MI_HTP × MI_ICEM)
- NEGATIVE for emergence: −0.124 outside bootstrap CI by > 0.05
- INCONCLUSIVE: −0.124 outside CI by ≤ 0.05 (borderline — wider stimulus set would be needed)

**Output artefacts:**
- `code/upgrade_angle2_engine_native_refit.py`
- `results/angle2_engine_M2_coefficients.csv`
- `results/angle2_bootstrap_distribution.npy`
- `results/angle2_decision.json`

### Angle 3 — LOSO inter-rater ceiling: pleasure AND surprise (chill-standard primary)

**Question 1:** Does the existing pleasure LOSO ceiling (+0.2169, CHILL_STANDARD_UPGRADE.md) reproduce bit-exact under the canonical engine SHA?
**Question 2:** What is the inter-rater ceiling for `data_surprise_2023.csv` (39,351 surprise ratings, parallel to pleasure)? Surprise is a different cognitive task — its ceiling may differ.

**Pipeline:**
1. Pivot trial-level CSV into matrix: 39 VPIDs × 1009 (song × chord) trials. Reproduce Cheung's own data layout from `OSFdata_code.Rmd`.
2. For each held-out VPID: consensus = mean of N−1 others, Spearman ρ with held-out's vector (NaN-safe).
3. Aggregate Fisher-Z mean across all 39 ρ values.
4. Bootstrap 95% CI: 5000 iterations resampling VPIDs with replacement, recompute Fisher-Z mean.
5. Apply to BOTH pleasure CSV (sanity = +0.2169 reproduce) AND surprise CSV (NEW).

**Frozen decision rule:**
- Pleasure ceiling **MUST** reproduce within ±0.005 of paper-anchor +0.2169 (else upstream methodology error → escalate)
- Surprise ceiling: report as-is + 95% CI (no decision rule; this is a measurement, not a hypothesis test)

**This angle is engine-free.** Runs in seconds. Computes the **ceiling reference point for all subsequent angles' interpretation.**

**Output artefacts:**
- `code/upgrade_angle3_loso_ceiling.py`
- `results/angle3_loso_ceiling.json` (pleasure ceiling + surprise ceiling + bootstrap dists)
- `results/angle3_loso_per_vpid.csv` (per-VPID Spearman ρ + held-out N)

### Angle 4 — Cross-rhythm consistency (architectural rhythm-invariance prediction)

**Question:** MI's HTP and ICEM are claimed to be CHORD-LEVEL surprise/uncertainty (Function F2 mechanisms reading R³ pitch-class + harmony features). Architecturally, they should be near-invariant to rhythm changes that preserve chord identity.

**Pipeline:**
1. Run engine on rhythm2 and rhythm3 stimulus sets (60 additional WAVs; total 90 cached).
2. For each of 30 stim_ids: compute event-triggered mean HTP and ICEM at chord onsets, separately for each of 3 rhythm conditions.
3. Per-stimulus Pearson correlation across rhythm pairs:
   - `r_HTP(stim_i_rhythm1, stim_i_rhythm2)` across the ~9-12 chord events per stimulus
   - Similarly for rhythm1-vs-rhythm3, rhythm2-vs-rhythm3
   - Same for ICEM
4. Aggregate: median + IQR across 30 stimuli × 3 rhythm pairs (90 r values per channel).

**Frozen decision rule:**
- POSITIVE rhythm-invariance: median r ≥ 0.7 across rhythm pairs (architectural prediction confirmed)
- NEGATIVE: median r ≤ 0.3 (HTP/ICEM rhythm-coupled, not chord-level)
- INCONCLUSIVE: in between

**Output artefacts:**
- `data/cheung_audio_outputs/mi_features_rhythm{2,3}/<stim_id>.npz`
- `results/angle4_cross_rhythm_consistency.csv`
- `results/angle4_decision.json`

### Angle 5 — Per-belief ECE calibration on Cheung corpus

**Question:** Phase 5 ECE methodology (held-out N=206k DEAM frames, ECE=0.079 pooled across 8 Core beliefs) — does the same pipeline produce well-calibrated beliefs on the Cheung 2024 corpus, or is calibration corpus-specific?

**Pipeline:**
1. From Angle 1 + Angle 4 cached engine features (90 stimuli × all 4 channels of each mech), extract the 8 Core belief π_pred and PE traces per frame.
2. Apply Phase 5 ECE methodology verbatim:
   - Bin π_pred into 10 equal-width bins
   - Compute |mean(predicted π) − fraction(|PE| ≤ 0.5)| per bin
   - Aggregate ECE = weighted mean of per-bin gaps
   - Brier score against PE; uniform baseline comparison
3. Pooled ECE across 90 stimuli × 8 beliefs.

**Frozen decision rule:**
- POSITIVE Cheung-corpus calibration: pooled ECE ≤ 0.10 AND Brier ≥ 5× better than uniform baseline (matches Phase 5 DEAM thresholds verbatim)
- NEGATIVE: ECE > 0.15 OR Brier < 3× uniform
- INCONCLUSIVE: in between

**Output artefacts:**
- `code/upgrade_angle5_ece_cheung.py`
- `results/angle5_ece_per_belief.csv`
- `results/angle5_pooled_ece.json`

---

## §3 Result composition rule (LOSO-relative framing — chill-standard)

For every angle producing a correlation with human ratings (Angle 2 held-out r, Angle 5 belief-vs-rating if applicable):

`MI value` is **always** reported alongside:
- Absolute value (e.g., r = +0.615)
- LOSO ceiling for that target (Angle 3 output)
- Ratio (MI / ceiling, e.g., 2.84×)

A held-out r above the LOSO ceiling means MI predicts the consensus rating better than typical individual humans agree with that consensus. This is the chill-standard interpretation per `CHILL_STANDARD_UPGRADE.md`.

---

## §4 Forbidden moves (frozen pre-execution)

- Re-running any angle with different bootstrap seed and reporting a different result.
- Adjusting decision-rule thresholds (0.5 / 0.2 / ±0.05 / 0.7 / 0.10) after seeing data.
- Changing channel selection (HTP.E0 / ICEM.E0) after seeing first-pass correlations.
- Cherry-picking which of the 30 stimuli or 39 VPIDs to include after looking at distributions.
- Switching from Spearman to Pearson (or vice versa) after seeing one favours the result.
- Engine source modification (canonical SHA `318eb2f5...` is FROZEN; monkey-patching for sensitivity tests requires a separate sub-pre-registration).
- Suppressing inconclusive or negative outcomes — every angle's decision goes into `02-RESULTS.md` revision verbatim.

---

## §5 Sequencing (frozen)

1. **Angle 3 first** (engine-free, ~10 sec runtime, computes ceiling reference for all subsequent interpretation).
2. **Angle 1 second** (engine on 90 WAVs, ~1-3 min wall, produces cache for Angles 2/4/5).
3. **Angles 2, 4, 5 in parallel** after caches exist (analysis-only, ~minutes each).

After all 5 angles close, write consolidated **`02-RESULTS.md` revision** preserving original Phase 10 closure intact and **adding** §6 "Audio-Native Upgrade Results" subsection with all 5 verdicts + LOSO-relative framing.

Paper-side revision (master `.tex`) decision deferred until all 5 angles report. **No paper edit before all results land.**

---

## §6 Authorisation

- **Frozen:** 2026-05-16
- **Engine SHA at freeze:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- **Aggregate SHA-256 at freeze:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- **Audio data SHA-256 manifest:** populated post-Angle-1 in `01-PROVENANCE.md` revision
- **Deposit:** local-only at this stage; OSF/GitHub deposit deferred until all 5 angles + paper revision close
