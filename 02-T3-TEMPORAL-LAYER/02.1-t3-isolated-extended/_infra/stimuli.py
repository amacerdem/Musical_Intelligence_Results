"""Analytical R³ feature-stream generators for T³ isolated validation.

T³ takes an R³ feature tensor of shape ``(B, T, 97)`` (values in ``[0, 1]``)
and a demand set, and returns sparse morphological-temporal features. To
test T³ in isolation, we need R³ feature streams whose temporal structure
is fully analytically known, so each morph operator's output is independently
predictable.

This module provides such generators. All return ``Tensor`` of shape
``(B, T, 97)`` unless documented otherwise. The default ``T = 1024`` frames
(~6 s at 172.27 Hz) is sufficient to cover Micro/Meso horizons; tests
needing Macro/Ultra horizons should pass larger ``T`` explicitly.

Source of truth
---------------
- ``Musical_Intelligence/ear/h3/constants/horizons.py`` for FRAME_RATE
- ``Musical_Intelligence/ear/h3/constants/morphs.py`` for morph definitions

All stimuli are deterministic: zero PRNG, zero seed, zero hidden state.
"""
from __future__ import annotations

from typing import Optional

import torch
from torch import Tensor

# Engine-canonical frame rate (matches Musical_Intelligence.ear.h3.constants.horizons.FRAME_RATE)
FRAME_RATE: float = 172.27
N_R3_DIMS: int = 97
DEFAULT_T: int = 1024  # ~5.94 s at 172.27 Hz


# ---------------------------------------------------------------------------
# Constant streams
# ---------------------------------------------------------------------------

def stim_constant(value: float = 0.5, T: int = DEFAULT_T, B: int = 1,
                   r3_dim: Optional[int] = None) -> Tensor:
    """All-ones (or any scalar) R³ stream. Optionally restrict to a single dim.

    Use cases:
    - L6.M0 mean → output = constant value
    - L6.M2 std  → output = 0
    - L6.M8 velocity → output = 0
    - L6.M14 periodicity → well-defined (constant has trivial autocorrelation)
    """
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"value must be in [0, 1], got {value}")
    out = torch.full((B, T, N_R3_DIMS), value, dtype=torch.float32)
    if r3_dim is not None:
        # Zero everything except the chosen dim
        mask = torch.zeros(N_R3_DIMS, dtype=torch.float32)
        mask[r3_dim] = 1.0
        out = out * mask
        out[:, :, r3_dim] = value  # restore the chosen dim's value
    return out


def stim_silence(T: int = DEFAULT_T, B: int = 1) -> Tensor:
    """All-zero R³ stream. Edge case: every morph well-defined on zeros."""
    return torch.zeros((B, T, N_R3_DIMS), dtype=torch.float32)


# ---------------------------------------------------------------------------
# Ramp streams
# ---------------------------------------------------------------------------

def stim_linear_ramp(start: float = 0.0, end: float = 1.0,
                     T: int = DEFAULT_T, B: int = 1,
                     r3_dim: Optional[int] = None) -> Tensor:
    """Linearly-increasing R³ stream from ``start`` to ``end`` over ``T`` frames.

    Use cases:
    - L6.M0 mean → ≈ (start + end) / 2
    - L6.M8 velocity → ≈ (end - start) / T (positive, constant)
    - L6.M18 trend → positive slope = (end - start) / T
    """
    ramp = torch.linspace(start, end, T, dtype=torch.float32)  # (T,)
    out = ramp.unsqueeze(0).unsqueeze(-1).expand(B, T, N_R3_DIMS).clone()
    if r3_dim is not None:
        out_zero = torch.zeros_like(out)
        out_zero[:, :, r3_dim] = out[:, :, r3_dim]
        return out_zero
    return out


def stim_step(low: float = 0.0, high: float = 1.0, step_at: Optional[int] = None,
              T: int = DEFAULT_T, B: int = 1,
              r3_dim: Optional[int] = None) -> Tensor:
    """Step function: low for first half, high for second half (or at ``step_at``).

    Use cases:
    - L6.M14 periodicity → low (no oscillation)
    - L6.M18 trend → positive (mean shifts up)
    - L6.M22 peak count → 0 or 1
    """
    if step_at is None:
        step_at = T // 2
    seq = torch.full((T,), low, dtype=torch.float32)
    seq[step_at:] = high
    out = seq.unsqueeze(0).unsqueeze(-1).expand(B, T, N_R3_DIMS).clone()
    if r3_dim is not None:
        out_zero = torch.zeros_like(out)
        out_zero[:, :, r3_dim] = out[:, :, r3_dim]
        return out_zero
    return out


# ---------------------------------------------------------------------------
# Periodic streams (analytically-known M14 / M22 outputs)
# ---------------------------------------------------------------------------

