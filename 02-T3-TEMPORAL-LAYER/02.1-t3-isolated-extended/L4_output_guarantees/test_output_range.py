"""L4.2 — Per-morph output range.

H3Output docstring (extractor.py:38-42):
> "Unsigned morphs are in [0, 1]; signed morphs (M6, M8, M9, M11, M12, M16,
>  M18, M23) are in [-1, 1]."

Engine source: `Musical_Intelligence/ear/h3/morphology/scaling.py` clamps
outputs via `clamp(raw / scale, lo, hi)` where (lo, hi) = (0, 1) for unsigned
and (-1, 1) for signed.

We test this contract on:
- Constant 0.5 stream (mid-range; trivial probe)
- Linear ramp 0→1 (full range, drives M8 velocity / M18 trend signed outputs)
- Sinusoid (drives oscillatory morphs)

For each stimulus and each of the 24 morphs, we assert the output stays
within the documented bounds.
"""
from __future__ import annotations

import pytest


# Source-of-truth set (mirrors `Musical_Intelligence/ear/h3/constants/morphs.py:99-108`)
SIGNED_MORPHS = frozenset({6, 8, 9, 11, 12, 16, 18, 23})


def _bounds_for_morph(morph_idx: int) -> tuple[float, float]:
    """Return documented (lo, hi) range for morph_idx after engine normalisation."""
    if morph_idx in SIGNED_MORPHS:
        return (-1.0, 1.0)
    return (0.0, 1.0)


def _check_all_morphs_in_range(out, r3_idx: int, horizon: int, law: int,
                                  tol: float = 1e-6) -> list[str]:
    """Return list of failure messages (empty if all morphs in range)."""
    failures = []
    for morph_idx in range(24):
        key = (r3_idx, horizon, morph_idx, law)
        tensor = out.features[key]
        lo, hi = _bounds_for_morph(morph_idx)
        actual_min = tensor.min().item()
        actual_max = tensor.max().item()
        if actual_min < lo - tol:
            failures.append(
                f"M{morph_idx} min={actual_min:.6f} below lo={lo} "
                f"(signed={morph_idx in SIGNED_MORPHS})"
            )
        if actual_max > hi + tol:
            failures.append(
                f"M{morph_idx} max={actual_max:.6f} above hi={hi} "
                f"(signed={morph_idx in SIGNED_MORPHS})"
            )
    return failures


# ===========================================================================
# Per-stimulus × per-morph range checks
# ===========================================================================

class TestRange_AllMorphs_Constant:
    """All 24 morphs on a constant-0.5 stream stay within documented bounds."""

    def test_at_H5_L0(self, h3_extract, stim):
        features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 5, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)

    def test_at_H10_L1(self, h3_extract, stim):
        features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=10, law=1)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 10, 1)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)

    def test_at_H15_L2(self, h3_extract, stim):
        features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=15, law=2)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 15, 2)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)


class TestRange_AllMorphs_Ramp:
    """All 24 morphs on a linear ramp 0→1 stream stay within documented bounds.
    This stimulus exercises signed morphs (M8 velocity, M18 trend → positive)."""

    def test_at_H5_L0(self, h3_extract, stim):
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 5, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)

    def test_at_H10_L1(self, h3_extract, stim):
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=10, law=1)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 10, 1)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)


class TestRange_AllMorphs_Sinusoid:
    """All 24 morphs on a sinusoidal stream — exercises rhythm/dynamics morphs."""

    def test_at_H5_L0(self, h3_extract, stim):
        features = stim.stim_sinusoid(freq_hz=4.0, amp=0.4, dc=0.5, T=1024, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 5, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)

    def test_at_H10_L0(self, h3_extract, stim):
        features = stim.stim_sinusoid(freq_hz=4.0, amp=0.4, dc=0.5, T=1024, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=10, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 10, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)


class TestRange_AllMorphs_Silence:
    """All 24 morphs on silence (zeros) — every morph should reduce to its documented zero/identity."""

    def test_at_H5_L0(self, h3_extract, stim):
        features = stim.stim_silence(T=512)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 5, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)


class TestRange_AllMorphs_Impulse:
    """All 24 morphs on a single-frame impulse — extreme test of derivative/peak morphs."""

    def test_at_H5_L0(self, h3_extract, stim):
        features = stim.stim_impulse(impulse_at=256, height=1.0, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        failures = _check_all_morphs_in_range(out, 10, 5, 0)
        assert not failures, "Range violations:\n  " + "\n  ".join(failures)


# ===========================================================================
# Signed-morph property: signed morphs CAN go negative; unsigned cannot
# ===========================================================================

class TestSignedMorphsCanGoNegative:
    """A descending ramp 1→0 should produce negative output for signed morphs M8, M18."""

    def test_M8_velocity_negative_on_descending_ramp(self, h3_extract, stim):
        features = stim.stim_linear_ramp(start=1.0, end=0.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=8, law=0)
        out = h3_extract(features, demand)
        v = out.features[(10, 5, 8, 0)][0, 256].item()
        assert v < 0.0, f"M8 (signed) on descending ramp expected < 0, got {v}"
        assert v >= -1.0, f"M8 in [-1, 1] bound, got {v}"

    def test_M18_trend_negative_on_descending_ramp(self, h3_extract, stim):
        features = stim.stim_linear_ramp(start=1.0, end=0.0, T=512, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=18, law=0)
        out = h3_extract(features, demand)
        v = out.features[(10, 5, 18, 0)][0, 256].item()
        assert v < 0.0, f"M18 (signed) on descending ramp expected < 0, got {v}"
        assert v >= -1.0, f"M18 in [-1, 1] bound, got {v}"


class TestUnsignedMorphsAlwaysNonNegative:
    """Unsigned morphs (M0, M2, M14, M20, etc.) must never go negative regardless of input."""

    def test_M0_M2_M14_nonnegative_on_descending_ramp(self, h3_extract, stim):
        features = stim.stim_linear_ramp(start=1.0, end=0.0, T=512, r3_dim=10)
        demand = {(10, 5, m, 0) for m in [0, 2, 14, 20]}
        out = h3_extract(features, demand)
        for m in [0, 2, 14, 20]:
            v = out.features[(10, 5, m, 0)][0, 256].item()
            assert v >= 0.0, f"M{m} (unsigned) returned negative {v}"
            assert v <= 1.0, f"M{m} (unsigned) returned > 1: {v}"
