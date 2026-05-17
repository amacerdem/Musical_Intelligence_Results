# ECE Reproduction — Methodology (locked)

**Locked at:** 2026-05-05 (V6 phase A2 close)
**Status:** Frozen. Any change to operationalization invalidates the reproduction and requires a new entry.

---

## 1. Inputs

### 1.1 Audio dataset

- **Source:** DEAM (Database for Emotional Analysis of Music) — Soleymani et al. 2013
- **Cache location:** `Science/datasets/emotion/DEAM/audio/MEMD_audio/{ID}.mp3`
- **Held-out songs (5):** IDs **1034, 1508, 1777, 1896, 1923**
- **Selection rule:** seed-42 random.choice from DEAM song_ids with `id > 1000` (per paper-time `compute_ece_brier.py`). Restriction `id > 1000` provides safety margin past F5 calibration N=200 range.
- **Clip:** first 30 seconds of each song (`MAX_DURATION_S = 30.0`).

### 1.2 Engine pin

- **HEAD:** `5b9aba41` (V3 architectural anchor, deterministic, bit-identical, |Δρ| ≤ 8.8e-5).
- **Engine path:** `Science/Musical_Intelligence/`
- **Engine modifications:** NONE. Reproduction calls `CoreBelief.run_cycle()` from frozen engine.

---

## 2. Audio pipeline (paper convention)

1. **Load:** `librosa.load(path, sr=44100, mono=True, duration=30.0)` → `(N,)` waveform.
2. **Tensorize:** `torch.from_numpy(y).unsqueeze(0).float()` → `(1, N)`.
3. **Mel spectrogram:** `torchaudio.transforms.MelSpectrogram(sample_rate=44100, n_fft=2048, hop_length=256, n_mels=128, power=2.0)`.
4. **Log + normalize:** `mel = log1p(mel); mel = mel / mel.amax((-2,-1), keepdim=True).clamp(min=1e-8)`.
5. **R³ extraction:** `R3Extractor.extract(mel, audio=audio_t, sr=44100)` → `(1, T, 97)`. Frame rate ≈ 172.27 Hz.
6. **H³ extraction:** `H3Extractor.extract(r3_features, h3_demands)` where `h3_demands` is the union of all mechanism demands + belief precision tuples.
7. **Mechanism execution:** Depth-ordered chain — `BCH → MIAA → HTP → SPH → ICEM → PSCL → PCCR`. PSCL depends on BCH; PCCR depends on BCH+PSCL.

---

## 3. Belief selection

### 3.1 Paper's 8 beliefs (PRIMARY — replication target)

| # | Function | Belief class | Mechanism | File path |
|---|---|---|---|---|
| 1 | F1 sensory | `HarmonicStability` | BCH | `f1/beliefs/bch/harmonic_stability.py` |
| 2 | F1 sensory | `PitchProminence` | PSCL | `f1/beliefs/pscl/pitch_prominence.py` |
| 3 | F1 sensory | `PitchIdentity` | PCCR | `f1/beliefs/pccr/pitch_identity.py` |
| 4 | F1 sensory | `TimbralCharacter` | MIAA | `f1/beliefs/miaa/timbral_character.py` |
| 5 | F2 prediction | `PredictionHierarchy` | HTP | `f2/beliefs/htp/prediction_hierarchy.py` |
| 6 | F2 prediction | `PredictionAccuracy` | HTP | `f2/beliefs/htp/prediction_accuracy.py` |
| 7 | F2 prediction | `SequenceMatch` | SPH | `f2/beliefs/sph/sequence_match.py` |
| 8 | F2 prediction | `InformationContent` | ICEM | `f2/beliefs/icem/information_content.py` |

**Rationale (paper-time):** F1 sensory + F2 prediction were chosen because their predict/observe/update cycle is deterministic and well-defined on raw audio; they share a common substrate (R³ → H³ feature space). The selection was published-and-frozen at T-R3-08 (V2/2026-04-23).

### 3.2 V6 extension — 6 additional beliefs (F3-F8)

| # | Function | Belief class | Mechanism |
|---|---|---|---|
| 9 | F3 attention | `AttentionCapture` | IACM |
| 10 | F4 memory | `EpisodicEncoding` | HCMC |
| 11 | F5 emotion | `EmotionalArousal` | AAC |
| 12 | F6 reward | `Pleasure` | SRP |
| 13 | F7 motor | `GrooveQuality` | HGSIC |
| 14 | F8 learning | `StatisticalModel` | SLEE |

**Rationale (V6, 2026-05-05):** The paper's 8 beliefs only cover F1+F2. V6 tests whether the calibration property generalizes to attention / memory / emotion / reward / motor / learning. This is a NOVEL test, not a replication.

---

## 4. Belief Bayesian cycle (per-frame)

For each (belief, song) pair, call:

```python
result = belief_instance.run_cycle(
    mechanism_output=mech_output,  # (1, T, D) — output of belief.MECHANISM
    context={},                      # empty dict (paper convention: V2/T-R3-08 line 264)
    h3_features=h3_feat,            # all H³ tuples from engine extraction
)
```

