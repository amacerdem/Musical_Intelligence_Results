#!/usr/bin/env python3
"""Phase 21 — Stage 4: MI encoder vs BOLD per region on Mendelssohn window.

Per pre-reg `01-METHODOLOGY-SPEC.md` Pillar 4 (HRF + residual lag) + Pillar 5
(efficiency ratio + saturation verdict, load-bearing per v1.1).

Pipeline:
  1. Load MI features from Stage 2 (80, 26) — already HRF-convolved + LPF +
     downsampled to TR=2s + N1 z-scored
  2. Load each subject's BOLD, crop to [tr_start:tr_start+80] using each
     subject's `_results.json` tr_start (Mendelssohn template-matched window)
  3. **Mendelssohn-window LOSO ceiling** — Fisher-Z mean of per-subject LOSO ρ
     where consensus = mean of N-1 subjects' BOLD; CI via cluster-bootstrap
     B=2000 (lower than Stage 3 because window is only 80 TRs, less data per
     bootstrap iteration)
  4. **MI encoder per region**: pearson(MI_features[:, r], subject_s_BOLD_window[:, r])
     across N=17 subjects → Fisher-Z mean. Lag sweep ±2 to +6s grid (in TR
     units, ±1 to +3 TRs); take best |r| per (subject, region).
  5. **Block-shuffle null** for encoder × N_PERM (preserves temporal autocorr)
  6. **Efficiency ratio + saturation verdict** per region per pre-reg §3:
       AT CEILING:  r_MI ∈ [r_ceiling_lo, r_ceiling_hi]
       BELOW:       0 < r_MI < r_ceiling_lo
       EXCEEDS:     r_MI > r_ceiling_hi (sampling-noise flag)
       AT FLOOR:    r_MI ≤ 0
  7. Per-region cohort (v1.4): SMA uses N=14 (sub-01/02/03 SMA NaN)

Output:
  data/stage4_encoder_ds002725.csv      — per-region encoder + ceiling + verdict
  results/_logs/stage4_summary.json     — headline summary

Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217
"""
from __future__ import annotations

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
BOLD_CHECKPOINTS = Path(os.environ.get(
    "DS002725_BOLD_ROOT",
    REPO_ROOT / "datasets/neuroimaging/ds002725/checkpoints",
))

DS002725_COHORT = ["sub-01", "sub-02", "sub-03", "sub-05", "sub-06", "sub-07",
                   "sub-08", "sub-09", "sub-11", "sub-12", "sub-13", "sub-14",
                   "sub-15", "sub-17", "sub-18", "sub-19", "sub-20"]

REGION_NAMES = [
    "A1_HG", "STG", "STS", "IFG", "dlPFC", "vmPFC", "OFC", "ACC", "SMA", "PMC",
    "AG", "TP", "VTA", "NAcc", "caudate", "amygdala", "hippocampus", "putamen",
    "MGB", "hypothalamus", "insula",
    "IC", "AN", "CN", "SOC", "PAG",
]
BRAINSTEM_REGION_IDX = {21, 22, 23, 24, 25}

N_TRS = 80
TR = 2.0
LAG_RANGE_S = (-2.0, 6.0)   # pre-reg §4 lag sweep
LAG_STEP_S = 1.0             # 1 TR = 1.0 s for ds002725 TR=2; we use 1 s granularity in BOLD samples = 0.5 TR
                              # but encoder uses TR units; use 1 TR steps (~2s)
SEED = 20260424
N_BOOTSTRAP = 2000
N_PERM = 5000
BLOCK_SHUFFLE_BLOCK_TRS = 10   # 20s blocks
EFFECT_FLOOR = 0.05


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def load_per_subject_bold_window(log):
    """For each subject in cohort, load BOLD + tr_start, crop to Mendelssohn window."""
    bold_window = {}
    for sub in DS002725_COHORT:
        bold_path = BOLD_CHECKPOINTS / f"{sub}_bold_26.npz"
        meta_path = BOLD_CHECKPOINTS / f"{sub}_results.json"
        d = np.load(bold_path)
        meta = json.load(open(meta_path))
        tr_start = int(meta["tr_start"])
        bold = d["bold"]
        T_full = bold.shape[0]
        if tr_start + N_TRS > T_full:
            log(f"  WARN: {sub} tr_start={tr_start} + N_TRS={N_TRS} exceeds T_full={T_full}; clamping")
            tr_start = max(0, T_full - N_TRS)
        bold_w = bold[tr_start:tr_start + N_TRS, :].astype(np.float64)
        # Pad to N_TRS if shorter (e.g., sub-01 has 930 TRs total)
        if bold_w.shape[0] < N_TRS:
            pad = np.full((N_TRS - bold_w.shape[0], bold.shape[1]), np.nan, dtype=np.float64)
            bold_w = np.concatenate([bold_w, pad], axis=0)
        bold_window[sub] = bold_w
        anchor_r = meta.get("anchor_r")
        log(f"  {sub}: tr_start={tr_start:4d}  anchor_r={anchor_r:+.3f}  bold_w shape={bold_w.shape}")
    return bold_window


