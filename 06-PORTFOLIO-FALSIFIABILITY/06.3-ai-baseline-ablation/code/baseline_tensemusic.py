"""Phase 06.3 — Baseline on TenseMusic (38 pieces, continuous tension prediction).

MI value to beat: top mech (MECH_AAC__F1:hr_pred_2s) Spearman ρ=+0.421 vs continuous
mean tension, evaluated per-piece + aggregated (38/38 directionally pass, 15/15
Bonferroni). LOSO inter-rater ceiling ρ=+0.386. MI exceeds ceiling (109%).

Baseline panel:
  Ridge LOSO over pieces on frame-level audio features (RMS, ZCR, spectral
  centroid, spectral rolloff, spectral flatness, 4-band energy ratios) at 1 Hz
  to match TenseMusic CSV rating cadence.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _baseline_common import load_audio_simple, OUTPUT_DIR, MASTER_SEED

SCIENCE_ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science")
TM_DIR = SCIENCE_ROOT / "datasets/emotion/TenseMusic"
MUSIC = TM_DIR / "music_files"
RAW = TM_DIR / "data_raw"

np.random.seed(MASTER_SEED)


def frame_features(audio, sr, hop_s=1.0):
    """Compute frame-level features at 1 Hz cadence. Returns (n_frames, 11)."""
    n_per_frame = int(hop_s * sr)
    n_frames = len(audio) // n_per_frame
    feats = np.zeros((n_frames, 11))
    for i in range(n_frames):
        seg = audio[i * n_per_frame:(i + 1) * n_per_frame]
        if len(seg) < n_per_frame:
            break
        # RMS
        feats[i, 0] = np.sqrt(np.mean(seg ** 2))
        # ZCR
        feats[i, 1] = np.mean(np.abs(np.diff(np.sign(seg))) > 0) * 0.5
        # STFT-based features
        from scipy.signal import welch
        f, psd = welch(seg, fs=sr, nperseg=min(1024, len(seg)))
        psd_norm = psd / (psd.sum() + 1e-12)
        # Spectral centroid
        feats[i, 2] = np.sum(f * psd_norm)
        # Spectral spread
        feats[i, 3] = np.sqrt(np.sum(((f - feats[i, 2]) ** 2) * psd_norm))
        # Spectral rolloff (95%)
        csum = np.cumsum(psd)
        idx = np.argmax(csum >= 0.95 * csum[-1])
        feats[i, 4] = f[idx]
        # Spectral flatness
        feats[i, 5] = np.exp(np.mean(np.log(psd + 1e-12))) / (np.mean(psd) + 1e-12)
        # 5-band energy ratios
        edges = [0, 250, 500, 1000, 2000, sr / 2]
        for b in range(5):
            mask = (f >= edges[b]) & (f < edges[b + 1])
            feats[i, 6 + b] = psd[mask].sum() / (psd.sum() + 1e-12)
    return feats[:n_frames]


def main():
    print("# Phase 06.3 — Baseline on TenseMusic (38 pieces, continuous tension)")
    print(f"Master seed: {MASTER_SEED}")
    print()

    wav_files = sorted(MUSIC.glob("*.wav"))
    csv_files = sorted(RAW.glob("*.csv"))
    print(f"  WAVs: {len(wav_files)}, raw CSVs: {len(csv_files)}")

    # Match WAV ↔ CSV by stem (Bach.wav ↔ Bach.csv)
    wav_by_stem = {p.stem: p for p in wav_files}
    csv_by_stem = {p.stem: p for p in csv_files}
    matched = sorted(set(wav_by_stem) & set(csv_by_stem))
    print(f"  Matched pieces: {len(matched)}")
    print()

    print("## Extracting features + ratings per piece ...")
    piece_features = {}
    piece_targets = {}
    for stem in matched:
        wav = wav_by_stem[stem]
        csv_p = csv_by_stem[stem]
        audio, sr = load_audio_simple(wav)
        feats = frame_features(audio, sr, hop_s=1.0)

        df = pd.read_csv(csv_p)
        rating_cols = [c for c in df.columns if c.startswith("rating")]
        df["mean_tension"] = df[rating_cols].mean(axis=1)
        df["t_sec"] = pd.to_datetime(df["time"]).astype("int64") / 1e9 \
            if df["time"].dtype == "object" else df["time"]
        df["t_sec"] = df["t_sec"] - df["t_sec"].iloc[0]
        # Resample to 1 Hz (mean over each 1s bin)
        df["t_bin"] = df["t_sec"].astype(int)
        target = df.groupby("t_bin")["mean_tension"].mean().values

        n = min(len(feats), len(target))
        if n < 5:
            continue
        piece_features[stem] = feats[:n]
        piece_targets[stem] = target[:n]

    pieces = sorted(piece_features.keys())
    print(f"  Pieces with valid features+targets: {len(pieces)}")
    print()

    print("## LOSO ridge (leave-one-piece-out) ...")
    from sklearn.linear_model import RidgeCV
    from scipy.stats import spearmanr
    alphas = np.logspace(-3, 3, 13)

    per_piece_rho = {}
    for held_out in pieces:
        train_X = np.concatenate([piece_features[p] for p in pieces if p != held_out])
        train_y = np.concatenate([piece_targets[p] for p in pieces if p != held_out])
        # Drop NaNs
        keep = ~(np.isnan(train_X).any(axis=1) | np.isnan(train_y))
        train_X, train_y = train_X[keep], train_y[keep]
        model = RidgeCV(alphas=alphas, cv=5)
        model.fit(train_X, train_y)
        test_X = piece_features[held_out]
        test_y = piece_targets[held_out]
        keep_t = ~(np.isnan(test_X).any(axis=1) | np.isnan(test_y))
        test_X, test_y = test_X[keep_t], test_y[keep_t]
        if len(test_y) < 3:
            continue
        pred = model.predict(test_X)
        rho, _ = spearmanr(pred, test_y)
        per_piece_rho[held_out] = float(rho) if not np.isnan(rho) else 0.0

    rho_values = list(per_piece_rho.values())
    median_rho = np.median(rho_values)
    mean_abs_rho = np.mean(np.abs(rho_values))
    n_positive = sum(1 for r in rho_values if r > 0)

    print(f"  Per-piece ρ — median: {median_rho:+.4f}, |mean|: {mean_abs_rho:.4f}")
    print(f"  Directional (ρ>0): {n_positive}/{len(rho_values)}")
    print(f"  Best piece ρ: {max(rho_values):+.4f}")
    print(f"  Worst piece ρ: {min(rho_values):+.4f}")
    print()

    mi_rho = 0.421
    comparison_rho = median_rho  # MI's reported number is across-piece aggregate
    verdict = "MI_WINS" if mi_rho > abs(comparison_rho) else "AI_WINS_OR_TIE"
    print("## Comparison to MI TenseMusic")
    print(f"  MI ρ (MECH_AAC F1 hr_pred_2s vs tension): {mi_rho:+.4f}")
    print(f"  Baseline median ρ:                        {median_rho:+.4f}")
    print(f"  Baseline |mean| ρ:                        {mean_abs_rho:+.4f}")
    print(f"  Per-dataset verdict:                      {verdict}")

    result = {
        "dataset": "TenseMusic",
        "baseline": "ridge_frame_level_audio_features",
        "n_pieces": len(rho_values),
        "median_piece_rho": float(median_rho),
        "mean_abs_piece_rho": float(mean_abs_rho),
        "n_positive_directional": int(n_positive),
        "per_piece_rho": per_piece_rho,
        "mi_value_to_beat": mi_rho,
        "mi_advantage": mi_rho - abs(comparison_rho),
        "per_dataset_verdict": verdict,
        "master_seed": MASTER_SEED,
        "engine_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
    }
    output_path = OUTPUT_DIR / "baseline_ridge_tensemusic.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
