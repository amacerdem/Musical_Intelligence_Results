# Phase 03.3 — Provenance / Chain of Custody

## Source artefacts (read-only)

### V2 T-R2-04 (canonical reanalysis, 2026-04-22, frozen `Musical_Intelligence/`)
- `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R2-04/results.json` — full numerical output (full_data_fit, bootstrap, delta_aic, held_out_cv_summary)
- `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R2-04/coefficients.csv` — per-model OLS coefficients
- `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R2-04/run_analysis.py` — analysis script (statsmodels 0.14.6, seed=42, B=5000)

### Engine architectural control
- `Science/Musical_Intelligence/brain/functions/f6/mechanisms/` — 16 reward-mechanism files; inspected to confirm Eq. 5 has no `IC*ENTROPY` product term (additive only)

### Dataset
- `Science/datasets/reward/cheung2024/data_pleasure_2023.csv` — Cheung 2024 OSF release of Cheung 2019 Exp 2 (39,351 trials × 39 subjects × 30 songs × 3 rhythms)
- `data/cheung_audio/stimuli_rhythm{1,2,3}/merged_wav_stim{01-30}_rhythm{01-03}.wav` — Cheung 2024 OSF deposit `5fk2q` audio release (90 stereo 44.1 kHz/16-bit WAVs, ~1.2 GB; ~72 s each). Discovered 2026-05-16 via OSF API enumeration; **superseded the earlier "audio never released" assumption recorded in §3 of 02-RESULTS.md (2026-05-07)**.
- `data/cheung_audio/pitches/pitches_merged_wav_stim{01-30}.txt` — 30 chord-onset metadata tables (song, onset_sec, pitch1..pitch5 in Hz), used for event-aligned windowed feature extraction.
- **Original framing (2026-05-07):** Cheung 2019 paper deposit lacked audio → reanalysis was IDyOM-column-substitution only. This characterisation remains correct for the **published Cheung 2019 deposit**; the audio is from the **Cheung 2024** OSF re-deposit and was not available at paper-time of the MI corrected-evidence draft.

### Paper anchor
- §Discussion *Reward uncertainty × surprise interaction* (Musical-Intelligence-corrected-evidence.tex)
- §Significance: "reproduction of the Cheung 2019 uncertainty × surprise reward interaction on N=39,351 chord judgements (β = −0.158 with Cheung's β = −0.124 inside our 95% CI)"
- Falsifiable Table 5 #3

## Reproduction strategy

Read the V2 T-R2-04 results.json + coefficients.csv directly, verify each of the 6 paper claims against numerical entries, plus a 7th sample-size sanity. Engine architectural control via source-tree regex inspection. **No engine call** — Cheung audio was not released, so the analysis cannot be audio-native; the V2 T-R2-04 analysis is the paper-canonical reanalysis.

## Derived artefacts

- `results/10_cheung_correlations.csv` — 7-row claim-level table (2026-05-07 closure)
- `results/10_cheung_manifest.json` — schema-valid manifest (2026-05-07 closure)
- `results/angle1_results.json` + `angle1_per_chord_aligned.csv` + `angle1_per_stim_correlations.csv` — Angle 1 substitution-validity (NEGATIVE)
- `results/angle2_results.json` + `angle2_bootstrap_distribution.npy` — Angle 2 engine-native M2 (INCONCLUSIVE_BORDERLINE)
- `results/angle3_loso_ceiling.json` + `angle3_loso_per_vpid.csv` — Angle 3 LOSO ceiling (sanity PASS pleasure 0.2169, surprise 0.4808)
- `results/angle4_results.json` + `angle4_cross_rhythm_per_stim_pair.csv` — Angle 4 cross-rhythm consistency (POSITIVE_RHYTHM_INVARIANT)
- `results/angle5_results.json` — Angle 5 per-belief ECE (POSITIVE_CHEUNG_CALIBRATED, pooled ECE 0.082)
- `AUDIO_NATIVE_UPGRADE.md` — 5-angle pre-registration spec (frozen 2026-05-16, CLOSED)

## Audio-native upgrade (2026-05-16)

The 5-angle audio-native deepening (see `02-RESULTS.md` §7) **strengthens** the 2026-05-07 closure without re-litigating it. Engine SHA `318eb2f5…` was verified by aggregate `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` before every angle. Chain of custody for the 90 audio WAVs is recorded in `results/angle1_results.json` per-stimulus SHA-256 (rhythm1) and the analogous entries in `angle4` cross-rhythm caches (rhythm2 + rhythm3).
