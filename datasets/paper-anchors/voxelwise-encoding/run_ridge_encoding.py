#!/usr/bin/env python3
"""
run_ridge_encoding.py — first-pass MI → BOLD voxel-level ridge encoding.

Design
------
For each (subject, encoder):
  - Load per-clip feature X[720, D] (or X[540, D] filtered).
  - Load per-clip BOLD Y[540, n_vox] for that subject.
  - Match via clip_indices.npy → X_sub = X[clip_indices], Y_sub = Y.
  - 5-fold CV across CLIPS (seed 20260424), per-voxel ridge(alpha=100).
  - Predict held-out fold → concatenate → per-voxel Pearson r of (pred vs. true).
  - Aggregate: top-5% voxels' mean r per (subject, encoder).

Encoders: mi_ram_26d, mi_naive_26d, mert_768d, random_26d, random_768d.

Outputs (ds003720/06_encoding/)
-------------------------------
  results_voxel_top5pct.csv
  results_per_voxel_r.npz (sub × encoder → per-voxel r array)
  meta.json
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

SEED = 20260424
BASE = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI")
DS = BASE / "ds003720"
FEAT = DS / "05_features"
ROI = DS / "04_roi_extraction"
OUT = DS / "06_encoding"
OUT.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["sub-001", "sub-003", "sub-004"]
ENCODERS = [
    ("mi_ram_26d",  FEAT / "mi_ram_26d.npy"),
    ("mi_naive_26d", FEAT / "mi_naive_26d.npy"),
    ("mert_768d",    FEAT / "mert_768d.npy"),
    ("random_26d",   FEAT / "random_26d.npy"),
    ("random_768d",  FEAT / "random_768d.npy"),
]
ALPHA = 100.0
N_FOLDS = 5
TOP_FRAC = 0.05


def pearson_per_col(pred: np.ndarray, true: np.ndarray) -> np.ndarray:
    """Per-column Pearson r for two (n, k) arrays."""
    pred = pred - pred.mean(axis=0, keepdims=True)
    true = true - true.mean(axis=0, keepdims=True)
    num = (pred * true).sum(axis=0)
    denom = np.sqrt((pred ** 2).sum(axis=0) * (true ** 2).sum(axis=0))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(denom > 1e-12, num / denom, 0.0)
    return r


def ridge_cv_voxelwise(X: np.ndarray, Y: np.ndarray, alpha: float, n_folds: int, seed: int):
    """5-fold CV, per-voxel ridge, returns per-voxel Pearson r on concatenated held-out preds."""
    n = X.shape[0]
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    pred_all = np.zeros_like(Y, dtype=np.float32)
    true_all = np.zeros_like(Y, dtype=np.float32)
    for fold_idx, (tr, te) in enumerate(kf.split(X)):
        model = Ridge(alpha=alpha, solver="auto")
        # Z-score features per fold (fit on train)
        mu = X[tr].mean(axis=0)
        sd = X[tr].std(axis=0) + 1e-8
        Xtr = (X[tr] - mu) / sd
        Xte = (X[te] - mu) / sd
        # Z-score BOLD per fold (fit on train)
        ymu = Y[tr].mean(axis=0)
        ysd = Y[tr].std(axis=0) + 1e-8
        Ytr = (Y[tr] - ymu) / ysd
        model.fit(Xtr, Ytr)
        pred = model.predict(Xte)
        pred_all[te] = pred
        true_all[te] = (Y[te] - ymu) / ysd
    return pearson_per_col(pred_all, true_all)


def main():
    t0 = time.time()
    clip_order = json.loads((FEAT / "clip_order.json").read_text())
    assert len(clip_order) == 720

    # Preload features once
    feats = {name: np.load(path).astype(np.float32) for name, path in ENCODERS}
    for k, v in feats.items():
        print(f"[feat] {k}: {v.shape}")
    assert all(v.shape[0] == 720 for v in feats.values())

    rows = []
    per_voxel_r = {}  # keys = f"{subj}__{enc}"

    for subj in SUBJECTS:
        print(f"\n[subj] {subj}", flush=True)
        bold = np.load(ROI / f"{subj}_bold_per_clip.npy").astype(np.float32)
        idxs = np.load(ROI / f"{subj}_clip_indices.npy")
        n_clips, n_vox = bold.shape
        print(f"  BOLD: {bold.shape}  clip_indices: {idxs.shape}  n_vox={n_vox}")

        for enc_name, _ in ENCODERS:
            ts = time.time()
            X = feats[enc_name][idxs]  # (n_clips, D)
            assert X.shape[0] == n_clips
            print(f"  [{enc_name}] X={X.shape}  ridge…", flush=True)
            r = ridge_cv_voxelwise(X, bold, alpha=ALPHA, n_folds=N_FOLDS, seed=SEED)
            r = r.astype(np.float32)
            per_voxel_r[f"{subj}__{enc_name}"] = r
            # Top-5%
            k_top = max(1, int(round(TOP_FRAC * n_vox)))
            top_idx = np.argpartition(r, -k_top)[-k_top:]
            top_mean = float(r[top_idx].mean())
            median_r = float(np.median(r))
            max_r = float(r.max())
            dt = time.time() - ts
            print(f"    top5%_mean_r={top_mean:+.4f}  median_r={median_r:+.4f}  max_r={max_r:+.4f}  ({dt:.1f}s)")
            rows.append({
                "subject": subj,
                "encoder": enc_name,
                "D": int(X.shape[1]),
                "n_clips": int(n_clips),
                "n_voxels": int(n_vox),
                "top5pct_mean_r": top_mean,
                "median_r": median_r,
                "max_r": max_r,
                "runtime_s": round(dt, 2),
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "results_voxel_top5pct.csv", index=False)
    np.savez_compressed(OUT / "results_per_voxel_r.npz", **per_voxel_r)

    meta = {
        "seed": SEED,
        "alpha": ALPHA,
        "n_folds": N_FOLDS,
        "top_frac": TOP_FRAC,
        "subjects": SUBJECTS,
        "encoders": [n for n, _ in ENCODERS],
        "runtime_total_s": round(time.time() - t0, 1),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\n[done] total {time.time()-t0:.1f}s. saved results_voxel_top5pct.csv + results_per_voxel_r.npz")

    print("\n=== SUMMARY ===")
    print(df.pivot(index="subject", columns="encoder", values="top5pct_mean_r").round(4))


if __name__ == "__main__":
    main()