def compute_per_region_results(mi_feat, bold_window, region_idx, rng_seed_base, log):
    """Per region r: LOSO ceiling + MI encoder + null."""
    n_subj = len(DS002725_COHORT)

    # Build (n_subj, 80) BOLD matrix for this region
    bold_mat = np.full((n_subj, N_TRS), np.nan)
    for i, sub in enumerate(DS002725_COHORT):
        bold_mat[i, :] = bold_window[sub][:, region_idx]
    # Per-subject N1 z-score within window
    bold_z = np.zeros_like(bold_mat)
    for i in range(n_subj):
        x = bold_mat[i]
        m = ~np.isnan(x)
        if m.sum() < 10:
            continue
        bold_z[i] = (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)

    # Valid subjects (non-fully-NaN)
    fully_nan = np.isnan(bold_mat).all(axis=1)
    valid_idx = np.where(~fully_nan)[0]
    n_valid = len(valid_idx)
    if n_valid < 4:
        return {"status": "INSUFFICIENT_N", "n_valid": n_valid}
    valid_bold = bold_z[valid_idx]

    # --- (A) LOSO ceiling on this window ---
    per_sub_r = []
    for i in range(n_valid):
        held = valid_bold[i]
        others = np.delete(valid_bold, i, axis=0)
        consensus = np.nanmean(others, axis=0)
        mask = ~(np.isnan(held) | np.isnan(consensus))
        if mask.sum() < 20:
            continue
        try:
            r, _ = scistats.pearsonr(held[mask], consensus[mask])
            if not np.isnan(r):
                per_sub_r.append(float(r))
        except Exception:
            continue
    if len(per_sub_r) < 3:
        return {"status": "TOO_FEW_LOSO_TRIALS"}
    r_ceiling_point = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_r]))

    rng = np.random.default_rng(rng_seed_base)
    boot_means = np.zeros(N_BOOTSTRAP, dtype=np.float32)
    arr = np.array(per_sub_r)
    for b in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(arr), size=len(arr))
        boot_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in arr[idx]]))
    ceiling_ci = (float(np.percentile(boot_means, 2.5)), float(np.percentile(boot_means, 97.5)))

    # --- (B) MI encoder per region with lag sweep ±2 to +6s ---
    mi_r = mi_feat[:, region_idx]  # (80,)
    mi_z = (mi_r - mi_r.mean()) / (mi_r.std() + 1e-9)
    # Lag in TR units: ±2s = ±1 TR; +6s = +3 TRs; grid: [-1, 0, +1, +2, +3]
    lag_trs = list(range(int(round(LAG_RANGE_S[0] / TR)), int(round(LAG_RANGE_S[1] / TR)) + 1))
    per_sub_mi_r = []
    per_sub_best_lag = []
    for i in range(n_valid):
        held = valid_bold[i]
        best_r = 0.0
        best_lag = 0
        for lag in lag_trs:
            # Shift MI features by lag TRs (positive = MI leads BOLD = shift MI right)
            if lag > 0:
                mi_s, bold_s = mi_z[:-lag] if lag else mi_z, held[lag:]
            elif lag < 0:
                mi_s, bold_s = mi_z[-lag:], held[:lag]
            else:
                mi_s, bold_s = mi_z, held
            mask = ~(np.isnan(mi_s) | np.isnan(bold_s))
            if mask.sum() < 20:
                continue
            try:
                r, _ = scistats.pearsonr(mi_s[mask], bold_s[mask])
                if not np.isnan(r) and abs(r) > abs(best_r):
                    best_r, best_lag = float(r), int(lag)
            except Exception:
                continue
        per_sub_mi_r.append(best_r)
        per_sub_best_lag.append(best_lag)
    r_mi_point = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_mi_r]))
    mean_lag_tr = float(np.mean(per_sub_best_lag))

    # --- (C) Block-shuffle null for encoder ---
    rng2 = np.random.default_rng(rng_seed_base + 10000)
    n_blocks = N_TRS // BLOCK_SHUFFLE_BLOCK_TRS
    null_means = np.zeros(N_PERM, dtype=np.float32)
    for b in range(N_PERM):
        block_order = rng2.permutation(n_blocks)
        mi_shuf = np.concatenate([mi_z[i * BLOCK_SHUFFLE_BLOCK_TRS:(i + 1) * BLOCK_SHUFFLE_BLOCK_TRS]
                                  for i in block_order])
        if len(mi_shuf) < N_TRS:
            mi_shuf = np.concatenate([mi_shuf, np.zeros(N_TRS - len(mi_shuf))])
        per_sub_null = []
        for i in range(n_valid):
            held = valid_bold[i]
            mask = ~(np.isnan(mi_shuf) | np.isnan(held))
            if mask.sum() < 20:
                continue
            try:
                r, _ = scistats.pearsonr(mi_shuf[mask], held[mask])
                if not np.isnan(r):
                    per_sub_null.append(float(r))
            except Exception:
                continue
        if per_sub_null:
            null_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_null]))
    p_null = float((np.abs(null_means) >= abs(r_mi_point)).sum() + 1) / (N_PERM + 1)

    # --- (D) Efficiency ratio + saturation verdict ---
    efficiency = float(r_mi_point / r_ceiling_point) if r_ceiling_point > 1e-6 else float("nan")
    efficiency_capped = float(min(efficiency, 1.0)) if not np.isnan(efficiency) else float("nan")
    if r_mi_point <= 0:
        verdict = "AT_FLOOR"
    elif ceiling_ci[0] <= r_mi_point <= ceiling_ci[1]:
        verdict = "AT_CEILING"
    elif r_mi_point > ceiling_ci[1]:
        verdict = "EXCEEDS"
    elif 0 < r_mi_point < ceiling_ci[0]:
        verdict = "BELOW_CEILING"
    else:
        verdict = "UNKNOWN"

    log(f"    [{region_idx:2d}] {REGION_NAMES[region_idx]:14s}  "
        f"r_MI={r_mi_point:+.4f}  r_ceil={r_ceiling_point:+.4f}  "
        f"eff={efficiency_capped:>5.2f}  lag={mean_lag_tr:+.1f}TR  "
        f"p_null={p_null:.4g}  verdict={verdict}")

    return {
        "status": "OK",
        "region_idx": region_idx,
        "region_name": REGION_NAMES[region_idx],
        "r_mi_point": float(r_mi_point),
        "r_ceiling_point": float(r_ceiling_point),
        "ceiling_ci_lo": ceiling_ci[0],
        "ceiling_ci_hi": ceiling_ci[1],
        "efficiency_capped": efficiency_capped,
        "p_null": p_null,
        "mean_best_lag_tr": mean_lag_tr,
        "n_valid_subjects": n_valid,
        "verdict": verdict,
    }


