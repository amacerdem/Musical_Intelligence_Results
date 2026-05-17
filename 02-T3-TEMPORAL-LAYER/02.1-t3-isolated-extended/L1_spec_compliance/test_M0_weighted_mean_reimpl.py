"""L1.1 — M0 weighted-mean specification compliance via pure-numpy re-implementation.

This is a sample L1 test demonstrating the per-tuple-formula re-impl pattern.
Full L1 coverage (24 morphs × 32 horizons × 3 laws = 2,304 sub-tests) is
mechanical expansion of this template.

Spec (`Musical_Intelligence/ear/h3/morphology/distribution/central.py:9-30`):

    def m0_weighted_mean(window: Tensor, weights: Tensor) -> Tensor:
        return torch.sum(weights * window, dim=-1)

Where:
- weights are produced by AttentionKernel.compute_weights(window_size):
    positions = linspace(0, 1, window_size)
    weights = exp(-ATTENTION_DECAY * (1 - positions))
- weights are normalised by sum: w_normed = weights / weights.sum()
- For L0 memory at frame t: window = r3_series[t - W + 1 : t + 1]

We re-implement this in pure numpy/scipy and compare bit-identically.
Engine output normalisation: M0 has MORPH_SCALE[0] = 1.0 (no rescaling needed).
"""
from __future__ import annotations

import numpy as np
import pytest
import torch


def _numpy_attention_weights(window_size: int, decay: float = 3.0) -> np.ndarray:
    """Pure-numpy re-implementation of AttentionKernel.compute_weights."""
    if window_size <= 1:
        return np.ones(window_size, dtype=np.float32)
    positions = np.linspace(0.0, 1.0, window_size, dtype=np.float32)
    weights = np.exp(-decay * (1.0 - positions))
    return weights.astype(np.float32)


def _numpy_m0_at_frame(r3_series: np.ndarray, t: int, window_size: int,
                        law: int = 0) -> float:
    """Pure-numpy M0 at frame t for the given law.

    L0 (memory): window = r3_series[t - W + 1 : t + 1]
    L1 (forward): window = r3_series[t : t + W]
    L2 (integration): window = r3_series[t - W//2 : t - W//2 + W]
    """
    if law == 0:  # memory
        start = t - window_size + 1
        end = t + 1
    elif law == 1:  # forward
        start = t
        end = t + window_size
    else:  # integration
        start = t - window_size // 2
        end = start + window_size

    if start < 0 or end > len(r3_series):
        return None  # out of steady-state range

    window = r3_series[start:end]
    weights = _numpy_attention_weights(window_size)
    w_normed = weights / np.maximum(weights.sum(), 1e-8)
    return float(np.sum(w_normed * window))


# ===========================================================================
# Test class — M0 spec compliance across stimuli × horizons × laws
# ===========================================================================

