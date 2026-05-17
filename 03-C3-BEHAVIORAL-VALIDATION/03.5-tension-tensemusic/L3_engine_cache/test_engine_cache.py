"""L3 — Engine cache .npz integrity for TenseMusic."""
from __future__ import annotations
import numpy as np
import pytest


def test_npz_loadable(engine_cache_dir):
    npzs = sorted(engine_cache_dir.glob("*.npz"))[:5]  # sample 5
    for p in npzs:
        z = np.load(p, allow_pickle=True)
        assert "r3" in z.files, f"{p.name} missing r3"
        # Check at least one MECH cluster exists
        mech_keys = [k for k in z.files if k.startswith("mech_")]
        assert len(mech_keys) >= 30, f"{p.name} missing mech keys: only {len(mech_keys)}"


def test_aac_cluster_present(engine_cache_dir):
    """AAC mechanism (load-bearing for tension prediction) must be in cache."""
    npz = next(engine_cache_dir.glob("*.npz"))
    z = np.load(npz, allow_pickle=True)
    assert "mech_AAC" in z.files
    aac = z["mech_AAC"]
    assert aac.shape[1] >= 12, f"AAC has too few dims: {aac.shape}"


def test_srp_cluster_present(engine_cache_dir):
    """SRP mechanism (T0:tension, T1:prediction_match) must be in cache."""
    npz = next(engine_cache_dir.glob("*.npz"))
    z = np.load(npz, allow_pickle=True)
    assert "mech_SRP" in z.files


def test_engine_output_duration_sane(engine_cache_dir):
    """Engine output should be ~60s at 172 Hz (TenseMusic is 60-63s)."""
    ENGINE_HZ = 172.265625
    durations = []
    for p in sorted(engine_cache_dir.glob("*.npz"))[:10]:
        z = np.load(p, allow_pickle=True)
        durations.append(z["r3"].shape[0] / ENGINE_HZ)
    # TenseMusic clips are ~60s
    assert min(durations) > 30, "Some clips suspiciously short"
    assert max(durations) < 120, "Some clips suspiciously long"