The `run_cycle` is defined at `Science/Musical_Intelligence/contracts/bases/belief.py` line 221+. It returns a dict with keys:

- `obs`: `(1, T)` — observation = `belief.observe(mechanism_output)`
- `pred`: `(1, T)` — prediction = `belief.predict(prev_posterior, context, h3_features)`
- `pe`: `(1, T)` — prediction error = `obs - pred`
- `pi_obs`: `(1, T)` — observation precision (from H³ stability)
- `pi_pred`: `(1, T)` — prediction precision (from PE history, 16-frame buffer)
- `gain`: `(1, T)` — Bayesian gain = `pi_obs / (pi_obs + pi_pred + ε)`, clamped to `[0.20, 0.80]`
- `posterior`: `(1, T)` — posterior = `(pred + gain × pe).clamp(0, 1)`

The `posterior` of frame `t` becomes the `prev` of frame `t+1` (recursive; this is the actual frame-by-frame Bayesian state).

---

## 5. Calibration metric

### 5.1 Continuous accuracy y

For each frame `t`:

```
y[t] = 1.0 - clip(|PE[t]|, 0.0, 1.0)
```

This is the paper convention (V2/T-R3-08 `ece_brier_analysis.py` line `y = 1.0 - np.clip(np.abs(pe), 0.0, 1.0)`). High `y` = small PE = well-predicted frame → directly comparable to `pi_pred` (the model's self-reported confidence).

### 5.2 Warm-up

Drop first **16 frames** per (song, belief) before computing metrics. This is the precision-window warm-up — `pi_pred` is unreliable while the PE buffer fills (paper convention: `compute_ece_brier.py` PRECISION_WINDOW = 16).

### 5.3 Equal-frequency bin ECE

10 bins. For each bin `b`:

- `n_b` = number of frames in bin `b`
- `mean_conf_b` = mean(`pi_pred`) within bin
- `mean_y_b` = mean(`y`) within bin

```
ECE = Σ_b |mean_conf_b - mean_y_b| × (n_b / N)
```

### 5.4 Brier

```
Brier = mean((pi_pred - y)²)
```

### 5.5 Brier decomposition (Murphy 1973)

```
Brier = reliability - resolution + uncertainty
```

Where:
- `uncertainty = ȳ × (1 - ȳ)` (variance of y)
- `reliability = Σ_b (n_b/N) × (mean_conf_b - mean_y_b)²` (within-bin gap)
- `resolution = Σ_b (n_b/N) × (mean_y_b - ȳ)²` (between-bin spread)

Pass criterion P3: `reliability / uncertainty < 1.0` (model is closer to perfectly calibrated than to perfectly uninformative).

### 5.6 Circular-shift permutation null (within song)

Per cell: draw `shift ~ Uniform[1, T-1]`, compute `pi_pred_shifted = roll(pi_pred, shift)`, recompute ECE. Repeat 10,000 times per cell. Seed: `2026050502`.

**Note:** This null is **degenerate** for high-N data with `pi_pred` saturated near 0.99. The shift preserves the marginal distributions of both `pi_pred` and `y`; only their pairing changes. With 5,152 frames per cell and `pi_pred` standard deviation < 0.05 for most beliefs, the null distribution collapses around the observed ECE value (null 5th-percentile ≈ observed ECE). The test has zero discriminative power for this data structure — it is reported but should not be load-bearing.

### 5.7 Reliability bootstrap (per-belief)

Per belief, pool across 5 songs. Resample songs with replacement (block bootstrap, N=1000, seed=`2026050502`), recompute bin-level `mean_y` per resample, take 2.5/97.5 percentiles per bin → 95% bootstrap CI on each bin's empirical accuracy.

---

## 6. Pre-registered pass criteria

| # | Test | Threshold | V6 Result |
|---|---|---|---|
| P1 | Median per-cell ECE on paper's 8 beliefs | `< 0.10` | **PASS** (0.083) |
| P2 | Pooled ECE < 5th percentile of permutation null | (degenerate; see §5.6) | DEGENERATE |
| P3 | Brier reliability/uncertainty | `< 1.0` | **PASS** (0.085) |

**Composite verdict:** PARTIAL PASS — replication confirmed (P1, P3); P2 degenerate due to data structure.

---

## 7. Ground-truth definition note

The "y" in this calibration is **NOT** DEAM valence/arousal annotations. It is the **internal belief consistency** of the engine: how well did `pred` match `obs` at frame `t`. This is the paper convention.

A separate calibration test against DEAM ground-truth annotations would require:
- Mapping a specific belief output (e.g., F5 EmotionalArousal) to DEAM arousal
- Resampling DEAM 2 Hz annotations to engine 172 Hz frames
- Defining what π_pred should predict in that context

This is **out of scope** for the current ECE reproduction. The paper claim is about internal Bayesian consistency, not external annotation alignment.
