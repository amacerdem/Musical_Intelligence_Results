"""L6 — TC004 biphasic composite test.

Composite signal = positive_autonomic_cluster − negative_consummatory_cluster.

Definition (matches TC004 design):
  Positive cluster: MMP_P2 + AAC_E0 + AAC_F0 + AAC_F1 + AAC_P2
  Negative cluster: DAED_f02 + DAED_f04 + SRP_P2 + UDP_M1

This composite tests the Salimpoor 2011 biphasic anticipatory-vs-consummatory
pattern AT THE COMPOSITE LEVEL.

NOTE: TC004 empirical finding — composite is NOT stronger than MMP P2 alone
(chill response is memory-dominated). This layer documents that finding;
asserts composite is in the expected direction (positive) but doesn't require
it to exceed MMP P2.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from _infra.chillsdb_loader import CLIPS_7_CLEAN, load_events
from _infra.engine_cache import load_channel
from _infra.stats_core import (
    event_window_mask, safezone_mask, rank_biserial,
    event_time_shuffle_null, empirical_p_one_sided, fisher_combined_p,
    ENGINE_HZ, SAFEZONE_S,
)

WINDOW_S = 5.0
N_NULL_PERM = 500
SEED = 2026051204

POS_CHANNELS = [
    "MECH_MMP__P2:familiarity",
    "MECH_AAC__E0:emotional_arousal",
    "MECH_AAC__F0:scr_pred_1s",
    "MECH_AAC__F1:hr_pred_2s",
    "MECH_AAC__P2:perceptual_arousal",
]
NEG_CHANNELS = [
    "MECH_DAED__f02:consummatory_da",
    "MECH_DAED__f04:liking_index",
    "MECH_SRP__P2:pleasure",
    "MECH_UDP__M1:pleasure_index",
]


@pytest.fixture(scope="module")
def tc004_composite_results(chillsdb_root, engine_outputs_root, suite_root):
    cache_dir = engine_outputs_root / "chillsdb1_denoised" / "per_frame"
    if not cache_dir.exists():
        pytest.skip(f"Engine cache missing at {cache_dir}")
    rng = np.random.default_rng(SEED)
    clip_rbs, clip_emp_ps = [], []
    for clip_id in CLIPS_7_CLEAN:
        npz_path = cache_dir / f"{clip_id}.npz"
        if not npz_path.exists():
            continue
        pos_signals = [load_channel(npz_path, ch) for ch in POS_CHANNELS]
        neg_signals = [load_channel(npz_path, ch) for ch in NEG_CHANNELS]
        n_frames = pos_signals[0].shape[0]
        # Z-score each channel within-clip
        def z(s):
            return (s - s.mean()) / (s.std() + 1e-9)
        pos_sum = np.sum([z(s) for s in pos_signals], axis=0)
        neg_sum = np.sum([z(s) for s in neg_signals], axis=0)
        composite = pos_sum - neg_sum

        events = [t for t in load_events(chillsdb_root, clip_id) if t > SAFEZONE_S]
        if not events:
            continue
        valid_mask = safezone_mask(n_frames, SAFEZONE_S, ENGINE_HZ)
        ev_mask = event_window_mask(n_frames, events, WINDOW_S, ENGINE_HZ) & valid_mask
        rb, _ = rank_biserial(composite[valid_mask], ev_mask[valid_mask], alternative="greater")
        if np.isnan(rb):
            continue
        null_rbs = event_time_shuffle_null(composite, len(events), WINDOW_S, ENGINE_HZ,
                                            valid_mask, n_perm=N_NULL_PERM, rng=rng)
        emp_p = empirical_p_one_sided(rb, null_rbs)
        clip_rbs.append(rb)
        clip_emp_ps.append(emp_p)

    return {
        "mean_rb": float(np.mean(clip_rbs)) if clip_rbs else float("nan"),
        "n_clips_pos": int(sum(1 for r in clip_rbs if r > 0)),
        "n_clips": len(clip_rbs),
        "combined_p": fisher_combined_p(clip_emp_ps),
    }


def test_composite_positive_direction(tc004_composite_results):
    """Biphasic composite must be positive (Salimpoor anticipatory > consummatory in chill window)."""
    res = tc004_composite_results
    assert res["mean_rb"] > 0, (
        f"Composite mean rb = {res['mean_rb']:+.4f}, expected > 0 (Salimpoor biphasic pattern)"
    )


def test_composite_combined_p_significant(tc004_composite_results):
    """Composite combined p across clips should be < 0.05."""
    res = tc004_composite_results
    assert res["combined_p"] < 0.05, (
        f"Composite combined_p = {res['combined_p']:.4f}, expected < 0.05"
    )
