"""L5 — Input-extreme behavior probes.

Documents engine behavior on R³ inputs that violate the documented domain
(values in [0, 1], no NaN, no Inf). Engine has NO INPUT VALIDATION at the
T³ stage — well-formed input is the upstream R³ extractor's contract.
This test documents what happens if upstream contracts are violated, so
downstream consumers can decide whether to validate before calling T³.

Tests cover:
  L5.8 NaN in R³ input → propagated to output (engine does NOT sanitize)
  L5.8 Inf in R³ input → implicitly clamped via output normalization
  L5.x Out-of-range R³ input ([-1, 2] instead of [0, 1]) → clamped via norm
"""
from __future__ import annotations

import pytest
import torch


def test_nan_in_input_propagates_to_output(h3_extract, stim):
    """DOCUMENTED BEHAVIOR: NaN in R³ input propagates to T³ output.

    Engine has no input validation at the T³ stage. Upstream R³ contract
    is "no NaN in output"; if violated, T³ propagates without error.
    """
    features = torch.full((1, 256, 97), 0.5, dtype=torch.float32)
    features[0, 100, 10] = float('nan')
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    # NaN propagates — engine has no input sanitization
    assert t.isnan().any().item(), (
        "NaN in input did NOT propagate to output — engine sanitization is "
        "undocumented behavior"
    )


def test_inf_in_input_clamped_via_normalization(h3_extract, stim):
    """DOCUMENTED BEHAVIOR: +Inf in R³ input is clamped via the engine's
    final clamp(raw / scale, lo, hi) normalization step.

    The output is therefore finite (no Inf) and bounded ([0, 1] for unsigned
    morphs, [-1, 1] for signed) even when the input contains Inf at one
    frame on one R³ dim.
    """
    features = torch.full((1, 256, 97), 0.5, dtype=torch.float32)
    features[0, 100, 10] = float('inf')
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    # Inf does NOT propagate — output is finite
    assert not t.isinf().any().item(), (
        "Inf in input propagated to output — clamp normalization failed"
    )


def test_negative_input_clamped(h3_extract, stim):
    """R³ inputs are documented in [0, 1]. If the user passes -0.5, M0 (unsigned,
    bounded [0, 1]) clamps any negative output back to 0."""
    features = torch.full((1, 256, 97), -0.5, dtype=torch.float32)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    # Unsigned M0 must be in [0, 1] regardless of input sign (clamped)
    assert (t >= 0.0).all().item(), f"M0 (unsigned) returned negative: min={t.min().item()}"
    assert (t <= 1.0).all().item(), f"M0 (unsigned) returned > 1: max={t.max().item()}"


def test_above_unit_input_clamped(h3_extract, stim):
    """R³ inputs > 1 (e.g., 2.5): unsigned M0 clamps to [0, 1]."""
    features = torch.full((1, 256, 97), 2.5, dtype=torch.float32)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert not t.isnan().any().item()
    assert not t.isinf().any().item()
    assert (t >= 0.0).all().item()
    assert (t <= 1.0).all().item()


def test_input_at_exact_boundaries_zero_and_one(h3_extract, stim):
    """R³ values at exact boundaries 0.0 and 1.0 — no overflow or underflow."""
    for val in [0.0, 1.0]:
        features = torch.full((1, 256, 97), val, dtype=torch.float32)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        for key, t in out.features.items():
            assert not t.isnan().any().item(), (
                f"NaN at {key} for boundary input {val}"
            )
            assert not t.isinf().any().item(), (
                f"Inf at {key} for boundary input {val}"
            )


def test_mixed_extreme_input_dimensions(h3_extract, stim):
    """One R³ dim has NaN, one has Inf, one has normal value — only the
    queried dim's behavior matters for that tuple's output."""
    features = torch.full((1, 256, 97), 0.5, dtype=torch.float32)
    features[0, :, 5] = float('nan')   # contaminate dim 5
    features[0, :, 20] = float('inf')  # contaminate dim 20
    # Query dim 10 (normal): should be unaffected
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    t = out.features[(10, 5, 0, 0)]
    assert not t.isnan().any().item(), (
        "Querying dim 10 (clean) leaked NaN from dim 5 (contaminated) — "
        "would violate L7 dependency narrowness"
    )
    assert not t.isinf().any().item()
    assert t[0, 100].item() == pytest.approx(0.5, abs=1e-6)
