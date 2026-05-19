#!/usr/bin/env python3
"""V-Reproduction Phase 05.6 — Cross-Dataset fMRI Consistency Analysis.

Question: Does the MI engine produce consistent per-region prediction patterns
across ds002725 (Daly 2019, N=17, continuous listening) and ds003720
(Nakai 2021, N=4, sparse-clip)?

If MI's architecture is genuine (region trajectories carry stimulus-driven
information), the per-region prediction r should show cross-dataset rank
consistency — regions that MI predicts well on one dataset should also
predict well on the other, despite different paradigms.

Three cross-dataset tests:

  (A) Per-region BOLD ceiling cross-dataset consistency
      ceiling_002725[R] vs ceiling_003720[R] over 21 non-brainstem regions
      → Pearson + Spearman + permutation null × 5000

  (B) Per-region MI encoder r cross-dataset consistency
      r_mi_002725[R] (Stage 4 Mendelssohn) vs r_mi_003720[R] (cycle-17)
      → Pearson + Spearman + permutation null × 5000

  (C) Frame-level MI feature magnitude/variance cross-dataset
      Per region, compute mean(|RAM|) and var(RAM) across all clip frames
      of ds002725 vs ds003720 → does the engine's per-region intensity
      profile carry across paradigms?

Inputs:
  V-Repro 25 stage3_ceiling_ds002725.csv (ds002725 full-scan ceiling)
  V-Repro 25 stage4_encoder_ds002725.csv (ds002725 Mendelssohn encoder)
  V-Repro 26 26_ds003720_per_region_ceiling.csv (ds003720 ceiling)
  Bold-fMRI/ds003720/06_encoding/per_subject_per_region_r.csv (encoder)
  MI per-frame .npz for both datasets

Outputs:
  data/05.6_cross_dataset_per_region.csv
  data/05.6_mi_feature_per_region.csv
  data/05.6_correlations_summary.json
  results/_logs/phase05_6.log
"""
from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import os

import numpy as np
from scipy import stats as scistats

REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE_ROOT = Path(__file__).resolve().parents[1]

# Inputs from Phase 05.3 (ds002725 ceiling + encoder)
DS002725_CEILING = REPO_ROOT / "05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17/data/stage3_ceiling_ds002725.csv"
DS002725_ENCODER = REPO_ROOT / "05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17/data/stage4_encoder_ds002725.csv"

# Inputs from Phase 05.5 (ds003720 ceiling) + external paper-time encoder CSV
DS003720_CEILING = REPO_ROOT / "05-FMRI-BRAIN-GROUNDING/05.5-ds003720-region-ceiling-N4/data/26_ds003720_per_region_ceiling.csv"
DS003720_ENCODER = Path(os.environ.get(
    "DS003720_PER_REGION_R_CSV",
    REPO_ROOT / "datasets/neuroimaging/ds003720/per_subject_per_region_r.csv",
))

# MI engine per-frame outputs (vendored in engine_outputs/)
MI_DS002725 = REPO_ROOT / "engine_outputs/neuroimaging/ds002725/per_frame"
MI_DS003720 = REPO_ROOT / "engine_outputs/neuroimaging/ds003720/per_frame"

REGION_NAMES = [
    "A1_HG", "STG", "STS", "IFG", "dlPFC", "vmPFC", "OFC", "ACC", "SMA", "PMC",
    "AG", "TP", "VTA", "NAcc", "caudate", "amygdala", "hippocampus", "putamen",
    "MGB", "hypothalamus", "insula",
    "IC", "AN", "CN", "SOC", "PAG",
]
BRAINSTEM_IDX = {21, 22, 23, 24, 25}
NON_BRAINSTEM_IDX = [i for i in range(26) if i not in BRAINSTEM_IDX]
SEED = 20260424
N_PERM = 5000


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def load_ceiling(csv_path, key="point_estimate"):
    """Map region_idx → ceiling value."""
    out = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") and row["status"] != "OK":
                continue
            try:
                r_idx = int(row["region_idx"])
                # Stage 3 uses 'point_estimate', Phase 05.5 uses 'r_ceiling'
                val_key = key if key in row else ("r_ceiling" if "r_ceiling" in row else "point_estimate")
                out[r_idx] = float(row[val_key])
            except (KeyError, ValueError):
                continue
    return out


def load_encoder_ds002725(csv_path):
    """Stage 4 encoder per region."""
    out = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") != "OK":
                continue
            try:
                out[int(row["region_idx"])] = float(row["r_mi_point"])
            except (KeyError, ValueError):
                continue
    return out


