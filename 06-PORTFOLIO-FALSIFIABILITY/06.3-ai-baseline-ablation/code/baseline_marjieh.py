"""Phase 06.3 — Baseline 1 on Marjieh 2024 (harmonic complex tones, 13 binned intervals).

Synthesise HARMONIC dyads per binned semitone (matching the rating data and MI's
own R3 feature computation), then Ridge LOO-CV on raw STFT-mel features. Same
constraints as the other Phase 06.3 baselines (no psychoacoustic priors).

Timbre note (2026-05-27 correction): the rating data is `rating_dyh3dd.csv`
(Marjieh 2024 Study 1A — dyadic consonance for HARMONIC complex tones, N=7,500),
and MI's R3 features on this set use the V1-default 6-partial 1/n harmonic
synthesis (see Phase 01.2 run_phase6.py). The earlier version of this baseline
synthesised a 5-equal-partial *stretched* timbre — following the paper text's
documented timbre mislabel (Divan-Final §3.1 L330) — which is the wrong timbre
for this rating set. It is corrected here to harmonic 6-partial 1/n.

Harmonic spec: partials at f0·n for n=1..6, amplitude 1/n. Dyad: lower tone at
C4 (f0=261.63 Hz), upper tone at f0·2^(s/12) for s ∈ {0,...,12}.
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

N_HARM = 6  # V1-default harmonic partial count (matches MI's R3 synthesis for Marjieh)


def synthesize_harmonic_dyad(s_int, f0_lower=261.63, sr=22050, duration=1.0, n_harm=N_HARM):
    """Synthesize a harmonic (6-partial, 1/n decay) dyad at given semitone interval.

    Matches the rating_dyh3dd Study 1A harmonic-complex-tone timbre and MI's
    own V1-default 6-partial 1/n synthesis.
    """
    n_samples = int(duration * sr)
    t = np.arange(n_samples) / sr

    f0_upper = f0_lower * (2 ** (s_int / 12))

    audio = np.zeros(n_samples)
    for f0 in (f0_lower, f0_upper):
        for n in range(1, n_harm + 1):          # harmonic partials f0·n
            freq = f0 * n
            if freq < sr / 2:
                audio += (1.0 / n) * np.sin(2 * np.pi * freq * t)   # 1/n amplitude decay

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
    print(f"Synthesis: harmonic {N_HARM}-partial 1/n dyad at f0=261.63Hz")
    print()

    # Load per-bin canonical ratings + MI R3 channels
    df = pd.read_csv(MARJIEH_PER_BIN)
    print(f"  Loaded {len(df)} binned intervals from {MARJIEH_PER_BIN.name}")
    print()

    # MI value to beat: roughness channel signed ρ vs the per-bin mean ratings,
    # computed live from the same CSV (no hardcoded/stale constant). This is MI's
    # primary consonance channel on this set; reported alongside |ρ|.
    from scipy.stats import spearmanr, pearsonr
    mi_rho_rough, _ = spearmanr(df["r3_roughness"], df["mean"])
    mi_rho_stumpf, _ = spearmanr(df["r3_stumpf_fusion"], df["mean"])
    mi_abs = abs(mi_rho_rough)

    # Synthesize + extract features for each bin
    print(f"## Synthesising harmonic {N_HARM}-partial 1/n dyads + extracting STFT-mel features ...")
    features = []
    targets = []
    labels = []
    for _, row in df.iterrows():
        s_int = int(row["s_int"])
        rating = float(row["mean"])
        audio, sr = synthesize_harmonic_dyad(s_int)
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

    rho_sp, p_sp = spearmanr(predictions, y)
    r_pearson, p_pearson = pearsonr(predictions, y)

    # Verdict: MI WINS if MI's consonance channel achieves higher |ρ| than the
    # from-scratch baseline. We also flag the baseline's SIGN: a negative ρ means
    # the baseline anti-predicts (orders intervals opposite to consonance), i.e.
    # it has not learned consonance at all — strengthening the MI-WINS conclusion.
    baseline_anti_predictive = rho_sp < 0
    mi_wins = mi_abs > abs(rho_sp)

    print(f"## Result")
    print(f"  Baseline Spearman ρ:  {rho_sp:+.4f}  (p={p_sp:.4f}) | |ρ| = {abs(rho_sp):.4f}")
    print(f"  Baseline Pearson r:   {r_pearson:+.4f}")
    print(f"  Anti-predictive (ρ<0): {baseline_anti_predictive}")
    print()
    print(f"## Comparison to MI Marjieh (computed live on the same ratings)")
    print(f"  MI roughness ρ:        {mi_rho_rough:+.4f}  (|ρ| = {mi_abs:.4f})")
    print(f"  MI stumpf_fusion ρ:    {mi_rho_stumpf:+.4f}")
    print(f"  Baseline |ρ|:          {abs(rho_sp):.4f}")
    print(f"  Per-dataset verdict:   {'MI_WINS' if mi_wins else 'AI_WINS_OR_TIE'}"
          + ("  (baseline anti-predicts consonance)" if baseline_anti_predictive else ""))

    result = {
        "dataset": "Marjieh 2024",
        "baseline": "ridge_stft_mel",
        "timbre": "harmonic 6-partial 1/n (Study 1A; corrected from 5-equal 2026-05-27)",
        "n_stimuli": int(len(y)),
        "spearman_rho": float(rho_sp),
        "spearman_p": float(p_sp),
        "pearson_r": float(r_pearson),
        "baseline_abs_rho": float(abs(rho_sp)),
        "baseline_anti_predictive": bool(baseline_anti_predictive),
        "predictions": predictions.tolist(),
        "targets": y.tolist(),
        "labels": labels,
        "mi_channel": "roughness",
        "mi_rho_roughness": float(mi_rho_rough),
        "mi_rho_stumpf_fusion": float(mi_rho_stumpf),
        "mi_value_to_beat": float(mi_abs),
        "mi_advantage": float(mi_abs - abs(rho_sp)),
        "per_dataset_verdict": "MI_WINS" if mi_wins else "AI_WINS_OR_TIE",
        "synthesis": "harmonic 6-partial 1/n dyad at f0=261.63Hz",
        "master_seed": MASTER_SEED,
        "engine_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "note": ("Timbre corrected 2026-05-27 from 5-equal-partial (paper-text "
                 "mislabel, Divan-Final §3.1 L330) to harmonic 6-partial 1/n, "
                 "matching rating_dyh3dd Study 1A and MI's R3 synthesis. MI value "
                 "computed live from marjieh_r3.csv (was stale hardcoded 0.7363). "
                 "The from-scratch ridge anti-predicts consonance (ρ<0) on the "
                 "correct ratings; MI's roughness channel orders it at |ρ|=0.835."),
    }
    output_path = OUTPUT_DIR / "baseline_ridge_marjieh.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
