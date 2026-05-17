#!/usr/bin/env python3
"""Phase 21 — Stage 3: LOSO inter-subject ceiling per region (PRIMARY metric).

Per pre-reg §3 (`01-METHODOLOGY-SPEC.md` Pillar 3):
  For each region r, for each held-out subject s:
    c_{r,s}(t) = mean_{s'≠s} x_{s',r}(t)         # consensus from N-1 others
    r_loso[s,r] = pearson(c_{r,s}, x_{s,r})       # held-out prediction
  r_ceiling(r) = Fisher-z mean over s
  CI 95% via cluster-bootstrap over subjects (B=5000, seed=20260424)
  Significance via circular-timepoint-shift null (B=5000)

ds002725: N=17 paper-canonical cohort, BOLD shape (934, 26).
  Per-region cohort (v1.4): sub-01/02/03 missing region 8 (SMA);
  SMA-only analysis uses N=14, others N=17.

ds003720: N=4 QC-pass (sub-001/003/004/005), voxelwise per_clip
  → first ROI-aggregated to 26 regions, then same LOSO protocol.
  v1.2 per-genre stratification (10 × 24 × 15s clips).

Output:
  data/stage3_ceiling_ds002725.csv       — per-region ceiling + CI + null p
  data/stage3_ceiling_ds003720.csv       — per-region ceiling + CI + null p
  data/stage3_ceiling_ds003720_per_genre.csv  — 10 × 21 per-genre ceiling matrix
  results/_logs/stage3_summary.json       — headline numbers

Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scistats


SCIENCE_ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science")
PHASE21_ROOT = SCIENCE_ROOT / "V8-Additional-fMRI/21-mi-fmri-rigorous-mapping"

DS002725_BOLD = SCIENCE_ROOT / "Bold-fMRI/exp-02-cross-subject-17/checkpoints"
DS002725_COHORT = ["sub-01", "sub-02", "sub-03", "sub-05", "sub-06", "sub-07",
                   "sub-08", "sub-09", "sub-11", "sub-12", "sub-13", "sub-14",
                   "sub-15", "sub-17", "sub-18", "sub-19", "sub-20"]

# 26-region order (paper RAM table)
REGION_NAMES = [
    "A1_HG", "STG", "STS", "IFG", "dlPFC", "vmPFC", "OFC", "ACC", "SMA", "PMC",
    "AG", "TP", "VTA", "NAcc", "caudate", "amygdala", "hippocampus", "putamen",
    "MGB", "hypothalamus", "insula",
    "IC", "AN", "CN", "SOC", "PAG",  # brainstem (excluded per Beissner 2015)
]
BRAINSTEM_REGION_IDX = {21, 22, 23, 24, 25}
NON_BRAINSTEM_IDX = [i for i in range(26) if i not in BRAINSTEM_REGION_IDX]

SEED = 20260424
N_BOOTSTRAP = 5000
N_PERM = 5000
EFFECT_FLOOR = 0.05  # Hasson 2010 entry-gate floor


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def load_ds002725_cohort_bold(log):
    """Return dict {subject: (T, 26) BOLD array} for full N=17."""
    bold_by_subject = {}
    for sub in DS002725_COHORT:
        npz_path = DS002725_BOLD / f"{sub}_bold_26.npz"
        d = np.load(npz_path)
        bold_by_subject[sub] = d["bold"].astype(np.float64)
    # Determine minimum length for cross-subject alignment
    min_len = min(b.shape[0] for b in bold_by_subject.values())
    if log:
        log(f"  ds002725 cohort loaded: {len(bold_by_subject)} subjects, BOLD lengths: "
            f"{[b.shape[0] for b in bold_by_subject.values()]}; trimming to T={min_len}")
    # Trim all to min_len, stack to (N, T, 26)
    bold_array = np.stack([bold_by_subject[s][:min_len] for s in DS002725_COHORT], axis=0)
    return bold_array, DS002725_COHORT, min_len


def compute_loso_ceiling_per_region(bold_array, region_idx, log):
    """LOSO ceiling for one region.

    Args:
        bold_array: (N, T, 26) BOLD; NaN-tolerant.
        region_idx: int region column to test.

    Returns: dict with point_estimate, ci_95, n_loso_trials, per_subject_r,
             and null p-value.
    """
    N, T, R = bold_array.shape
    region_data = bold_array[:, :, region_idx]  # (N, T)

    # Identify subjects with valid (non-fully-NaN) data for this region
    per_sub_nan = np.isnan(region_data).all(axis=1)
    valid_idx = np.where(~per_sub_nan)[0]
    n_valid = len(valid_idx)
    if n_valid < 4:
        return {"status": "INSUFFICIENT_N", "n_valid": n_valid}

    valid_data = region_data[valid_idx]  # (n_valid, T)
    # Z-score within subject (N1 normalization)
    valid_z = np.zeros_like(valid_data)
    for i in range(n_valid):
        x = valid_data[i]
        m = ~np.isnan(x)
        if m.sum() < 10:
            continue
        valid_z[i] = (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)

    # LOSO loop
    per_sub_r = []
    for i in range(n_valid):
        held = valid_z[i]
        others_mask = np.ones(n_valid, dtype=bool)
        others_mask[i] = False
        consensus = np.nanmean(valid_z[others_mask], axis=0)
        valid_t = ~(np.isnan(held) | np.isnan(consensus))
        if valid_t.sum() < 20:
            continue
        try:
            r, _ = scistats.pearsonr(held[valid_t], consensus[valid_t])
            if not np.isnan(r):
                per_sub_r.append(float(r))
        except Exception:
            continue

    if len(per_sub_r) < 3:
        return {"status": "TOO_FEW_LOSO_TRIALS", "n_loso_trials": len(per_sub_r)}

    point = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_r]))

    # Cluster-bootstrap over subjects
    rng = np.random.default_rng(SEED + region_idx)
    arr = np.array(per_sub_r)
    boot_means = np.zeros(N_BOOTSTRAP, dtype=np.float32)
    for b in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(arr), size=len(arr))
        boot_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in arr[idx]]))
    ci_lo, ci_hi = float(np.percentile(boot_means, 2.5)), float(np.percentile(boot_means, 97.5))

    # Circular-shift null
    rng2 = np.random.default_rng(SEED + 1000 + region_idx)
    null_means = np.zeros(N_PERM, dtype=np.float32)
    T_eff = valid_z.shape[1]
    for b in range(N_PERM):
        per_sub_null = []
        for i in range(n_valid):
            shift = int(rng2.integers(T_eff // 10, 9 * T_eff // 10))
            shifted = np.roll(valid_z[i], shift)
            others_mask = np.ones(n_valid, dtype=bool)
            others_mask[i] = False
            consensus = np.nanmean(valid_z[others_mask], axis=0)
            valid_t = ~(np.isnan(shifted) | np.isnan(consensus))
            if valid_t.sum() < 20:
                continue
            try:
                r, _ = scistats.pearsonr(shifted[valid_t], consensus[valid_t])
                if not np.isnan(r):
                    per_sub_null.append(float(r))
            except Exception:
                continue
        if per_sub_null:
            null_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_null]))
    p_null = float((np.abs(null_means) >= abs(point)).sum() + 1) / (N_PERM + 1)

    if log:
        log(f"    [{region_idx:2d}] {REGION_NAMES[region_idx]:10s}  "
            f"r_ceiling={point:+.4f}  [95% CI {ci_lo:+.4f}, {ci_hi:+.4f}]  "
            f"p_null={p_null:.4g}  N_loso={len(per_sub_r)}")

    return {
        "status": "OK",
        "region_idx": region_idx,
        "region_name": REGION_NAMES[region_idx],
        "point_estimate": float(point),
        "ci_95_lo": ci_lo,
        "ci_95_hi": ci_hi,
        "n_loso_trials": len(per_sub_r),
        "n_valid_subjects": n_valid,
        "p_null": p_null,
        "passes_floor": bool(point > EFFECT_FLOOR),
    }


def run_ds002725(log):
    log(f"\n--- Stage 3: ds002725 LOSO ceiling (N=17, 26 regions) ---")
    bold_array, cohort, T = load_ds002725_cohort_bold(log)
    log(f"  BOLD stack shape: {bold_array.shape}; N={len(cohort)}, T={T}")

    results = []
    for r_idx in range(26):
        is_brainstem = r_idx in BRAINSTEM_REGION_IDX
        log(f"  region {r_idx:2d} {REGION_NAMES[r_idx]:10s} ({'brainstem' if is_brainstem else 'cortical/subcortical'})")
        res = compute_loso_ceiling_per_region(bold_array, r_idx, log)
        res["is_brainstem"] = is_brainstem
        results.append(res)

    return results


def write_ceiling_csv(results, output_path):
    rows = ["region_idx,region_name,is_brainstem,status,point_estimate,ci_95_lo,ci_95_hi,p_null,n_loso_trials,n_valid_subjects,passes_floor"]
    for r in results:
        rows.append(
            f"{r.get('region_idx', '')},{r.get('region_name', '')},"
            f"{r.get('is_brainstem', '')},{r.get('status', '')},"
            f"{r.get('point_estimate', '')},{r.get('ci_95_lo', '')},{r.get('ci_95_hi', '')},"
            f"{r.get('p_null', '')},{r.get('n_loso_trials', '')},{r.get('n_valid_subjects', '')},"
            f"{r.get('passes_floor', '')}"
        )
    output_path.write_text("\n".join(rows) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=["ds002725"],
                        choices=["ds002725", "ds003720", "both"])
    args = parser.parse_args()

    t_start = time.time()
    data_dir = PHASE21_ROOT / "data"
    logs_dir = PHASE21_ROOT / "results" / "_logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "stage3.log"
    log_fp = open(log_path, "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Stage 3 LOSO ceiling @ {datetime.utcnow().isoformat()}Z ===")
    log(f"Pre-reg v1.4; N_BOOTSTRAP={N_BOOTSTRAP}; N_PERM={N_PERM}; seed={SEED}")

    summary = {}

    if "ds002725" in args.datasets or "both" in args.datasets:
        results_ds002725 = run_ds002725(log)
        write_ceiling_csv(results_ds002725, data_dir / "stage3_ceiling_ds002725.csv")
        log(f"  wrote: {data_dir / 'stage3_ceiling_ds002725.csv'}")
        # Headline summary: regions passing floor & q < 0.05
        n_pass_floor = sum(1 for r in results_ds002725
                          if r.get("status") == "OK" and r.get("passes_floor") and not r.get("is_brainstem"))
        # BH-FDR over 21 non-brainstem regions
        p_vals = [r.get("p_null", 1.0) for r in results_ds002725
                  if r.get("status") == "OK" and not r.get("is_brainstem")]
        p_arr = np.array(p_vals)
        sorted_idx = np.argsort(p_arr)
        m = len(p_arr)
        q_vals = np.minimum.accumulate((p_arr[sorted_idx] * m / (np.arange(m) + 1))[::-1])[::-1]
        q_vals = np.clip(q_vals, 0, 1)
        bh_q = np.empty(m)
        bh_q[sorted_idx] = q_vals
        n_pass_q05 = int((bh_q < 0.05).sum())
        summary["ds002725"] = {
            "n_non_brainstem": 21,
            "n_pass_effect_floor": n_pass_floor,
            "n_pass_BH_q05": n_pass_q05,
            "regions": [
                {"name": r.get("region_name"), "r": r.get("point_estimate"),
                 "ci_lo": r.get("ci_95_lo"), "ci_hi": r.get("ci_95_hi"),
                 "p_null": r.get("p_null"), "passes_floor": r.get("passes_floor")}
                for r in results_ds002725 if r.get("status") == "OK"
            ],
        }
        log(f"\n  ds002725 SUMMARY:")
        log(f"    regions passing effect floor (r > {EFFECT_FLOOR}): {n_pass_floor}/21 non-brainstem")
        log(f"    regions passing BH-FDR q < 0.05: {n_pass_q05}/21 non-brainstem")

    if "ds003720" in args.datasets or "both" in args.datasets:
        log(f"\n--- Stage 3: ds003720 LOSO ceiling (DEFERRED: requires ROI extraction from voxelwise cache) ---")
        log(f"  Skipping ds003720 for now (Stage 1 ds003720 ROI extract not yet built)")
        summary["ds003720"] = {"status": "DEFERRED", "reason": "Stage 1 ROI extract not yet built"}

    summary["_meta"] = {
        "phase": "21-mi-fmri-rigorous-mapping",
        "stage": 3,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pre_reg_version": "v1.4",
        "n_bootstrap": N_BOOTSTRAP,
        "n_perm": N_PERM,
        "seed": SEED,
        "wallclock_s": time.time() - t_start,
    }
    (logs_dir / "stage3_summary.json").write_text(json.dumps(summary, indent=2))
    log(f"\n  wrote: {logs_dir / 'stage3_summary.json'}")
    log(f"  wallclock: {summary['_meta']['wallclock_s']:.1f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
