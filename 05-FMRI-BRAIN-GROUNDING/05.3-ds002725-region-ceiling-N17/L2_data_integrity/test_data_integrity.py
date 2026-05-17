"""L2 — ds002725 BOLD cache + MI engine cache present and well-formed."""
from __future__ import annotations
import numpy as np
import pytest

COHORT = ["sub-01", "sub-02", "sub-03", "sub-05", "sub-06", "sub-07",
          "sub-08", "sub-09", "sub-11", "sub-12", "sub-13", "sub-14",
          "sub-15", "sub-17", "sub-18", "sub-19", "sub-20"]


def test_bold_cache_dir_exists(ds002725_bold_cache):
    assert ds002725_bold_cache.exists(), f"BOLD cache not found: {ds002725_bold_cache}"


def test_bold_npz_complete(ds002725_bold_cache):
    """All N=17 paper-canonical subjects must have *_bold_26.npz."""
    missing = [s for s in COHORT if not (ds002725_bold_cache / f"{s}_bold_26.npz").exists()]
    assert not missing, f"Missing BOLD npz for: {missing}"


def test_bold_per_region_cohort(ds002725_bold_cache):
    """Each subject: 26-region BOLD, ≥20 regions with valid (non-fully-NaN) data."""
    for sub in COHORT:
        d = np.load(ds002725_bold_cache / f"{sub}_bold_26.npz")
        bold = d["bold"]
        assert bold.ndim == 2 and bold.shape[1] == 26, f"{sub} bad shape {bold.shape}"
        per_region_all_nan = np.isnan(bold).all(axis=0)
        n_ok = int(np.sum(~per_region_all_nan))
        assert n_ok >= 20, f"{sub} only {n_ok}/26 regions intact"


def test_mi_cache_dir_exists(ds002725_mi_cache):
    assert ds002725_mi_cache.exists(), f"MI cache not found: {ds002725_mi_cache}"


def test_mendelssohn_mi_npz_exists(ds002725_mi_cache):
    npz = ds002725_mi_cache / "classical_p5_mendelssohn-variations-serieuses-op54-larrard.npz"
    assert npz.exists(), f"Mendelssohn MI cache npz not found"
