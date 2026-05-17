"""L5 — Short-clip robustness.

Engine must produce well-defined output for any T ≥ 1, including T much
smaller than the requested horizon's window size. Boundary handling uses
edge replication (per executor.py:193-198 + module docstring lines 19-20):

> "Boundary frames (truncated windows at sequence edges) are filled via
> edge replication — the nearest valid steady-state value is copied into
> boundary positions to prevent zero-artifacts in downstream layers that
> use semantic inversions (e.g. 1.0 - value)."

Tests cover:
  L5.5 single-frame clip (T=1, sub-horizon)
  L5.6 clip exactly at horizon-window boundary (T = H_frames)
  L5.6 clip smaller than horizon-window
"""
from __future__ import annotations

import pytest


def test_T1_single_frame_returns_shape_1(h3_extract, stim):
    """T=1 (single frame, much smaller than H5 window=8) → shape (1,1), no NaN."""
    features = stim.stim_constant(value=0.5, T=1, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert t.shape == (1, 1)
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    # Engine returns single value; for constant 0.5 input, M0 mean ≈ 0.5
    assert t[0, 0].item() == pytest.approx(0.5, abs=1e-6)


def test_T_at_horizon_boundary(h3_extract, stim):
    """T equals H5 window (8 frames): engine produces full output, every value 0.5."""
    features = stim.stim_constant(value=0.5, T=8, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert t.shape == (1, 8)
    assert not t.isnan().any().item()
    for i in range(8):
        assert t[0, i].item() == pytest.approx(0.5, abs=1e-6)


def test_T_smaller_than_horizon_window(h3_extract, stim):
    """T=4 (< H5 window=8): engine still produces (1, 4) output via edge replication."""
    features = stim.stim_constant(value=0.5, T=4, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert t.shape == (1, 4)
    assert not t.isnan().any().item()
    for i in range(4):
        assert t[0, i].item() == pytest.approx(0.5, abs=1e-6)


def test_T_smaller_than_largest_requested_horizon_macro(h3_extract, stim):
    """T=200 frames; request M0 at H16 (Macro, 172 frames) — works (window < T)."""
    features = stim.stim_constant(value=0.5, T=200, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=16, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 16, 0, 0)]
    assert t.shape == (1, 200)
    assert not t.isnan().any().item()
    assert t[0, 100].item() == pytest.approx(0.5, abs=1e-3)


def test_T_smaller_than_macro_horizon_window(h3_extract, stim):
    """T=50 frames; request M0 at H16 (Macro, 172 frames) — T<window, engine still produces."""
    features = stim.stim_constant(value=0.5, T=50, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=16, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 16, 0, 0)]
    assert t.shape == (1, 50)
    assert not t.isnan().any().item()
    # Whole window is the entire sequence; output should be near-constant 0.5
    assert t[0, 25].item() == pytest.approx(0.5, abs=1e-3)


def test_T_smaller_than_ultra_horizon_window(h3_extract, stim):
    """T=100; request M0 at H24 (Ultra, 6,202 frames) — T tiny vs window. Engine handles."""
    features = stim.stim_constant(value=0.5, T=100, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=24, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 24, 0, 0)]
    assert t.shape == (1, 100)
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    # Fall-back computation: single-value over full sequence, broadcast
    assert t[0, 50].item() == pytest.approx(0.5, abs=1e-3)


def test_T_at_largest_horizon_minus_one(h3_extract, stim):
    """T=H16-1=171; H16 window=172. Should still work via fall-back."""
    features = stim.stim_constant(value=0.5, T=171, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=16, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 16, 0, 0)]
    assert t.shape == (1, 171)
    assert not t.isnan().any().item()


def test_T1_silence(h3_extract, stim):
    """T=1 with silence input: M0 mean = 0, M2 std = 0 (well-defined for single frame)."""
    features = stim.stim_silence(T=1)
    demand = {(10, 5, 0, 0), (10, 5, 2, 0)}
    out = h3_extract(features, demand)
    assert out.features[(10, 5, 0, 0)][0, 0].item() == 0.0
    assert out.features[(10, 5, 2, 0)][0, 0].item() == 0.0


def test_short_clip_all_morphs_no_nan(h3_extract, stim):
    """T=4: all 24 morphs at H5 must produce finite, in-range output."""
    features = stim.stim_constant(value=0.5, T=4, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert tensor.shape == (1, 4)
        assert not tensor.isnan().any().item(), f"NaN in {key} on T=4"
        assert not tensor.isinf().any().item(), f"Inf in {key} on T=4"
