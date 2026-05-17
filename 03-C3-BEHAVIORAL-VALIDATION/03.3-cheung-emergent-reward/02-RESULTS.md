# V-Reproduction Phase 03.3 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **7 PASS / 0 CAVEAT / 0 FAIL** (single iteration)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Wall:** ~1 s (no engine call required).

---

## 1. Headline

All 6 paper Cheung-2019 reward-interaction claims (β = −0.158, bootstrap CI [−0.228, −0.084], Cheung −0.124 inside CI, ΔAIC = −33.5, held-out Pearson r = +0.615 for M3 Eq. 5, Eq. 5 architectural additivity) reproduce exactly from the preserved V2 T-R2-04 artefact (`Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R2-04/`). Engine architectural control re-confirmed by source inspection: 16 F6 reward-mechanism files contain no `IC×ENTROPY` product term — the Cheung interaction is therefore properly characterised in the paper as **emerging from HTP×ICEM dynamic coupling**, not from the static reward formula.

## 2. Per-claim verdict (7 rows)

| Claim | Paper value | Reproduced | Verdict |
|---|---|---|---|
| C-CHEUNG-01 | β(IC × ENTROPY) M2 OLS = **−0.158** | **−0.1578** | **PASS** (\|Δ\|=0.0002) |
| C-CHEUNG-02 | Bootstrap 95% CI = **[−0.228, −0.084]** | **[−0.2277, −0.0839]** | **PASS** (\|Δ\|≤0.0004) |
| C-CHEUNG-03 | Cheung published **β=−0.124 inside our bootstrap CI** | −0.124 ∈ [−0.2277, −0.0839] | **PASS** |
| C-CHEUNG-04 | ΔAIC (M2 − M1) = **−33.5** | **−33.54** | **PASS** (\|Δ\|=0.04) |
| C-CHEUNG-05 | Held-out Pearson r (M3 Eq. 5) = **+0.615** | **+0.6149** | **PASS** (\|Δ\|=0.0001) |
| C-CHEUNG-06 | Eq.5 reward formula additive (architectural control) | 16 F6 mech files: additive=True | **PASS** |
| C-CHEUNG-07-meta | N=39,351 / 1,009 / 39 / 30 (trials/chord-rows/subjects/songs) | 39,351 / 1,009 / 39 / 30 | **PASS** |

## 3. Why no engine call is needed

Cheung 2019 audio was never released — only chord symbols + rhythm indices. The paper analysis is a deterministic post-hoc statistical reanalysis on Cheung 2024 OSF CSV (`data_pleasure_2023.csv`), using IDyOM-derived IC + ENTROPY columns directly as the MI HTP/ICEM proxies. The numerical analysis is not engine-state-dependent in any compute path. The architectural control (Eq. 5 additivity) is engine-state-dependent but is a static source-code property, not a runtime quantity — confirmed by inspecting the engine source.

V2 T-R2-04 was authored 2026-04-22 with `frozen-code confirmation: YES, no Musical_Intelligence/ edits` and `seed=42, B=5000`. Phase 10 verifies the preserved numerical entries against paper claims; no re-execution was performed.

## 4. Compute profile

- Wall: 1 s (JSON read + 6 numerical comparisons + engine source-tree regex scan)
- Memory peak: <100 MB
- 0 engine pipeline runs (audio not available; analysis is statistical only)

## 5. Concerns and disclosures

**Audio-native re-derivation deferred (paper-side disclosure).** Paper §Discussion already discloses that Cheung audio was not released and the reanalysis uses Cheung's IDyOM IC/ENTROPY columns directly. An audio-native re-derivation (synthesise Cheung's chord stimuli, run MI R³+H³+C³ pipeline, derive engine's own surprise/uncertainty traces, re-fit M2) would test a stronger architectural claim. Phase 10 does not perform this; the deferred upgrade is documented in V2 T-R2-04 §Scope caveat and remains a future-work item, not a Phase 10 obligation.

**Architectural control finding (engine source).** 16 F6 reward-mechanism files inspected — none contain a `IC*ENTROPY` or `ENTROPY*IC` product term. This validates the paper's architectural disclosure: the static reward formula (Eq. 5) is purely additive, and the Cheung interaction signature *emerges dynamically* from HTP × ICEM coupling within the belief pipeline (not from a hard-coded interaction term in the formula).

