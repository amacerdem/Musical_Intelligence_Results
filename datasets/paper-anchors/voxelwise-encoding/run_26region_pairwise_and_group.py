#!/usr/bin/env python3
"""
run_26region_pairwise_and_group.py — bootstrap pairwise (MI vs MERT, MI vs MI-naive)
+ group-mean dual-scale, at per-region level.

Inputs
------
  per_subject_per_region_r.npz  ({subj}__{enc} -> (26,) r array)
  {subj}__meta in per_subject_per_region_r.csv

Pairwise bootstrap (Step 5)
---------------------------
  For each region r: across 4 subjects, MI - MERT Δr; 2000-BCa bootstrap of
  per-subject Δr (resample subjects with replacement). 95% CI, sig flag.

Group-mean dual-scale (Step 6)
------------------------------
  group_bold[:, r] = mean across subjects of per-clip per-region BOLD
  (intersect of clips seen in all subjects). Ridge (MI -> group_bold[:, r])
  per region; also MI-naive, MERT, random. Compare group-mean r vs mean of
  individual-subject r (from Step 4).

Outputs
-------
  mi_vs_mert_pairwise_per_region.csv
  mi_vs_mi_naive_pairwise_per_region.csv
  group_mean_per_region_r.csv
  pairwise_structure.csv
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

SEED = 20260424
TR_S = 1.5
HRF_LAG_TR = 4
POOL_WIN_TR = 4

BASE = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI")
SHARED = BASE / "_shared"
sys.path.insert(0, str(SHARED))
from regions_mi_atlas import REGION_NAMES, REGION_TIERS, BRAINSTEM_EXCLUDED  # noqa: E402

DS = BASE / "ds003720"
FEAT = DS / "05_features"
OUT = DS / "06_encoding"

CKPT_BOLD = Path(
    "/Volumes/SRC-9/SRC Musical Intelligence/Science/V2/reviewer-sims/"
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
N_BOOT = 2000
N_REGIONS = 26


def pool_run(bold: np.ndarray, n_clips: int) -> np.ndarray:
    t, n = bold.shape
    out = np.full((n_clips, n), np.nan, dtype=np.float32)
    for c in range(n_clips):
        s = c * 10 + HRF_LAG_TR
        e = min(s + POOL_WIN_TR, t)
        if s < t:
            out[c] = bold[s:e].mean(axis=0)
    return out


def build_subject_bold(subj: str, clip_order: list[str]):
    id_to_idx = {cid: i for i, cid in enumerate(clip_order)}
    per_clip: dict[int, np.ndarray] = {}
    for f in sorted(CKPT_BOLD.glob(f"{subj}_Training_run-*.npy")):
        bold = np.load(f).astype(np.float32)
        parts = f.stem.split("_")
        run_idx = int(parts[2].replace("run-", ""))
        clip_bold = pool_run(bold, 40)
        for pos in range(1, 41):
            prefix = f"Stim_Training_Run{run_idx:02d}_{pos:02d}_"
            matches = [c for c in clip_order if c.startswith(prefix)]
            if len(matches) == 1:
                per_clip[id_to_idx[matches[0]]] = clip_bold[pos - 1]
    idx = sorted(per_clip.keys())
    Y = np.stack([per_clip[i] for i in idx], axis=0).astype(np.float32)
    return np.asarray(idx, dtype=np.int32), Y


def ridge_cv_per_region_r(X, Y, alpha, n_folds, seed):
    n = X.shape[0]
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_r = np.zeros((n_folds, Y.shape[1]), dtype=np.float32)
    for fi, (tr, te) in enumerate(kf.split(X)):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
        Xtr = (X[tr] - mu) / sd
        Xte = (X[te] - mu) / sd
        per_r = np.full(Y.shape[1], np.nan, dtype=np.float32)
        for rr in range(Y.shape[1]):
            ytr, yte = Y[tr, rr], Y[te, rr]
            if np.isnan(ytr).any() or np.isnan(yte).any():
                continue
            if ytr.std() < 1e-9 or yte.std() < 1e-9:
                continue
            m_ = Ridge(alpha=alpha, solver="auto").fit(Xtr, ytr)
            pred = m_.predict(Xte)
            a, b = pred - pred.mean(), yte - yte.mean()
            den = np.sqrt((a * a).sum() * (b * b).sum())
            per_r[rr] = (a * b).sum() / den if den > 1e-12 else 0.0
        fold_r[fi] = per_r
    z = np.arctanh(np.clip(fold_r, -0.9999, 0.9999))
    return np.tanh(np.nanmean(z, axis=0)).astype(np.float32)


def pairwise_bootstrap_per_region(r_mat_a: np.ndarray, r_mat_b: np.ndarray, n_boot: int, seed: int):
    """r_mat_a,b: (n_sub, n_reg). Returns (observed, ci_lo, ci_hi, sig) per region."""
    rng = np.random.default_rng(seed)
    n_sub, n_reg = r_mat_a.shape
    observed = np.nanmean(r_mat_a - r_mat_b, axis=0)  # (n_reg,)
    draws = np.full((n_boot, n_reg), np.nan, dtype=np.float32)
    for b in range(n_boot):
        samp = rng.integers(0, n_sub, size=n_sub)
        draws[b] = np.nanmean(r_mat_a[samp] - r_mat_b[samp], axis=0)
    ci_lo = np.nanpercentile(draws, 2.5, axis=0)
    ci_hi = np.nanpercentile(draws, 97.5, axis=0)
    sig = (ci_lo > 0) | (ci_hi < 0)
    return observed, ci_lo, ci_hi, sig


def bh_fdr(p: np.ndarray, q: float = 0.1):
    """BH-FDR. Returns boolean reject array and p_adj."""
    n = len(p)
    order = np.argsort(p)
    p_sorted = p[order]
    p_adj = np.empty(n)
    min_adj = 1.0
    for i in range(n - 1, -1, -1):
        adj = min(1.0, p_sorted[i] * n / (i + 1))
        min_adj = min(min_adj, adj)
        p_adj[order[i]] = min_adj
    reject = p_adj < q
    return reject, p_adj


def main():
    t0 = time.time()
    clip_order = json.loads((FEAT / "clip_order.json").read_text())
    data = np.load(OUT / "per_subject_per_region_r.npz")

    # Per-subject per-region r matrix: (n_sub, n_reg) per encoder
    r_per_enc = {}
    for enc_name, _ in ENCODERS:
        mat = np.zeros((len(SUBJECTS), N_REGIONS), dtype=np.float32)
        for si, subj in enumerate(SUBJECTS):
            mat[si] = data[f"{subj}__{enc_name}"]
        r_per_enc[enc_name] = mat

    # --- Step 5: Pairwise bootstrap per region ---
    rows_mert = []
    obs, lo, hi, sig = pairwise_bootstrap_per_region(r_per_enc["mi_ram_26d"], r_per_enc["mert_768d"], N_BOOT, SEED)
    for i, nm in enumerate(REGION_NAMES):
        rows_mert.append({
            "region_idx": i, "region": nm, "tier": REGION_TIERS[i],
            "observed_delta_r": float(obs[i]),
            "bootstrap_ci95_lo": float(lo[i]),
            "bootstrap_ci95_hi": float(hi[i]),
            "significant_95CI": bool(sig[i]),
            "n_boot": N_BOOT, "n_subjects": len(SUBJECTS),
        })
    df_mert = pd.DataFrame(rows_mert)
    # BH-FDR on two-sided p from Δ>0 (approximated via sign+CI width)
    # Use per-region one-sample t statistic across subjects as p-source
    from scipy.stats import ttest_1samp
    deltas_sub = r_per_enc["mi_ram_26d"] - r_per_enc["mert_768d"]
    ps_mert = np.array([ttest_1samp(deltas_sub[:, i], 0.0).pvalue for i in range(N_REGIONS)])
    reject, p_adj = bh_fdr(ps_mert, q=0.1)
    df_mert["ttest_p"] = ps_mert
    df_mert["bh_fdr_q01_reject"] = reject
    df_mert["bh_fdr_p_adj"] = p_adj
    df_mert.to_csv(OUT / "mi_vs_mert_pairwise_per_region.csv", index=False)

    rows_naive = []
    obs_n, lo_n, hi_n, sig_n = pairwise_bootstrap_per_region(r_per_enc["mi_ram_26d"], r_per_enc["mi_naive_26d"], N_BOOT, SEED)
    for i, nm in enumerate(REGION_NAMES):
        rows_naive.append({
            "region_idx": i, "region": nm, "tier": REGION_TIERS[i],
            "observed_delta_r": float(obs_n[i]),
            "bootstrap_ci95_lo": float(lo_n[i]),
            "bootstrap_ci95_hi": float(hi_n[i]),
            "significant_95CI": bool(sig_n[i]),
            "n_boot": N_BOOT, "n_subjects": len(SUBJECTS),
        })
    df_naive = pd.DataFrame(rows_naive)
    deltas_naive = r_per_enc["mi_ram_26d"] - r_per_enc["mi_naive_26d"]
    ps_naive = np.array([ttest_1samp(deltas_naive[:, i], 0.0).pvalue for i in range(N_REGIONS)])
    rej_n, padj_n = bh_fdr(ps_naive, q=0.1)
    df_naive["ttest_p"] = ps_naive
    df_naive["bh_fdr_q01_reject"] = rej_n
    df_naive["bh_fdr_p_adj"] = padj_n
    df_naive.to_csv(OUT / "mi_vs_mi_naive_pairwise_per_region.csv", index=False)

    print("[pairwise] MI vs MERT — per-region Δr:")
    print(df_mert[["region", "tier", "observed_delta_r", "bootstrap_ci95_lo", "bootstrap_ci95_hi", "significant_95CI", "bh_fdr_q01_reject"]].to_string(index=False))
    print(f"  MI>MERT regions: {int((df_mert.observed_delta_r > 0).sum())}/26")
    print(f"  sig_95CI: {int(df_mert.significant_95CI.sum())}/26")
    print(f"  bh_fdr_q01: {int(df_mert.bh_fdr_q01_reject.sum())}/26")

    # --- Step 6: Group-mean dual-scale ---
    # Build per-subject BOLD matrices keyed on clip_index -> (Y, X_idx)
    per_subj_bold: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for subj in SUBJECTS:
        X_idx, Y = build_subject_bold(subj, clip_order)
        per_subj_bold[subj] = (X_idx, Y)

    # Intersection of clip indices across subjects
    shared = set(per_subj_bold[SUBJECTS[0]][0].tolist())
    for s in SUBJECTS[1:]:
        shared &= set(per_subj_bold[s][0].tolist())
    shared_idx = np.array(sorted(shared), dtype=np.int32)
    print(f"\n[group] shared Training clips across {len(SUBJECTS)} subjects: {len(shared_idx)}")

    # Group-mean BOLD: average per-clip per-region across subjects
    group_bold = np.zeros((len(shared_idx), N_REGIONS), dtype=np.float32)
    for si, subj in enumerate(SUBJECTS):
        X_idx, Y = per_subj_bold[subj]
        id_to_pos = {int(c): i for i, c in enumerate(X_idx)}
        sub_positions = np.array([id_to_pos[int(c)] for c in shared_idx])
        Y_aligned = Y[sub_positions]  # (n_shared, 26)
        group_bold += Y_aligned / len(SUBJECTS)

    # Ridge: X (n_shared, D) -> group_bold[:, r]
    feats = {name: np.load(p).astype(np.float32) for name, p in ENCODERS}
    group_rows = []
    group_r_per_enc = {}
    for enc_name, _ in ENCODERS:
        X = feats[enc_name][shared_idx]
        r_group = ridge_cv_per_region_r(X, group_bold, alpha=ALPHA, n_folds=N_FOLDS, seed=SEED)
        group_r_per_enc[enc_name] = r_group
        for i, nm in enumerate(REGION_NAMES):
            group_rows.append({
                "region_idx": i, "region": nm, "tier": REGION_TIERS[i],
                "encoder": enc_name,
                "D": int(X.shape[1]),
                "n_clips": int(X.shape[0]),
                "r_group": float(r_group[i]) if not np.isnan(r_group[i]) else None,
                "r_individual_mean": float(np.nanmean(r_per_enc[enc_name][:, i])),
            })
    df_group = pd.DataFrame(group_rows)
    df_group.to_csv(OUT / "group_mean_per_region_r.csv", index=False)

    # Dual-scale design-intent summary
    mi_indiv_mean = float(np.nanmean(r_per_enc["mi_ram_26d"]))
    mi_group_mean = float(np.nanmean(group_r_per_enc["mi_ram_26d"]))
    print(f"\n[dual-scale] MI individual per-region mean r: {mi_indiv_mean:+.4f}")
    print(f"[dual-scale] MI group per-region mean r:      {mi_group_mean:+.4f}")
    print(f"[dual-scale] group > individual? {mi_group_mean > mi_indiv_mean}")

    # --- Step 7: pairwise_structure.csv (per region: who wins + margins) ---
    rows_struct = []
    for i, nm in enumerate(REGION_NAMES):
        rs = {enc: float(np.nanmean(r_per_enc[enc][:, i])) for enc, _ in ENCODERS}
        winner = max(rs, key=lambda k: rs[k])
        rows_struct.append({
            "region_idx": i, "region": nm, "tier": REGION_TIERS[i],
            **{f"r_mean_{enc}": rs[enc] for enc, _ in ENCODERS},
            "winner_encoder": winner,
            "mi_minus_mert": rs["mi_ram_26d"] - rs["mert_768d"],
            "mi_minus_mi_naive": rs["mi_ram_26d"] - rs["mi_naive_26d"],
            "mi_minus_random": rs["mi_ram_26d"] - rs["random_26d"],
            "r_group_mi_ram": float(group_r_per_enc["mi_ram_26d"][i]),
        })
    df_struct = pd.DataFrame(rows_struct)
    df_struct.to_csv(OUT / "pairwise_structure.csv", index=False)

    # Save also provenance JSON
    meta = {
        "seed": SEED, "alpha": ALPHA, "n_folds": N_FOLDS, "n_boot": N_BOOT,
        "n_subjects": len(SUBJECTS), "subjects": SUBJECTS,
        "n_regions": N_REGIONS,
        "training_only": True,
        "n_shared_clips_group": int(len(shared_idx)),
        "mi_individual_mean_r": mi_indiv_mean,
        "mi_group_mean_r": mi_group_mean,
        "group_gt_individual": bool(mi_group_mean > mi_indiv_mean),
        "mi_vs_mert_regions_mi_wins": int((df_mert.observed_delta_r > 0).sum()),
        "mi_vs_mert_regions_sig_95CI": int(df_mert.significant_95CI.sum()),
        "mi_vs_mert_regions_bh_fdr_q01": int(df_mert.bh_fdr_q01_reject.sum()),
        "mi_vs_naive_regions_mi_wins": int((df_naive.observed_delta_r > 0).sum()),
        "mi_vs_naive_regions_sig_95CI": int(df_naive.significant_95CI.sum()),
        "mi_vs_naive_regions_bh_fdr_q01": int(df_naive.bh_fdr_q01_reject.sum()),
        "runtime_s": round(time.time() - t0, 1),
    }
    (OUT / "meta_pairwise_group.json").write_text(json.dumps(meta, indent=2))
    print(f"\n[done] {time.time()-t0:.1f}s  meta saved.")


if __name__ == "__main__":
    main()
