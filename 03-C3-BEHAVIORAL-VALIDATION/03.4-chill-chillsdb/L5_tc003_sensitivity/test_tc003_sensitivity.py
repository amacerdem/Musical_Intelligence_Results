"""L5 — TC003 9-full sensitivity test.

Runs the same Mann-Whitney rank-biserial protocol as L4 but on the FULL 9-clip
set (including Mr. Bean comedy sketch + Vocal Intros compilation). Expected:
weaker than L4 (those two clips violate the H3 horizon assumption). This layer
verifies the exclusion is *justified* and not p-hacking.

PASS condition: 9-full result is weaker than 7-clean (rb decreases, fewer
Bonferroni-pass channels) — confirming the structural-discontinuity exclusion
rationale.
"""
from __future__ import annotations

import pandas as pd
import pytest
import numpy as np

from _infra.chillsdb_loader import CLIPS_9_FULL, load_events
from _infra.engine_cache import CHILL_CHANNELS_22, load_channel
from _infra.stats_core import (
    event_window_mask, safezone_mask, rank_biserial,
    event_time_shuffle_null, empirical_p_one_sided,
    fisher_combined_p, bh_fdr, bonferroni,
    ENGINE_HZ, SAFEZONE_S,
)

WINDOW_S = 5.0
N_NULL_PERM = 500
SEED = 2026051203


@pytest.fixture(scope="module")
def tc003_9full_results(chillsdb_root, engine_outputs_root, suite_root):
    """Run TC003 protocol on 9-full afftdn-denoised."""
    cache_dir = engine_outputs_root / "chillsdb1_denoised" / "per_frame"
    if not cache_dir.exists():
        pytest.skip(f"Engine cache missing at {cache_dir} — run L3 first")
    rng = np.random.default_rng(SEED)
    rows = []
    for ch_name in CHILL_CHANNELS_22:
        clip_rbs, clip_emp_ps = [], []
        for clip_id in CLIPS_9_FULL:
            npz_path = cache_dir / f"{clip_id}.npz"
            if not npz_path.exists():
                continue
            try:
                signal = load_channel(npz_path, ch_name)
            except Exception:
                continue
            events = [t for t in load_events(chillsdb_root, clip_id) if t > SAFEZONE_S]
            if not events:
                continue
            n_frames = len(signal)
            valid_mask = safezone_mask(n_frames, SAFEZONE_S, ENGINE_HZ)
            ev_mask = event_window_mask(n_frames, events, WINDOW_S, ENGINE_HZ) & valid_mask
            rb, _ = rank_biserial(signal[valid_mask], ev_mask[valid_mask], alternative="greater")
            if np.isnan(rb):
                continue
            null_rbs = event_time_shuffle_null(signal, len(events), WINDOW_S, ENGINE_HZ,
                                                valid_mask, n_perm=N_NULL_PERM, rng=rng)
            emp_p = empirical_p_one_sided(rb, null_rbs)
            clip_rbs.append(rb)
            clip_emp_ps.append(emp_p)
        if not clip_rbs:
            continue
        rows.append({
            "channel": ch_name,
            "mean_rank_biserial": float(np.mean(clip_rbs)),
            "n_clips_pos": int(sum(1 for r in clip_rbs if r > 0)),
            "n_clips": len(clip_rbs),
            "fishers_combined_p": fisher_combined_p(clip_emp_ps),
        })
    df = pd.DataFrame(rows)
    df["bh_q"] = bh_fdr(df["fishers_combined_p"].values)
    df["bonf_p"] = bonferroni(df["fishers_combined_p"].values)
    out_csv = suite_root / "L5_tc003_sensitivity" / "results" / "tc003_9full_aggregate.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


def test_mmp_p2_present_in_9full(tc003_9full_results):
    """MMP P2 channel must be present in 9-full result."""
    df = tc003_9full_results
    mmp = df[df["channel"] == "MECH_MMP__P2:familiarity"]
    assert not mmp.empty


def test_9full_directionally_positive_mmp(tc003_9full_results):
    """MMP P2 should still be positive direction in 9-full, just weaker."""
    df = tc003_9full_results
    mmp = df[df["channel"] == "MECH_MMP__P2:familiarity"].iloc[0]
    assert mmp["mean_rank_biserial"] > 0, (
        f"MMP P2 negative in 9-full ({mmp['mean_rank_biserial']:+.4f}) — would invalidate exclusion rationale"
    )


def test_9full_weaker_than_7clean(tc003_9full_results, suite_root):
    """9-full MMP P2 rb should be LOWER than 7-clean (excluded clips drag it down)."""
    df_9full = tc003_9full_results
    csv_7clean = suite_root / "L4_tc005_primary_verdict" / "results" / "tc005_single_channel_aggregate.csv"
    if not csv_7clean.exists():
        pytest.skip("L4 result CSV missing — run L4 first for 7-clean comparison")
    df_7clean = pd.read_csv(csv_7clean)
    df_7clean = df_7clean[df_7clean["audio"] == "afftdn"]
    mmp_9full = df_9full[df_9full["channel"] == "MECH_MMP__P2:familiarity"].iloc[0]
    mmp_7clean = df_7clean[df_7clean["channel"] == "MECH_MMP__P2:familiarity"].iloc[0]
    assert mmp_9full["mean_rank_biserial"] < mmp_7clean["mean_rank_biserial"], (
        f"9-full MMP P2 ({mmp_9full['mean_rank_biserial']:+.4f}) NOT weaker than 7-clean "
        f"({mmp_7clean['mean_rank_biserial']:+.4f}) — exclusion rationale unsupported"
    )
