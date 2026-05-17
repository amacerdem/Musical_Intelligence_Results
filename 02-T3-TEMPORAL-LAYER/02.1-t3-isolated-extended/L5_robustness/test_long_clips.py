"""L5 — Long-clip robustness (Macro / Ultra horizons).

Engine must produce well-defined output for clips long enough to cover
Macro (H16-H23: 172-4,307 frames = 1-25 s) and Ultra (H24-H31: 6,202-168,999
frames = 36-981 s) horizon windows.

Tests cover:
  L5.7 clip approaching MAX_DURATION_S: Ultra horizons properly bounded
"""
from __future__ import annotations

import pytest


def test_macro_horizon_full_window(h3_extract, stim):
    """T=200 frames covers H16 (172 frames) — Macro band entry."""
    features = stim.stim_constant(value=0.5, T=200, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=16, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 16, 0, 0)]
    assert t.shape == (1, 200)
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()


def test_macro_horizon_multi_window(h3_extract, stim):
    """T=600 frames covers H16 multiple times (3.5×); H17 (259 frames) about twice."""
    features = stim.stim_constant(value=0.7, T=600, r3_dim=10)
    demand = {(10, h, 0, 0) for h in [16, 17, 18]}
    out = h3_extract(features, demand)
    for h in [16, 17, 18]:
        t = out.features[(10, h, 0, 0)]
        assert t.shape == (1, 600)
        assert not t.isnan().any().item()
        # Constant input → M0 mean ≈ 0.7 throughout
        assert t[0, 300].item() == pytest.approx(0.7, abs=1e-3)


def test_ultra_horizon_short_subwindow(h3_extract, stim):
    """T=1000 << H24 window (6,202 frames). Engine fall-back to single-value-broadcast."""
    features = stim.stim_constant(value=0.7, T=1000, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=24, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 24, 0, 0)]
    assert t.shape == (1, 1000)
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    # Constant → M0 mean = 0.7 broadcast across all frames
    assert t[0, 500].item() == pytest.approx(0.7, abs=1e-3)


def test_ultra_horizon_full_window_H24(h3_extract, stim):
    """T=8000 frames > H24 window (6,202). Both fall-back and steady-state available."""
    features = stim.stim_constant(value=0.5, T=8000, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=24, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 24, 0, 0)]
    assert t.shape == (1, 8000)
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    # Constant → output = 0.5 throughout
    assert t[0, 4000].item() == pytest.approx(0.5, abs=1e-3)


def test_max_duration_envelope_30s(h3_extract, stim):
    """T=5165 frames ≈ 30 s @ 172.27 Hz (engine MAX_DURATION_S envelope per L9.4 / L8.4).
    Macro horizons H16-H22 should all produce well-defined output."""
    features = stim.stim_constant(value=0.5, T=5165, r3_dim=10)
    demand = {(10, h, 0, 0) for h in [16, 17, 18, 19, 20, 21, 22]}
    out = h3_extract(features, demand)
    for h in [16, 17, 18, 19, 20, 21, 22]:
        t = out.features[(10, h, 0, 0)]
        assert t.shape == (1, 5165)
        assert not t.isnan().any().item(), f"NaN at H{h}"
        assert not t.isinf().any().item(), f"Inf at H{h}"


def test_ultra_band_all_horizons_short_clip(h3_extract, stim):
    """All 8 Ultra horizons (H24-H31) on a short clip (T=200): all must produce finite output via fall-back."""
    features = stim.stim_constant(value=0.5, T=200, r3_dim=10)
    demand = {(10, h, 0, 0) for h in range(24, 32)}
    out = h3_extract(features, demand)
    for h in range(24, 32):
        t = out.features[(10, h, 0, 0)]
        assert t.shape == (1, 200)
        assert not t.isnan().any().item(), f"NaN at H{h}"
        assert not t.isinf().any().item(), f"Inf at H{h}"
        # All Ultra horizons fall-back to whole-sequence; constant → 0.5
        assert t[0, 100].item() == pytest.approx(0.5, abs=1e-3)
