"""Phase 06.3 — Baseline 1 on Harrison Carillon (real-bell partial timbre, 13 binned intervals).

Synthesise Carillon dyads using the real upper/lower bell spectra (SUSTAINED mode,
A5=880Hz f0 — same configuration that reproduces the canonical paper number
|ρ|=0.8297 via V2 04_carillon_sweep). Bin behavioural ratings to 13 semitone bins.
Ridge LOO-CV on raw STFT-mel features.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _baseline_common import stft_mel_features, loo_ridge_regression, OUTPUT_DIR, MASTER_SEED

REPO_ROOT = Path(__file__).resolve().parents[3]
CARILLON_DATA = REPO_ROOT / "datasets/consonance/harrison2024_carillon"

np.random.seed(MASTER_SEED)


def synthesize_carillon_dyad(s_int, lower_spec, upper_spec, f0_lower=880.0, sr=22050, duration=1.0):
    """Real-bell SUSTAINED dyad: lower bell at f0=880Hz, upper at f0·2^(s/12)."""
    n_samples = int(duration * sr)
    t = np.arange(n_samples) / sr

    f0_upper = f0_lower * (2 ** (s_int / 12))

    audio = np.zeros(n_samples)
    for f0, spec in ((f0_lower, lower_spec), (f0_upper, upper_spec)):
        for _, row in spec.iterrows():
            ratio = float(row["FrequencyRatio"])
            amp = float(row["Amplitude"])
            freq = f0 * ratio
            if 0 < freq < sr / 2:
                audio += amp * np.sin(2 * np.pi * freq * t)

    audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.8

    fade_n = int(0.05 * sr)
    envelope = np.ones(n_samples)
    envelope[:fade_n] = np.linspace(0, 1, fade_n)
    envelope[-fade_n:] = np.linspace(1, 0, fade_n)
    audio = audio * envelope

    return audio, sr


def main():
    print("# Phase 06.3 — Baseline 1 (Ridge on STFT-mel) — Harrison Carillon")
    print(f"Master seed: {MASTER_SEED}")
    print(f"Synthesis: real-bell SUSTAINED at f0=880Hz (A5), 13 semitone bins")
    print()

    profile = pd.read_csv(CARILLON_DATA / "carillon-behavioural-profile.csv")
    profile = profile[profile["type"] == "Carillon"].dropna(subset=["pleasantness"]).copy()
    profile["bin"] = profile["pitch_interval"].round().clip(0, 12).astype(int)
    binned = profile.groupby("bin")["pleasantness"].mean().reset_index().sort_values("bin").reset_index(drop=True)
    print(f"  Binned to {len(binned)} semitone bins (0–12)")

    lower_spec = pd.read_csv(CARILLON_DATA / "lower_bell_spectrum.csv")
    upper_spec = pd.read_csv(CARILLON_DATA / "upper_bell_spectrum.csv")
    print(f"  Lower bell partials: {len(lower_spec)}, upper bell partials: {len(upper_spec)}")
    print()

    print("## Synthesising real-bell dyads + extracting STFT-mel features ...")
    features = []
    targets = []
    labels = []
    for _, row in binned.iterrows():
        s_int = int(row["bin"])
        rating = float(row["pleasantness"])
        audio, sr = synthesize_carillon_dyad(s_int, lower_spec, upper_spec)
        feat = stft_mel_features(audio, sr)
        features.append(feat)
        targets.append(rating)
        labels.append(f"s{s_int}")
    X = np.array(features)
    y = np.array(targets)
    print(f"  Shape: X={X.shape}, y={y.shape}")
    print()

    print("## Leave-one-out ridge regression ...")
    predictions, best_alphas = loo_ridge_regression(X, y)
    print(f"  Predictions: {predictions.round(3).tolist()}")
    print(f"  Targets:     {y.round(3).tolist()}")
    print()

    from scipy.stats import spearmanr, pearsonr
    rho_sp, p_sp = spearmanr(predictions, y)
    r_pearson, p_pearson = pearsonr(predictions, y)

    print(f"## Result")
    print(f"  Spearman ρ:  {rho_sp:.4f}  (p={p_sp:.4f})")
    print(f"  Pearson r:   {r_pearson:.4f}")
    print()
    print(f"## Comparison to MI Carillon")
    print(f"  MI |ρ| (stumpf_fusion vs Carillon):  0.8297")
    print(f"  Ridge LOO |ρ|:                       {abs(rho_sp):.4f}")
    print(f"  Per-dataset verdict:                 {'MI WINS' if 0.8297 > abs(rho_sp) else 'AI WINS / TIE'}")

    result = {
        "dataset": "Harrison Carillon",
        "baseline": "ridge_stft_mel",
        "n_stimuli": int(len(y)),
        "spearman_rho": float(rho_sp),
        "spearman_p": float(p_sp),
        "pearson_r": float(r_pearson),
        "predictions": predictions.tolist(),
        "targets": y.tolist(),
        "labels": labels,
        "mi_value_to_beat": 0.8297,
        "mi_advantage": 0.8297 - abs(rho_sp),
        "per_dataset_verdict": "MI_WINS" if 0.8297 > abs(rho_sp) else "AI_WINS_OR_TIE",
        "synthesis": "real-bell SUSTAINED at f0=880Hz (A5)",
        "master_seed": MASTER_SEED,
        "engine_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
    }
    output_path = OUTPUT_DIR / "baseline_ridge_carillon.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
