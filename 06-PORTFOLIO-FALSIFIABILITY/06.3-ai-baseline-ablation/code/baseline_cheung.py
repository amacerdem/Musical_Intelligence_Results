"""Phase 06.3 — Baseline on Cheung 2019 emergent reward (1,009 chord-level rows, leave-songs-out CV).

Cheung 2019 audio was never released — same-data baseline restricted to features
shipped in the OSF CSV. MI's r=+0.615 is the held-out Pearson r between MI Eq.5
reward and chord-level mean pleasantness rating under 5-fold leave-songs-out CV.

Baseline panel:
  B1 strict   : ridge on (IC_z, ENTROPY_z, IC_z*ENTROPY_z, IC_z**2, ENTROPY_z**2)
                — IDyOM features only, no psychoacoustic priors, no controls
  B2 lenient  : ridge on B1 + (spectralcentroid_z, spectralcomplexity_z)
                — generic spectral descriptors (no Leman6 / dissonance — those
                are literature-derived psychoacoustic; pre-reg excluded)

Both baselines violate the strict "no external priors" rule because IC/ENTROPY are
themselves IDyOM predictions trained on an external corpus. The same caveat applies
to MI Eq.5 (which uses the same IC/ENTROPY as inputs), so the like-for-like
comparison preserves the dataset-paucity asymmetry honestly.

Protocol: 5-fold leave-songs-out CV on chord-level aggregate. Pearson r between
held-out predictions and held-out rating_z, pooled across folds.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _baseline_common import OUTPUT_DIR, MASTER_SEED

REPO_ROOT = Path(__file__).resolve().parents[3]
# Cheung 2024 raw data (data_pleasure_2023.csv) is gitignored. Either place it
# at MI_Results/datasets/reward/cheung2024/, or set CHEUNG_2024_CSV to point
# at your local copy.
CHEUNG_CSV = Path(os.environ.get(
    "CHEUNG_2024_CSV",
    REPO_ROOT / "datasets/reward/cheung2024/data_pleasure_2023.csv",
))

np.random.seed(MASTER_SEED)


def zscore(x):
    return (x - np.mean(x)) / np.std(x, ddof=1)


def aggregate_chord_level(df):
    df = df.dropna(subset=["IC", "ENTROPY", "rating", "spectralcentroid",
                            "spectralcomplexity"]).copy()
    agg = (df.groupby(["song", "chordnumber"], as_index=False)
             .agg({"IC": "mean", "ENTROPY": "mean", "rating": "mean",
                   "spectralcentroid": "mean", "spectralcomplexity": "mean"}))
    for col in ("IC", "ENTROPY", "rating", "spectralcentroid", "spectralcomplexity"):
        agg[col + "_z"] = zscore(agg[col])
    return agg


def loso_ridge(X, y, song_ids, alphas=None):
    """5-fold leave-songs-out CV ridge (RidgeCV inside)."""
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    if alphas is None:
        alphas = np.logspace(-3, 3, 13)
    rng = np.random.default_rng(MASTER_SEED)
    unique_songs = np.array(sorted(set(song_ids)))
    rng.shuffle(unique_songs)
    folds = np.array_split(unique_songs, 5)

    predictions = np.full(len(y), np.nan)
    for fold_songs in folds:
        test_mask = np.isin(song_ids, fold_songs)
        train_mask = ~test_mask
        model = RidgeCV(alphas=alphas, cv=5)
        model.fit(X[train_mask], y[train_mask])
        predictions[test_mask] = model.predict(X[test_mask])
    return predictions


def main():
    print("# Phase 06.3 — Baseline on Cheung 2019 (1,009 chord-level rows)")
    print(f"Master seed: {MASTER_SEED}")
    print()

    df = pd.read_csv(CHEUNG_CSV)
    agg = aggregate_chord_level(df)
    print(f"  Chord-level rows: {len(agg)}")
    print(f"  Unique songs:     {agg['song'].nunique()}")
    print()

    song_ids = agg["song"].to_numpy()
    y = agg["rating_z"].to_numpy()
    ic = agg["IC_z"].to_numpy()
    ent = agg["ENTROPY_z"].to_numpy()

    # B1 strict: IDyOM features only
    X_strict = np.column_stack([ic, ent, ic * ent, ic ** 2, ent ** 2])
    pred_strict = loso_ridge(X_strict, y, song_ids)
    from scipy.stats import pearsonr, spearmanr
    r_strict, p_strict = pearsonr(pred_strict, y)
    rho_strict, _ = spearmanr(pred_strict, y)
    print("## B1 strict (IDyOM features only) — 5-fold leave-songs-out ridge")
    print(f"  Pearson r:  {r_strict:+.4f}  (p={p_strict:.3g})")
    print(f"  Spearman ρ: {rho_strict:+.4f}")

    # B2 lenient: + generic spectral
    sc = agg["spectralcentroid_z"].to_numpy()
    sx = agg["spectralcomplexity_z"].to_numpy()
    X_lenient = np.column_stack([ic, ent, ic * ent, ic ** 2, ent ** 2, sc, sx])
    pred_lenient = loso_ridge(X_lenient, y, song_ids)
    r_lenient, p_lenient = pearsonr(pred_lenient, y)
    rho_lenient, _ = spearmanr(pred_lenient, y)
    print()
    print("## B2 lenient (IDyOM + generic spectral) — 5-fold leave-songs-out ridge")
    print(f"  Pearson r:  {r_lenient:+.4f}  (p={p_lenient:.3g})")
    print(f"  Spearman ρ: {rho_lenient:+.4f}")
    print()

    mi_r = 0.615
    print("## Comparison to MI Cheung")
    print(f"  MI held-out r (Eq.5 vs rating):       {mi_r:+.4f}")
    print(f"  Baseline B1 strict r:                 {r_strict:+.4f}")
    print(f"  Baseline B2 lenient r:                {r_lenient:+.4f}")
    best_baseline_r = max(abs(r_strict), abs(r_lenient))
    verdict = "MI_WINS" if mi_r > best_baseline_r else "AI_WINS_OR_TIE"
    print(f"  Best baseline |r|:                    {best_baseline_r:+.4f}")
    print(f"  Per-dataset verdict:                  {verdict}")

    result = {
        "dataset": "Cheung 2019",
        "baseline_panel": ["ridge_idyom_only", "ridge_idyom_plus_generic_spectral"],
        "protocol": "5-fold leave-songs-out CV, chord-level aggregation",
        "n_chord_rows": int(len(agg)),
        "n_songs": int(agg["song"].nunique()),
        "B1_strict_r": float(r_strict), "B1_strict_rho": float(rho_strict),
        "B2_lenient_r": float(r_lenient), "B2_lenient_rho": float(rho_lenient),
        "mi_value_to_beat": mi_r,
        "best_baseline_r": float(best_baseline_r),
        "mi_advantage": mi_r - best_baseline_r,
        "per_dataset_verdict": verdict,
        "caveat": ("IC/ENTROPY are IDyOM predictions trained on external corpus; "
                   "both MI Eq.5 and the AI baselines depend on them. The strict "
                   "no-external-priors rule cannot be satisfied for Cheung since "
                   "the dataset ships no raw audio."),
        "master_seed": MASTER_SEED,
        "engine_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
    }
    output_path = OUTPUT_DIR / "baseline_ridge_cheung.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