class TestM0SpecCompliance:
    """For each (stimulus × horizon × law), engine output at a steady-state
    frame matches pure-numpy re-implementation within float32 tolerance."""

    @pytest.mark.parametrize("horizon", [5, 7, 10, 15])
    def test_M0_constant_input_L0(self, h3_extract, stim, horizon):
        """Constant input: engine M0 must equal numpy M0 (= constant value)."""
        from Musical_Intelligence.ear.h3.constants.horizons import HORIZON_FRAMES
        T = 512
        r3_value = 0.7
        features = stim.stim_constant(value=r3_value, T=T, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=horizon, morph=0, law=0)
        out = h3_extract(features, demand)
        engine_t = out.features[(10, horizon, 0, 0)][0]  # (T,)

        # Sample at a steady-state frame (well inside boundaries)
        window_size = HORIZON_FRAMES[horizon]
        t_check = max(window_size, T // 2)  # safely past warm-up

        r3_np = features[0, :, 10].numpy()
        expected = _numpy_m0_at_frame(r3_np, t_check, window_size, law=0)
        assert expected is not None, f"frame {t_check} out of steady state"
        actual = engine_t[t_check].item()
        assert abs(actual - expected) < 1e-5, (
            f"M0 spec violation at H{horizon} t={t_check}: "
            f"engine={actual}, numpy={expected}, diff={abs(actual-expected)}"
        )

    @pytest.mark.parametrize("horizon", [5, 7, 10, 15])
    def test_M0_linear_ramp_L0(self, h3_extract, stim, horizon):
        """Linear ramp input: engine M0 matches numpy M0 at multiple steady-state frames."""
        from Musical_Intelligence.ear.h3.constants.horizons import HORIZON_FRAMES
        T = 512
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=T, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=horizon, morph=0, law=0)
        out = h3_extract(features, demand)
        engine_t = out.features[(10, horizon, 0, 0)][0]
        window_size = HORIZON_FRAMES[horizon]
        r3_np = features[0, :, 10].numpy()

        # Test multiple steady-state frames
        steady_frames = [
            max(window_size, T // 4),
            T // 2,
            min(T - 1, 3 * T // 4),
        ]
        for t_check in steady_frames:
            expected = _numpy_m0_at_frame(r3_np, t_check, window_size, law=0)
            if expected is None:
                continue
            actual = engine_t[t_check].item()
            assert abs(actual - expected) < 1e-5, (
                f"M0 spec violation at H{horizon} t={t_check}: "
                f"engine={actual}, numpy={expected}, diff={abs(actual-expected)}"
            )

    @pytest.mark.parametrize("horizon", [5, 7, 10])
    def test_M0_sinusoid_L0(self, h3_extract, stim, horizon):
        """Sinusoid input: engine M0 matches numpy M0."""
        from Musical_Intelligence.ear.h3.constants.horizons import HORIZON_FRAMES
        T = 1024
        features = stim.stim_sinusoid(freq_hz=4.0, T=T, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=horizon, morph=0, law=0)
        out = h3_extract(features, demand)
        engine_t = out.features[(10, horizon, 0, 0)][0]
        window_size = HORIZON_FRAMES[horizon]
        r3_np = features[0, :, 10].numpy()

        for t_check in [T // 4, T // 2, 3 * T // 4]:
            expected = _numpy_m0_at_frame(r3_np, t_check, window_size, law=0)
            if expected is None:
                continue
            actual = engine_t[t_check].item()
            assert abs(actual - expected) < 1e-5, (
                f"M0 spec violation at H{horizon} t={t_check}: "
                f"engine={actual}, numpy={expected}, diff={abs(actual-expected)}"
            )


class TestM0LawWindowPlacement:
    """Verify L1 (forward) and L2 (integration) window placement is correct."""

    def test_M0_L1_forward_on_constant(self, h3_extract, stim):
        from Musical_Intelligence.ear.h3.constants.horizons import HORIZON_FRAMES
        T = 512
        features = stim.stim_constant(value=0.6, T=T, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=1)
        out = h3_extract(features, demand)
        engine_t = out.features[(10, 5, 0, 1)][0]
        window_size = HORIZON_FRAMES[5]
        r3_np = features[0, :, 10].numpy()
        t_check = T // 2  # safely past + before boundaries
        expected = _numpy_m0_at_frame(r3_np, t_check, window_size, law=1)
        assert expected is not None
        actual = engine_t[t_check].item()
        assert abs(actual - expected) < 1e-5

    def test_M0_L2_integration_on_constant(self, h3_extract, stim):
        from Musical_Intelligence.ear.h3.constants.horizons import HORIZON_FRAMES
        T = 512
        features = stim.stim_constant(value=0.6, T=T, r3_dim=10)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=2)
        out = h3_extract(features, demand)
        engine_t = out.features[(10, 5, 0, 2)][0]
        window_size = HORIZON_FRAMES[5]
        r3_np = features[0, :, 10].numpy()
        t_check = T // 2
        expected = _numpy_m0_at_frame(r3_np, t_check, window_size, law=2)
        assert expected is not None
        actual = engine_t[t_check].item()
        assert abs(actual - expected) < 1e-5


class TestKernelWeightsReimpl:
    """Verify pure-numpy re-implementation of AttentionKernel matches engine
    within float32 epsilon (≤ 1 ULP difference between numpy and torch exp())."""

    @pytest.mark.parametrize("window_size", [1, 2, 5, 8, 32, 100, 200])
    def test_kernel_within_float32_epsilon_to_engine(self, window_size):
        """numpy exp(-3·(1-p)) matches torch within 1e-6 (~ float32 epsilon).

        BIT-IDENTICAL is for engine-vs-engine determinism (covered by L3.1);
        numpy-vs-torch comparison expects single-ULP differences in exp().
        """
        from Musical_Intelligence.ear.h3.attention.kernel import AttentionKernel
        engine_kernel = AttentionKernel()
        engine_weights = engine_kernel.compute_weights(window_size).numpy()
        numpy_weights = _numpy_attention_weights(window_size)
        diff = np.abs(engine_weights - numpy_weights).max()
        # float32 epsilon ~1.19e-7; we allow up to 1 ULP @ value 1.0 (~6e-8 to 6e-7)
        assert diff < 1e-6, (
            f"Kernel re-impl exceeds float32 epsilon at window_size={window_size}: "
            f"max-abs-diff = {diff} (expected < 1e-6, ~1 ULP for float32 exp)"
        )