## 6. Hand-off

- Update `MASTER-VERDICT.md` Phase 10 row to CLOSED, 7/7 PASS.
- Phases 11–18 + 17 (Zenodo bundle) remain pending.

---

## 7. Audio-Native Upgrade (2026-05-16) — 5-angle deepening

**Trigger.** §5 "Audio-native re-derivation deferred" was lifted on 2026-05-16: Cheung 2024 OSF deposit `5fk2q` was discovered to contain the audio (90 WAVs across 3 rhythm conditions × 30 chord progressions, stereo 44.1 kHz/16-bit, ~72 s each) plus chord onset metadata (`pitches_merged_wav_stim{01–30}.txt`). The §1–§6 closure (2026-05-07, 7/7 PASS) is **preserved unchanged**; this is a strengthening upgrade, not a re-litigation.

**Pre-registration.** Five decision rules + forbidden moves frozen 2026-05-16 in `AUDIO_NATIVE_UPGRADE.md` (now CLOSED). Engine SHA pin `318eb2f5…` verified by aggregate `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` before every angle.

### 7.1 Per-angle results

| Angle | Question | Verdict | Headline number |
|---|---|---|---|
| **3 — LOSO ceiling** | Inter-rater ceiling on Cheung 2019 pleasure ratings (Fisher-Z, N=39, 1,009 chord-rows × 39 VPID) | **PASS sanity** | **+0.2169** vs paper anchor +0.2169 (\|Δ\|=3.8×10⁻⁵). NEW: surprise ceiling **+0.4808** (N=25, 1,039 chord-rows) |
| **1 — Substitution validity** | Do MI's HTP/ICEM (event-aligned, ±200 ms windowed mean) substitute for IDyOM IC/ENT? | **NEGATIVE** (pre-registered, expected) | median r(HTP, ENT) = **−0.132** CI95 [−0.337, −0.063]; median r(ICEM, IC) = **−0.035** CI95 [−0.122, +0.038]. Architectural difference confirmed — MI features are **not** IDyOM-style relatives. |
| **2 — Engine-native interaction** | Does β(MI_HTP × MI_ICEM) reproduce Cheung 2019's β = −0.124 inside engine bootstrap CI? | **INCONCLUSIVE_BORDERLINE** | β = **−0.0603**, SE = 0.0266 (**same sign**); bootstrap CI95 [−0.111, −0.007]; distance outside CI = 0.013 (Cheung −0.124 sits 0.013 below upper bound, inside the [−0.05, +0.05] borderline band). Held-out 5-fold CV r = **+0.462** = **2.13× LOSO pleasure ceiling +0.217**. Cheung's IDyOM M2 in the same fold scheme = +0.543 = 2.50× ceiling. |
| **4 — Cross-rhythm consistency** | Are MI HTP/ICEM rhythm-near-invariant on the **same chord progression** across rhythms 1–3? (Architectural prediction: HTP/ICEM are **chord-level** features) | **POSITIVE_RHYTHM_INVARIANT** | median r(HTP) = **+0.9932** CI95 [+0.9914, +0.9945], range [+0.965, +0.999]; median r(ICEM) = **+0.8276** CI95 [+0.8117, +0.8508]. 90 stim×pair samples per channel, all positive. |
| **5 — Per-belief calibration** | Does the engine's predictive calibration (ECE on 8 Core beliefs, equal-mass 10-bin) generalise from DEAM to Cheung audio? | **POSITIVE_CHEUNG_CALIBRATED** | Pooled **ECE = 0.0819** (vs DEAM paper-anchor 0.079, \|Δ\| = 0.003); Brier 13.47× better than uniform baseline; 30 stim × 30 s × 8 beliefs = 1,236,480 frames pooled. Per-belief ECE range 0.014–0.141 (PitchIdentity/PCCR outlier at 0.141 replicates the Phase 5 monophonic-input disclosure). |

### 7.2 LOSO-relative framing (chill-standard)

Following the chill-standard discipline (`CHILL_STANDARD_UPGRADE.md`): no above-ceiling claim is made without explicit ratio to the held-out inter-rater ceiling.