def load_encoder_ds003720(csv_path):
    """Cycle-17 per-subject per-region encoder → Fisher-Z mean per region."""
    by_region = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row["encoder"] != "mi_ram_26d":
                continue
            try:
                r_idx = int(row["region_idx"])
                by_region.setdefault(r_idx, []).append(float(row["r"]))
            except (KeyError, ValueError):
                continue
    out = {}
    for r_idx, rs in by_region.items():
        if len(rs) >= 2:
            out[r_idx] = fisher_z_inv(np.mean([fisher_z(r) for r in rs]))
    return out


def aggregate_mi_features_per_region(mi_dir, log, max_files=None):
    """Compute per-region mean|RAM| and var(RAM) across all clip frames.

    Returns: (mean_abs, var) → each (26,) numpy array.
    """
    files = sorted(mi_dir.glob("*.npz"))
    if max_files:
        files = files[:max_files]
    log(f"    aggregating {len(files)} MI clip files from {mi_dir.name}...")
    sum_abs = np.zeros(26, dtype=np.float64)
    sum_sq = np.zeros(26, dtype=np.float64)
    sum_x = np.zeros(26, dtype=np.float64)
    n_total = 0
    for f in files:
        try:
            d = np.load(f)
            if "ram" not in d.files:
                continue
            ram = d["ram"].astype(np.float64)  # (T, 26)
            if ram.ndim != 2 or ram.shape[1] != 26:
                continue
            sum_abs += np.abs(ram).sum(axis=0)
            sum_x += ram.sum(axis=0)
            sum_sq += (ram ** 2).sum(axis=0)
            n_total += ram.shape[0]
        except Exception:
            continue
    if n_total == 0:
        return np.zeros(26), np.zeros(26)
    mean_abs = sum_abs / n_total
    mean_x = sum_x / n_total
    var = sum_sq / n_total - mean_x ** 2
    return mean_abs, np.maximum(var, 0.0)


def cross_dataset_correlation(x, y, n_perm, log):
    """Pearson + Spearman + permutation null on (x, y) pair vectors."""
    mask = ~(np.isnan(x) | np.isnan(y))
    x_v, y_v = x[mask], y[mask]
    if len(x_v) < 3:
        return {"status": "INSUFFICIENT_N"}
    pearson_r, pearson_p = scistats.pearsonr(x_v, y_v)
    spearman_r, spearman_p = scistats.spearmanr(x_v, y_v)

    # Permutation null: shuffle y labels
    rng = np.random.default_rng(SEED)
    null_pearson = np.zeros(n_perm, dtype=np.float32)
    null_spearman = np.zeros(n_perm, dtype=np.float32)
    for b in range(n_perm):
        shuf = rng.permutation(len(y_v))
        try:
            null_pearson[b], _ = scistats.pearsonr(x_v, y_v[shuf])
            null_spearman[b], _ = scistats.spearmanr(x_v, y_v[shuf])
        except Exception:
            null_pearson[b] = 0
            null_spearman[b] = 0
    p_perm_pearson = float((null_pearson >= pearson_r).sum() + 1) / (n_perm + 1)
    p_perm_spearman = float((null_spearman >= spearman_r).sum() + 1) / (n_perm + 1)
    return {
        "status": "OK",
        "n_pairs": len(x_v),
        "pearson_r": float(pearson_r),
        "pearson_p_parametric": float(pearson_p),
        "pearson_p_permutation": p_perm_pearson,
        "spearman_r": float(spearman_r),
        "spearman_p_parametric": float(spearman_p),
        "spearman_p_permutation": p_perm_spearman,
        "null_pearson_mean": float(null_pearson.mean()),
        "null_pearson_std": float(null_pearson.std()),
    }


