#!/usr/bin/env python3
"""
run_26region_ridge.py — per-region ridge encoding for MI 26-region atlas.

Data-integrity pivot (2026-04-24)
---------------------------------
Local BIDS BOLD (.nii) on this drive is truncated for 58/72 runs. Native-space
6mm sphere extraction at MI's MNI coords is therefore not possible here.

We use pre-extracted 26-region BOLD timecourses from the RunPod-Exp-01
compute_encoding_nakai.py checkpoint cache (Harvard-Oxford labels + 4mm γ-tier
spheres, 15/18 runs/subject available — Test runs 04-06 missing from cache).

ckpt_bold source:
  .../V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/
        T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold/{sub}_{task}_run-{NN}.npy
  shape per run: (410 TRs, 26 regions), z-scored per region within run.

Atlas: 26 channels exactly match Science/Bold-fMRI/_shared/regions_mi_atlas.py
REGIONS order. The 7 γ-tier ROIs (VTA, MGB, hypothalamus, IC, AN, CN, SOC, PAG)
use 4mm spheres at slightly different MNI coords than our atlas (from lit. peaks);
flagged in report.

Method
------
Per subject, per run: align 40 clips/run (Training) or 40 clips/run (Test) to
BOLD using HRF lag 4 TRs + mean-pool next 4 TRs. Collect per-clip per-region
vectors. Ridge-cv (5-fold, alpha=100, seed 20260424) per region with X=features.

Encoders: mi_ram_26d, mi_naive_26d, mert_768d, random_26d.

Outputs (ds003720/06_encoding/)
-------------------------------
  per_subject_per_region_r.csv
  per_subject_per_region_r.npz  (per-subject per-encoder per-region r arrays)
  meta_26region.json
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")

SEED = 20260424
TR_S = 1.5
HRF_LAG_TR = 4
POOL_WIN_TR = 4
CLIPS_PER_TRAINING_RUN = 40
CLIPS_PER_TEST_RUN = 40  # each run has 40 events (10 unique × 4 repeats)

BASE = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI")
SHARED = BASE / "_shared"
sys.path.insert(0, str(SHARED))
from regions_mi_atlas import REGION_NAMES, REGION_TIERS  # noqa: E402

DS = BASE / "ds003720"
FEAT = DS / "05_features"
OUT = DS / "06_encoding"
OUT.mkdir(parents=True, exist_ok=True)

CKPT_BOLD = Path(
    "<PAPER_TIME_SCIENCE_ROOT>/Science/V2/reviewer-sims/"
    "divan-major-revision-2026-04-22/computing-phase/"
    "T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold"
)

SUBJECTS = ["sub-001", "sub-003", "sub-004", "sub-005"]
ENCODERS = [
    ("mi_ram_26d",   FEAT / "mi_ram_26d.npy"),
    ("mi_naive_26d", FEAT / "mi_naive_26d.npy"),
    ("mert_768d",    FEAT / "mert_768d.npy"),
    ("random_26d",   FEAT / "random_26d.npy"),
]
ALPHA = 100.0
N_FOLDS = 5


def pool_run(bold: np.ndarray, n_clips: int) -> np.ndarray:
    """(T=410, 26) -> (n_clips, 26) HRF-lagged pool."""
    t, n = bold.shape
    out = np.full((n_clips, n), np.nan, dtype=np.float32)
    for c in range(n_clips):
        s = c * 10 + HRF_LAG_TR   # 10 TRs per clip
        e = min(s + POOL_WIN_TR, t)
        if s < t:
            out[c] = bold[s:e].mean(axis=0)
    return out


def build_subject_data(subj: str, clip_order: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Return (X_indices, Y) where X_indices = (N,) into clip_order, Y = (N, 26).

    Walks the checkpoint cache directory for all runs of subj, pools per-run BOLD
    to per-clip 26-d, maps to canonical clip indices.
    """
    id_to_idx = {cid: i for i, cid in enumerate(clip_order)}

    per_clip: dict[int, np.ndarray] = {}

    files = sorted(CKPT_BOLD.glob(f"{subj}_Training_run-*.npy"))
    print(f"[{subj}] {len(files)} cached Training runs (Test excluded: repeats of same stimuli)")
    for f in files:
        # Parse filename: sub-001_Training_run-05.npy
        stem = f.stem
        parts = stem.split("_")
        assert parts[0] == subj
        task = parts[1]
        run_str = parts[2].replace("run-", "")
        run_idx = int(run_str)
        assert task == "Training"

        bold = np.load(f).astype(np.float32)  # (410, 26)
        n_clips_run = CLIPS_PER_TRAINING_RUN
        prefix_template = f"Stim_Training_Run{run_idx:02d}_"

        clip_bold = pool_run(bold, n_clips_run)  # (40, 26)

        # 40 unique clips in filename-position order
        for pos in range(1, 41):
            prefix = f"{prefix_template}{pos:02d}_"
            matches = [c for c in clip_order if c.startswith(prefix)]
            if len(matches) != 1:
                print(f"    [warn] {prefix}: {len(matches)} matches")
                continue
            cid = matches[0]
            ci = id_to_idx[cid]
            row = clip_bold[pos - 1]
            per_clip[ci] = row

    # Build (N, 26), (N,) index arrays
    clip_indices = sorted(per_clip.keys())
    Y = np.stack([per_clip[c] for c in clip_indices], axis=0).astype(np.float32)
    X_idx = np.asarray(clip_indices, dtype=np.int32)
    # Remove rows that are all-NaN (should be rare now with HO extraction)
    valid = ~np.isnan(Y).all(axis=1)
    return X_idx[valid], Y[valid]


