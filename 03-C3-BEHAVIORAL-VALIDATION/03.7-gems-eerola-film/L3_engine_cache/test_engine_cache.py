"""L3 — Engine cache .npz integrity for Eerola (Set 1 + Set 2)."""
from __future__ import annotations
import numpy as np
import pytest


def test_set2_npz_loadable(engine_cache_set2):
    npzs = sorted(engine_cache_set2.glob("*.npz"))[:5]
    for p in npzs:
        z = np.load(p, allow_pickle=True)
        assert "r3" in z.files, f"{p.name} missing r3"
        mech_keys = [k for k in z.files if k.startswith("mech_")]
        assert len(mech_keys) >= 30, f"{p.name} missing mech keys: only {len(mech_keys)}"


def test_critical_mech_clusters_set2(engine_cache_set2):
    """All paper-headline driving mechs must be present."""
    npz = next(engine_cache_set2.glob("*.npz"))
    z = np.load(npz, allow_pickle=True)
    required = {"mech_NEMAC", "mech_DAP", "mech_CDMR", "mech_AAC", "mech_SRP", "mech_TAR", "mech_PNH", "mech_VMM"}
    missing = required - set(z.files)
    assert not missing, f"Set 2 cache missing: {missing}"


def test_set1_npz_loadable(engine_cache_set1):
    npzs = sorted(engine_cache_set1.glob("*.npz"))[:5]
    for p in npzs:
        z = np.load(p, allow_pickle=True)
        assert "r3" in z.files
        mech_keys = [k for k in z.files if k.startswith("mech_")]
        assert len(mech_keys) >= 30
