"""L4.1 — Demand contract: request a tuple, receive exactly that tuple back.

The H3Extractor's contract is "you ask for {(r3_idx, h, m, ℓ), ...}, you
get back exactly that set as feature_map keys; no surprises". This test
verifies the contract holds across multiple demand cardinalities.
"""
from __future__ import annotations

import pytest


def test_empty_demand_returns_empty(h3_extract, stim):
    out = h3_extract(stim.stim_silence(T=128), set())
    assert out.n_tuples == 0
    assert out.features == {}


def test_single_tuple_request_returns_single_tuple(h3_extract, stim):
    features = stim.stim_constant(value=0.5, T=256, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    assert out.n_tuples == 1
    assert set(out.features.keys()) == demand


def test_all_morphs_one_horizon_returns_24(h3_extract, stim):
    features = stim.stim_constant(value=0.5, T=256, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    out = h3_extract(features, demand)
    assert out.n_tuples == 24
    assert set(out.features.keys()) == demand


def test_all_horizons_one_morph_returns_32(h3_extract, stim):
    features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
    demand = stim.demand_all_horizons_one_morph(r3_idx=10, morph=0, law=0)
    out = h3_extract(features, demand)
    assert out.n_tuples == 32
    assert set(out.features.keys()) == demand


def test_all_laws_one_tuple_returns_3(h3_extract, stim):
    features = stim.stim_constant(value=0.5, T=256, r3_dim=10)
    demand = stim.demand_all_laws_one_tuple(r3_idx=10, horizon=5, morph=0)
    out = h3_extract(features, demand)
    assert out.n_tuples == 3
    assert set(out.features.keys()) == demand


def test_mixed_demand_returns_exact_set(h3_extract, stim):
    """A heterogeneous demand mixing different r3_idx, horizons, morphs, laws."""
    features = stim.stim_constant(value=0.5, T=512, r3_dim=10)
    demand = {
        (10, 0, 0, 0),    # M0 at H0, L0
        (10, 5, 14, 0),   # M14 at H5, L0
        (10, 7, 18, 1),   # M18 at H7, L1
        (10, 10, 2, 2),   # M2 at H10, L2
        (10, 15, 8, 0),   # M8 at H15, L0
    }
    out = h3_extract(features, demand)
    assert out.n_tuples == 5
    assert set(out.features.keys()) == demand


def test_output_shape_is_BT(h3_extract, stim):
    """For B=1, T=256 input, every output tensor has shape (1, 256)."""
    features = stim.stim_constant(value=0.5, T=256, r3_dim=10, B=1)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    out = h3_extract(features, demand)
    for key, tensor in out.features.items():
        assert tensor.shape == (1, 256), (
            f"Tuple {key} returned shape {tensor.shape}, expected (1, 256)"
        )


def test_output_shape_with_batch(h3_extract, stim):
    """For B=4, T=128, every output tensor has shape (4, 128)."""
    features = stim.stim_constant(value=0.5, T=128, r3_dim=10, B=4)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)
    out = h3_extract(features, demand)
    tensor = out.features[(10, 5, 0, 0)]
    assert tensor.shape == (4, 128)


def test_n_tuples_matches_features_dict_length(h3_extract, stim):
    """H3Output.n_tuples must equal len(H3Output.features)."""
    features = stim.stim_constant(value=0.5, T=128, r3_dim=10)
    for demand in [
        set(),
        stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0),
        stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0),
        stim.demand_all_horizons_one_morph(r3_idx=10, morph=0, law=0),
    ]:
        out = h3_extract(features, demand)
        assert out.n_tuples == len(out.features)
