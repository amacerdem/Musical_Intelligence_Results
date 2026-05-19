"""Phase 06.3 — Baseline 1 on Marjieh 2024 (5-equal-partial timbre, 13 binned intervals).

Synthesise 5-equal-partial dyads per binned semitone, then Ridge LOO-CV
on raw STFT-mel features. Same constraints as the other Phase 06.3 baselines.

5-equal partial spec: f0 · 2^(k/5) for k=0,1,2,3,4 (stretched non-harmonic).
Dyad: lower tone at C4 (f0=261.63Hz), upper tone at f0 · 2^(s/12) for s ∈ {0,...,12}.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _baseline_common import stft_mel_features, loo_ridge_regression, OUTPUT_DIR, MASTER_SEED

REPO_ROOT = Path(__file__).resolve().parents[3]
MARJIEH_PER_BIN = REPO_ROOT / "01-R3-PERCEPTUAL-FRONT-END/01.2-r3-oos-consonance/results/marjieh_r3.csv"

np.random.seed(MASTER_SEED)


def synthesize_5equal_dyad(s_int, f0_lower=261.63, sr=22050, duration=1.0):
    """Synthesize a 5-equal-partial dyad at given semitone interval."""
    n_samples = int(duration * sr)
    t = np.arange(n_samples) / sr

    # 5 partials per timbre: f · 2^(k/5)
    partial_ratios = np.array([2 ** (k / 5) for k in range(5)])
    partial_amplitudes = np.array([1.0, 0.7, 0.5, 0.35, 0.25])  # generic decreasing envelope

    f0_upper = f0_lower * (2 ** (s_int / 12))

    audio = np.zeros(n_samples)
    for f0 in (f0_lower, f0_upper):
        for ratio, amp in zip(partial_ratios, partial_amplitudes):
            freq = f0 * ratio
            if freq < sr / 2:
                audio += amp * np.sin(2 * np.pi * freq * t)

    # Normalise
    audio = audio / np.max(np.abs(audio) + 1e-9) * 0.8

    # Apply 50ms attack/release envelope
    fade_n = int(0.05 * sr)
    envelope = np.ones(n_samples)
    envelope[:fade_n] = np.linspace(0, 1, fade_n)
    envelope[-fade_n:] = np.linspace(1, 0, fade_n)
    audio = audio * envelope

    return audio, sr


def main():
    print("# Phase 06.3 — Baseline 1 (Ridge on STFT-mel) — Marjieh 2024")
    print(f"Master seed: {MASTER_SEED}")
    print(f"Synthesis: 5-equal-partial dyad at f0=261.63Hz")
    print()

    # Load per-bin canonical ratings
    df = pd.read_csv(MARJIEH_PER_BIN)
    print(f"  Loaded {len(df)} binned intervals from {MARJIEH_PER_BIN.name}")
    print()

    # Synthesize + extract features for each bin
    print("## Synthesising 5-equal-partial dyads + extracting STFT-mel features ...")
    features = []
    targets = []
    labels = []
    for _, row in df.iterrows():
        s_int = int(row["s_int"])
        rating = float(row["mean"])
        audio, sr = synthesize_5equal_dyad(s_int)
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
    print(f"## Comparison to MI Marjieh")
    print(f"  MI |ρ| (roughness vs Marjieh):     0.7363")
    print(f"  Ridge LOO |ρ|:                     {abs(rho_sp):.4f}")
    print(f"  Per-dataset verdict:               {'MI WINS' if 0.7363 > abs(rho_sp) else 'AI WINS / TIE'}")

    result = {
        "dataset": "Marjieh 2024",
        "baseline": "ridge_stft_mel",
        "n_stimuli": int(len(y)),
        "spearman_rho": float(rho_sp),
        "spearman_p": float(p_sp),
        "pearson_r": float(r_pearson),
        "predictions": predictions.tolist(),
        "targets": y.tolist(),
        "labels": labels,
        "mi_value_to_beat": 0.7363,
        "mi_advantage": 0.7363 - abs(rho_sp),
        "per_dataset_verdict": "MI_WINS" if 0.7363 > abs(rho_sp) else "AI_WINS_OR_TIE",
        "synthesis": "5-equal-partial dyad at f0=261.63Hz",
        "master_seed": MASTER_SEED,
        "engine_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
    }
    output_path = OUTPUT_DIR / "baseline_ridge_marjieh.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
