#!/usr/bin/env python3
"""
Cycle 17 Deney 4: Per-region MI-full vs MI-naive encoding on ds003720.

R5 H3 pending: the 5-region architectural signature (A1_HG, MGB, IFG, PAG, IC)
needs a per-region breakdown on the ecosystem-valid dataset. v9.5.6 ds002725
group-mean shuffle was suggestive; this is the replicated per-region test.

Design
------
For each of the 26 MI regions, for each of 4 subjects:
    X_full  = MI-full (720 clips, 26-D)[clip_idx, region_idx_keep_dim] reshaped to (540, 26)
    X_naive = MI-naive (720 clips, 26-D)[clip_idx, same shape]
    y       = per-region per-clip BOLD (540,) = mean of 6mm sphere voxels
    Ridge 5-fold CV (nested alpha), held-out Pearson r per region, per encoder.

Honest-disclosure: brainstem regions (IC, AN, CN, SOC, PAG) are pre-registered
as excluded from BOLD analysis per Beissner 2015 (brainstem BOLD SNR poor).
We run the analysis anyway to document this empirically and report the result
alongside the 3 non-brainstem R5-signature regions (A1_HG, MGB, IFG).

Dependencies
------------
Requires: {subj}_bold_per_clip_26regions.npy (540, 26) — output of
build_bold_26regions_per_clip.py. That script aggregates the per-run (T, 26)
output of extract_bold_26regions.py to per-clip using the same HRF lag + pool
window as the main (540, V) extraction.

Usage
-----
    python3 build_bold_26regions_per_clip.py  # one-time, ~2 min
    python3 C17_deney_4_per_region_encoding.py
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.multitest import multipletests

BASE = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI")
SHARED = BASE / "_shared"
sys.path.insert(0, str(SHARED))
from regions_mi_atlas import REGION_NAMES, BRAINSTEM_EXCLUDED  # noqa: E402

DS = BASE / "ds003720"
FEATURES = DS / "05_features"
ROI = DS / "04_roi_extraction"
OUT = DS / "06_encoding"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260424
N_FOLDS = 5
N_PERM_NULL = 500
ALPHA_GRID = [0.1, 1.0, 10.0, 100.0, 1000.0]

SUBJECTS = ["sub-001", "sub-003", "sub-004", "sub-005"]

# R5's 5-region architectural signature
R5_SIGNATURE = ["A1_HG", "MGB", "IFG", "PAG", "IC"]


def ridge_kfold_heldout_r(X: np.ndarray, y: np.ndarray, n_folds: int, seed: int) -> float:
    """K-fold CV ridge with nested alpha selection; return held-out Pearson r."""
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    inner_kf = KFold(n_splits=3, shuffle=True, random_state=seed + 1)
    y_pred = np.zeros_like(y)
    for tr_idx, te_idx in kf.split(X):
        X_tr, X_te = X[tr_idx], X[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)

        best_alpha, best_r2 = ALPHA_GRID[0], -np.inf
        for alpha in ALPHA_GRID:
            fold_r2s = []
            for itr, ite in inner_kf.split(X_tr_s):
                m = Ridge(alpha=alpha).fit(X_tr_s[itr], y_tr[itr])
                p = m.predict(X_tr_s[ite])
                ss_res = ((y_tr[ite] - p) ** 2).sum()
                ss_tot = ((y_tr[ite] - y_tr[ite].mean()) ** 2).sum()
                fold_r2s.append(1 - ss_res / (ss_tot + 1e-10))
            if np.mean(fold_r2s) > best_r2:
                best_r2, best_alpha = np.mean(fold_r2s), alpha

        m = Ridge(alpha=best_alpha).fit(X_tr_s, y_tr)
        y_pred[te_idx] = m.predict(X_te_s)

    y_z = (y - y.mean()) / (y.std() + 1e-10)
    p_z = (y_pred - y_pred.mean()) / (y_pred.std() + 1e-10)
    return float((y_z * p_z).mean())


def shuffle_null_per_region(X: np.ndarray, y: np.ndarray, n_perm: int, seed: int) -> np.ndarray:
    """Return (n_perm,) null distribution of correlation between X @ X.T.mean() and shuffled y.

    Light-weight null — Pearson r between X-first-PC (mean across features) and shuffled y.
    Matches the shuffle-null-level test from Deney 1 but per-region.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    # Pearson r between mean(X) and y is the smallest-possible model; null is shuffled y.
    x_mean = X.mean(axis=1)
    x_z = (x_mean - x_mean.mean()) / (x_mean.std() + 1e-10)
    nulls = np.zeros(n_perm, dtype=np.float32)
    for p in range(n_perm):
        y_perm = rng.permutation(y)
        y_z = (y_perm - y_perm.mean()) / (y_perm.std() + 1e-10)
        nulls[p] = (x_z * y_z).mean()
    return nulls


