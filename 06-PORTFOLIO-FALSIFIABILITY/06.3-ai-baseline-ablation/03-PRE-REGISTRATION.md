# Phase 06.3 Pre-Registration — Same-data from-scratch AI baseline ablation

**Frozen:** 2026-05-13 (scaffold + decision rule; baselines NOT YET RUN)
**Engine SHA:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Author:** A. Erdem (sole-authored)

## Hypothesis (verbatim from master paper §Limitations §Same-data learning-frontier hypothesis)

> A from-scratch AI learner restricted to the same dataset MI uses, with no external priors --- no pretrained audio encoder, no hand-engineered psychoacoustic features, no literature-derived constants, no transfer from outside corpora --- cannot match MI's value on small-stimulus high-theory-density paradigms.

## Datasets (5 small-stimulus phases)

For each dataset, the protocol is:
1. **Input:** Raw audio waveform (or, where stimulus is per-spectrum synthesised, the raw spectrum vector — Marjieh, Carillon). No hand-engineered psychoacoustic features.
2. **Target:** Per-stimulus consensus rating (consonance / chord pleasantness / arousal / tension / reward).
3. **Cross-validation:** Leave-one-stimulus-out for small-N corpora; leave-songs-out 5-fold for Cheung, DEAM-5, TenseMusic.
4. **Metric:** Spearman $\rho$ or Pearson $r$ on held-out predictions vs. consensus ratings, matched to the MI evaluation protocol of the corresponding paradigm.

| Dataset | N stimuli | N raters | MI value to beat |
|---|---|---|---|
| Marjieh 2024 | 13 binned intervals | 147 | $|\rho| = 0.736$ |
| Harrison Carillon | 13 binned intervals | 113 | $|\rho| = 0.830$ |
| Cheung 2019 | 1,009 chord trials | 39 | $r = +0.615$ |
| DEAM-5-song F4 MMP | 5 songs | DEAM raters | $|\rho| = 0.581$ |
| TenseMusic tension | 38 pieces | 30/piece × 50 Hz | $\rho = +0.421$ |

## Baseline panel (5 from-scratch AI architectures)

All baselines respect the same-data constraint: trained only on the target dataset, no pretrained encoders, no hand-engineered psychoacoustic features, no external transfer.

1. **Ridge regression on raw STFT mel-spectrogram features.** $1024$-bin STFT magnitude, $128$-bin mel filterbank (Slaney mel, $27.5$--$16{,}000$ Hz, no psychoacoustic Bark/Plomp-Levelt adjustment), $L_2$ regularisation $\alpha$ swept on a log grid from $10^{-3}$ to $10^{3}$, optimal $\alpha$ chosen by inner-LOO-CV.

2. **Elastic net on the same STFT-mel features.** $\alpha = 0.5$ mixing, $L_1 + L_2$ regularisation strength swept on log grid.

3. **Gradient-boosted trees (XGBoost).** Input: $4$-band FFT energy ratios, zero-crossing rate, RMS energy, spectral centroid, spectral spread, spectral rolloff (six generic audio descriptors). No psychoacoustic parameterisation. Trees: depth $\leq 4$, learning rate $0.1$, $\leq 100$ trees, early stopping on inner-CV.

4. **Small MLP from scratch on raw waveform.** $3$-layer fully-connected ($512 \to 128 \to 32$ hidden), random initialisation, AdamW optimiser, leave-one-stimulus-out training, early stopping on inner-CV.

5. **Small CNN encoder from scratch on mel-spectrogram.** $3$-layer Conv1D ($32 \to 64 \to 128$ channels with kernel sizes $5/3/3$) followed by global average pooling + linear head, random initialisation, same training protocol as MLP.

**Hyperparameter selection:** all hyperparameters are selected via inner-LOO-CV on the training set, not held-out test set. No baseline parameter is tuned against the held-out result that decides the verdict.

## Decision rule (LOCKED before any baseline runs)

For each dataset and each baseline, compute the LOSO/LOO-CV correlation $r$ (or $\rho$) using identical procedure to MI's evaluation. Compare to MI's value on the same dataset:

- **Per-dataset verdict:** MI WINS if MI > every baseline; AI WINS if any baseline $\geq$ MI; tied otherwise.

- **Aggregate verdict (locked):**
  - **POSITIVE (hypothesis supported):** MI WINS on $\geq 4$ of $5$ datasets, AND no baseline beats MI by $|\Delta r| \geq 0.05$ on the remaining dataset(s).
  - **NEGATIVE (hypothesis falsified):** $\geq 2$ baselines reach or exceed MI on $\geq 2$ datasets.
  - **OPEN:** any state between these two regimes; the result is reported but the same-data learning-frontier framing must be revised in the master paper to reflect partial support / mixed evidence.

## Confounders excluded

- **Pretrained encoders** (MERT, CLAP, OpenL3, Wav2Vec, AST): would violate "no external priors" constraint. Reported separately as upper-bound references in `_infra/manifests/reference_upper_bound.json`.
- **Hand-engineered psychoacoustic features** (Sethares roughness, Stumpf fusion, Krumhansl key profile, Plomp--Levelt critical bands, Zwicker--Fastl sharpness): same constraint.
- **Music-theoretic features** (chord identity, interval class, tonal hierarchy): same constraint.
- **Cross-dataset transfer learning:** each dataset trained independently; no shared weight initialisation across datasets.

## Random seeds (frozen)

- Master seed: `20260513` (deterministic SHA-256 derived sub-seeds per baseline × dataset)
- Per-baseline sub-seed: `master_seed + hash(baseline_id + dataset_id)` mod $2^{32}$
- All random-init layers, optimiser state, train/test splits seeded from this hierarchy.

## Audit verification

The baseline panel is executed against the canonical engine SHA `318eb2f5...` to ensure MI's reported values match the audit's MI value for direct comparison. Any baseline-vs-MI comparison uses MI values computed on the same engine pin.

## What this pre-registration does NOT commit

- Specific deep-network architectures beyond the panel above (transformer, audio diffusion, etc.) are out of scope for v1.0. If the v1.0 verdict is POSITIVE, v1.1 may add deeper architectures with their own pre-registration extension.
- Pretrained-encoder reference baselines (MERT, CLAP) are reported separately and do NOT enter the decision rule.
- Phase 06.3 v1.0 is the falsifiability test for the same-data learning-frontier hypothesis; v1.1+ extensions may test additional architectural ablations.

## Status

- 2026-05-13: scaffold + pre-registration frozen
- Baselines NOT YET RUN
- Awaiting per-invocation execution authorisation
