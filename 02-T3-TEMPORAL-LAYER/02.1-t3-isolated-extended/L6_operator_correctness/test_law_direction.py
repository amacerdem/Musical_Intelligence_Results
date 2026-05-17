"""L6 — Causal-law direction (L0/L1/L2) sign-asymmetry.

Build two streams that are byte-identical for `t < T_split` and differ for
`t >= T_split`. Then for any frame `t_check` whose window is entirely
before `T_split`:
  * L0 (memory; reads `[t-h, t]`): outputs IDENTICAL when `t_check + 0 < T_split`
  * L1 (forward; reads `[t, t+h]`): outputs DIFFER when `t_check + h >= T_split`
  * L2 (integration; reads `[t-h/2, t+h/2]`): outputs DIFFER when `t_check + h/2 >= T_split`

This is the key behavioural test of the engine's causal-law contract: the
predictive-coding interpretation requires L0 to be strictly causal.
"""
from __future__ import annotations

import pytest
import torch


def _build_perturbation_pair(T_total: int, T_split: int, r3_dim: int = 10):
    """Return (stream_A, stream_B) identical for t<T_split, differ for t>=T_split."""
    from _infra import stimuli as stim
    ramp = torch.linspace(0.0, 1.0, T_total)
    stream_A = stim.stim_single_dim_only(ramp, r3_dim=r3_dim)
    ramp_B = ramp.clone()
    ramp_B[T_split:] = 0.5  # Perturb future: hold at 0.5 instead of continuing ramp
    stream_B = stim.stim_single_dim_only(ramp_B, r3_dim=r3_dim)
    return stream_A, stream_B


# ===========================================================================
# L6.law.L0 — Memory (causal-only, past-window)
# ===========================================================================

class TestL0_Memory_Causal:
    """L0 reads `[t-h, t]`: a perturbation at frames `>= T_split` cannot affect
    output at any `t_check < T_split`. Bit-identical."""

    def test_L0_unaffected_by_future_perturbation_H5(self, h3_extract, stim):
        """At H5 (window=8), L0 at t=195 reads [188-195] (entirely before split=200)."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)  # L0
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        for t_check in [50, 100, 150, 195, 199]:
            a = out_A.features[(10, 5, 0, 0)][0, t_check].item()
            b = out_B.features[(10, 5, 0, 0)][0, t_check].item()
            assert a == b, (
                f"L0 not strictly causal at t={t_check}: a={a}, b={b}, diff={abs(a-b)}"
            )

    def test_L0_unaffected_at_larger_horizon_H10(self, h3_extract, stim):
        """At H10 (window=69), L0 at t<=199 reads [t-68, t] which never crosses 200."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=10, morph=0, law=0)
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        for t_check in [100, 150, 175, 195, 199]:
            a = out_A.features[(10, 10, 0, 0)][0, t_check].item()
            b = out_B.features[(10, 10, 0, 0)][0, t_check].item()
            assert a == b, (
                f"L0 not strictly causal at t={t_check}, H10: a={a}, b={b}, diff={abs(a-b)}"
            )


# ===========================================================================
# L6.law.L1 — Forward (anticipatory, future-window)
# ===========================================================================

class TestL1_Forward_Anticipatory:
    """L1 reads `[t, t+h]`: a perturbation at `t_split` SHOULD affect output at any
    `t_check` such that `t_check + h >= T_split`. Outputs DIFFER."""

    def test_L1_affected_by_future_perturbation_H5(self, h3_extract, stim):
        """At H5 (window=8), L1 at t=195 reads [195-202]: spans the split=200."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=1)  # L1
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        # Frames whose forward window crosses T_split=200: t in [193, 200)
        for t_check in [195, 197, 199]:
            a = out_A.features[(10, 5, 0, 1)][0, t_check].item()
            b = out_B.features[(10, 5, 0, 1)][0, t_check].item()
            assert a != b, (
                f"L1 not anticipatory at t={t_check}: outputs identical "
                f"despite perturbation in [t, t+7] window"
            )

    def test_L1_unaffected_when_window_fully_before_split(self, h3_extract, stim):
        """At H5, L1 at t=190 reads [190-197]: entirely before split=200."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=1)
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        for t_check in [50, 100, 150, 190]:
            a = out_A.features[(10, 5, 0, 1)][0, t_check].item()
            b = out_B.features[(10, 5, 0, 1)][0, t_check].item()
            assert a == b, (
                f"L1 affected at t={t_check} where window does not reach split"
            )


# ===========================================================================
# L6.law.L2 — Integration (bidirectional symmetric)
# ===========================================================================

class TestL2_Integration_Bidirectional:
    """L2 reads `[t-h/2, t+h/2]`: differs from A's output when window reaches future."""

    def test_L2_affected_when_symmetric_window_reaches_split(self, h3_extract, stim):
        """At H5 (window=8, half=4), L2 at t=197 reads [193-201]: crosses split=200."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=2)  # L2
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        for t_check in [197, 199]:
            a = out_A.features[(10, 5, 0, 2)][0, t_check].item()
            b = out_B.features[(10, 5, 0, 2)][0, t_check].item()
            assert a != b, (
                f"L2 not bidirectional at t={t_check}: outputs identical "
                f"despite future portion of window crossing split"
            )

    def test_L2_unaffected_when_symmetric_window_fully_before_split(self, h3_extract, stim):
        """At H5, L2 at t=190 reads [186-194]: entirely before split=200."""
        T_split = 200
        A, B = _build_perturbation_pair(T_total=512, T_split=T_split)
        demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=2)
        out_A = h3_extract(A, demand)
        out_B = h3_extract(B, demand)
        for t_check in [50, 100, 150, 190]:
            a = out_A.features[(10, 5, 0, 2)][0, t_check].item()
            b = out_B.features[(10, 5, 0, 2)][0, t_check].item()
            assert a == b, (
                f"L2 affected at t={t_check} where window does not reach split"
            )


# ===========================================================================
# L6.law.cross — Sign-asymmetry: L0/L1 differ on directional input
# ===========================================================================

class TestLawSignAsymmetry:
    """On a positive ramp, L0 (looks back at smaller values) outputs LESS than
    L1 (looks forward at larger values). Both should be positive but L0 < L1
    at frames not too close to the boundaries.

    Documented as 'L0 memory and L1 forward differ by 0.0126' in the T³ paper
    (analytical T11)."""

    def test_L0_lt_L1_on_positive_ramp(self, h3_extract, stim):
        """Mid-ramp, L0 (past mean) < L1 (future mean) for an increasing signal."""
        features = stim.stim_linear_ramp(start=0.0, end=1.0, T=512, r3_dim=10)
        demand = {(10, 7, 0, l) for l in [0, 1]}  # H7 = 43 frames
        out = h3_extract(features, demand)
        T = 512
        # Sample at the middle (t=256), where past and future windows are balanced
        v_L0 = out.features[(10, 7, 0, 0)][0, T // 2].item()
        v_L1 = out.features[(10, 7, 0, 1)][0, T // 2].item()
        assert v_L0 < v_L1, (
            f"On positive ramp at midpoint, expected L0 < L1; got L0={v_L0}, L1={v_L1}"
        )
