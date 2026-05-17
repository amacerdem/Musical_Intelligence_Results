"""L5 — PRIMARY: TENSION-15 lag-aware Spearman + lag-sweep null + Bonferroni.

Re-runs the chill-standard tension test inline and asserts the headline
verdict matches paper-time baseline.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scistats

ENGINE_HZ = 172.265625
SLIDER_HZ = 50.0
LAG_RANGE_S = 5.0
LAG_STEP_S = 0.5
SEED = 2026051302
N_NULL_PERMS = 200

TENSION_POOL = [
    "MECH_PUPF__E0:prediction_err",
    "MECH_PUPF__E1:uncertainty",
    "MECH_PUPF__U0:entropy_H",
    "MECH_PUPF__U1:surprise_S",
    "MECH_PUPF__U2:HS_interaction",
    "MECH_PUPF__P0:surprise_pleasure",
    "MECH_SRP__C2:prediction_error",
    "MECH_SRP__T0:tension",
    "MECH_SRP__T1:prediction_match",
    "MECH_SRP__M0:harmonic_tension",
    "MECH_AAC__F0:scr_pred_1s",
    "MECH_AAC__F1:hr_pred_2s",
    "MECH_CDMR__f01:mismatch_amplitude",
    "MECH_CDMR__P0:mismatch_signal",
    "MECH_RPEM__rpe_magnitude",
]


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def zscore(s):
    s = np.asarray(s, dtype=np.float64)
    sd = np.nanstd(s)
    return (s - np.nanmean(s)) / (sd + 1e-9)


def lag_aware_spearman(engine, slider, lags):
    best_rho, best_lag = 0.0, 0
    for lag in lags:
        if lag > 0:
            e, s = engine[:-lag] if lag else engine, slider[lag:]
        elif lag < 0:
            e, s = engine[-lag:], slider[:lag]
        else:
            e, s = engine, slider
        n = min(len(e), len(s))
        if n < 100:
            continue
        try:
            r, _ = scistats.spearmanr(e[:n], s[:n])
        except Exception:
            continue
        if np.isnan(r):
            continue
        if abs(r) > abs(best_rho):
            best_rho, best_lag = float(r), int(lag)
    return best_rho, best_lag


def circular_shift_null(engine, slider, lags, n_perms, rng):
    n = min(len(engine), len(slider))
    if n < 100:
        return np.array([])
    e, s = engine[:n], slider[:n]
    nulls = np.zeros(n_perms, dtype=np.float32)
    for i in range(n_perms):
        shift = int(rng.integers(low=50, high=n - 50))
        s_shuf = np.roll(s, shift)
        best, _ = lag_aware_spearman(e, s_shuf, lags)
        nulls[i] = best
    return nulls


def resample(eng_172, n_target):
    n_src = len(eng_172)
    t_src = np.linspace(0, 1, n_src)
    t_dst = np.linspace(0, 1, n_target)
    return np.interp(t_dst, t_src, eng_172).astype(np.float32)


@pytest.fixture(scope="module")
def h8_results(tensemusic_data_dir, engine_cache_dir, project_root):
    """Run H8 test inline and cache results."""
    # Build channel route from any pooled.csv
    pooled_candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "TenseMusic" / "pooled.csv",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "TenseMusic" / "pooled.csv",
    ]
    pooled_path = next(p for p in pooled_candidates if p.exists())
    pooled_cols = pd.read_csv(pooled_path, nrows=1).columns.tolist()
    route = {}
    for ch in TENSION_POOL:
        cls = ch[len("MECH_"):].split("__", 1)[0]
        class_cols = [c for c in pooled_cols if c.startswith(f"MECH_{cls}__")]
        if ch in class_cols:
            route[ch] = (f"mech_{cls}", class_cols.index(ch))

    rng = np.random.default_rng(SEED)
    lag_max = int(LAG_RANGE_S * SLIDER_HZ)
    lag_step = int(LAG_STEP_S * SLIDER_HZ)
    lags = list(range(-lag_max, lag_max + 1, lag_step))

    rows = []
    for csv in sorted(tensemusic_data_dir.glob("*.csv")):
        piece = csv.stem
        npz = engine_cache_dir / f"{piece}.npz"
        if not npz.exists():
            continue
        z = np.load(npz, allow_pickle=True)
        df = pd.read_csv(csv)
        rating_cols = [c for c in df.columns if c.startswith("rating") and c[len("rating"):].isdigit()]
        if not rating_cols:
            continue
        consensus = df[rating_cols].mean(axis=1).values.astype(np.float64)
        slider_z = zscore(consensus)
        for ch in TENSION_POOL:
            if ch not in route:
                continue
            mech_key, idx = route[ch]
            engine_172 = z[mech_key][:, idx].astype(np.float32)
            engine_50 = resample(engine_172, len(consensus))
            e = zscore(engine_50)
            best_rho, _ = lag_aware_spearman(e, slider_z, lags)
            nulls = circular_shift_null(e, slider_z, lags, N_NULL_PERMS, rng)
            emp_p = (1 + np.sum(np.abs(nulls) >= abs(best_rho))) / (1 + len(nulls)) if len(nulls) else float("nan")
            rows.append({"piece": piece, "channel": ch, "best_rho": best_rho, "emp_p_null": emp_p})

    df_trials = pd.DataFrame(rows)
    # Per-channel aggregate
    channel_rows = []
    for ch in TENSION_POOL:
        sub = df_trials[df_trials["channel"] == ch]
        if sub.empty:
            continue
        rhos = sub["best_rho"].values
        emp_ps = sub["emp_p_null"].dropna().values
        fz_mean = fisher_z_inv(np.mean([fisher_z(r) for r in rhos]))
        n_pos = int((rhos > 0).sum())
        n_total = len(rhos)
        ps = np.asarray([p for p in emp_ps if not np.isnan(p) and p > 0])
        if len(ps) > 0:
            chi2 = -2 * np.sum(np.log(np.maximum(ps, 1e-300)))
            combined_p = float(scistats.chi2.sf(chi2, 2 * len(ps)))
        else:
            combined_p = float("nan")
        channel_rows.append({
            "channel": ch, "fz_mean_rho": fz_mean,
            "n_pieces_pos": n_pos, "n_pieces": n_total,
            "direction_pct": 100 * n_pos / n_total,
            "combined_p": combined_p,
        })
    res_df = pd.DataFrame(channel_rows)
    k = len(res_df)
    res_df["p_bonf"] = np.clip(res_df["combined_p"] * k, 0, 1)
    return res_df


def test_top_channel_correct(h8_results, paper_baseline):
    top = h8_results.sort_values("fz_mean_rho", key=lambda s: s.abs(), ascending=False).iloc[0]
    expected = paper_baseline["primary_verdict_h8"]["top_channel"]
    assert top["channel"] == expected, f"Top channel mismatch: got {top['channel']}, expected {expected}"


def test_top_rho_within_tolerance(h8_results, paper_baseline):
    top = h8_results.sort_values("fz_mean_rho", key=lambda s: s.abs(), ascending=False).iloc[0]
    expected = paper_baseline["primary_verdict_h8"]["top_fz_mean_rho"]
    tol = paper_baseline["tolerance"]["fz_mean_rho_abs"]
    assert abs(top["fz_mean_rho"] - expected) < tol, (
        f"Top rho drift: {top['fz_mean_rho']:.4f} vs expected {expected:.4f} (tol {tol})"
    )


def test_direction_at_paper_level(h8_results, paper_baseline):
    top = h8_results.sort_values("fz_mean_rho", key=lambda s: s.abs(), ascending=False).iloc[0]
    expected = paper_baseline["primary_verdict_h8"]["top_direction_pct"]
    tol = paper_baseline["tolerance"]["direction_pct_abs"]
    assert abs(top["direction_pct"] - expected) < tol, (
        f"Direction drift: {top['direction_pct']:.1f}% vs expected {expected:.1f}% (tol {tol})"
    )


def test_bonferroni_pass_count(h8_results, paper_baseline):
    n_bonf = int((h8_results["p_bonf"] < 0.05).sum())
    expected_min = paper_baseline["tolerance"]["n_bonferroni_pass_min"]
    assert n_bonf >= expected_min, f"Only {n_bonf} Bonferroni-pass (expected ≥{expected_min})"
