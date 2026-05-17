"""Pin-integrity self-tests.

Run via:  pytest _infra/test_pin_integrity.py

These tests guard the validation suite itself. If any of them fail, every
downstream layer's results are invalid and the suite must be re-run after
the engine pin is reconciled.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

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
# Engine returns 97 dims with the canonical names
# ---------------------------------------------------------------------------

def test_engine_dim_count(r3_extract, stim):
    out = r3_extract(stim.stim_white(duration_s=2.0))
    assert out.features.shape[-1] == 97
    assert len(out.feature_names) == 97


def test_engine_dim_names_match_canonical(r3_extract, stim):
    from _infra.dims import DIM_NAMES
    out = r3_extract(stim.stim_white(duration_s=2.0))
    assert tuple(out.feature_names) == DIM_NAMES, (
        "engine feature_names drift relative to _infra/dims.py — "
        "either a dim was renamed or the engine pin is stale"
    )


def test_group_layout_sums_to_97(engine_pin):
    layout = engine_pin["group_layout"]
    total = 0
    for name, info in layout.items():
        s, e = info["slice"]
        assert s < e
        total += e - s
    assert total == 97


# ---------------------------------------------------------------------------
# Output range guarantee (sanity — full L4 lives in L4_output_guarantees/)
# ---------------------------------------------------------------------------

def test_output_in_unit_interval(r3_extract, stim):
    out = r3_extract(stim.stim_mix(duration_s=2.0))
    f = out.features
    assert f.min().item() >= 0.0 - 1e-7
    assert f.max().item() <= 1.0 + 1e-7
    assert not f.isnan().any().item()
    assert not f.isinf().any().item()
