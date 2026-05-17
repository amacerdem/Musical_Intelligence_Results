"""L4 — PRIMARY verdict: TC005 7-clean Bonferroni Mann-Whitney rank-biserial.

The paper's headline Tier-1 chill finding:
  - `MECH_MMP__P2:familiarity` rank-biserial = +0.231 ± 0.005
  - p_bonf = 0.009 across 22 chill-related channels
  - 7/7 clips positive direction
  - On 7-clean continuous-music subset of ChillsDB v1
  - On afftdn-denoised audio

This test loads engine cache for the 7-clean clips on afftdn-denoised audio,
runs the canonical Mann-Whitney rank-biserial per channel with within-clip
event-time-shuffle null, applies Bonferroni over 22 channels, and asserts the
headline channels match the paper-time baseline within tolerance.

NOTE: depends on L3 having built the engine cache for chillsdb1_denoised.
If cache is missing, test skips with a clear message.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from _infra.chillsdb_loader import CLIPS_7_CLEAN, load_events
from _infra.engine_cache import CHILL_CHANNELS_22, load_channel
from _infra.stats_core import (
    event_window_mask, rank_biserial,
    fisher_combined_p, bh_fdr, bonferroni,
    ENGINE_HZ,
)


WINDOW_S = 5.0  # ±5 s event window
N_NULL_PERM = 500  # per (channel × clip)
SEED = 20260512_05  # match TC005 seed for byte-identical replication


def _audio_variant_cache_dir(engine_outputs_root: Path, variant: str) -> Path:
    """Resolve engine cache dir for an audio variant."""
    if variant == "afftdn":
        return engine_outputs_root / "chillsdb1_denoised" / "per_frame"
    elif variant == "noisereduce":
        return engine_outputs_root / "chillsdb1_noisereduce" / "per_frame"
    elif variant == "original":
        return engine_outputs_root / "chillsdb1" / "per_frame"
    else:
        raise ValueError(f"Unknown variant: {variant}")


def _run_tc005_protocol(chillsdb_root: Path, engine_outputs_root: Path,
                         variant: str, output_csv: Path) -> pd.DataFrame:
    """Run TC005 single-channel signed Mann-Whitney rank-biserial protocol
    on the 7-clean subset for one audio variant. Returns aggregate DataFrame.

    Protocol matches True_Calibration_005_clean7.py:
      - load_channel z-scores within-clip
      - event_window: ±5 s around each chill event timestamp (NO safezone)
      - null: 500 random event-times uniform in [0, duration]
      - empirical_p = (1 + sum(null >= obs)) / (1 + n_null)
      - per-clip Fisher-combined p across clips via chi2.sf
    """
    cache_dir = _audio_variant_cache_dir(engine_outputs_root, variant)
    if not cache_dir.exists():
        pytest.skip(f"Engine cache not built for variant '{variant}' at {cache_dir} — run L3 first")

    pooled_csv = cache_dir.parent / "pooled.csv"
    if not pooled_csv.exists():
        pytest.skip(f"pooled.csv missing for variant '{variant}' at {pooled_csv}")

    from scipy import stats as scistats
    rng = np.random.default_rng(SEED)
    rows = []
    for ch_name in CHILL_CHANNELS_22:
        clip_rbs = []
        clip_emp_ps = []
        for clip_id in CLIPS_7_CLEAN:
            npz_path = cache_dir / f"{clip_id}.npz"
            if not npz_path.exists():
                continue
            try:
                signal = load_channel(npz_path, ch_name, pooled_csv=pooled_csv)
            except Exception:
                continue
            events = load_events(chillsdb_root, clip_id)
            if not events:
                continue
            n_frames = len(signal)
            duration_s = n_frames / ENGINE_HZ

            ev_mask = event_window_mask(n_frames, events, WINDOW_S, ENGINE_HZ)
            rb, _p = rank_biserial(signal, ev_mask, alternative="greater")
            if np.isnan(rb):
                continue

            # Per-clip null — random event-times uniform in [0, duration]
            null_rbs = []
            for _ in range(N_NULL_PERM):
                nt = rng.uniform(0, duration_s, size=len(events))
                nm = event_window_mask(n_frames, nt.tolist(), WINDOW_S, ENGINE_HZ)
                rb_n, _ = rank_biserial(signal, nm, alternative="greater")
                if not np.isnan(rb_n):
                    null_rbs.append(rb_n)
            null_arr = np.asarray(null_rbs)
            emp_p = (1 + (null_arr >= rb).sum()) / (1 + len(null_arr)) if len(null_arr) else float("nan")
            clip_rbs.append(rb)
            clip_emp_ps.append(emp_p)

        if not clip_rbs:
            continue
        # Fisher-Z aggregate of rb across clips
        z_vals = np.arctanh(np.clip(np.asarray(clip_rbs), -0.999, 0.999))
        mean_rb = float(np.tanh(z_vals.mean()))
        median_rb = float(np.median(clip_rbs))
        n_pos = int(sum(1 for r in clip_rbs if r > 0))
        n_p05 = int(sum(1 for p in clip_emp_ps if p < 0.05))
        # Fisher's combined p (chi2 on -2*sum(log(p))) across clips
        ps = np.asarray([p for p in clip_emp_ps if not np.isnan(p) and p > 0], dtype=float)
        chi2 = -2 * np.sum(np.log(np.maximum(ps, 1e-300)))
        combined_p = float(scistats.chi2.sf(chi2, 2 * len(ps))) if len(ps) else float("nan")
        rows.append({
            "audio": variant,
            "channel": ch_name,
            "mean_rank_biserial": mean_rb,
            "median_rank_biserial": median_rb,
            "n_clips_pos": n_pos,
            "n_clips_emp_p05": n_p05,
            "n_clips": len(clip_rbs),
            "fishers_combined_p": combined_p,
        })

    df = pd.DataFrame(rows)
    df["bh_q"] = bh_fdr(df["fishers_combined_p"].values)
    df["bonf_p"] = bonferroni(df["fishers_combined_p"].values)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


@pytest.fixture(scope="module")
def tc005_results(chillsdb_root, engine_outputs_root, suite_root):
    """Run TC005 on afftdn variant once per module, return DataFrame."""
    output_csv = suite_root / "L4_tc005_primary_verdict" / "results" / "tc005_single_channel_aggregate.csv"
    return _run_tc005_protocol(chillsdb_root, engine_outputs_root, "afftdn", output_csv)


def test_mmp_p2_bonferroni_pass(tc005_results, paper_baseline):
    """Primary headline: MMP P2:familiarity must Bonferroni-pass on afftdn 7-clean."""
    df = tc005_results
    mmp_row = df[df["channel"] == "MECH_MMP__P2:familiarity"]
    assert not mmp_row.empty, "MMP P2:familiarity missing from result CSV"
    mmp = mmp_row.iloc[0]
    assert mmp["bonf_p"] < 0.05, (
        f"MMP P2 Bonferroni-pass FAILED: bonf_p = {mmp['bonf_p']:.4f} (paper-time = 0.009)"
    )
    assert mmp["mean_rank_biserial"] > 0.20, (
        f"MMP P2 effect size too small: rb = {mmp['mean_rank_biserial']:.4f} (paper-time = 0.231)"
    )
    assert mmp["n_clips_pos"] == 7, (
        f"MMP P2 direction agreement FAILED: {int(mmp['n_clips_pos'])}/7 clips positive (paper-time = 7/7)"
    )


def test_mmp_p2_within_tolerance(tc005_results, paper_baseline):
    """MMP P2 must reproduce paper-time numbers within declared tolerance."""
    df = tc005_results
    mmp = df[df["channel"] == "MECH_MMP__P2:familiarity"].iloc[0]
    primary = paper_baseline["primary_verdict_tc005_clean7_afftdn"]
    expected_rb = next(c["rank_biserial_mean"] for c in primary["headline_channels"]
                       if c["channel"] == "MECH_MMP__P2:familiarity")
    expected_p = next(c["p_bonf"] for c in primary["headline_channels"]
                      if c["channel"] == "MECH_MMP__P2:familiarity")
    tol_rb = paper_baseline["tolerance"]["rank_biserial_abs"]
    tol_p = paper_baseline["tolerance"]["p_bonf_abs"]
    assert abs(mmp["mean_rank_biserial"] - expected_rb) < tol_rb, (
        f"MMP P2 rb drift outside tolerance:\n"
        f"  expected: {expected_rb:+.4f}\n"
        f"  actual:   {mmp['mean_rank_biserial']:+.4f}\n"
        f"  tol:      ±{tol_rb}"
    )
    assert abs(mmp["bonf_p"] - expected_p) < tol_p, (
        f"MMP P2 bonf_p drift outside tolerance:\n"
        f"  expected: {expected_p:.4f}\n"
        f"  actual:   {mmp['bonf_p']:.4f}\n"
        f"  tol:      ±{tol_p}"
    )


def test_aac_cluster_directionally_correct(tc005_results):
    """AAC autonomic cluster (E0, F0, F1, P2) should be positive direction."""
    df = tc005_results
    autonomic_channels = [
        "MECH_AAC__E0:emotional_arousal",
        "MECH_AAC__F0:scr_pred_1s",
        "MECH_AAC__F1:hr_pred_2s",
        "MECH_AAC__P2:perceptual_arousal",
    ]
    for ch in autonomic_channels:
        row = df[df["channel"] == ch]
        assert not row.empty, f"{ch} missing from result CSV"
        rb = row.iloc[0]["mean_rank_biserial"]
        assert rb > 0, (
            f"{ch} expected positive (anticipatory autonomic activation during chill); got rb={rb:+.4f}"
        )


def test_daed_cluster_negative_direction(tc005_results):
    """DAED consummatory-DA cluster should be negative (biphasic Salimpoor pattern)."""
    df = tc005_results
    consum_channels = [
        "MECH_DAED__f02:consummatory_da",
        "MECH_DAED__f04:liking_index",
    ]
    for ch in consum_channels:
        row = df[df["channel"] == ch]
        assert not row.empty, f"{ch} missing from result CSV"
        rb = row.iloc[0]["mean_rank_biserial"]
        assert rb < 0, (
            f"{ch} expected negative (consummatory DA depressed in chill window per Salimpoor 2011); got rb={rb:+.4f}"
        )


def test_at_least_2_bonferroni_passes(tc005_results):
    """At least 2 channels must pass Bonferroni (paper-time = 4)."""
    df = tc005_results
    n_bonf = int((df["bonf_p"] < 0.05).sum())
    assert n_bonf >= 2, (
        f"Bonferroni-pass channels = {n_bonf}, expected ≥ 2 (paper-time = 4)"
    )
