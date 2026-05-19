#!/usr/bin/env python3
"""V-Reproduction Phase 05.5 — ds003720 per-region cross-subject LOSO ceiling.

Companion to V-Reproduction Phase 05.4 (which is voxelwise, paper-canonical).
This package adds CEILING-SATURATION analysis at the per-region scale.

Source data:
  Cycle-17 RunPod-Exp-01 ckpt_bold:
    Science/V2/reviewer-sims/divan-major-revision-2026-04-22/
      computing-phase/T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold/
    sub-XXX_{Training|Test}_run-{NN}.npy → (410, 26) per run

  Per-subject encoder r:
    Science/Bold-fMRI/ds003720/06_encoding/per_subject_per_region_r.csv

Pipeline:
  1. For each subject S ∈ {sub-001, sub-002, sub-003, sub-004, sub-005}:
     - Load all 15 runs → concatenate → (6150, 26) BOLD timeseries
     - Per-region within-subject z-score
  2. Per region R (26 total, 21 non-brainstem):
     - For each held-out S, consensus = mean of N-1 other subjects' BOLD
     - r_LOSO[S, R] = pearson(consensus, S's BOLD)
     - Fisher-Z mean across S → r_ceiling(R)
     - Cluster-bootstrap over subjects → 95% CI
     - Circular-shift null × 5000 → p_null
  3. Compare to existing per-subject per-region encoder r values
     (cycle-17 per_subject_per_region_r.csv mi_ram_26d):
     - Fisher-Z mean across N subjects → r_MI(R)
     - Saturation verdict per region

Outputs:
  data/05.5_ds003720_per_region_ceiling.csv
  data/05.5_ds003720_per_region_saturation.csv
  data/05.5_ds003720_manifest.json

Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217
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

# Paper-time fMRI BOLD checkpoints and per-region encoding outputs live
# outside MI_Results. Set DS003720_BOLD_ROOT to override defaults.
CKPT_BOLD = Path(os.environ.get(
    "DS003720_BOLD_ROOT",
    REPO_ROOT / "datasets/neuroimaging/ds003720/checkpoints",
))
PER_REGION_R_CSV = Path(os.environ.get(
    "DS003720_PER_REGION_R_CSV",
    REPO_ROOT / "datasets/neuroimaging/ds003720/per_subject_per_region_r.csv",
))

# Subjects: all 5, but Phase 05.4 paper QC excludes sub-002
# We compute ceiling on N=4 (paper-canonical QC) but expose N=5 figures for context
COHORT_N4 = ["sub-001", "sub-003", "sub-004", "sub-005"]
COHORT_N5 = ["sub-001", "sub-002", "sub-003", "sub-004", "sub-005"]

REGION_NAMES = [
    "A1_HG", "STG", "STS", "IFG", "dlPFC", "vmPFC", "OFC", "ACC", "SMA", "PMC",
    "AG", "TP", "VTA", "NAcc", "caudate", "amygdala", "hippocampus", "putamen",
    "MGB", "hypothalamus", "insula",
    "IC", "AN", "CN", "SOC", "PAG",
]
BRAINSTEM_IDX = {21, 22, 23, 24, 25}

SEED = 20260424
N_BOOTSTRAP = 5000
N_PERM = 5000
EFFECT_FLOOR = 0.05


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def load_subject_concatenated_bold(sub: str, log) -> np.ndarray | None:
    """Concatenate all 15 runs (T per run, 26 regions) → (T_total, 26)."""
    files = sorted(CKPT_BOLD.glob(f"{sub}_*.npy"))
    if len(files) != 15:
        log(f"    {sub}: expected 15 runs, got {len(files)}")
        return None
    parts = []
    for f in files:
        a = np.load(f).astype(np.float64)
        if a.shape != (410, 26):
            log(f"    {sub}: bad shape {f.name} {a.shape}")
            return None
        parts.append(a)
    return np.concatenate(parts, axis=0)


def compute_per_region_ceiling(bold_stack: np.ndarray, region_idx: int, log) -> dict:
    """LOSO ceiling for one region.

    Args:
        bold_stack: (N_subj, T, 26) BOLD.
        region_idx: int region column.

    Returns: dict with point + CI + null p + per_sub_r.
    """
    N, T, R = bold_stack.shape
    region_data = bold_stack[:, :, region_idx]  # (N, T)

    # Per-subject z-score
    bold_z = np.zeros_like(region_data)
    for i in range(N):
        x = region_data[i]
        bold_z[i] = (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)

    # LOSO
    per_sub_r = []
    for i in range(N):
        held = bold_z[i]
        others = np.delete(bold_z, i, axis=0)
        consensus = np.nanmean(others, axis=0)
        mask = ~(np.isnan(held) | np.isnan(consensus))
        if mask.sum() < 50:
            continue
        try:
            r, _ = scistats.pearsonr(held[mask], consensus[mask])
            if not np.isnan(r):
                per_sub_r.append(float(r))
        except Exception:
            continue
    if len(per_sub_r) < 2:
        return {"status": "INSUFFICIENT_N"}

    point = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_r]))

    # Cluster bootstrap
    rng = np.random.default_rng(SEED + region_idx)
    arr = np.array(per_sub_r)
    boot_means = np.zeros(N_BOOTSTRAP, dtype=np.float32)
    for b in range(N_BOOTSTRAP):
        idx = rng.integers(0, len(arr), size=len(arr))
        boot_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in arr[idx]]))
    ci_lo = float(np.percentile(boot_means, 2.5))
    ci_hi = float(np.percentile(boot_means, 97.5))

    # Circular-shift null
    rng2 = np.random.default_rng(SEED + 1000 + region_idx)
    null_means = np.zeros(N_PERM, dtype=np.float32)
    for b in range(N_PERM):
        per_sub_null = []
        for i in range(N):
            shift = int(rng2.integers(T // 10, 9 * T // 10))
            shifted = np.roll(bold_z[i], shift)
            others = np.delete(bold_z, i, axis=0)
            consensus = np.nanmean(others, axis=0)
            mask = ~(np.isnan(shifted) | np.isnan(consensus))
            if mask.sum() < 50:
                continue
            try:
                r, _ = scistats.pearsonr(shifted[mask], consensus[mask])
                if not np.isnan(r):
                    per_sub_null.append(float(r))
            except Exception:
                continue
        if per_sub_null:
            null_means[b] = fisher_z_inv(np.mean([fisher_z(r) for r in per_sub_null]))
    p_null = float((np.abs(null_means) >= abs(point)).sum() + 1) / (N_PERM + 1)

    return {
        "status": "OK",
        "point_estimate": float(point),
        "ci_95_lo": ci_lo,
        "ci_95_hi": ci_hi,
        "n_loso_trials": len(per_sub_r),
        "p_null": p_null,
        "passes_floor": bool(point > EFFECT_FLOOR),
    }


def load_per_subject_encoder_r(cohort) -> dict:
    """Load cycle-17 per-subject per-region mi_ram_26d encoder r → region_idx → list of r."""
    by_region = {}
    with open(PER_REGION_R_CSV) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row["encoder"] != "mi_ram_26d":
                continue
            if row["subject"] not in cohort:
                continue
            r_idx = int(row["region_idx"])
            try:
                r = float(row["r"])
                by_region.setdefault(r_idx, []).append(r)
            except ValueError:
                continue
    return by_region


def saturation_verdict(r_mi: float, ceiling_ci: tuple) -> str:
    if r_mi <= 0:
        return "AT_FLOOR"
    if ceiling_ci[0] <= r_mi <= ceiling_ci[1]:
        return "AT_CEILING"
    if r_mi > ceiling_ci[1]:
        return "EXCEEDS"
    return "BELOW_CEILING"


def main():
    t_start = time.time()
    data_dir = PHASE_ROOT / "data"
    logs_dir = PHASE_ROOT / "results" / "_logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "phase05_5.log"
    log_fp = open(log_path, "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Phase 05.5 ds003720 per-region ceiling @ {datetime.utcnow().isoformat()}Z ===")

    # Load N=4 cohort BOLD
    log(f"\n  Loading N=4 paper-canonical cohort:")
    bold_by_sub = {}
    for sub in COHORT_N4:
        bold = load_subject_concatenated_bold(sub, log)
        if bold is None:
            log(f"    {sub}: SKIP")
            continue
        bold_by_sub[sub] = bold
        log(f"    {sub}: shape={bold.shape}")
    if len(bold_by_sub) < 3:
        log(f"  ERROR: insufficient cohort ({len(bold_by_sub)} subjects)")
        sys.exit(1)
    cohort = list(bold_by_sub.keys())

    # Stack: (N, T, 26)
    T = min(b.shape[0] for b in bold_by_sub.values())
    bold_stack = np.stack([bold_by_sub[s][:T] for s in cohort], axis=0)
    log(f"\n  Stacked BOLD: {bold_stack.shape}")

    # Per-region ceiling
    log(f"\n  Per-region LOSO ceiling (cluster-bootstrap × {N_BOOTSTRAP}, circular-shift null × {N_PERM}):")
    log(f"  {'idx':>4} {'name':<14} {'BS':<3} {'ceiling':>10} {'95% CI':<25} {'p_null':>9} {'pass_floor':<10}")
    ceiling_results = []
    for r_idx in range(26):
        is_bs = r_idx in BRAINSTEM_IDX
        res = compute_per_region_ceiling(bold_stack, r_idx, log)
        if res.get("status") != "OK":
            log(f"  {r_idx:>4} {REGION_NAMES[r_idx]:<14} {'BS' if is_bs else '':<3} {'INSUFFICIENT_N':>30}")
            ceiling_results.append({"region_idx": r_idx, "region_name": REGION_NAMES[r_idx],
                                    "is_brainstem": is_bs, "status": "INSUFFICIENT_N"})
            continue
        ci_str = f"[{res['ci_95_lo']:+.3f}, {res['ci_95_hi']:+.3f}]"
        log(f"  {r_idx:>4} {REGION_NAMES[r_idx]:<14} {'BS' if is_bs else '':<3} "
            f"{res['point_estimate']:>+10.4f} {ci_str:<25} {res['p_null']:>9.4g} "
            f"{'PASS' if res['passes_floor'] and res['p_null']<0.05 else 'fail':<10}")
        ceiling_results.append({
            "region_idx": r_idx,
            "region_name": REGION_NAMES[r_idx],
            "is_brainstem": is_bs,
            "status": "OK",
            **res,
        })

    # Per-region MI encoder r (Fisher-Z mean across cohort)
    log(f"\n  Per-region MI encoder r (from cycle-17 per_subject_per_region_r.csv):")
    encoder_by_region = load_per_subject_encoder_r(cohort)
    encoder_fz = {}
    for r_idx, rs in encoder_by_region.items():
        if len(rs) < 2:
            continue
        encoder_fz[r_idx] = fisher_z_inv(np.mean([fisher_z(r) for r in rs]))

    # Saturation verdict
    sat_results = []
    log(f"\n  Saturation verdict (r_MI vs ceiling CI):")
    log(f"  {'idx':>4} {'name':<14} {'BS':<3} {'r_MI':>9} {'r_ceil':>9} {'eff':>6} {'verdict':<16}")
    n_at_ceiling = 0; n_exceeds = 0; n_below = 0; n_floor = 0
    for c in ceiling_results:
        r_idx = c["region_idx"]
        is_bs = c["is_brainstem"]
        if c.get("status") != "OK":
            continue
        r_mi = encoder_fz.get(r_idx)
        if r_mi is None:
            continue
        verdict = saturation_verdict(r_mi, (c["ci_95_lo"], c["ci_95_hi"]))
        if c["point_estimate"] > 1e-6:
            eff = float(min(r_mi / c["point_estimate"], 1.0))
        else:
            eff = float("nan")
        log(f"  {r_idx:>4} {c['region_name']:<14} {'BS' if is_bs else '':<3} "
            f"{r_mi:+9.4f} {c['point_estimate']:+9.4f} {eff:>6.2f} {verdict:<16}")
        sat_results.append({
            "region_idx": r_idx,
            "region_name": c["region_name"],
            "is_brainstem": is_bs,
            "r_mi": float(r_mi),
            "r_ceiling": float(c["point_estimate"]),
            "ceiling_ci_lo": c["ci_95_lo"],
            "ceiling_ci_hi": c["ci_95_hi"],
            "efficiency_capped": eff,
            "p_null": c["p_null"],
            "verdict": verdict,
        })
        if not is_bs:
            if verdict == "AT_CEILING": n_at_ceiling += 1
            elif verdict == "EXCEEDS": n_exceeds += 1
            elif verdict == "BELOW_CEILING": n_below += 1
            elif verdict == "AT_FLOOR": n_floor += 1

    # Save CSV: ceiling
    with open(data_dir / "05.5_ds003720_per_region_ceiling.csv", "w") as f:
        f.write("region_idx,region_name,is_brainstem,status,r_ceiling,ci_95_lo,ci_95_hi,p_null,n_loso_trials,passes_floor\n")
        for c in ceiling_results:
            if c.get("status") != "OK":
                f.write(f"{c['region_idx']},{c['region_name']},{c['is_brainstem']},{c.get('status')},,,,,,\n")
            else:
                f.write(f"{c['region_idx']},{c['region_name']},{c['is_brainstem']},OK,"
                        f"{c['point_estimate']},{c['ci_95_lo']},{c['ci_95_hi']},"
                        f"{c['p_null']},{c['n_loso_trials']},{c['passes_floor']}\n")
    log(f"\n  wrote: {data_dir / '05.5_ds003720_per_region_ceiling.csv'}")

    # Save CSV: saturation
    with open(data_dir / "05.5_ds003720_per_region_saturation.csv", "w") as f:
        f.write("region_idx,region_name,is_brainstem,r_mi,r_ceiling,ceiling_ci_lo,ceiling_ci_hi,efficiency_capped,p_null,verdict\n")
        for r in sat_results:
            f.write(f"{r['region_idx']},{r['region_name']},{r['is_brainstem']},"
                    f"{r['r_mi']},{r['r_ceiling']},{r['ceiling_ci_lo']},{r['ceiling_ci_hi']},"
                    f"{r['efficiency_capped']},{r['p_null']},{r['verdict']}\n")
    log(f"  wrote: {data_dir / '05.5_ds003720_per_region_saturation.csv'}")

    # Manifest
    n_pass_floor = sum(1 for c in ceiling_results
                       if c.get("status") == "OK" and c.get("passes_floor")
                       and c.get("p_null", 1.0) < 0.05 and not c["is_brainstem"])
    n_saturating = n_at_ceiling + n_exceeds

    manifest = {
        "phase": "05.5-ds003720-region-ceiling-N4",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "engine_sha_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "cohort_used": cohort,
        "n_subjects": len(cohort),
        "n_bootstrap": N_BOOTSTRAP,
        "n_perm": N_PERM,
        "seed": SEED,
        "headline_ceiling_pass_floor_q05_non_brainstem": int(n_pass_floor),
        "headline_saturation_at_ceiling": int(n_at_ceiling),
        "headline_saturation_exceeds": int(n_exceeds),
        "headline_saturation_below": int(n_below),
        "headline_saturation_floor": int(n_floor),
        "headline_saturation_total_non_brainstem": int(n_saturating),
        "wallclock_s": time.time() - t_start,
    }
    (data_dir / "05.5_ds003720_manifest.json").write_text(json.dumps(manifest, indent=2))
    log(f"  wrote: {data_dir / '05.5_ds003720_manifest.json'}")

    log(f"\n  === HEADLINE SUMMARY (N={len(cohort)}) ===")
    log(f"    Ceiling pass (floor + p_null<0.05, non-brainstem): {n_pass_floor}/21")
    log(f"    Saturation verdict (non-brainstem 21 regions):")
    log(f"      AT_CEILING:      {n_at_ceiling}")
    log(f"      EXCEEDS:         {n_exceeds}")
    log(f"      Ceiling-saturating (AT+EXCEEDS): {n_saturating}")
    log(f"      BELOW_CEILING:   {n_below}")
    log(f"      AT_FLOOR:        {n_floor}")
    log(f"  wallclock: {manifest['wallclock_s']:.1f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
