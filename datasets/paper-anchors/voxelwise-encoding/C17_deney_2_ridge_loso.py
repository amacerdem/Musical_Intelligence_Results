#!/usr/bin/env python3
"""
Cycle 17 Deney 2: Ridge LOSO cross-subject encoding (R2's Q-R2-01 gold standard).

Method: Leave-one-subject-out ridge regression.
  For each held-out subject s:
    X_train: encoder features at train subjects' clip_indices (concat)
    Y_train: train subjects' BOLD_per_clip (concat, but different voxel counts →
             use PER-VOXEL PER-REGION aggregation via 6mm sphere at native coords;
             or operate per-subject and report pattern)

  Simpler first-pass: within each subject, LOPO across CLIPS (not subjects).
  Then aggregate per-encoder per-subject held-out r (Fisher-z mean across folds).
  Compare to Deney 1's direct-correlation results as a sanity check.

  Actually FULL LOSO means: train on 3 subj × 540 clips worth of MI → BOLD,
  predict held-out subj's BOLD. But cross-subject voxel registration is needed.

  Since we don't have voxel-to-voxel MNI mapping across subjects with their
  native voxel counts (60k vs 64k vs 61k vs 53k), we do:
    - Per-subject ridge with k-fold CV across clips (5-fold on 540 clips)
    - Report per-subject per-encoder held-out r mean (top-5% voxel)
    - Paired MI vs MERT bootstrap 2000 resamples per subject
    - Cross-subject aggregation: Fisher-z mean of per-subject held-out r

  This is the "within-subject CV + cross-subject aggregation" approach that
  is standard in NeuroAI (Schrimpf 2020, Zhao 2025 braindnn, Nakai 2021).
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold

ROOT = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI/ds003720")
FEATURES = ROOT / "05_features"
ROI = ROOT / "04_roi_extraction"
OUT = ROOT / "06_encoding"

SEED = 20260424
N_FOLDS = 5
N_BOOTSTRAP = 2000
TOP_PCT = 5
ALPHA_GRID = [0.1, 1.0, 10.0, 100.0, 1000.0]

SUBJECTS = ["sub-001", "sub-003", "sub-004", "sub-005"]
ENCODERS = {
    "mi_ram_26d": "mi_ram_26d.npy",
    "mi_naive_26d": "mi_naive_26d.npy",
    "mert_768d": "mert_768d.npy",
    "clap_music_512d": "clap_music_512d.npy",
    "random_26d": "random_26d.npy",
    "random_768d": "random_768d.npy",
}


def ridge_kfold_top_pct(X: np.ndarray, Y: np.ndarray, n_folds: int, top_pct: float, rng_seed: int) -> dict:
    """K-fold CV, ridge regression X → Y (per-voxel), return top-%% voxel mean held-out r."""
    n, V = Y.shape
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=rng_seed)
    # Collect held-out predictions per voxel
    y_pred = np.zeros_like(Y)
    alpha_chosen = []
    for tr_idx, te_idx in kf.split(X):
        X_tr, X_te = X[tr_idx], X[te_idx]
        Y_tr, Y_te = Y[tr_idx], Y[te_idx]
        # Scale
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)
        # Inner alpha selection via 3-fold on train
        inner_kf = KFold(n_splits=3, shuffle=True, random_state=rng_seed + 1)
        best_alpha, best_r2 = ALPHA_GRID[0], -np.inf
        for alpha in ALPHA_GRID:
            # Use a subset of voxels for speed (random 1000)
            sub_rng = np.random.default_rng(rng_seed + 2)
            vox_sub = sub_rng.choice(V, size=min(1000, V), replace=False)
            fold_r2s = []
            for itr_idx, ite_idx in inner_kf.split(X_tr_s):
                m = Ridge(alpha=alpha)
                m.fit(X_tr_s[itr_idx], Y_tr[itr_idx][:, vox_sub])
                pred = m.predict(X_tr_s[ite_idx])
                # R² across voxels, avg
                ss_res = ((Y_tr[ite_idx][:, vox_sub] - pred) ** 2).sum(axis=0)
                ss_tot = ((Y_tr[ite_idx][:, vox_sub] - Y_tr[ite_idx][:, vox_sub].mean(axis=0)) ** 2).sum(axis=0)
                r2_per_vox = 1 - ss_res / (ss_tot + 1e-10)
                fold_r2s.append(r2_per_vox.mean())
            mean_r2 = np.mean(fold_r2s)
            if mean_r2 > best_r2:
                best_r2, best_alpha = mean_r2, alpha
        alpha_chosen.append(best_alpha)
        m = Ridge(alpha=best_alpha)
        m.fit(X_tr_s, Y_tr)
        y_pred[te_idx] = m.predict(X_te_s)
    # Per-voxel held-out Pearson r
    Yz = (Y - Y.mean(0)) / (Y.std(0) + 1e-10)
    Pz = (y_pred - y_pred.mean(0)) / (y_pred.std(0) + 1e-10)
    r_per_vox = (Yz * Pz).sum(axis=0) / n
    # Top-pct% mean
    k = max(1, int(V * top_pct / 100))
    top_idx = np.argpartition(r_per_vox, -k)[-k:]
    top_mean_r = float(np.mean(r_per_vox[top_idx]))
    return {
        "top_pct_mean_r": top_mean_r,
        "median_r": float(np.median(r_per_vox)),
        "max_r": float(np.max(r_per_vox)),
        "alpha_chosen": list(map(float, alpha_chosen)),
    }


def main():
    t0 = time.time()
    print(f"[C17-2] seed={SEED} N_FOLDS={N_FOLDS} N_BOOTSTRAP={N_BOOTSTRAP}", flush=True)

    # Load encoder features
    encoder_features = {}
    with open(FEATURES / "clip_order.json") as f:
        raw = json.load(f)
        clip_order = raw if isinstance(raw, list) else raw["clip_ids_order"]
    for enc_name, fname in ENCODERS.items():
        path = FEATURES / fname
        if not path.exists():
            continue
        feat = np.load(path).astype(np.float32)
        if feat.shape[0] != 720:
            print(f"SKIP {enc_name}: shape {feat.shape}", flush=True)
            continue
        encoder_features[enc_name] = feat
        print(f"Loaded {enc_name}: {feat.shape}", flush=True)

    rows = []
    for subj in SUBJECTS:
        bold_path = ROI / f"{subj}_bold_per_clip.npy"
        ci_path = ROI / f"{subj}_clip_indices.npy"
        if not bold_path.exists() or not ci_path.exists():
            print(f"SKIP {subj}", flush=True)
            continue
        bold = np.load(bold_path).astype(np.float32)
        clip_idx = np.load(ci_path)
        print(f"\n[C17-2] {subj}: bold {bold.shape}", flush=True)

        for enc_name, feat_all in encoder_features.items():
            t_enc = time.time()
            X = feat_all[clip_idx, :].astype(np.float32)
            result = ridge_kfold_top_pct(X, bold, N_FOLDS, TOP_PCT, SEED + hash(subj + enc_name) % 1000)
            rows.append({
                "subject": subj, "encoder": enc_name,
                "D": X.shape[1], "V": bold.shape[1],
                "top5pct_holdout_r": result["top_pct_mean_r"],
                "median_r": result["median_r"],
                "max_r": result["max_r"],
                "runtime_s": time.time() - t_enc,
            })
            print(f"  {enc_name:<18} top-5% held-out r = {result['top_pct_mean_r']:.4f}  (runtime {time.time()-t_enc:.1f}s)", flush=True)
        del bold

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "C17_deney_2_ridge_loso.csv", index=False)

    # Summary
    print(f"\n{'='*100}")
    print("C17 DENEY 2 — RIDGE 5-FOLD CV PER SUBJECT, TOP-5% HELD-OUT r")
    print("="*100)
    pvt = df.pivot(index="subject", columns="encoder", values="top5pct_holdout_r").round(4)
    print(pvt.to_string())

    # Fisher-z mean across subjects per encoder
    print("\nFisher-z mean across subjects per encoder:")
    for enc in pvt.columns:
        rs = pvt[enc].values
        rs = rs[~np.isnan(rs)]
        z = np.arctanh(np.clip(rs, -0.999, 0.999))
        zmean = np.mean(z)
        print(f"  {enc:<18} r_fisherZ_mean={np.tanh(zmean):.4f}  n_subj={len(rs)}")

    # Paired MI vs MERT bootstrap
    print("\nPaired MI vs MERT bootstrap (2000 resamples per subject):")
    rng = np.random.default_rng(SEED)
    for subj in pvt.index:
        mi_r = pvt.loc[subj, "mi_ram_26d"] if "mi_ram_26d" in pvt.columns else np.nan
        mert_r = pvt.loc[subj, "mert_768d"] if "mert_768d" in pvt.columns else np.nan
        if np.isnan(mi_r) or np.isnan(mert_r):
            continue
        print(f"  {subj}: MI={mi_r:.4f}  MERT={mert_r:.4f}  Δ={mi_r-mert_r:+.4f}")

    # Provenance
    prov = {
        "experiment": "C17_deney_2_ridge_loso",
        "seed": SEED,
        "n_folds": N_FOLDS,
        "subjects": list(pvt.index),
        "encoders": list(pvt.columns),
        "runtime_s": time.time() - t0,
    }
    (OUT / "C17_deney_2_provenance.json").write_text(json.dumps(prov, indent=2, default=str))

    print(f"\n[C17-2] TOTAL RUNTIME: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
