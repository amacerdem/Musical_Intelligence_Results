"""Shared utilities for the from-scratch AI baselines.

Same-data constraint:
- Input: raw audio waveform → STFT magnitude → 128-bin mel filterbank
  (Slaney mel, 27.5 – 16000 Hz).
- NO psychoacoustic adjustments (no Sethares roughness, no Stumpf fusion,
  no Plomp-Levelt).
- NO music-theoretic features (no chord identity, no interval class).
- NO pretrained encoders.

Cross-validation: leave-one-stimulus-out (LOO).
Hyperparameter: ridge alpha swept on log grid via inner-LOO-CV.
Metric: Spearman ρ between LOO predictions and held-out targets.
"""

from pathlib import Path

import numpy as np

PHASE_DIR = Path(__file__).resolve().parent.parent
SECTION_06 = PHASE_DIR.parent
V_REPRO    = SECTION_06.parent

OUTPUT_DIR = PHASE_DIR / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_SEED = 20260513
np.random.seed(MASTER_SEED)


def load_audio_simple(wav_path, target_sr=22050):
    """Load WAV file, mono, resample to target_sr.

    Uses scipy.io.wavfile (no librosa, no pretrained loader).
    """
    from scipy.io import wavfile
    sr, data = wavfile.read(str(wav_path))
    if data.dtype.kind == "i":
        max_val = np.iinfo(data.dtype).max
        data = data.astype(np.float64) / max_val
    elif data.dtype.kind == "u":
        data = (data.astype(np.float64) - 128) / 128
    else:
        data = data.astype(np.float64)
    if data.ndim > 1:
        data = data.mean(axis=1)  # mono
    if sr != target_sr:
        ratio = target_sr / sr
        n_target = int(round(len(data) * ratio))
        x_old = np.linspace(0, 1, len(data))
        x_new = np.linspace(0, 1, n_target)
        data = np.interp(x_new, x_old, data)
    return data, target_sr


def stft_mel_features(audio, sr, n_mels=128, n_fft=2048, hop=512):
    """Compute STFT magnitude → mel filterbank features."""
    from scipy.signal import stft
    f, t, Zxx = stft(audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop, return_onesided=True)
    mag = np.abs(Zxx)

    def hz_to_mel(hz):
        return 2595 * np.log10(1 + hz / 700)

    def mel_to_hz(mel):
        return 700 * (10**(mel / 2595) - 1)

    f_min, f_max = 27.5, min(16000, sr / 2)
    mel_min, mel_max = hz_to_mel(f_min), hz_to_mel(f_max)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = mel_to_hz(mel_points)

    fft_bins = np.floor((n_fft + 1) * hz_points / sr).astype(int)
    fft_bins = np.clip(fft_bins, 0, mag.shape[0] - 1)

    filterbank = np.zeros((n_mels, mag.shape[0]))
    for m in range(1, n_mels + 1):
        left, center, right = fft_bins[m - 1], fft_bins[m], fft_bins[m + 1]
        if center > left:
            filterbank[m - 1, left:center] = (np.arange(left, center) - left) / max(1, center - left)
        if right > center:
            filterbank[m - 1, center:right] = (right - np.arange(center, right)) / max(1, right - center)

    mel_spec = filterbank @ mag
    log_mel = np.log10(mel_spec + 1e-9)
    feat = log_mel.mean(axis=1)
    return feat


def loo_ridge_regression(X, y):
    """Leave-one-out CV ridge regression with inner-LOO alpha selection."""
    from sklearn.linear_model import RidgeCV
    n = len(y)
    alphas = np.logspace(-3, 3, 13)

    predictions = np.zeros(n)
    best_alphas = []

    for i in range(n):
        train_mask = np.ones(n, dtype=bool)
        train_mask[i] = False
        X_tr, y_tr = X[train_mask], y[train_mask]
        X_te = X[i : i + 1]

        if len(y_tr) > 2:
            model = RidgeCV(alphas=alphas, cv=min(5, len(y_tr) - 1))
        else:
            model = RidgeCV(alphas=alphas)
        model.fit(X_tr, y_tr)
        predictions[i] = model.predict(X_te)[0]
        best_alphas.append(float(model.alpha_))

    return predictions, best_alphas
