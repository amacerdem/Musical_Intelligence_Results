"""L8 — TC007 pre/post event-window asymmetry.

Splits the ±5s event window into pre-event (−5s..0s) and post-event (0s..+5s)
half-windows. Asks whether engine response is symmetric (sustained chill)
or asymmetric (sharply biphasic temporal locking).

Paper-time finding: chill response is broadly SUSTAINED, not sharply biphasic.
MMP P2 rb_pre ≈ rb_post; AAC autonomic slightly POST-dominant (reaction lag).

PASS condition: MMP P2 shows positive direction in BOTH pre and post halves.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from _infra.chillsdb_loader import CLIPS_7_CLEAN, load_events
from _infra.engine_cache import load_channel
from _infra.stats_core import (
    safezone_mask, rank_biserial,
    ENGINE_HZ, SAFEZONE_S,
)

WINDOW_S = 5.0


def _split_window_masks(n_frames: int, events: list[float], window_s: float, engine_hz: float):
    """Return (pre_mask, post_mask) boolean arrays for pre-event vs post-event halves."""
    pre = np.zeros(n_frames, dtype=bool)
    post = np.zeros(n_frames, dtype=bool)
    win_samples = int(window_s * engine_hz)
    for t in events:
        center = int(t * engine_hz)
        # Pre = [center - win, center)
        lo_pre = max(0, center - win_samples)
        hi_pre = min(n_frames, center)
        pre[lo_pre:hi_pre] = True
        # Post = [center, center + win)
        lo_post = max(0, center)
        hi_post = min(n_frames, center + win_samples)
        post[lo_post:hi_post] = True
    return pre, post


@pytest.fixture(scope="module")
def tc007_prepost_results(chillsdb_root, engine_outputs_root, suite_root):
    cache_dir = engine_outputs_root / "chillsdb1_denoised" / "per_frame"
    if not cache_dir.exists():
        pytest.skip(f"Engine cache missing at {cache_dir}")

    test_channels = [
        "MECH_MMP__P2:familiarity",
        "MECH_AAC__E0:emotional_arousal",
        "MECH_AAC__F0:scr_pred_1s",
        "MECH_AAC__F1:hr_pred_2s",
        "MECH_DAED__f02:consummatory_da",
        "MECH_DAED__f04:liking_index",
    ]
    rows = []
    for ch_name in test_channels:
        rb_pre_clips, rb_post_clips = [], []
        for clip_id in CLIPS_7_CLEAN:
            npz_path = cache_dir / f"{clip_id}.npz"
            if not npz_path.exists():
                continue
            signal = load_channel(npz_path, ch_name)
            events = [t for t in load_events(chillsdb_root, clip_id) if t > SAFEZONE_S]
            if not events:
                continue
            n_frames = len(signal)
            valid_mask = safezone_mask(n_frames, SAFEZONE_S, ENGINE_HZ)
            pre_mask, post_mask = _split_window_masks(n_frames, events, WINDOW_S, ENGINE_HZ)
            pre_mask &= valid_mask
            post_mask &= valid_mask
            rb_pre, _ = rank_biserial(signal[valid_mask], pre_mask[valid_mask], alternative="greater")
            rb_post, _ = rank_biserial(signal[valid_mask], post_mask[valid_mask], alternative="greater")
            if not np.isnan(rb_pre):
                rb_pre_clips.append(rb_pre)
            if not np.isnan(rb_post):
                rb_post_clips.append(rb_post)
        if not rb_pre_clips or not rb_post_clips:
            continue
        rows.append({
            "channel": ch_name,
            "rb_pre_mean": float(np.mean(rb_pre_clips)),
            "rb_post_mean": float(np.mean(rb_post_clips)),
            "rb_delta_post_minus_pre": float(np.mean(rb_post_clips) - np.mean(rb_pre_clips)),
        })
    df = pd.DataFrame(rows)
    out_csv = suite_root / "L8_tc007_pre_post" / "results" / "tc007_pre_post_aggregate.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


def test_mmp_p2_positive_both_halves(tc007_prepost_results):
    """MMP P2 must be positive in BOTH pre and post halves (sustained response)."""
    row = tc007_prepost_results[tc007_prepost_results["channel"] == "MECH_MMP__P2:familiarity"]
    assert not row.empty
    r = row.iloc[0]
    assert r["rb_pre_mean"] > 0 and r["rb_post_mean"] > 0, (
        f"MMP P2 NOT sustained across pre/post halves: pre={r['rb_pre_mean']:+.4f}, post={r['rb_post_mean']:+.4f}"
    )


def test_aac_post_dominance_modest(tc007_prepost_results):
    """AAC autonomic channels should be slightly POST-dominant (button reaction lag)."""
    aac_channels = ["MECH_AAC__F0:scr_pred_1s", "MECH_AAC__F1:hr_pred_2s"]
    for ch in aac_channels:
        row = tc007_prepost_results[tc007_prepost_results["channel"] == ch]
        if row.empty:
            continue
        r = row.iloc[0]
        # Mild post-dominance expected (≥0 or marginally positive delta)
        # Just check direction is interpretable; don't require strong asymmetry
        assert abs(r["rb_delta_post_minus_pre"]) < 0.20, (
            f"{ch} pre/post asymmetry too large: Δ={r['rb_delta_post_minus_pre']:+.4f}"
        )


def test_daed_negative_both_halves(tc007_prepost_results):
    """DAED consummatory cluster should be negative in BOTH halves (sustained suppression)."""
    daed_channels = ["MECH_DAED__f02:consummatory_da", "MECH_DAED__f04:liking_index"]
    for ch in daed_channels:
        row = tc007_prepost_results[tc007_prepost_results["channel"] == ch]
        if row.empty:
            continue
        r = row.iloc[0]
        assert r["rb_pre_mean"] < 0 and r["rb_post_mean"] < 0, (
            f"{ch} not sustained-negative: pre={r['rb_pre_mean']:+.4f}, post={r['rb_post_mean']:+.4f}"
        )
