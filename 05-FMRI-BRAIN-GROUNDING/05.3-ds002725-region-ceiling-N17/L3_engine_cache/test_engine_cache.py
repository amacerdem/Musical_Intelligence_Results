"""L3 — Mendelssohn MI engine cache integrity (RAM 26-region trajectory)."""
from __future__ import annotations
import numpy as np
import pytest


def test_mendelssohn_npz_loadable(ds002725_mi_cache):
    npz = ds002725_mi_cache / "classical_p5_mendelssohn-variations-serieuses-op54-larrard.npz"
    z = np.load(npz, allow_pickle=True)
    assert "ram" in z.files
    ram = z["ram"]
    assert ram.ndim == 2 and ram.shape[1] == 26, f"unexpected RAM shape {ram.shape}"
    # ~160s @ 172.27 Hz = ~27,608 frames
    assert 25_000 < ram.shape[0] < 30_000, f"unexpected RAM length {ram.shape[0]}"


def test_mendelssohn_ram_finite(ds002725_mi_cache):
    npz = ds002725_mi_cache / "classical_p5_mendelssohn-variations-serieuses-op54-larrard.npz"
    z = np.load(npz, allow_pickle=True)
    ram = z["ram"]
    assert np.isfinite(ram).all(), "RAM must contain only finite values"


def test_stage2_features_consumed(suite_root):
    """Stage 2 N1-normalized MI features (80, 26) must be cached for downstream."""
    stage2_npz = suite_root / "data" / "stage2_mi_mendelssohn.npz"
    if not stage2_npz.exists():
        pytest.skip("Stage 2 features not yet computed; run code/stage2_mi_features.py first")
    d = np.load(stage2_npz, allow_pickle=True)
    assert "mi_feat" in d.files
    assert d["mi_feat"].shape == (80, 26)