def stim_sinusoid(freq_hz: float = 4.0, amp: float = 0.5, dc: float = 0.5,
                   T: int = DEFAULT_T, B: int = 1,
                   r3_dim: Optional[int] = None,
                   phase_rad: float = 0.0) -> Tensor:
    """Sinusoidal R³ stream at ``freq_hz`` (cycles per second).

    output[t] = dc + amp * sin(2π * freq_hz * t / FRAME_RATE + phase)

    Use cases:
    - L6.M14 periodicity → strong autocorrelation peak at horizon ≈ FRAME_RATE / freq_hz
    - L6.M22 peak count → ≈ duration_s * freq_hz
    - L6.M2  std → amp / sqrt(2)
    """
    if not (0.0 <= dc - amp and dc + amp <= 1.0):
        raise ValueError(f"sinusoid (dc={dc}, amp={amp}) must stay in [0, 1]")
    t_axis = torch.arange(T, dtype=torch.float32)
    seq = dc + amp * torch.sin(2 * torch.pi * freq_hz * t_axis / FRAME_RATE + phase_rad)
    out = seq.unsqueeze(0).unsqueeze(-1).expand(B, T, N_R3_DIMS).clone()
    if r3_dim is not None:
        out_zero = torch.zeros_like(out)
        out_zero[:, :, r3_dim] = out[:, :, r3_dim]
        return out_zero
    return out


def stim_am_modulated(carrier_dc: float = 0.5, mod_freq_hz: float = 4.0,
                       mod_depth: float = 0.5, T: int = DEFAULT_T, B: int = 1,
                       r3_dim: Optional[int] = None) -> Tensor:
    """Amplitude-modulated R³ stream: dc * (1 + mod_depth * sin(2π * f_m * t / FRAME_RATE)).

    Equivalent to ``stim_sinusoid(freq_hz=mod_freq_hz, amp=carrier_dc*mod_depth, dc=carrier_dc)``
    but conceptually emphasises the AM-modulation interpretation.
    """
    return stim_sinusoid(
        freq_hz=mod_freq_hz, amp=carrier_dc * mod_depth, dc=carrier_dc,
        T=T, B=B, r3_dim=r3_dim,
    )


# ---------------------------------------------------------------------------
# Impulse / Dirac
# ---------------------------------------------------------------------------

def stim_impulse(impulse_at: Optional[int] = None, height: float = 1.0,
                  baseline: float = 0.0, T: int = DEFAULT_T, B: int = 1,
                  r3_dim: Optional[int] = None) -> Tensor:
    """Single-frame impulse at ``impulse_at`` (default: T//2).

    Use cases:
    - L6.M22 peak count → 1
    - L6.M0 mean → ≈ height/T (very small)
    - L6.M2 std → ≈ sqrt(height² / T)
    """
    if impulse_at is None:
        impulse_at = T // 2
    seq = torch.full((T,), baseline, dtype=torch.float32)
    seq[impulse_at] = height
    out = seq.unsqueeze(0).unsqueeze(-1).expand(B, T, N_R3_DIMS).clone()
    if r3_dim is not None:
        out_zero = torch.zeros_like(out)
        out_zero[:, :, r3_dim] = out[:, :, r3_dim]
        return out_zero
    return out


# ---------------------------------------------------------------------------
# Composite — one dim varies, others zero
# ---------------------------------------------------------------------------

def stim_single_dim_only(values: Tensor, r3_dim: int = 10, B: int = 1) -> Tensor:
    """Wrap a 1-D ``values`` tensor (length T) into shape (B, T, 97), placing
    it at ``r3_dim`` and zeroing all other dims.

    Useful when testing how a single R³ feature's temporal structure
    propagates through T³, isolating from cross-feature interactions.
    """
    T = values.shape[0]
    out = torch.zeros((B, T, N_R3_DIMS), dtype=torch.float32)
    out[:, :, r3_dim] = values
    return out


# ---------------------------------------------------------------------------
# Demand factories — minimal demand sets for testing
# ---------------------------------------------------------------------------

def demand_single(r3_idx: int = 10, horizon: int = 5, morph: int = 0,
                   law: int = 0) -> set:
    """Return a single-tuple demand set."""
    return {(r3_idx, horizon, morph, law)}


def demand_all_morphs_one_horizon(r3_idx: int = 10, horizon: int = 5,
                                    law: int = 0) -> set:
    """Demand all 24 morphs at one (r3_idx, horizon, law) combination."""
    return {(r3_idx, horizon, m, law) for m in range(24)}


def demand_all_horizons_one_morph(r3_idx: int = 10, morph: int = 0,
                                    law: int = 0) -> set:
    """Demand all 32 horizons for one (r3_idx, morph, law) combination."""
    return {(r3_idx, h, morph, law) for h in range(32)}


def demand_all_laws_one_tuple(r3_idx: int = 10, horizon: int = 5,
                                morph: int = 0) -> set:
    """Demand all 3 laws for one (r3_idx, horizon, morph) combination."""
    return {(r3_idx, horizon, morph, l) for l in range(3)}
