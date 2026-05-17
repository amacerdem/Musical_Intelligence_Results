"""L6 — Morph operator correctness via analytical anchors.

Each test stimulus has analytically-known temporal structure; we assert that
the corresponding T³ morph reproduces the expected qualitative + quantitative
behavior. The empirical anchors below were measured against engine HEAD
(SHA 482ade45c..., 2026-05-08) on 2026-05-09 with the harness in `_infra/`.

Numeric tolerances are explicit: most morph outputs match within 1e-3 to
1e-2 because of the engine's float32 + attention-weighted averaging. Where
the operator output saturates at 0.0 / 1.0 (no boundary noise), tolerance
is tightened to bit-identical equality.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helper to extract value at the middle frame (avoids boundary effects)
# ---------------------------------------------------------------------------

def mid_value(out, key) -> float:
    """Return the middle-frame value of an extract output for one tuple."""
    tensor = out.features[key]
    T = tensor.shape[1]
    return tensor[0, T // 2].item()


# ===========================================================================
# L6.M0 — value (attention-weighted mean)
# ===========================================================================

class TestM0_Value:
    """Level operator: attention-weighted mean over the window."""

    def test_constant_07_returns_07(self, h3_extract, stim):
        """On constant input 0.7, M0 returns 0.7 exactly (no noise)."""
        features = stim.stim_constant(value=0.7, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 0, 0)) == pytest.approx(0.7, abs=1e-6)

    def test_silence_returns_zero(self, h3_extract, stim):
        """On silence (zero stream), M0 returns 0."""
        features = stim.stim_silence(T=512)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 0, 0)) == 0.0

    def test_linear_ramp_midpoint_near_05(self, h3_extract, stim):
        """On linear ramp 0→1, M0 at the midpoint is near 0.5 (attention-weighted toward recent)."""
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
        out = h3_extract(features, demand)
        v = mid_value(out, (10, 5, 0, 0))
        # Empirical anchor: 0.4978 measured at engine HEAD 482ade45c
        assert v == pytest.approx(0.498, abs=5e-3)


# ===========================================================================
# L6.M2 — std (standard deviation of windowed values)
# ===========================================================================

class TestM2_Std:
    """Dispersion operator: std deviation. On constant or silence → 0."""

    def test_constant_returns_zero(self, h3_extract, stim):
        features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=2, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 2, 0)) == 0.0

    def test_silence_returns_zero(self, h3_extract, stim):
        features = stim.stim_silence(T=512)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=2, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 2, 0)) == 0.0

    def test_ramp_std_positive(self, h3_extract, stim):
        """On a linear ramp, std is positive (not zero) but small for small windows."""
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=2, law=0)
        out = h3_extract(features, demand)
        v = mid_value(out, (10, 5, 2, 0))
        # Empirical: 0.019 (M2 normalized by MORPH_SCALE[2]=0.25)
        assert 0.001 < v < 0.05


# ===========================================================================
# L6.M8 — velocity (first temporal derivative)
# ===========================================================================

class TestM8_Velocity:
    """Dynamics operator: M8 velocity. On constant → 0; on positive ramp → positive."""

    def test_constant_returns_zero(self, h3_extract, stim):
        features = stim.stim_constant(value=0.7, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=8, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 8, 0)) == 0.0

    def test_silence_returns_zero(self, h3_extract, stim):
        features = stim.stim_silence(T=512)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=8, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 8, 0)) == 0.0

    def test_positive_ramp_returns_positive(self, h3_extract, stim):
        """On linear ramp 0→1 over T frames, M8 velocity is positive."""
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=8, law=0)
        out = h3_extract(features, demand)
        v = mid_value(out, (10, 5, 8, 0))
        assert v > 0.0


# ===========================================================================
# L6.M14 — periodicity (autocorrelation peak)
# ===========================================================================

class TestM14_Periodicity:
    """Rhythm operator: M14 periodicity. Low on constant/silence; high on sinusoid
    when the horizon window matches or exceeds the signal period."""

    def test_silence_returns_zero(self, h3_extract, stim):
        features = stim.stim_silence(T=512)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=14, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 14, 0)) == 0.0

    def test_constant_near_zero(self, h3_extract, stim):
        """On constant, periodicity is near-zero (no oscillation to detect)."""
        features = stim.stim_constant(value=0.7, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=14, law=0)
        out = h3_extract(features, demand)
        v = mid_value(out, (10, 5, 14, 0))
        assert v < 0.05

    def test_sinusoid_peak_at_matching_horizon(self, h3_extract, stim):
        """On 4Hz sinusoid (period=43 frames), M14 peaks at H7 (43 frames) and stays high
        for larger horizons. H3 (4 frames) is too short → low; H7+ → high."""
        features = stim.stim_sinusoid(freq_hz=4.0, T=1024, r3_dim=10)
        demand = {(10, h, 14, 0) for h in [3, 5, 7, 9, 11]}
        out = h3_extract(features, demand)
        v_H3 = mid_value(out, (10, 3, 14, 0))
        v_H5 = mid_value(out, (10, 5, 14, 0))
        v_H7 = mid_value(out, (10, 7, 14, 0))
        v_H9 = mid_value(out, (10, 9, 14, 0))
        # H3 (4 frames) too short to see the period
        assert v_H3 < 0.05
        # H7 (43 frames) matches one period → high
        assert v_H7 > 0.85
        # H9 (60 frames) covers more than one period → still high
        assert v_H9 > 0.85
        # Monotone-ish increase from H3 → H7 (the period-matching horizon)
        assert v_H7 > v_H5 > v_H3


# ===========================================================================
# L6.M18 — trend (linear regression slope)
# ===========================================================================

class TestM18_Trend:
    """Dynamics operator: M18 trend = OLS slope.
    Constant → 0; positive ramp → positive (saturating); negative ramp → negative."""

    def test_constant_returns_zero(self, h3_extract, stim):
        features = stim.stim_constant(value=0.7, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=18, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 18, 0)) == 0.0

    def test_silence_returns_zero(self, h3_extract, stim):
        features = stim.stim_silence(T=512)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=18, law=0)
        out = h3_extract(features, demand)
        assert mid_value(out, (10, 5, 18, 0)) == 0.0

    def test_positive_ramp_returns_positive(self, h3_extract, stim):
        """On linear ramp 0→1 (slope=1/512 per frame), M18 saturates positive."""
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=18, law=0)
        out = h3_extract(features, demand)
        v = mid_value(out, (10, 5, 18, 0))
        # Empirical: 1.000 (saturated at MORPH_SCALE[18]=0.01 → small slope still saturates)
        assert v > 0.5  # any clearly-positive trend
