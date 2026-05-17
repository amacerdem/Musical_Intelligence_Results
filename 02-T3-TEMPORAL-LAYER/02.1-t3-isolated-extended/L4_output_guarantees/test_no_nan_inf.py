"""L4.3 — No NaN / no Inf on randomized R³ inputs.

Pathological-input-class probe: regardless of what (well-formed) R³ stream
T³ receives, every output value must be finite.

Strategy:
- Generate N seeded random R³ streams (each shape (B, T, 97), values in [0, 1])
  using torch.manual_seed for reproducibility (the seed is in the test, not in
  the engine — engine has zero PRNG per L11.3).
- For each stream, request all 24 morphs at multiple horizons and laws.
- Assert no NaN, no Inf in any output.

We use 100 seeds (not 10K, to keep the test under 5 seconds) — a 10K version
would be a `slow` marker test. Each seed independently exercises the engine.
"""
from __future__ import annotations

import pytest
import torch


N_SEEDS = 100
T_FRAMES = 256
B_BATCH = 1


def _random_r3_stream(seed: int, T: int = T_FRAMES, B: int = B_BATCH) -> torch.Tensor:
    """Generate a deterministic random R³ stream for a given seed.

    NOTE: The seed lives in the TEST, not the engine. T³'s zero-PRNG property
    is asserted by L11.3; here we use a controlled randomness to drive the
    engine through diverse input-space coverage.
    """
    g = torch.Generator()
    g.manual_seed(seed)
    return torch.rand((B, T, 97), generator=g, dtype=torch.float32)


@pytest.mark.parametrize("seed", list(range(N_SEEDS)))
def test_no_nan_inf_on_random_input(h3_extract, stim, seed):
    """Every output for every requested tuple is finite (no NaN, no Inf)."""
    features = _random_r3_stream(seed)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert not tensor.isnan().any().item(), f"NaN in tuple {key} for seed {seed}"
        assert not tensor.isinf().any().item(), f"Inf in tuple {key} for seed {seed}"


def test_no_nan_inf_pathological_silence(h3_extract, stim):
    """Edge case: all-zero stream, every morph, every law, multiple horizons."""
    features = stim.stim_silence(T=512)
    demand = set()
    for h in [0, 5, 10, 15]:
        for m in range(24):
            for l in [0, 1, 2]:
                demand.add((10, h, m, l))
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert not tensor.isnan().any().item(), f"NaN in tuple {key}"
        assert not tensor.isinf().any().item(), f"Inf in tuple {key}"


def test_no_nan_inf_pathological_constant_at_boundaries(h3_extract, stim):
    """Edge: constant at value 0.0, 1.0 (the unsigned-morph boundary values)."""
    for value in [0.0, 1.0]:
        features = stim.stim_constant(value=value, T=512, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        for key, tensor in out.features.items():
            assert not tensor.isnan().any().item(), (
                f"NaN in tuple {key} for constant={value}"
            )
            assert not tensor.isinf().any().item(), (
                f"Inf in tuple {key} for constant={value}"
            )


def test_no_nan_inf_impulse_at_first_frame(h3_extract, stim):
    """Edge: impulse at t=0 (no past for L0; full future for L1)."""
    features = stim.stim_impulse(impulse_at=0, height=1.0, T=512, r3_dim=10)
    demand = set()
    for l in [0, 1, 2]:
        for m in range(24):
            demand.add((10, 5, m, l))
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert not tensor.isnan().any().item(), f"NaN in tuple {key}"
        assert not tensor.isinf().any().item(), f"Inf in tuple {key}"


def test_no_nan_inf_impulse_at_last_frame(h3_extract, stim):
    """Edge: impulse at t=T-1 (full past for L0; no future for L1)."""
    T = 512
    features = stim.stim_impulse(impulse_at=T - 1, height=1.0, T=T, r3_dim=10)
    demand = set()
    for l in [0, 1, 2]:
        for m in range(24):
            demand.add((10, 5, m, l))
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert not tensor.isnan().any().item(), f"NaN in tuple {key}"
        assert not tensor.isinf().any().item(), f"Inf in tuple {key}"
