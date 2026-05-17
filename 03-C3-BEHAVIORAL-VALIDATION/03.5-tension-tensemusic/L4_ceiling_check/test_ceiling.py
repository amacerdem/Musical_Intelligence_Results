"""L4 — Reproduce LOSO inter-rater ceiling +0.386 [95% CI 0.36, 0.41].

Re-runs compute_tensemusic_loso_ceiling.py logic inline and checks the
ceiling matches paper-time baseline within tolerance.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scistats


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def _compute_ceiling(tensemusic_dir: Path) -> tuple[float, int, int]:
    rho_per_trial = []
    n_pieces = 0
    for csv_path in sorted(tensemusic_dir.glob("*.csv")):
        df = pd.read_csv(csv_path)
        rating_cols = [c for c in df.columns if c.startswith("rating") and c[len("rating"):].isdigit()]
        if len(rating_cols) < 2:
            continue
        rater_trajs = []
        for c in rating_cols:
            traj = df[c].values.astype(np.float64)
            if not np.all(np.isnan(traj)) and np.nanstd(traj) > 1e-6:
                rater_trajs.append(traj)
        if len(rater_trajs) < 2:
            continue
        n_pieces += 1
        for i in range(len(rater_trajs)):
            others = [rater_trajs[j] for j in range(len(rater_trajs)) if j != i]
            consensus = np.nanmean(others, axis=0)
            held = rater_trajs[i]
            mask = ~np.isnan(consensus) & ~np.isnan(held)
            if mask.sum() < 50:
                continue
            try:
                r, _ = scistats.spearmanr(consensus[mask], held[mask])
            except Exception:
                continue
            if not np.isnan(r):
                rho_per_trial.append(float(r))
    if not rho_per_trial:
        return float("nan"), 0, 0
    point = fisher_z_inv(np.mean([fisher_z(r) for r in rho_per_trial]))
    return point, len(rho_per_trial), n_pieces


def test_ceiling_reproduces(tensemusic_data_dir, paper_baseline):
    point, n_trials, n_pieces = _compute_ceiling(tensemusic_data_dir)
    expected = paper_baseline["loso_ceiling"]["point_estimate"]
    tol = paper_baseline["tolerance"]["ceiling_abs"]
    assert abs(point - expected) < tol, (
        f"Ceiling drift outside tolerance:\n"
        f"  expected: {expected:.4f}\n"
        f"  actual:   {point:.4f}\n"
        f"  diff:     {abs(point-expected):.4f}\n"
        f"  tol:      {tol}"
    )
    # Sanity
    assert n_pieces >= 38, f"Only {n_pieces} pieces processed (expected ≥38)"
    assert n_trials >= 1000, f"Only {n_trials} LOSO trials (expected ≥1000)"