def ridge_cv_per_region_r(X: np.ndarray, Y: np.ndarray, alpha: float, n_folds: int, seed: int) -> np.ndarray:
    """Fisher-z-averaged per-region Pearson r over k folds."""
    n, d = X.shape
    n, r = Y.shape
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_r = np.zeros((n_folds, r), dtype=np.float32)
    for fi, (tr, te) in enumerate(kf.split(X)):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xtr = (X[tr] - mu) / sd
        Xte = (X[te] - mu) / sd
        # Per-region fit; skip regions with NaN in Y[tr]
        per_r = np.full(r, np.nan, dtype=np.float32)
        for rr in range(r):
            ytr = Y[tr, rr]
            yte = Y[te, rr]
            if np.isnan(ytr).any() or np.isnan(yte).any():
                continue
            if ytr.std() < 1e-9 or yte.std() < 1e-9:
                continue
            m_ = Ridge(alpha=alpha, solver="auto")
            m_.fit(Xtr, ytr)
            pred = m_.predict(Xte)
            # Pearson
            a = pred - pred.mean()
            b = yte - yte.mean()
            den = np.sqrt((a * a).sum() * (b * b).sum())
            per_r[rr] = (a * b).sum() / den if den > 1e-12 else 0.0
        fold_r[fi] = per_r
    # Fisher-z average
    z = np.arctanh(np.clip(fold_r, -0.9999, 0.9999))
    mean_z = np.nanmean(z, axis=0)
    return np.tanh(mean_z).astype(np.float32)


def main():
    t0 = time.time()
    clip_order = json.loads((FEAT / "clip_order.json").read_text())
    assert len(clip_order) == 720

    feats = {name: np.load(p).astype(np.float32) for name, p in ENCODERS}
    for k, v in feats.items():
        print(f"[feat] {k}: {v.shape}")

    # Build per-subject data
    subj_data: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for subj in SUBJECTS:
        X_idx, Y = build_subject_data(subj, clip_order)
        subj_data[subj] = (X_idx, Y)
        nan_cols = np.isnan(Y).any(axis=0)
        print(f"[{subj}] usable clips: {Y.shape}  NaN_regions: {[REGION_NAMES[i] for i in np.where(nan_cols)[0]]}")

    # Per-subject per-encoder per-region r
    rows = []
    per_region_r = {}  # keys: {subj}__{enc} -> (26,) array
    for subj in SUBJECTS:
        X_idx, Y = subj_data[subj]
        for enc_name, _ in ENCODERS:
            ts = time.time()
            X = feats[enc_name][X_idx]
            r_per_region = ridge_cv_per_region_r(X, Y, alpha=ALPHA, n_folds=N_FOLDS, seed=SEED)
            per_region_r[f"{subj}__{enc_name}"] = r_per_region
            dt = time.time() - ts
            print(f"  [{subj} {enc_name}] mean_r={np.nanmean(r_per_region):+.4f}  max={np.nanmax(r_per_region):+.4f}  ({dt:.1f}s)")
            for i, nm in enumerate(REGION_NAMES):
                rows.append({
                    "subject": subj,
                    "region_idx": i,
                    "region": nm,
                    "tier": REGION_TIERS[i],
                    "encoder": enc_name,
                    "D": int(X.shape[1]),
                    "n_clips": int(X.shape[0]),
                    "r": float(r_per_region[i]) if not np.isnan(r_per_region[i]) else None,
                })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "per_subject_per_region_r.csv", index=False)
    np.savez_compressed(OUT / "per_subject_per_region_r.npz", **per_region_r)

    meta = {
        "seed": SEED,
        "alpha": ALPHA,
        "n_folds": N_FOLDS,
        "subjects": SUBJECTS,
        "encoders": [n for n, _ in ENCODERS],
        "bold_source": str(CKPT_BOLD),
        "atlas_note": "Harvard-Oxford labels + 4mm γ-tier spheres (from RunPod ckpt_bold cache).",
        "n_runs_per_subject_cached": 15,
        "n_runs_per_subject_expected": 18,
        "missing_runs": "Test run-04, run-05, run-06 (60 clips × subject = 240 clips short)",
        "simplification_note": (
            "Local BIDS BOLD truncated for 58/72 runs; native-space 6mm MI-MNI-coord "
            "sphere extraction not possible. Used pre-cached HO-atlas ROI timecourses "
            "from RunPod as functional equivalent (same 26-channel order)."
        ),
        "runtime_total_s": round(time.time() - t0, 1),
    }
    (OUT / "meta_26region.json").write_text(json.dumps(meta, indent=2))
    print(f"\n[done] {time.time()-t0:.1f}s")

    # Quick summary pivot
    piv = df.pivot_table(index=["region", "tier"], columns="encoder", values="r", aggfunc="mean").round(3)
    print("\n=== PER-REGION MEAN r (avg across subjects) ===")
    print(piv.to_string())


if __name__ == "__main__":
    main()
