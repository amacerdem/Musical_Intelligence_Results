# Phase 03.3 — Cheung 2019 Emergent Reward Interaction

**Status:** CLOSED — Stage A 2026-05-07, Stage B audio-native upgrade 2026-05-16
**Verdict:**
- **Stage A** (statistical reanalysis on Cheung's deposit): **7 PASS / 0 CAVEAT / 0 FAIL** across 6 paper claims + 1 sample-size sanity
- **Stage B** (audio-native upgrade, 5-angle frozen pre-registration): **10 verdict cells — 8 PASS + 1 PASS-NEW (parallel surprise ceiling) + 1 PASS-MIXED aggregate**; sub-verdicts: 4 POSITIVE + 1 INCONCLUSIVE_BORDERLINE (engine-native β CI containment, 0.013 outside, same sign) + 1 architectural-disambiguation NEGATIVE (pre-registered, confirmed)

**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`

## 1-paragraph summary

**Stage A (paper-time closure, 2026-05-07).** All 6 paper Cheung-2019 reward-interaction claims (β(IC×ENT)=−0.158, bootstrap CI [−0.228,−0.084] containing Cheung's −0.124, ΔAIC=−33.5, held-out r=+0.615 for M3 Eq. 5, Eq. 5 architectural additivity) reproduce paper-exact from the preserved V2 T-R2-04 reanalysis artefact (2026-04-22, frozen-engine, statsmodels 0.14.6, seed=42, B=5000). Engine architectural control verified by source-tree inspection: 16 F6 reward-mechanism files contain no `IC*ENTROPY` product term, confirming the paper's claim that the Cheung interaction *emerges* from HTP×ICEM dynamic coupling rather than being hard-coded into Eq. 5. No engine pipeline call required (Cheung 2019 audio was assumed unavailable at Stage A).

**Stage B (audio-native upgrade, 2026-05-16).** Discovery of the Cheung 2024 OSF deposit (5fk2q) released 90 stimulus WAVs + 30 chord-pitch TSVs + surprise-rating column. Under a 5-angle frozen pre-registration, MI was run audio-native on the full 90-stimulus set (3 rhythm × 30 chord progressions). Five orthogonal findings: **(i)** LOSO inter-rater pleasure ceiling reproduces bit-exactly at ρ=+0.21686 vs paper-anchor +0.2169 (|Δ|=3.8×10⁻⁵); parallel surprise ceiling +0.481. **(ii)** Architectural rhythm-invariance: HTP r=+0.993 [+0.991, +0.994], ICEM r=+0.828 [+0.812, +0.851] across 90 stimulus-pair samples — MI's chord-level prediction channels are not rhythm-driven. **(iii)** Engine-native M2 re-fit: β(MI_HTP × MI_ICEM)=−0.060, bootstrap CI [−0.111, −0.007] (B=5,000); Cheung's −0.124 sits 0.013 outside CI → **INCONCLUSIVE_BORDERLINE** (same sign, half magnitude); held-out 5-fold CV r=+0.462 (2.13× LOSO ceiling). **(iv)** Per-belief pooled ECE on 1,236,480 Cheung audio frames = 0.082 (cross-corpus replication of Phase 03.2 DEAM anchor 0.079 to |Δ|=0.003); Brier 13.47× uniform; PitchIdentity outlier ECE=0.141 (Phase 03.2 §Limitations preserved). **(v)** Substitution-validity NEGATIVE test (pre-registered NEGATIVE confirmed): r(HTP, ENT)=−0.13, r(ICEM, IC)=−0.04 — MI channels are architecturally distinct from IDyOM symbol-stream entropies, not a re-substitution.

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`
- `AUDIO_NATIVE_UPGRADE.md` — Stage B pre-registration + 5-angle frozen decision rules (cited from paper §435)
- `CHILL_STANDARD_UPGRADE.md` — LOSO ceiling discipline disclosure (2026-05-12)
- `code/run.sh` + `run_phase10.py` — Stage A entry point
- `code/upgrade_angle{1..5}_*.py` — Stage B 5-angle execution scripts
- `code/compute_cheung_loso_ceiling.py` — Stage B Angle 3 LOSO inter-rater ceiling
- `data/README.md` — pointers
- `results/10_cheung_correlations.csv` + `10_cheung_manifest.json` — Stage A 7 PASS
- `results/10.B_cheung_audio_native_correlations.csv` — **Stage B 10 verdict cells**
- `results/angle{1..5}_*.json` + `angle{1,3,4}_*.csv` + `angle2_bootstrap_distribution.npy` — Stage B raw artefacts
- `results/cheung_loso_ceiling.json` — Stage B Angle 3 LOSO ceiling bootstrap output