| Quantity | Value | Ratio vs pleasure ceiling +0.2169 |
|---|---|---|
| Cheung M2 (IDyOM) CV r | +0.543 | **2.50×** |
| MI engine-native M2 CV r | +0.462 | **2.13×** |
| Routing ablation reference (paper §Voxelwise, lift over MI-naive) | — | (out of scope) |

The engine-native CV r at 2.13× the LOSO ceiling is **above the inter-rater floor**, while preserving the same sign as Cheung 2019's published interaction. The borderline verdict on β(CI containment) is a CI-width effect: Cheung −0.124 sits 0.013 outside the upper bound; sample reweighting cannot rescue a missed-by-0.013 containment, so we report it as INCONCLUSIVE rather than overclaim either direction.

### 7.3 What the upgrade demonstrates (and what it does not)

**Demonstrated:**
- **Architectural rhythm-invariance** of MI's HTP/ICEM channels — these are chord-level features by construction, and a 30-stim × 3-rhythm audio test confirms r(HTP) ≈ +0.99 and r(ICEM) ≈ +0.83 across pure rhythmic variation of identical pitch content. This is a falsifiable, audio-grounded architectural prediction that **passed**.
- **Cross-corpus calibration generalisation** — engine's predictive ECE on Cheung audio (0.082, 1.24 M frames, 8 Core beliefs) matches DEAM paper-anchor ECE 0.079 to within 0.003. Same calibration discipline, audio-distinct corpus.
- **Engine M2 interaction same sign, above-ceiling held-out CV** — the engine-native uncertainty × surprise interaction is negative (as in Cheung 2019), and the held-out CV r is 2.13× the inter-rater ceiling.

**Not demonstrated:**
- That MI HTP/ICEM = IDyOM IC/ENT (Angle 1 NEGATIVE — and pre-registered to be so; these are architecturally distinct constructs).
- That β(MI_HTP × MI_ICEM) bootstrap CI contains Cheung's −0.124 (Angle 2 INCONCLUSIVE; same sign and direction, half magnitude, 0.013 outside CI).

### 7.4 Compute profile (audio-native angles only)

- Wall: ~28 minutes total (90 WAVs × ~10 s engine extraction + chord-aligned windowing + bootstraps + ECE pooling). Apple M2 base + 8 GB unified.
- Memory peak: ~580 MB / 30 s stimulus (engine pipeline cache npz outputs).
- Engine pipeline runs: **90** (rhythm1 + rhythm2 + rhythm3, full R³ → H³ → execute → compute_beliefs for the 8 Core PAPER_BELIEFS).

### 7.5 Phase status

- **2026-05-07 closure (§1–§6):** UNCHANGED — 7/7 PASS.
- **2026-05-16 upgrade (§7):** added. 1 NEGATIVE (pre-registered, architectural disambiguation), 1 INCONCLUSIVE_BORDERLINE (same sign, above-ceiling CV), 2 POSITIVE (rhythm-invariance, cross-corpus calibration), 1 sanity-PASS (LOSO ceiling bit-exact paper-anchor reproduction).
- **Net Phase 10 verdict:** **CLOSED-STRENGTHENED**.

### 7.6 Artefact pointers (audio-native)

```
data/cheung_audio/
  stimuli_rhythm{1,2,3}/merged_wav_stim{01-30}_rhythm{01-03}.wav      (90 WAVs, ~1.2 GB)
  pitches/pitches_merged_wav_stim{01-30}.txt                          (30 chord-onset tables)
data/cheung_audio_outputs/
  mi_features_rhythm{1,2,3}/*.npz                                     (90 engine extraction caches)
  belief_traces_rhythm1/*.npz                                         (30 Angle-5 belief traces)
results/
  angle1_results.json + angle1_per_chord_aligned.csv + angle1_per_stim_correlations.csv
  angle2_results.json + angle2_bootstrap_distribution.npy
  angle3_loso_ceiling.json + angle3_loso_per_vpid.csv
  angle4_results.json + angle4_cross_rhythm_per_stim_pair.csv
  angle5_results.json
code/
  upgrade_angle1_audio_native_extraction.py
  upgrade_angle2_engine_native_refit.py
  upgrade_angle3_loso_ceiling.py
  upgrade_angle4_cross_rhythm.py
  upgrade_angle5_ece_cheung.py
AUDIO_NATIVE_UPGRADE.md                                                (pre-registration, CLOSED 2026-05-16)
```