def main():
    t_start = time.time()
    data_dir = PHASE_ROOT / "data"
    logs_dir = PHASE_ROOT / "results" / "_logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_fp = open(logs_dir / "phase05_6.log", "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Phase 05.6 Cross-Dataset fMRI @ {datetime.utcnow().isoformat()}Z ===")

    log(f"\n  Loading V-Repro 25 (ds002725) ceiling + encoder...")
    c_002725 = load_ceiling(DS002725_CEILING)
    e_002725 = load_encoder_ds002725(DS002725_ENCODER)
    log(f"    ceilings: {len(c_002725)} regions  encoders: {len(e_002725)} regions")

    log(f"\n  Loading V-Repro 26 (ds003720) ceiling + cycle-17 encoder...")
    c_003720 = load_ceiling(DS003720_CEILING, key="r_ceiling")
    e_003720 = load_encoder_ds003720(DS003720_ENCODER)
    log(f"    ceilings: {len(c_003720)} regions  encoders: {len(e_003720)} regions")

    # Build per-region (ds002725, ds003720) pair vectors
    # 4 metrics: ceiling_002725, ceiling_003720, encoder_002725, encoder_003720
    log(f"\n  Per-region cross-dataset matrix:")
    log(f"  {'idx':>4} {'name':<14} {'BS':<3} {'C002725':>9} {'C003720':>9} {'E002725':>9} {'E003720':>9}")
    rows = []
    for r_idx in range(26):
        c1 = c_002725.get(r_idx, np.nan)
        c2 = c_003720.get(r_idx, np.nan)
        e1 = e_002725.get(r_idx, np.nan)
        e2 = e_003720.get(r_idx, np.nan)
        rows.append({
            "region_idx": r_idx,
            "region_name": REGION_NAMES[r_idx],
            "is_brainstem": r_idx in BRAINSTEM_IDX,
            "ceiling_002725": c1,
            "ceiling_003720": c2,
            "encoder_002725": e1,
            "encoder_003720": e2,
        })
        log(f"  {r_idx:>4} {REGION_NAMES[r_idx]:<14} {'BS' if r_idx in BRAINSTEM_IDX else '':<3} "
            f"{c1:+8.4f} {c2:+8.4f} {e1:+8.4f} {e2:+8.4f}")

    # Save per-region matrix CSV
    with open(data_dir / "05.6_cross_dataset_per_region.csv", "w") as f:
        f.write("region_idx,region_name,is_brainstem,ceiling_002725,ceiling_003720,encoder_002725,encoder_003720\n")
        for r in rows:
            f.write(f"{r['region_idx']},{r['region_name']},{r['is_brainstem']},"
                    f"{r['ceiling_002725']},{r['ceiling_003720']},"
                    f"{r['encoder_002725']},{r['encoder_003720']}\n")
    log(f"\n  wrote: {data_dir / '05.6_cross_dataset_per_region.csv'}")

    # ===== Cross-dataset correlations =====
    log(f"\n  ===  CROSS-DATASET CORRELATIONS (21 non-brainstem regions) ===")

    non_bs = [r for r in rows if not r["is_brainstem"]]
    c1_arr = np.array([r["ceiling_002725"] for r in non_bs])
    c2_arr = np.array([r["ceiling_003720"] for r in non_bs])
    e1_arr = np.array([r["encoder_002725"] for r in non_bs])
    e2_arr = np.array([r["encoder_003720"] for r in non_bs])

    log(f"\n  (A) BOLD CEILING cross-dataset (ds002725 vs ds003720):")
    A = cross_dataset_correlation(c1_arr, c2_arr, N_PERM, log)
    log(f"    Pearson  ρ = {A['pearson_r']:+.4f}  p_perm = {A['pearson_p_permutation']:.4g}  (param p = {A['pearson_p_parametric']:.4g})")
    log(f"    Spearman ρ = {A['spearman_r']:+.4f}  p_perm = {A['spearman_p_permutation']:.4g}  (param p = {A['spearman_p_parametric']:.4g})")

    log(f"\n  (B) MI ENCODER r cross-dataset (Mendelssohn ds002725 vs cycle-17 ds003720):")
    B = cross_dataset_correlation(e1_arr, e2_arr, N_PERM, log)
    log(f"    Pearson  ρ = {B['pearson_r']:+.4f}  p_perm = {B['pearson_p_permutation']:.4g}  (param p = {B['pearson_p_parametric']:.4g})")
    log(f"    Spearman ρ = {B['spearman_r']:+.4f}  p_perm = {B['spearman_p_permutation']:.4g}  (param p = {B['spearman_p_parametric']:.4g})")

    # ===== (C) MI feature magnitude/variance cross-dataset =====
    log(f"\n  (C) MI engine feature stats cross-dataset (per-region mean|RAM| + var):")
    log(f"    ds002725: aggregating per-region MI features over all clips...")
    mi_mean_002725, mi_var_002725 = aggregate_mi_features_per_region(MI_DS002725, log)
    log(f"    ds003720: aggregating per-region MI features over all clips...")
    mi_mean_003720, mi_var_003720 = aggregate_mi_features_per_region(MI_DS003720, log)

    log(f"")
    log(f"  Per-region MI feature stats:")
    log(f"  {'idx':>4} {'name':<14} {'mean|R|_002725':>15} {'mean|R|_003720':>15} {'var_002725':>12} {'var_003720':>12}")
    feat_rows = []
    for r_idx in range(26):
        row = {
            "region_idx": r_idx,
            "region_name": REGION_NAMES[r_idx],
            "is_brainstem": r_idx in BRAINSTEM_IDX,
            "mi_mean_abs_002725": float(mi_mean_002725[r_idx]),
            "mi_mean_abs_003720": float(mi_mean_003720[r_idx]),
            "mi_var_002725": float(mi_var_002725[r_idx]),
            "mi_var_003720": float(mi_var_003720[r_idx]),
        }
        feat_rows.append(row)
        log(f"  {r_idx:>4} {REGION_NAMES[r_idx]:<14} {row['mi_mean_abs_002725']:>15.5f} {row['mi_mean_abs_003720']:>15.5f} "
            f"{row['mi_var_002725']:>12.5f} {row['mi_var_003720']:>12.5f}")

    with open(data_dir / "05.6_mi_feature_per_region.csv", "w") as f:
        f.write("region_idx,region_name,is_brainstem,mi_mean_abs_002725,mi_mean_abs_003720,mi_var_002725,mi_var_003720\n")
        for r in feat_rows:
            f.write(f"{r['region_idx']},{r['region_name']},{r['is_brainstem']},"
                    f"{r['mi_mean_abs_002725']},{r['mi_mean_abs_003720']},"
                    f"{r['mi_var_002725']},{r['mi_var_003720']}\n")
    log(f"\n  wrote: {data_dir / '05.6_mi_feature_per_region.csv'}")

    # MI feature cross-dataset correlations (non-brainstem)
    mean1_arr = np.array([feat_rows[i]["mi_mean_abs_002725"] for i in NON_BRAINSTEM_IDX])
    mean2_arr = np.array([feat_rows[i]["mi_mean_abs_003720"] for i in NON_BRAINSTEM_IDX])
    var1_arr = np.array([feat_rows[i]["mi_var_002725"] for i in NON_BRAINSTEM_IDX])
    var2_arr = np.array([feat_rows[i]["mi_var_003720"] for i in NON_BRAINSTEM_IDX])

    log(f"\n  (C1) MI mean|RAM| cross-dataset:")
    C1 = cross_dataset_correlation(mean1_arr, mean2_arr, N_PERM, log)
    log(f"    Pearson  ρ = {C1['pearson_r']:+.4f}  p_perm = {C1['pearson_p_permutation']:.4g}")
    log(f"    Spearman ρ = {C1['spearman_r']:+.4f}  p_perm = {C1['spearman_p_permutation']:.4g}")

    log(f"\n  (C2) MI variance cross-dataset:")
    C2 = cross_dataset_correlation(var1_arr, var2_arr, N_PERM, log)
    log(f"    Pearson  ρ = {C2['pearson_r']:+.4f}  p_perm = {C2['pearson_p_permutation']:.4g}")
    log(f"    Spearman ρ = {C2['spearman_r']:+.4f}  p_perm = {C2['spearman_p_permutation']:.4g}")

    # ===== Verdict =====
    summary = {
        "_meta": {
            "phase": "05.6-cross-dataset-region-prediction",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "engine_sha_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
            "n_perm": N_PERM,
            "seed": SEED,
            "n_non_brainstem_regions": len(NON_BRAINSTEM_IDX),
            "wallclock_s": time.time() - t_start,
        },
        "A_bold_ceiling_cross_dataset": A,
        "B_mi_encoder_cross_dataset": B,
        "C1_mi_feature_mean_cross_dataset": C1,
        "C2_mi_feature_variance_cross_dataset": C2,
    }
    (logs_dir / "phase05_6_summary.json").write_text(json.dumps(summary, indent=2))
    (data_dir / "05.6_correlations_summary.json").write_text(json.dumps(summary, indent=2))
    log(f"\n  wrote: {logs_dir / 'phase05_6_summary.json'}")

    # ===== Headline =====
    log(f"\n  === HEADLINE ===")
    log(f"    (A) BOLD ceiling ds002725 ↔ ds003720:  Pearson {A['pearson_r']:+.3f}  Spearman {A['spearman_r']:+.3f}")
    log(f"    (B) MI encoder  ds002725 ↔ ds003720:  Pearson {B['pearson_r']:+.3f}  Spearman {B['spearman_r']:+.3f}")
    log(f"    (C1) MI mean|R| ds002725 ↔ ds003720:  Pearson {C1['pearson_r']:+.3f}  Spearman {C1['spearman_r']:+.3f}")
    log(f"    (C2) MI var(R)  ds002725 ↔ ds003720:  Pearson {C2['pearson_r']:+.3f}  Spearman {C2['spearman_r']:+.3f}")
    log(f"")
    log(f"  Interpretation:")
    log(f"    Significant cross-dataset r for MI feature stats (C1/C2) = engine produces")
    log(f"      paradigm-invariant per-region representation profiles.")
    log(f"    Significant cross-dataset r for BOLD ceilings (A) = same regions stimulus-driven")
    log(f"      in both paradigms (paradigm-invariant brain signal).")
    log(f"    Significant cross-dataset r for MI encoder r (B) = MI's prediction pattern")
    log(f"      transfers across paradigms (paradigm-invariant model behavior).")
    log(f"")
    log(f"  wallclock: {summary['_meta']['wallclock_s']:.1f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
