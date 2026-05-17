"""Phase 10 Audio-Native Upgrade — Angle 3 — LOSO inter-rater ceiling.

Pre-registration: ../AUDIO_NATIVE_UPGRADE.md §2 Angle 3 (frozen 2026-05-16).
Engine NOT invoked (this is a pure data-side measurement on Cheung trial-level CSVs).

Computes:
  1. Pleasure LOSO ceiling — sanity-must-reproduce CHILL_STANDARD_UPGRADE.md +0.2169
     within ±0.005 (else upstream methodology error → escalate)
  2. Surprise LOSO ceiling (NEW) — measurement on data_surprise_2023.csv
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scistats

PHASE_DIR = Path(__file__).resolve().parent.parent
DATA_ROOT = PHASE_DIR.parent.parent / "Science" / "datasets" / "reward" / "cheung2024"
PLEASURE_CSV = DATA_ROOT / "data_pleasure_2023.csv"
SURPRISE_CSV = DATA_ROOT / "data_surprise_2023.csv"

OUT_DIR = PHASE_DIR / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = OUT_DIR / "angle3_loso_ceiling.json"
PER_VPID_CSV = OUT_DIR / "angle3_loso_per_vpid.csv"

SEED = 2026051222   # match CHILL_STANDARD_UPGRADE.md seed for pleasure replication
N_BOOTSTRAP = 5000
PAPER_ANCHOR_PLEASURE_CEILING = 0.2169
SANITY_TOL_PLEASURE = 0.005


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def loso_ceiling(csv_path: Path, rating_col: str, label: str) -> dict:
    """Leave-one-subject-out inter-rater Spearman ceiling.

    Pivot: 39 VPIDs × 1009 (song × chord) trials.
    Per held-out VPID: consensus = mean of N-1 others, Spearman ρ with held-out vector.
    Aggregate: Fisher-Z mean. Bootstrap 95% CI by resampling VPIDs with replacement.
    """
    print(f"\n[{label}] loading {csv_path.name} ...")
    df = pd.read_csv(csv_path)
    df.columns = [c.lstrip("﻿") for c in df.columns]

    # Sanity: required columns
    for col in ["VPID", "song", "chordnumber", rating_col]:
        if col not in df.columns:
            raise RuntimeError(f"[{label}] required column missing: {col}; have: {list(df.columns)}")

    # Aggregate within (VPID, song, chordnumber) — Cheung's own pipeline
    agg = (df.groupby(["VPID", "song", "chordnumber"], as_index=False)
             .agg({rating_col: "mean"}))
    n_vpid_raw = agg["VPID"].nunique()
    print(f"[{label}] aggregated rows: {len(agg):,}, VPIDs: {n_vpid_raw}")

    # Pivot to wide: rows = (song, chordnumber); cols = VPID; values = rating
    wide = agg.pivot_table(index=["song", "chordnumber"],
                            columns="VPID", values=rating_col, aggfunc="mean")
    print(f"[{label}] wide matrix: {wide.shape[0]} trials × {wide.shape[1]} VPIDs")
    n_complete_per_vpid = wide.notna().sum(axis=0).to_dict()

    vpids = list(wide.columns)
    per_vpid = []
    for vp in vpids:
        held = wide[vp].to_numpy(dtype=np.float64)
        others_mat = wide.drop(columns=[vp]).to_numpy(dtype=np.float64)
        consensus = np.nanmean(others_mat, axis=1)
        # Spearman on common non-NaN positions
        mask = ~(np.isnan(held) | np.isnan(consensus))
        n_valid = int(mask.sum())
        if n_valid < 30:
            rho = np.nan
            p = np.nan
        else:
            rho_val, p_val = scistats.spearmanr(held[mask], consensus[mask])
            rho = float(rho_val)
            p = float(p_val)
        per_vpid.append({"VPID": int(vp), "rho_loso": rho, "p_loso": p,
                         "n_valid": n_valid, "n_total": int(n_complete_per_vpid.get(vp, 0))})

    rhos = np.array([r["rho_loso"] for r in per_vpid if not np.isnan(r["rho_loso"])])
    # Fisher-Z mean
    z = np.arctanh(np.clip(rhos, -0.999, 0.999))
    z_mean = float(np.mean(z))
    fisher_z_rho = float(np.tanh(z_mean))

    # Bootstrap: resample VPIDs with replacement, recompute Fisher-Z mean
    rng = np.random.default_rng(SEED)
    boot_rhos = []
    n = len(rhos)
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, n, size=n)
        boot_z = np.mean(np.arctanh(np.clip(rhos[idx], -0.999, 0.999)))
        boot_rhos.append(np.tanh(boot_z))
    boot_arr = np.array(boot_rhos)
    ci_lo = float(np.quantile(boot_arr, 0.025))
    ci_hi = float(np.quantile(boot_arr, 0.975))

    return {
        "label": label,
        "csv_sha256": file_sha256(csv_path),
        "csv_bytes": csv_path.stat().st_size,
        "n_trials_raw": int(len(df)),
        "n_trials_aggregated": int(len(agg)),
        "n_vpids": int(len(vpids)),
        "n_unique_chord_rows": int(wide.shape[0]),
        "fisher_z_rho": fisher_z_rho,
        "ci95_bootstrap": [ci_lo, ci_hi],
        "rho_min": float(np.min(rhos)),
        "rho_max": float(np.max(rhos)),
        "rho_per_vpid": per_vpid,
        "n_bootstrap": N_BOOTSTRAP,
        "seed": SEED,
    }


def main() -> int:
    if not PLEASURE_CSV.exists():
        print(f"ERROR: missing {PLEASURE_CSV}", file=sys.stderr); return 2
    if not SURPRISE_CSV.exists():
        print(f"ERROR: missing {SURPRISE_CSV}", file=sys.stderr); return 2

    print("=" * 70)
    print("Phase 10 Audio-Native Upgrade — Angle 3 — LOSO ceiling")
    print(f"Pre-reg: AUDIO_NATIVE_UPGRADE.md §2 Angle 3 (frozen 2026-05-16)")
    print("=" * 70)

    pleasure = loso_ceiling(PLEASURE_CSV, "rating", "PLEASURE")
    surprise = loso_ceiling(SURPRISE_CSV, "rating", "SURPRISE")

    # Sanity check: pleasure must reproduce paper-anchor +0.2169 within ±0.005
    pleasure_match = abs(pleasure["fisher_z_rho"] - PAPER_ANCHOR_PLEASURE_CEILING) <= SANITY_TOL_PLEASURE
    sanity = {
        "paper_anchor": PAPER_ANCHOR_PLEASURE_CEILING,
        "tolerance": SANITY_TOL_PLEASURE,
        "reproduced": float(pleasure["fisher_z_rho"]),
        "abs_diff": float(abs(pleasure["fisher_z_rho"] - PAPER_ANCHOR_PLEASURE_CEILING)),
        "pass": bool(pleasure_match),
    }

    output = {
        "stage": "Phase 10 Audio-Native Upgrade — Angle 3",
        "engine_pin_commit": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "engine_invoked": False,
        "pleasure_ceiling": pleasure,
        "surprise_ceiling": surprise,
        "pleasure_sanity_check": sanity,
        "library_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {RESULTS_PATH}")

    # Per-VPID CSV
    rows = []
    for src_label, ceil in [("PLEASURE", pleasure), ("SURPRISE", surprise)]:
        for r in ceil["rho_per_vpid"]:
            rows.append({"target": src_label, **r})
    pd.DataFrame(rows).to_csv(PER_VPID_CSV, index=False)
    print(f"Wrote {PER_VPID_CSV}")

    print()
    print("=" * 70)
    print(f"PLEASURE LOSO ceiling = {pleasure['fisher_z_rho']:+.4f}  "
          f"95% CI [{pleasure['ci95_bootstrap'][0]:+.4f}, {pleasure['ci95_bootstrap'][1]:+.4f}]")
    print(f"SURPRISE LOSO ceiling = {surprise['fisher_z_rho']:+.4f}  "
          f"95% CI [{surprise['ci95_bootstrap'][0]:+.4f}, {surprise['ci95_bootstrap'][1]:+.4f}]")
    print()
    if pleasure_match:
        print(f"SANITY ✓ PASS: pleasure ceiling matches paper-anchor +{PAPER_ANCHOR_PLEASURE_CEILING:.4f} "
              f"(|Δ|={sanity['abs_diff']:.5f} ≤ {SANITY_TOL_PLEASURE})")
    else:
        print(f"SANITY ✗ FAIL: pleasure ceiling DEVIATES from paper-anchor +{PAPER_ANCHOR_PLEASURE_CEILING:.4f} "
              f"(|Δ|={sanity['abs_diff']:.5f} > {SANITY_TOL_PLEASURE})")
        print("→ ESCALATE: methodology divergence from CHILL_STANDARD_UPGRADE.md")
    print("=" * 70)
    return 0 if pleasure_match else 1


if __name__ == "__main__":
    sys.exit(main())
