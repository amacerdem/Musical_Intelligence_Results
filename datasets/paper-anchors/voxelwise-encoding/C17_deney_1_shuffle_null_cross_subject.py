#!/usr/bin/env python3
"""
Cycle 17 Deney 1: ds003720 cross-subject encoding with shuffle-clip null.

Extends first-pass voxel-top-5% analysis:
  - 4 subjects (sub-001, sub-003, sub-004, sub-005 — sub-005 missing from first-pass)
  - 8 encoders (MI-26, MI-naive-26, MERT-768, CLAP-512, MusicFM-1024, MuQ-1024, Random-26, Random-768)
  - SHUFFLE-CLIP NULL (500 perms per subject per encoder, critical gate)
  - Per-subject per-encoder top-5% |r| mean with BH-FDR

Methodology:
  For each (subject, encoder):
    X: (540, D) per-clip feature matrix
    Y: (540, V) per-clip per-voxel BOLD response (from Zenodo preproc, cached)

    Per-voxel per-dim Pearson r: R = corr(X, Y) → shape (D, V)
    Per-voxel best r: R_best = max(|R|, axis=0) * sign(R[argmax|R|, v])
    Top-5% voxels: sort R_best desc, take top V//20, mean |r|

    Shuffle null: shuffle clip labels in X, repeat above, 500 perms.
    p: fraction of null top-5% >= real top-5% (one-tailed).

Memory: <500 MB peak per subject. Sequential subject × encoder iteration.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI")
DS_DIR = ROOT / "ds003720"
FEATURES = DS_DIR / "05_features"
ROI = DS_DIR / "04_roi_extraction"
OUT = DS_DIR / "06_encoding"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260424
N_PERM = 500
TOP_PCT = 5  # top-5% voxel mean |r|

SUBJECTS = ["sub-001", "sub-003", "sub-004", "sub-005"]
ENCODERS = {
    "mi_ram_26d": ("mi_ram_26d.npy", 26),
    "mi_naive_26d": ("mi_naive_26d.npy", 26),
    "mert_768d": ("mert_768d.npy", 768),
    "clap_music_512d": ("clap_music_512d.npy", 512),
    "musicfm_1024d": ("musicfm_1024d.npy", 1024),
    "muq_1024d": ("muq_1024d.npy", 1024),
    "random_26d": ("random_26d.npy", 26),
    "random_768d": ("random_768d.npy", 768),
}


def per_voxel_best_r(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Per-voxel best |r| across feature dims.

    X: (n_clips, D) features
    Y: (n_clips, V) BOLD
    Returns: (V,) best |r| per voxel.
    """
    # Standardize columns (in-place z-score)
    Xz = (X - X.mean(0)) / (X.std(0) + 1e-10)
    Yz = (Y - Y.mean(0)) / (Y.std(0) + 1e-10)
    n = X.shape[0]
    # Pearson r = (Xz.T @ Yz) / n → (D, V)
    R = (Xz.T @ Yz) / n
    # Best |r| per voxel
    return np.max(np.abs(R), axis=0).astype(np.float32)


def top_pct_mean(abs_r: np.ndarray, pct: float) -> float:
    """Top-pct% voxels' mean |r|."""
    k = max(1, int(len(abs_r) * pct / 100))
    top_idx = np.argpartition(abs_r, -k)[-k:]
    return float(np.mean(abs_r[top_idx]))


