"""Pin-integrity self-tests for T³ isolated validation infrastructure.

Run via:  pytest _infra/test_pin_integrity.py

These tests guard the validation suite itself. If any of them fail, every
downstream layer's results are invalid and the suite must be re-run after
the engine pin is reconciled or the infra is fixed.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Engine SHA-256 aggregate matches the manifest
# ---------------------------------------------------------------------------

def test_engine_sha_aggregate_matches_pin(engine_pin, project_root):
    from _infra.sha_utils import aggregate_engine_sha
    actual = aggregate_engine_sha(project_root / "Musical_Intelligence")
    assert actual == engine_pin["content_aggregate_sha256"], (
        "engine drift: tree no longer matches the pin manifest"
    )


# ---------------------------------------------------------------------------
# Engine imports cleanly (sanity)
# ---------------------------------------------------------------------------

def test_h3_extractor_imports():
    from Musical_Intelligence.ear.h3 import H3Extractor, H3Output
    assert H3Extractor is not None
    assert H3Output is not None


def test_h3_constants_import_and_match_spec():
    from Musical_Intelligence.ear.h3.constants.horizons import (
        N_HORIZONS, HORIZON_MS, HORIZON_FRAMES, FRAME_RATE,
    )
    from Musical_Intelligence.ear.h3.constants.morphs import (
        N_MORPHS, MORPH_NAMES, SIGNED_MORPHS,
    )
    from Musical_Intelligence.ear.h3.constants.laws import (
        N_LAWS, LAW_NAMES, ATTENTION_DECAY,
    )
    assert N_HORIZONS == 32
    assert N_MORPHS == 24
    assert N_LAWS == 3
    assert len(HORIZON_MS) == 32
    assert len(HORIZON_FRAMES) == 32
    assert len(MORPH_NAMES) == 24
    assert len(LAW_NAMES) == 3
    assert ATTENTION_DECAY == 3.0
    assert FRAME_RATE == 172.27
    assert HORIZON_MS[0] == 5.8
    assert HORIZON_MS[31] == 981_000
    assert len(SIGNED_MORPHS) == 8


# ---------------------------------------------------------------------------
# Empty-demand smoke test
# ---------------------------------------------------------------------------

def test_h3_extract_empty_demand_returns_empty(h3_extract, stim):
    r3_features = stim.stim_silence(T=128)
    out = h3_extract(r3_features, set())
    assert out.n_tuples == 0
    assert out.features == {}


# ---------------------------------------------------------------------------
# Single-tuple smoke test (sanity that the pipeline runs end-to-end)
# ---------------------------------------------------------------------------

def test_h3_extract_single_tuple_runs(h3_extract, stim):
    """Demand a single tuple on a simple sinusoid; verify shape only.

    Numerical correctness of the M14 periodicity output is L6's responsibility;
    here we only confirm the pipeline returns a tensor of the documented shape.
    """
    r3_features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=14, law=0)
    out = h3_extract(r3_features, demand)
    assert out.n_tuples == 1
    key = (10, 5, 14, 0)
    assert key in out.features
    tensor = out.features[key]
    # Shape should be (B, T) = (1, 512)
    assert tensor.shape == (1, 512), f"expected (1, 512), got {tensor.shape}"
    assert not tensor.isnan().any().item(), "M14 output contains NaN"
    assert not tensor.isinf().any().item(), "M14 output contains Inf"


# ---------------------------------------------------------------------------
# Determinism smoke test (canary; full L3 lives in L3_determinism/)
# ---------------------------------------------------------------------------

def test_h3_extract_twice_bit_identical(h3_extract, stim):
    r3_features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=14, law=0)
    out1 = h3_extract(r3_features, demand)
    out2 = h3_extract(r3_features, demand)
    key = (10, 5, 14, 0)
    diff = (out1.features[key] - out2.features[key]).abs().max().item()
    assert diff == 0.0, f"non-deterministic: max-abs-diff = {diff}"


# ---------------------------------------------------------------------------
# H3Output frozen dataclass sanity (full L12 lives in L12_api/)
# ---------------------------------------------------------------------------

def test_h3_output_is_frozen_dataclass():
    import dataclasses
    from Musical_Intelligence.ear.h3 import H3Output
    assert dataclasses.is_dataclass(H3Output)
    instance = H3Output(features={}, n_tuples=0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        instance.features = {"hack": None}  # type: ignore