def main():
    t0 = time.time()
    print(f"[C17-4] seed={SEED} N_FOLDS={N_FOLDS} N_PERM={N_PERM_NULL}", flush=True)

    # Encoder features
    mi_full = np.load(FEATURES / "mi_ram_26d.npy").astype(np.float32)   # (720, 26)
    mi_naive = np.load(FEATURES / "mi_naive_26d.npy").astype(np.float32)
    print(f"MI-full {mi_full.shape}, MI-naive {mi_naive.shape}", flush=True)

    name_to_idx = {n: i for i, n in enumerate(REGION_NAMES)}
    print(f"Region atlas: {len(REGION_NAMES)} regions", flush=True)
    print(f"R5 signature: {R5_SIGNATURE}", flush=True)
    print(f"Brainstem pre-excluded: {sorted(BRAINSTEM_EXCLUDED)}", flush=True)

    rows = []
    for subj in SUBJECTS:
        bold_region_path = ROI / f"{subj}_bold_per_clip_26regions.npy"
        if not bold_region_path.exists():
            print(f"SKIP {subj}: missing {bold_region_path.name}", flush=True)
            continue
        bold_reg = np.load(bold_region_path).astype(np.float32)   # (540, 26)
        clip_idx = np.load(ROI / f"{subj}_clip_indices.npy")
        print(f"\n[C17-4 {subj}] bold {bold_reg.shape}", flush=True)

        for region_name in REGION_NAMES:
            r_idx = name_to_idx[region_name]
            y = bold_reg[:, r_idx]

            # Missing / all-zero columns = extraction failure
            if np.any(np.isnan(y)) or np.std(y) < 1e-9:
                rows.append({
                    "subject": subj, "region": region_name, "r_idx": r_idx,
                    "tier": "excluded-no-signal",
                    "r_mi_full": np.nan, "r_mi_naive": np.nan, "delta": np.nan,
                    "null_mean": np.nan, "null_std": np.nan, "pass_gt_null": False,
                })
                continue

            Xf = mi_full[clip_idx, :].astype(np.float32)
            Xn = mi_naive[clip_idx, :].astype(np.float32)

            rng_seed = SEED + hash(subj + region_name) % 10000
            r_full = ridge_kfold_heldout_r(Xf, y, N_FOLDS, rng_seed)
            r_naive = ridge_kfold_heldout_r(Xn, y, N_FOLDS, rng_seed + 500)
            null = shuffle_null_per_region(Xf, y, N_PERM_NULL, rng_seed + 1000)

            tier_lbl = "r5-signature" if region_name in R5_SIGNATURE else "other"
            if region_name in BRAINSTEM_EXCLUDED:
                tier_lbl = f"{tier_lbl}-brainstem-excluded"

            rows.append({
                "subject": subj, "region": region_name, "r_idx": r_idx,
                "tier": tier_lbl,
                "r_mi_full": r_full, "r_mi_naive": r_naive,
                "delta": r_full - r_naive,
                "null_mean": float(null.mean()),
                "null_std": float(null.std()),
                "pass_gt_null": bool(r_full > np.percentile(null, 95)),
            })
            mark = "*" if region_name in R5_SIGNATURE else " "
            print(f"  {mark}{region_name:<14} full={r_full:+.4f}  naive={r_naive:+.4f}  Δ={r_full-r_naive:+.4f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "C17_deney_4_per_region_encoding.csv", index=False)

    print(f"\n{'='*80}")
    print("C17-4 R5 SIGNATURE SUMMARY (Fisher-z mean across subjects, per region)")
    print('='*80)
    r5_rows = df[df['region'].isin(R5_SIGNATURE) & df['delta'].notna()]
    for region in R5_SIGNATURE:
        sub = r5_rows[r5_rows['region'] == region]
        if len(sub) == 0:
            marker = "EXCLUDED" if region in BRAINSTEM_EXCLUDED else "NO DATA"
            print(f"  {region:<10}  [{marker}]")
            continue
        # Fisher-z mean
        def fisher_mean(vals):
            z = np.arctanh(np.clip(vals.values, -0.999, 0.999))
            return np.tanh(z.mean())
        mf = fisher_mean(sub['r_mi_full'])
        mn = fisher_mean(sub['r_mi_naive'])
        dl = fisher_mean(sub['delta'])
        n_subj = len(sub)
        n_pass = int(sub['pass_gt_null'].sum())
        marker = " [BRAINSTEM]" if region in BRAINSTEM_EXCLUDED else ""
        print(f"  {region:<10}  full={mf:+.4f}  naive={mn:+.4f}  Δ={dl:+.4f}  null-pass: {n_pass}/{n_subj} subj{marker}")

    # Provenance
    (OUT / "C17_deney_4_provenance.json").write_text(json.dumps({
        "experiment": "C17_deney_4_per_region_encoding",
        "seed": SEED,
        "n_folds": N_FOLDS,
        "n_perm_null": N_PERM_NULL,
        "alpha_grid": ALPHA_GRID,
        "subjects": SUBJECTS,
        "region_count": len(REGION_NAMES),
        "r5_signature": R5_SIGNATURE,
        "brainstem_excluded_per_beissner_2015": sorted(BRAINSTEM_EXCLUDED),
        "runtime_s": time.time() - t0,
    }, indent=2))

    print(f"\n[C17-4] runtime: {time.time()-t0:.1f}s")
    print(f"Output: {OUT}/C17_deney_4_per_region_encoding.csv")


if __name__ == "__main__":
    main()