def main():
    t0 = time.time()
    print(f"[C17-1] seed={SEED} N_PERM={N_PERM} TOP_PCT={TOP_PCT}", flush=True)
    rng = np.random.default_rng(SEED)

    # Load canonical clip order + MI RAM (base for ordering)
    with open(FEATURES / "clip_order.json") as f:
        raw = json.load(f)
        clip_order = raw if isinstance(raw, list) else raw["clip_ids_order"]
    n_clips_total = len(clip_order)
    print(f"[C17-1] {n_clips_total} canonical clips in order", flush=True)

    # Pre-load ALL encoder features (720 × D)
    encoder_features = {}
    for enc_name, (fname, D) in ENCODERS.items():
        path = FEATURES / fname
        if path.exists():
            feat = np.load(path).astype(np.float32)
            if feat.shape[0] != n_clips_total:
                print(f"[C17-1] SKIP {enc_name}: shape {feat.shape} != expected ({n_clips_total}, D) — malformed, likely truncated extraction", flush=True)
                continue
            encoder_features[enc_name] = feat
            print(f"[C17-1] loaded {enc_name}: {feat.shape}", flush=True)
        else:
            print(f"[C17-1] MISSING {enc_name}: {path}", flush=True)

    rows_real = []
    rows_null = []

    for subj in SUBJECTS:
        t_sub = time.time()
        bold_path = ROI / f"{subj}_bold_per_clip.npy"
        ci_path = ROI / f"{subj}_clip_indices.npy"
        if not bold_path.exists() or not ci_path.exists():
            print(f"[C17-1] SKIP {subj}: missing bold_per_clip or clip_indices", flush=True)
            continue

        bold = np.load(bold_path).astype(np.float32)  # (540, V)
        clip_idx = np.load(ci_path)  # (540,) indices into clip_order
        n_sub_clips, n_voxels = bold.shape
        print(f"\n[C17-1] {subj}: bold {bold.shape}, {n_sub_clips} clips, {n_voxels} voxels", flush=True)

        # Map subject's 540 clips into the canonical 720-clip encoder feature order
        # clip_idx[i] is the index into clip_order[] for subject's clip i
        # Extract encoder features at those indices → (540, D)

        for enc_name, feat_all in encoder_features.items():
            X = feat_all[clip_idx, :].astype(np.float32)  # (540, D)

            # REAL top-5% |r|
            abs_r = per_voxel_best_r(X, bold)
            real_top = top_pct_mean(abs_r, TOP_PCT)

            # Shuffle-clip null
            null_tops = np.zeros(N_PERM, dtype=np.float32)
            for p in range(N_PERM):
                perm = rng.permutation(n_sub_clips)
                X_sh = X[perm, :]
                abs_r_sh = per_voxel_best_r(X_sh, bold)
                null_tops[p] = top_pct_mean(abs_r_sh, TOP_PCT)

            # One-tailed p: fraction of null >= real
            p_one = (np.sum(null_tops >= real_top) + 1) / (N_PERM + 1)
            null_median = float(np.median(null_tops))
            null_p95 = float(np.percentile(null_tops, 95))
            null_p99 = float(np.percentile(null_tops, 99))

            rows_real.append({
                "subject": subj, "encoder": enc_name,
                "D": X.shape[1], "n_voxels": n_voxels,
                "real_top5pct_mean_r": real_top,
                "null_median_top5pct": null_median,
                "null_p95_top5pct": null_p95,
                "null_p99_top5pct": null_p99,
                "p_one_tailed": float(p_one),
                "effect_size_abs": real_top - null_median,
            })
            print(f"  {enc_name:<18} real={real_top:.4f}  null_median={null_median:.4f}  p={p_one:.4f}", flush=True)

        # Free memory
        del bold
        print(f"[C17-1] {subj} done in {time.time()-t_sub:.1f}s", flush=True)

    real_df = pd.DataFrame(rows_real)
    # BH-FDR across 32 tests (4 subj × 8 encoders)
    pvals = real_df["p_one_tailed"].values
    bh = multipletests(pvals, method="fdr_bh", alpha=0.05)
    real_df["q_bh"] = bh[1]
    real_df["pass_bh_q05"] = bh[0]
    real_df.to_csv(OUT / "C17_deney_1_shuffle_null_results.csv", index=False)

    # Summary per encoder (mean across subjects)
    print(f"\n{'='*100}")
    print(f"C17 DENEY 1 — SHUFFLE-CLIP NULL SUMMARY (N={N_PERM} perms, {len(real_df)} total tests, BH-FDR)")
    print(f"{'='*100}")
    print("\nPer-encoder mean (across 4 subjects):")
    enc_summary = real_df.groupby("encoder").agg({
        "real_top5pct_mean_r": "mean",
        "null_median_top5pct": "mean",
        "effect_size_abs": "mean",
        "p_one_tailed": "median",
        "pass_bh_q05": "sum",
    }).round(4)
    enc_summary = enc_summary.rename(columns={"pass_bh_q05": "n_subj_pass_BH"})
    print(enc_summary.to_string())

    print("\nPer-subject per-encoder real vs null:")
    pvt = real_df.pivot_table(index="subject", columns="encoder", values="real_top5pct_mean_r", aggfunc="first").round(4)
    print(pvt.to_string())

    print("\nEffect size (real - null_median):")
    pvt_effect = real_df.pivot_table(index="subject", columns="encoder", values="effect_size_abs", aggfunc="first").round(4)
    print(pvt_effect.to_string())

    print("\nBH-FDR q-values:")
    pvt_q = real_df.pivot_table(index="subject", columns="encoder", values="q_bh", aggfunc="first").round(4)
    print(pvt_q.to_string())

    # Provenance
    prov = {
        "experiment": "C17_deney_1_shuffle_null_cross_subject",
        "seed": SEED, "n_perm": N_PERM, "top_pct": TOP_PCT,
        "subjects": SUBJECTS,
        "encoders": list(ENCODERS.keys()),
        "n_tests": int(len(real_df)),
        "n_pass_bh_q05": int(real_df["pass_bh_q05"].sum()),
        "runtime_s": time.time() - t0,
    }
    (OUT / "C17_deney_1_provenance.json").write_text(json.dumps(prov, indent=2))

    print(f"\n[C17-1] TOTAL RUNTIME: {time.time()-t0:.1f}s")
    print(f"[C17-1] {real_df['pass_bh_q05'].sum()} / {len(real_df)} tests survive BH q<0.05")
    print(f"Artifacts → {OUT}")


if __name__ == "__main__":
    main()
