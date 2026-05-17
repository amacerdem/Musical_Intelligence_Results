"""compute_cheung_loso_ceiling.py — Chill-standard LOSO ceiling for Cheung 2019 pleasure ratings.

Cheung 2019 uses pleasure ratings as the target variable in the emergent
reward interaction (β_IC×ENTROPY = -0.124). MI's reproduction achieves
β = -0.158 [95% CI -0.228, -0.084].

This script computes the inter-rater predictability ceiling for Cheung's
pleasure rating itself — how reliably can the underlying rating signal be
predicted from N-1 other listeners?

Method:
  1. Pivot: VPID × (song × chordnumber) → rating
  2. For each held-out VPID: consensus = mean of N-1 OTHERS, Spearman vs held-out
  3. Fisher-Z aggregate; bootstrap CI

Output: results/cheung_loso_ceiling.json
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats as scistats

THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parents[4]
CHEUNG_CSV = PROJECT_ROOT / "Science/datasets/reward/cheung2024/data_pleasure_2023.csv"
RESULTS_DIR = THIS.parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 2026051222
N_BOOTSTRAP = 5000


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def main():
    print(f"Cheung 2019 LOSO inter-rater ceiling — pleasure rating")
    print(f"=" * 70)

    df = pd.read_csv(CHEUNG_CSV)
    print(f"  Raw trials: {len(df)} (VPIDs={df.VPID.nunique()})")

    # Build trial key (song × chord)
    df["trial"] = df["song"].astype(str) + "_" + df["chordnumber"].astype(str)
    pivot = df.pivot_table(index="VPID", columns="trial", values="rating", aggfunc="mean")
    print(f"  Pivot shape: {pivot.shape} (VPIDs × trials)")
    coverage = pivot.notna().sum(axis=1)
    print(f"  Coverage per VPID: min={coverage.min()}, median={coverage.median():.0f}, max={coverage.max()}")

    # LOSO
    vpids = pivot.index.tolist()
    rhos = []
    print(f"  Computing LOSO for {len(vpids)} VPIDs...")
    for vpid in vpids:
        held_vec = pivot.loc[vpid].values
        others = pivot.drop(vpid).mean(axis=0).values
        mask = ~np.isnan(held_vec) & ~np.isnan(others)
        if mask.sum() < 30:
            continue
        try:
            r, _ = scistats.spearmanr(held_vec[mask], others[mask])
        except Exception:
            continue
        if not np.isnan(r):
            rhos.append(float(r))

    n_trials = len(rhos)
    point_est = fisher_z_inv(np.mean([fisher_z(r) for r in rhos]))
    print(f"  N valid LOSO trials: {n_trials}")
    print(f"  Fisher-Z mean LOSO ρ: +{point_est:.4f}")
    print(f"  Range: [{min(rhos):+.4f}, {max(rhos):+.4f}]")

    # Bootstrap CI
    rng = np.random.default_rng(SEED)
    arr = np.array(rhos)
    boot = np.empty(N_BOOTSTRAP)
    for i in range(N_BOOTSTRAP):
        idx = rng.integers(0, n_trials, size=n_trials)
        boot[i] = fisher_z_inv(np.mean([fisher_z(r) for r in arr[idx]]))
    ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
    print(f"  95% bootstrap CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

    # MI vs ceiling
    print(f"")
    print(f"  Comparison:")
    print(f"    Cheung 2019 published β_IC×ENTROPY: -0.124")
    print(f"    MI engine reproduction β: -0.158 (95% CI [-0.228, -0.084], includes published)")
    print(f"")
    print(f"  IMPORTANT: The Cheung interaction β is a regression coefficient (not Spearman ρ),")
    print(f"  so it cannot be directly compared to LOSO ρ ceiling. However, the LOSO ceiling")
    print(f"  on PLEASURE rating quantifies the underlying signal's stability:")
    print(f"    LOSO ceiling = +{point_est:.4f} → 'humans agree at ρ={point_est:.3f} on pleasure ratings'")
    print(f"")
    print(f"  Cheung's M3 model held-out r = +0.615 (paper Phase 05)")
    print(f"    → MI captures {0.615/point_est*100:.1f}% of the inter-rater predictability ceiling")

    summary = {
        "_schema": "Cheung 2019 pleasure rating LOSO inter-rater ceiling",
        "_computed_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "_seed": SEED,
        "_n_bootstrap": N_BOOTSTRAP,
        "n_trials_total": len(df),
        "n_vpids": int(df.VPID.nunique()),
        "n_loso_trials": n_trials,
        "loso_point_estimate": point_est,
        "loso_ci_95": list(ci),
        "min_loso_rho": float(min(rhos)),
        "max_loso_rho": float(max(rhos)),
        "cheung_published_beta": -0.124,
        "mi_reproduction_beta": -0.158,
        "mi_reproduction_ci": [-0.228, -0.084],
        "mi_m3_held_out_r": 0.615,
        "mi_m3_ceiling_relative_pct": 0.615 / point_est * 100,
    }
    out = RESULTS_DIR / "cheung_loso_ceiling.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
