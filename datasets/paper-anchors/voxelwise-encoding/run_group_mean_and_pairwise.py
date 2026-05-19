#!/usr/bin/env python3
"""
run_group_mean_and_pairwise.py — group-mean dual-scale test + MI-vs-MERT bootstrap.

Uses the per-voxel r arrays saved by run_ridge_encoding.py. Because voxel grids
differ across subjects (native space), we can't average per-voxel r. Instead:

  * **Dual-scale test (feature-level)**: rank-correlate each subject's clip-wise
    feature with the group-mean clip-wise feature — NOT applicable since features
    are identical across subjects. What IS comparable:
        For each subject, compute per-clip mean BOLD over top-5% voxels.
        Rank-correlate this "subject top-5% composite BOLD" across subjects.
        Then correlate MI-predicted composite with (a) each subject individually,
        (b) the cross-subject-averaged composite.
    First-pass output: Pearson r(MI prediction, mean-top5%-BOLD) per subject
    + the cross-subject correlation of those per-clip top-5% composites.

  * **MI vs MERT pairwise bootstrap**: 2000 bootstrap samples of voxels,
    per-subject, computing (top5%_MI_r − top5%_MERT_r). Report mean + 95% CI.

Outputs: results_pairwise_mi_vs_mert.csv, results_dual_scale.csv
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
BASE = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI")
DS = BASE / "ds003720"
FEAT = DS / "05_features"
ROI = DS / "04_roi_extraction"
OUT = DS / "06_encoding"

SUBJECTS = ["sub-001", "sub-003", "sub-004"]
ALPHA = 100.0
N_FOLDS = 5
TOP_FRAC = 0.05
N_BOOT = 2000


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a*a).sum() * (b*b).sum())
    return float((a*b).sum() / d) if d > 1e-12 else 0.0


def pearson_per_col(pred, true):
    pred = pred - pred.mean(axis=0, keepdims=True)
    true = true - true.mean(axis=0, keepdims=True)
    num = (pred * true).sum(axis=0)
    denom = np.sqrt((pred**2).sum(axis=0) * (true**2).sum(axis=0))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(denom > 1e-12, num/denom, 0.0)
    return r


def ridge_cv_predictions(X, Y, alpha, n_folds, seed):
    """Return held-out predictions (n, n_vox) aligned to Y. Y must be 2D."""
    Y = np.atleast_2d(Y)
    if Y.shape[0] == 1:
        Y = Y.T
    n = X.shape[0]
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    pred_all = np.zeros_like(Y, dtype=np.float32)
    true_all = np.zeros_like(Y, dtype=np.float32)
    for tr, te in kf.split(X):
        mu, sd = X[tr].mean(axis=0), X[tr].std(axis=0) + 1e-8
        Xtr = (X[tr] - mu) / sd
        Xte = (X[te] - mu) / sd
        ymu, ysd = Y[tr].mean(axis=0), Y[tr].std(axis=0) + 1e-8
        Ytr = (Y[tr] - ymu) / ysd
        m = Ridge(alpha=alpha, solver="auto").fit(Xtr, Ytr)
        pred = m.predict(Xte)
        if pred.ndim == 1:
            pred = pred.reshape(-1, 1)
        pred_all[te] = pred
        tr_true = (Y[te] - ymu) / ysd
        if tr_true.ndim == 1:
            tr_true = tr_true.reshape(-1, 1)
        true_all[te] = tr_true
    return pred_all, true_all


def main():
    t0 = time.time()
    data = np.load(OUT / "results_per_voxel_r.npz")
    keys = list(data.keys())

    # Pairwise MI vs MERT bootstrap per subject
    rng = np.random.default_rng(SEED)
    pair_rows = []
    for subj in SUBJECTS:
        r_mi = data[f"{subj}__mi_ram_26d"]
        r_mert = data[f"{subj}__mert_768d"]
        n_vox = r_mi.shape[0]
        k_top = max(1, int(round(TOP_FRAC * n_vox)))
        diffs = []
        for b in range(N_BOOT):
            samp = rng.integers(0, n_vox, size=n_vox)
            ri = r_mi[samp]
            rm = r_mert[samp]
            top_i = np.argpartition(ri, -k_top)[-k_top:]
            top_m = np.argpartition(rm, -k_top)[-k_top:]
            diffs.append(float(ri[top_i].mean() - rm[top_m].mean()))
        diffs = np.array(diffs)
        ci_lo, ci_hi = np.percentile(diffs, [2.5, 97.5])
        observed = float(r_mi[np.argpartition(r_mi, -k_top)[-k_top:]].mean()
                         - r_mert[np.argpartition(r_mert, -k_top)[-k_top:]].mean())
        pair_rows.append({
            "subject": subj,
            "observed_mi_minus_mert_top5pct": round(observed, 4),
            "bootstrap_mean": round(float(diffs.mean()), 4),
            "bootstrap_ci95_lo": round(float(ci_lo), 4),
            "bootstrap_ci95_hi": round(float(ci_hi), 4),
            "n_boot": N_BOOT,
            "sig_95": bool(ci_lo > 0 or ci_hi < 0),
        })
    pd.DataFrame(pair_rows).to_csv(OUT / "results_pairwise_mi_vs_mert.csv", index=False)
    print("[pair] MI vs MERT bootstrap:")
    print(pd.DataFrame(pair_rows).to_string(index=False))

    # Dual-scale test: top5% composite BOLD per clip per subject
    # Then (a) cross-subject rank correlation (shared signal?), (b) MI-prediction → composite r
    print("\n[dual] building top-5% composite BOLD per subject…")
    composites = {}
    mi_full = np.load(FEAT / "mi_ram_26d.npy").astype(np.float32)
    for subj in SUBJECTS:
        bold = np.load(ROI / f"{subj}_bold_per_clip.npy").astype(np.float32)
        idxs = np.load(ROI / f"{subj}_clip_indices.npy")
        # Use MI r map to identify top voxels
        r_mi = data[f"{subj}__mi_ram_26d"]
        k_top = max(1, int(round(TOP_FRAC * r_mi.shape[0])))
        top_voxels = np.argpartition(r_mi, -k_top)[-k_top:]
        # Per-clip composite: mean BOLD over top voxels
        comp = bold[:, top_voxels].mean(axis=1)  # (n_clips,)
        composites[subj] = {"indices": idxs, "composite": comp}

    # Cross-subject pairwise r of composites (on shared clip indices)
    pairs = [(a, b) for i, a in enumerate(SUBJECTS) for b in SUBJECTS[i+1:]]
    cross = []
    for a, b in pairs:
        ia = set(composites[a]["indices"].tolist())
        ib = set(composites[b]["indices"].tolist())
        shared = sorted(ia & ib)
        ia_idx = np.array([np.where(composites[a]["indices"] == k)[0][0] for k in shared])
        ib_idx = np.array([np.where(composites[b]["indices"] == k)[0][0] for k in shared])
        ca = composites[a]["composite"][ia_idx]
        cb = composites[b]["composite"][ib_idx]
        cross.append({"pair": f"{a}↔{b}", "n_shared_clips": len(shared), "pearson_r": round(pearson(ca, cb), 4)})
    print("\n[dual] cross-subject composite r:")
    for c in cross: print(" ", c)

    # Group-mean composite (average across subjects on intersect clips)
    shared = sorted(set.intersection(*[set(composites[s]["indices"].tolist()) for s in SUBJECTS]))
    print(f"\n[dual] shared clips across 3 subjects: {len(shared)}")
    group_comp = np.zeros(len(shared))
    for subj in SUBJECTS:
        m = {k: v for k, v in zip(composites[subj]["indices"], composites[subj]["composite"])}
        for i, k in enumerate(shared):
            group_comp[i] += m[k] / len(SUBJECTS)

    # MI → group composite CV prediction: ridge X=MI features at shared_clips, Y=group_comp
    Xg = mi_full[np.array(shared)]
    Xg_std = (Xg - Xg.mean(0)) / (Xg.std(0) + 1e-8)
    group_comp_std = (group_comp - group_comp.mean()) / (group_comp.std() + 1e-8)
    pred_g, true_g = ridge_cv_predictions(Xg_std, group_comp_std[:, None].astype(np.float32),
                                           alpha=ALPHA, n_folds=N_FOLDS, seed=SEED)
    r_group = pearson(pred_g[:, 0], true_g[:, 0])
    # Individual MI → composite r (mean across subjects)
    r_individual = []
    for subj in SUBJECTS:
        idxs = composites[subj]["indices"]
        comp = composites[subj]["composite"]
        X = mi_full[idxs]
        X_std = (X - X.mean(0)) / (X.std(0) + 1e-8)
        comp_std = (comp - comp.mean()) / (comp.std() + 1e-8)
        pred, true = ridge_cv_predictions(X_std, comp_std[:, None].astype(np.float32),
                                           alpha=ALPHA, n_folds=N_FOLDS, seed=SEED)
        r_individual.append({"subject": subj, "r_mi_vs_composite": round(pearson(pred[:, 0], true[:, 0]), 4)})

    r_ind_mean = float(np.mean([x["r_mi_vs_composite"] for x in r_individual]))
    dual_summary = {
        "group_mean_r_mi_vs_group_composite": round(r_group, 4),
        "individual_mean_r_mi_vs_composite": round(r_ind_mean, 4),
        "group_greater_than_individual": r_group > r_ind_mean,
        "per_subject": r_individual,
        "cross_subject_composite_r": cross,
        "n_shared_clips": len(shared),
    }
    (OUT / "results_dual_scale.json").write_text(json.dumps(dual_summary, indent=2))
    # Also dump individual per-subject rows as CSV
    pd.DataFrame(r_individual + [{"subject": "GROUP_MEAN", "r_mi_vs_composite": round(r_group, 4)}]
                 ).to_csv(OUT / "results_dual_scale.csv", index=False)
    print("\n[dual] individual mean r:", round(r_ind_mean, 4), " vs group r:", round(r_group, 4))
    print(f"[dual] verdict: group > individual? {r_group > r_ind_mean}")

    print(f"\n[done] {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
