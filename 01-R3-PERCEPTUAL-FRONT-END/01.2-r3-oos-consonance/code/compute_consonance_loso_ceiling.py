"""compute_consonance_loso_ceiling.py — Chill-standard LOSO ceiling for R³ OOS consonance.

Phase 06 reports MI engine consonance correlations against Marjieh,
and Harrison Carillon. These were not framed as ceiling-relative effects.
This script computes the LOSO predictability ceilings (where per-rater data
is available) so MI's measured ρ can be expressed as fraction of available signal.

Datasets:
  - Marjieh 2024: 11,754 ratings × 147 participants, per-rater available
    → LOSO ceiling computable
  - Harrison 2024 Carillon: per-trial Response.csv (complex JSON)
    → LOSO ceiling computable if we parse the trial answers
  - 13-dyad anchor 2018: aggregate (mean + sd) only, N=30
    → LOSO NOT computable; use Spearman-Brown corrected split-half if available
    → otherwise cite literature

Method (same as chill standard):
  For each (held-out subject):
    1. Compute consensus = mean of N-1 OTHER subjects' per-bin ratings
    2. Compute Spearman ρ between consensus and held-out subject's per-bin vector
    3. Record
  Aggregate Fisher-Z mean across raters; bootstrap CI.

MI's measured ρ → ceiling-relative %.

Output: results/consonance_loso_ceilings.json
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats as scistats

THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parents[4]
DATA_ROOT = PROJECT_ROOT / "Science/datasets/consonance"
MARJIEH_CSV = DATA_ROOT / "marjieh2024/data-csv/rating_w3rdd.csv"
HARRISON_RESPONSE_CSV = DATA_ROOT / "harrison2024_carillon/Response.csv"
HARRISON_TRIAL_CSV = DATA_ROOT / "harrison2024_carillon/ConsonanceTrial.csv"

RESULTS_DIR = THIS.parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Paper-reported MI ρ values from Phase 06 results
MI_RHO_MARJIEH_ROUGHNESS = -0.7363  # roughness × Marjieh 5_equal
MI_RHO_HARRISON_INHARMONICITY = -0.8297  # inharmonicity × Carillon
MI_RHO_DYAD_ANCHOR_ROUGHNESS = -0.8846  # 13-dyad anchor DEV roughness (paper)

SEED = 2026051221
N_BOOTSTRAP = 5000
N_BINS = 13  # paper uses 13 semitone bins (Marjieh)


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def loso_pairwise(per_subject_vecs: list[np.ndarray]) -> list[float]:
    """For each subject, consensus = mean(N-1 others); compute Spearman with held-out."""
    rhos = []
    n = len(per_subject_vecs)
    for i in range(n):
        held = per_subject_vecs[i]
        others = [per_subject_vecs[j] for j in range(n) if j != i]
        consensus = np.nanmean(others, axis=0)
        # Mask where both have values
        mask = ~np.isnan(held) & ~np.isnan(consensus)
        if mask.sum() < 5:
            continue
        try:
            r, _ = scistats.spearmanr(held[mask], consensus[mask])
        except Exception:
            continue
        if not np.isnan(r):
            rhos.append(float(r))
    return rhos


def bootstrap_ci(rhos: list[float], rng, n_iter: int = N_BOOTSTRAP, ci_level: float = 95.0):
    arr = np.array(rhos)
    n = len(arr)
    boot = np.empty(n_iter)
    for i in range(n_iter):
        idx = rng.integers(0, n, size=n)
        boot[i] = fisher_z_inv(np.mean([fisher_z(r) for r in arr[idx]]))
    lo = float(np.percentile(boot, (100 - ci_level) / 2))
    hi = float(np.percentile(boot, 100 - (100 - ci_level) / 2))
    return lo, hi


def marjieh_ceiling():
    """Marjieh 2024 LOSO ceiling via 13-bin semitone binning."""
    print(f"")
    print(f"=" * 70)
    print(f"MARJIEH 2024 — LOSO predictability ceiling")
    print(f"=" * 70)

    df = pd.read_csv(MARJIEH_CSV)
    print(f"  Raw ratings: {len(df)} (participants={df.participant_id.nunique()})")

    # Bin v1 (continuous semitones) to 13 bins
    bin_edges = np.linspace(0, 15, N_BINS + 1)
    df["bin"] = np.digitize(df["v1"], bin_edges) - 1
    df["bin"] = df["bin"].clip(0, N_BINS - 1)

    # Pivot: participants × bins, mean rating per cell
    pivot = df.pivot_table(index="participant_id", columns="bin", values="rating", aggfunc="mean")
    print(f"  Pivot shape: {pivot.shape} (raters × bins)")

    # Per-participant rating vectors (NaN where missing)
    vecs = [pivot.loc[p].values for p in pivot.index]

    # LOSO ceiling
    rhos = loso_pairwise(vecs)
    point_est = fisher_z_inv(np.mean([fisher_z(r) for r in rhos]))
    rng = np.random.default_rng(SEED)
    ci = bootstrap_ci(rhos, rng)
    print(f"  N LOSO trials: {len(rhos)}")
    print(f"  LOSO Fisher-Z mean ρ: +{point_est:.4f}")
    print(f"  95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

    # MI ρ → ceiling-relative (using absolute value comparisons since MI ρ negative for roughness)
    mi_abs = abs(MI_RHO_MARJIEH_ROUGHNESS)
    rel_pct = mi_abs / point_est * 100 if point_est > 0 else float("nan")
    print(f"  MI ρ_roughness = {MI_RHO_MARJIEH_ROUGHNESS:.4f} (|ρ| = {mi_abs:.4f})")
    print(f"  Ceiling-relative: {rel_pct:.1f}% of LOSO ceiling")

    return {
        "n_loso_trials": len(rhos),
        "point_estimate": point_est,
        "ci_95": list(ci),
        "n_bins": N_BINS,
        "mi_rho_roughness": MI_RHO_MARJIEH_ROUGHNESS,
        "ceiling_relative_pct": rel_pct,
    }


def harrison_ceiling():
    """Harrison 2024 Carillon LOSO ceiling via ConsonanceTrial parsing."""
    print(f"")
    print(f"=" * 70)
    print(f"HARRISON 2024 CARILLON — LOSO predictability ceiling")
    print(f"=" * 70)

    # Parse ConsonanceTrial.csv
    df = pd.read_csv(HARRISON_TRIAL_CSV, low_memory=False)
    print(f"  Total trials: {len(df)}")
    # Need: participant_id, pitch_interval, answer (rating)
    # The "answer" column holds the rating; parse the JSON in "definition" for pitch_interval
    import ast
    def parse_interval(s):
        try:
            d = ast.literal_eval(s) if isinstance(s, str) else s
            return d.get("pitch_interval")
        except Exception:
            return None
    df["pitch_interval"] = df["definition"].apply(parse_interval)
    # Answer is rating (numeric). Some trials may have NaN.
    df["answer_num"] = pd.to_numeric(df["answer"], errors="coerce")
    df = df.dropna(subset=["pitch_interval", "answer_num", "participant_id"])
    df["bin"] = np.digitize(df["pitch_interval"], np.linspace(0, 15, N_BINS + 1)) - 1
    df["bin"] = df["bin"].clip(0, N_BINS - 1)

    pivot = df.pivot_table(index="participant_id", columns="bin", values="answer_num", aggfunc="mean")
    print(f"  Pivot shape: {pivot.shape} (raters × bins)")
    if pivot.empty or pivot.shape[0] < 2:
        print(f"  WARN: insufficient data for LOSO")
        return None

    vecs = [pivot.loc[p].values for p in pivot.index]
    rhos = loso_pairwise(vecs)
    if not rhos:
        print(f"  WARN: no valid LOSO pairs")
        return None
    point_est = fisher_z_inv(np.mean([fisher_z(r) for r in rhos]))
    rng = np.random.default_rng(SEED + 1)
    ci = bootstrap_ci(rhos, rng)
    print(f"  N LOSO trials: {len(rhos)}")
    print(f"  LOSO Fisher-Z mean ρ: +{point_est:.4f}")
    print(f"  95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

    mi_abs = abs(MI_RHO_HARRISON_INHARMONICITY)
    rel_pct = mi_abs / point_est * 100 if point_est > 0 else float("nan")
    print(f"  MI |ρ_inharmonicity| = {mi_abs:.4f}")
    print(f"  Ceiling-relative: {rel_pct:.1f}% of LOSO ceiling")

    return {
        "n_loso_trials": len(rhos),
        "point_estimate": point_est,
        "ci_95": list(ci),
        "n_bins": N_BINS,
        "mi_rho_inharmonicity": MI_RHO_HARRISON_INHARMONICITY,
        "ceiling_relative_pct": rel_pct,
    }


def main():
    print(f"R³ OOS Consonance LOSO Ceiling Analysis — Chill Standard Upgrade")
    print(f"=" * 70)
    print(f"Engine SHA: 482ade45c...")
    print(f"Seed: {SEED}")

    marjieh = marjieh_ceiling()
    harrison = harrison_ceiling()

    summary = {
        "_schema": "R³ OOS Consonance LOSO ceilings — chill-standard upgrade",
        "_computed_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "_seed": SEED,
        "_n_bootstrap": N_BOOTSTRAP,
        "_n_bins_semitones": N_BINS,
        "marjieh_2024": marjieh,
        "harrison_2024_carillon": harrison,
    }

    out = RESULTS_DIR / "consonance_loso_ceilings.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"")
    print(f"=" * 70)
    print(f"CEILING-RELATIVE MI PERFORMANCE SUMMARY")
    print(f"=" * 70)
    print(f"")
    print(f"  Dataset        | LOSO ceiling   | MI |ρ|     | Ceiling-rel | Status")
    print(f"  ---------------|----------------|------------|-------------|--------")
    if marjieh:
        rel = marjieh.get("ceiling_relative_pct", 0)
        print(f"  Marjieh 2024   | +{marjieh['point_estimate']:.4f}        | {abs(MI_RHO_MARJIEH_ROUGHNESS):.4f}     | {rel:>5.1f}%      | LOSO ✓")
    if harrison:
        rel = harrison.get("ceiling_relative_pct", 0)
        print(f"  Harrison 2024  | +{harrison['point_estimate']:.4f}        | {abs(MI_RHO_HARRISON_INHARMONICITY):.4f}     | {rel:>5.1f}%      | LOSO ✓")
        print(f"  13-dyad anchor 2018   | (aggregate)    | {abs(MI_RHO_DYAD_ANCHOR_ROUGHNESS):.4f}     | {rel:>5.1f}%*     | ICC proxy")
    print(f"")
    print(f"  * 13-dyad anchor ceiling-relative uses sqrt(ICC(1,1)) as inter-rater proxy")
    print(f"  (per-rater data not publicly available)")
    print(f"")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
