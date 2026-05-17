# Phase 06.3 — Same-data from-scratch AI baseline ablation

**Purpose:** Falsifiable test of the same-data learning-frontier hypothesis (Ceiling 3 of the three-ceilings framework). The hypothesis: a from-scratch AI learner restricted to the same dataset MI uses, with no external priors (no pretrained encoders, no hand-engineered psychoacoustic features inherited from external literature), cannot match MI's value on small-stimulus high-theory-density paradigms.

## Scope

**Engine pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (canonical commit)
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Phase status:** PRELIMINARY POSITIVE — 4/5 datasets executed 2026-05-14 (Marjieh, Carillon, Cheung, TenseMusic); DEAM-5-song F4 MMP deferred to v1.1. Pre-registration frozen 2026-05-13 prior to any baseline training. See `L9_verdict/REPORT.md` for the interim verdict and `03-PRE-REGISTRATION.md` for the locked decision rule.
**Audit relationship:** Locks Ceiling 3 of the master paper's three-ceilings framework (§Methods §Three-ceilings interpretive framework).

## Pre-registration

Decision rule and protocol are frozen at `03-PRE-REGISTRATION.md` prior to any baseline training. Decision rule summary:

- **POSITIVE (hypothesis supported):** if MI's value exceeds every from-scratch AI baseline on $\geq 4$ of $5$ datasets (Marjieh 2024, Harrison Carillon, Cheung 2019, DEAM-5-song F4 memory-pleasure, TenseMusic continuous tension).
- **NEGATIVE (hypothesis falsified):** if $\geq 2$ from-scratch AI baselines reach or exceed MI on $\geq 2$ datasets.
- **OPEN:** between these two regimes.

## Baseline panel

Five from-scratch AI architectures, no external priors:

1. Ridge regression on raw STFT mel-spectrogram features (no psychoacoustic adjustments)
2. Elastic net on the same STFT-mel features
3. Gradient-boosted trees (XGBoost) on generic audio descriptors (FFT energy bands, ZCR, spectral centroid, RMS — all standard MIR descriptors with no psychoacoustic-literature parameterisation)
4. Small multilayer perceptron (MLP) from scratch on raw audio waveform
5. Small CNN encoder from scratch on raw audio mel-spectrogram with random initialisation

**Excluded by design (would violate the same-data constraint):**
- Pretrained audio encoders (MERT, CLAP, OpenL3, Wav2Vec, AST)
- Hand-engineered psychoacoustic features (Sethares roughness, Stumpf fusion, Krumhansl key profiles, Plomp--Levelt critical bands, Zwicker--Fastl sharpness, etc.)
- Music-theoretic features (chord identity, interval class, tonal hierarchy)
- Cross-dataset transfer learning

Pretrained-encoder + linear-probe baselines, where applicable, are reported separately in `_infra/manifests/reference_upper_bound.json` as upper-bound references for the unrestricted-prior regime, NOT as same-data learners.

## Datasets (5 small-stimulus phases)

| Dataset | N stimuli | N raters | MI value | Source |
|---|---|---|---|---|
| Marjieh 2024 | 13 binned intervals | 147 participants | $|\rho| = 0.736$ | Phase 01.2 |
| Harrison Carillon | 13 binned intervals | 113 participants | $|\rho| = 0.830$ | Phase 01.2 |
| Cheung 2019 reward | 1,009 chord trials | 39 raters | $r = +0.615$ | Phase 03.3 |
| DEAM-5-song F4 MMP | 5 songs | DEAM ratings | $|\rho| = 0.581$ | Phase 03.2 |
| TenseMusic tension | 38 pieces | 30 raters | $\rho = +0.421$ | Phase 03.5 |

## Layer scaffold (L1-L9)

- `L1_engine_pin/` — engine SHA pin verification
- `L4_baselines/` — baseline training + LOSO/leave-songs-out evaluation
- `L5_decision_rule/` — decision rule application on results
- `L9_verdict/` — final verdict (POSITIVE / NEGATIVE / OPEN) reconciliation

## Source documents

- Master paper: `The Paper/Musical-Intelligence/S1/Musical-Intelligence-S1.tex` §Limitations §Same-data learning-frontier hypothesis
- Three-ceilings framework: §Methods §Three-ceilings interpretive framework
- Pre-registration: `03-PRE-REGISTRATION.md` (locked before execution)
