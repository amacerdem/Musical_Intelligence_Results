"""L5 — PRIMARY: PMEmo arousal + valence inline re-run, both pilot200.

Runs H4 (arousal) and H5 (valence) tests inline on the first 200 clips of
PMEmo (matching paper-time baseline scope) and asserts:
  - H4 top channel = MECH_AAC__E0:emotional_arousal, ρ within tolerance
  - H4 top ceiling-relative ≥ 0.85
  - H5 top channel = MECH_SRP__P0:wanting, Bonferroni-pass
  - H5 ≥2 Bonferroni-pass channels
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scistats

ENGINE_HZ = 172.265625
SLIDER_HZ = 2.0
LAG_RANGE_S = 5.0
LAG_STEP_S = 0.5
SEED = 2026051304
N_NULL_PERMS = 100
N_CLIPS = 200

AROUSAL_POOL = [
    "MECH_AAC__A0:scr",
    "MECH_AAC__A1:hr",
    "MECH_AAC__E0:emotional_arousal",
    "MECH_AAC__E1:ans_response",
    "MECH_AAC__F0:scr_pred_1s",
    "MECH_AAC__F1:hr_pred_2s",
    "MECH_AAC__P0:current_intensity",
    "MECH_AAC__P1:driving_signal",
    "MECH_AAC__P2:perceptual_arousal",
    "MECH_CSG__E0:salience_activation",
    "MECH_CSG__E1:sensory_evidence",
    "MECH_PUPF__E0:prediction_err",
    "MECH_PUPF__E1:uncertainty",
    "MECH_PUPF__U0:entropy_H",
    "MECH_PUPF__U1:surprise_S",
    "MECH_PUPF__U2:HS_interaction",
    "MECH_PUPF__P0:surprise_pleasure",
    "MECH_MCCN__E2:arousal_index",
    "MECH_DAED__f01:anticipatory_da",
]

VALENCE_POOL = [
    "MECH_VMM__V0:valence",
    "MECH_VMM__V1:mode_signal",
    "MECH_VMM__R0:happy_pathway",
    "MECH_VMM__R1:sad_pathway",
    "MECH_VMM__M0:mode_consonance",
    "MECH_SRP__P0:wanting",
    "MECH_SRP__P1:liking",
    "MECH_SRP__P2:pleasure",
    "MECH_PUPF__G0:pleasure_P",
    "MECH_CLAM__P1:valence_tracking",
    "MECH_CMAT__S0:supramodal_valence",
    "MECH_CSG__P1:affective_evaluation",
    "MECH_UDP__M1:pleasure_index",
    "MECH_DAP__P1:familiarity_warmth",
    "MECH_NEMAC__M0:mpfc_activation",
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


def parse_pmemo_rater_csv(path):
    raters = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(',')
            if not parts[0].isdigit():
                continue
            dyn = np.array([float(x) for x in parts[2:]], dtype=np.float64)
            raters.append(dyn)
    return raters


def resample_to_n(seg, n_target):
    if len(seg) < 2:
        return None
    t_src = np.linspace(0, 1, len(seg))
    t_dst = np.linspace(0, 1, n_target)
    return np.interp(t_dst, t_src, seg).astype(np.float32)


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
        if n < 8:
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
    if n < 20:
        return np.array([])
    e, s = engine[:n], slider[:n]
    nulls = np.zeros(n_perms, dtype=np.float32)
    for i in range(n_perms):
        shift = int(rng.integers(low=2, high=max(3, n - 2)))
        best, _ = lag_aware_spearman(e, np.roll(s, shift), lags)
        nulls[i] = best
    return nulls


def _build_route(pool, pooled_cols):
    route = {}
    for ch in pool:
        cls = ch[len("MECH_"):].split("__", 1)[0]
        class_cols = [c for c in pooled_cols if c.startswith(f"MECH_{cls}__")]
        if ch in class_cols:
            route[ch] = (f"mech_{cls}", class_cols.index(ch))
    return route


def _run_h4_h5(annot_dir: Path, suffix: str, pool: list, engine_cache_dir: Path, pooled_csv: Path):
    """Run lag-aware Spearman + Bonferroni over a pool for the first N_CLIPS clips."""
    rng = np.random.default_rng(SEED)
    lag_max = int(LAG_RANGE_S * SLIDER_HZ)
    lag_step = int(LAG_STEP_S * SLIDER_HZ)
    lags = list(range(-lag_max, lag_max + 1, lag_step))

    pooled_cols = pd.read_csv(pooled_csv, nrows=1).columns.tolist()
    route = _build_route(pool, pooled_cols)
    pool_valid = [c for c in pool if c in route]
    k = len(pool_valid)

    clip_ids = []
    for csv in sorted(annot_dir.glob(f"*-{suffix}.csv")):
        cid = csv.stem.split('-')[0]
        if (engine_cache_dir / f"{cid}.npz").exists():
            clip_ids.append(cid)
    clip_ids = clip_ids[:N_CLIPS]

    rows = []
    for cid in clip_ids:
        csv = annot_dir / f"{cid}-{suffix}.csv"
        raters = parse_pmemo_rater_csv(csv)
        if len(raters) < 2:
            continue
        min_len = min(len(r) for r in raters)
        if min_len < 8:
            continue
        consensus = np.mean(np.stack([r[:min_len] for r in raters]), axis=0)
        slider_z = zscore(consensus)
        n_target = len(slider_z)

        z = np.load(engine_cache_dir / f"{cid}.npz", allow_pickle=True)
        for ch in pool_valid:
            mech_key, idx = route[ch]
            engine_172 = z[mech_key][:, idx].astype(np.float32)
            mech_2hz = resample_to_n(engine_172, n_target)
            if mech_2hz is None:
                continue
            e = zscore(mech_2hz)
            best_rho, _ = lag_aware_spearman(e, slider_z, lags)
            nulls = circular_shift_null(e, slider_z, lags, N_NULL_PERMS, rng)
            emp_p = (1 + np.sum(np.abs(nulls) >= abs(best_rho))) / (1 + len(nulls)) if len(nulls) else float("nan")
            rows.append({"clip_id": cid, "channel": ch, "best_rho": best_rho, "emp_p_null": emp_p})

    df_trials = pd.DataFrame(rows)
    channel_rows = []
    for ch in pool_valid:
        sub = df_trials[df_trials["channel"] == ch]
        if sub.empty:
            continue
        rhos = sub["best_rho"].values
        fz_mean = fisher_z_inv(np.mean([fisher_z(r) for r in rhos]))
        n_pos = int((rhos > 0).sum())
        n_total = len(rhos)
        ps = np.asarray([p for p in sub["emp_p_null"].dropna().values if p > 0])
        if len(ps) > 0:
            chi2 = -2 * np.sum(np.log(np.maximum(ps, 1e-300)))
            combined_p = float(scistats.chi2.sf(chi2, 2 * len(ps)))
        else:
            combined_p = float("nan")
        channel_rows.append({
            "channel": ch,
            "fz_mean_rho": fz_mean,
            "direction_pct": 100 * n_pos / n_total,
            "combined_p": combined_p,
        })
    res_df = pd.DataFrame(channel_rows)
    res_df["p_bonf"] = np.clip(res_df["combined_p"] * k, 0, 1)
    return res_df.sort_values("fz_mean_rho", key=lambda s: s.abs(), ascending=False)


@pytest.fixture(scope="module")
def h4_results(pmemo_annotations_arousal, engine_cache_dir, pooled_csv):
    return _run_h4_h5(pmemo_annotations_arousal, "A", AROUSAL_POOL, engine_cache_dir, pooled_csv)


@pytest.fixture(scope="module")
def h5_results(pmemo_annotations_valence, engine_cache_dir, pooled_csv):
    return _run_h4_h5(pmemo_annotations_valence, "V", VALENCE_POOL, engine_cache_dir, pooled_csv)


def test_h4_top_channel_aac(h4_results, paper_baseline):
    top = h4_results.iloc[0]
    expected_top = paper_baseline["primary_verdict_h4_arousal"]["top_channel"]
    assert top["channel"] == expected_top, (
        f"H4 top channel mismatch: got {top['channel']}, expected {expected_top}"
    )


def test_h4_top_rho_tolerance(h4_results, paper_baseline):
    top = h4_results.iloc[0]
    expected = paper_baseline["primary_verdict_h4_arousal"]["top_fz_mean_rho"]
    tol = paper_baseline["tolerance"]["fz_mean_rho_abs"]
    assert abs(top["fz_mean_rho"] - expected) < tol, (
        f"H4 top ρ drift: {top['fz_mean_rho']:.4f} vs {expected:.4f} (tol {tol})"
    )


def test_h4_ceiling_relative_at_or_near_one(h4_results, paper_baseline):
    top = h4_results.iloc[0]
    ceiling = paper_baseline["loso_ceiling_arousal"]["point_estimate"]
    ceiling_rel = top["fz_mean_rho"] / ceiling
    assert ceiling_rel > 0.85, f"H4 ceiling-relative dropped: {ceiling_rel:.3f}"


def test_h5_top_channel_srp_wanting(h5_results, paper_baseline):
    top = h5_results.iloc[0]
    expected_top = paper_baseline["primary_verdict_h5_valence"]["top_channel"]
    assert top["channel"] == expected_top, (
        f"H5 top channel mismatch: got {top['channel']}, expected {expected_top}"
    )


def test_h5_bonferroni_pass_count(h5_results, paper_baseline):
    n_bonf = int((h5_results["p_bonf"] < 0.05).sum())
    expected_min = paper_baseline["tolerance"]["n_bonferroni_pass_min_h5"]
    assert n_bonf >= expected_min, (
        f"H5 only {n_bonf} Bonferroni-pass (expected ≥{expected_min})"
    )