def main():
    t_start = time.time()
    data_dir = PHASE_ROOT / "data"
    logs_dir = PHASE_ROOT / "results" / "_logs"
    log_path = logs_dir / "stage4.log"
    log_fp = open(log_path, "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Stage 4 MI encoder + saturation verdict @ {datetime.utcnow().isoformat()}Z ===")
    log(f"Pre-reg v1.4; Mendelssohn window N_TRS={N_TRS}; TR={TR}s")
    log(f"Lag sweep: {LAG_RANGE_S} s grid step {LAG_STEP_S}s")
    log(f"N_BOOTSTRAP={N_BOOTSTRAP}; N_PERM={N_PERM}; seed={SEED}")

    # Load Stage 2 features
    mi_path = data_dir / "stage2_mi_mendelssohn.npz"
    if not mi_path.exists():
        log(f"  ERROR: Stage 2 output missing at {mi_path}")
        sys.exit(1)
    mi_data = np.load(mi_path, allow_pickle=True)
    mi_feat = mi_data["mi_feat"]
    log(f"  MI features loaded: {mi_feat.shape}")

    # Load per-subject BOLD windows
    log(f"\n  Loading per-subject BOLD Mendelssohn windows:")
    bold_window = load_per_subject_bold_window(log)

    # Per region
    log(f"\n  Computing encoder + ceiling per region:")
    results = []
    for r_idx in range(26):
        res = compute_per_region_results(mi_feat, bold_window, r_idx,
                                         rng_seed_base=SEED + r_idx, log=log)
        res["is_brainstem"] = r_idx in BRAINSTEM_REGION_IDX
        results.append(res)

    # Write CSV
    csv_path = data_dir / "stage4_encoder_ds002725.csv"
    rows = ["region_idx,region_name,is_brainstem,status,r_mi_point,r_ceiling_point,ceiling_ci_lo,ceiling_ci_hi,efficiency_capped,p_null,mean_best_lag_tr,n_valid_subjects,verdict"]
    for r in results:
        rows.append(
            f"{r.get('region_idx', '')},{r.get('region_name', '')},"
            f"{r.get('is_brainstem', '')},{r.get('status', '')},"
            f"{r.get('r_mi_point', '')},{r.get('r_ceiling_point', '')},"
            f"{r.get('ceiling_ci_lo', '')},{r.get('ceiling_ci_hi', '')},"
            f"{r.get('efficiency_capped', '')},{r.get('p_null', '')},"
            f"{r.get('mean_best_lag_tr', '')},{r.get('n_valid_subjects', '')},"
            f"{r.get('verdict', '')}"
        )
    csv_path.write_text("\n".join(rows) + "\n")
    log(f"\n  wrote: {csv_path}")

    # Headline summary
    non_brainstem = [r for r in results if not r.get("is_brainstem") and r.get("status") == "OK"]
    n_at_ceiling = sum(1 for r in non_brainstem if r["verdict"] == "AT_CEILING")
    n_exceeds = sum(1 for r in non_brainstem if r["verdict"] == "EXCEEDS")
    n_below = sum(1 for r in non_brainstem if r["verdict"] == "BELOW_CEILING")
    n_floor = sum(1 for r in non_brainstem if r["verdict"] == "AT_FLOOR")
    n_saturating = n_at_ceiling + n_exceeds

    # BH-FDR over non-brainstem regions for encoder p_null
    p_arr = np.array([r["p_null"] for r in non_brainstem])
    sorted_idx = np.argsort(p_arr)
    m = len(p_arr)
    q = (p_arr[sorted_idx] * m / (np.arange(m) + 1))
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.clip(q, 0, 1)
    bh_q = np.empty(m)
    bh_q[sorted_idx] = q
    n_q05 = int((bh_q < 0.05).sum())

    summary = {
        "_meta": {
            "phase": "21-mi-fmri-rigorous-mapping",
            "stage": 4,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pre_reg_version": "v1.4",
            "wallclock_s": time.time() - t_start,
            "n_bootstrap": N_BOOTSTRAP,
            "n_perm": N_PERM,
            "block_shuffle_block_trs": BLOCK_SHUFFLE_BLOCK_TRS,
            "seed": SEED,
        },
        "headline": {
            "n_non_brainstem_regions": len(non_brainstem),
            "n_AT_CEILING": n_at_ceiling,
            "n_EXCEEDS": n_exceeds,
            "n_BELOW_CEILING": n_below,
            "n_AT_FLOOR": n_floor,
            "n_ceiling_saturating": n_saturating,  # AT_CEILING + EXCEEDS
            "n_bh_fdr_q05": n_q05,
        },
        "per_region": non_brainstem + [r for r in results if r.get("is_brainstem")],
    }
    (logs_dir / "stage4_summary.json").write_text(json.dumps(summary, indent=2))
    log(f"  wrote: {logs_dir / 'stage4_summary.json'}")

    log(f"\n  === HEADLINE SUMMARY (21 non-brainstem regions) ===")
    log(f"    AT_CEILING:      {n_at_ceiling}")
    log(f"    EXCEEDS:         {n_exceeds}")
    log(f"    Ceiling-saturating (AT+EXCEEDS): {n_saturating}")
    log(f"    BELOW_CEILING:   {n_below}")
    log(f"    AT_FLOOR:        {n_floor}")
    log(f"    Encoder BH-FDR q<0.05: {n_q05}/21")
    log(f"  wallclock: {time.time() - t_start:.1f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
