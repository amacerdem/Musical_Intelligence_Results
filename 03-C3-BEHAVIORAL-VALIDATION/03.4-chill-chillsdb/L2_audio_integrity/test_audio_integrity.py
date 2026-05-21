"""L2 — ChillsDB cache integrity (cache-only reviewer mode).

The audit deposit ships engine_outputs/emotion/chillsdb{1,1_denoised,1_noisereduce}/
per_frame/*.npz — pre-computed engine outputs over the 9 ChillsDB v1 clips
across three audio-preprocessing variants. WAV inputs are licence-restricted
and not vendored.

This layer verifies the cache is present and consistent. Live audio readback
is not required: downstream layers operate on the cached npz tensors.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest


EXPECTED_CLIPS = {
    "C1ZL5AxmK_A", "CwzjlmBLfrQ", "FOjdXSrtUxA", "H3v9unphfi0",
    "Y1UiD2sxoWo", "YbNYinfj1h0", "fRL447oDId4", "va1oiojnGrA",
    "zx_dTSPzXlk",
}

VARIANTS = ("chillsdb1", "chillsdb1_denoised", "chillsdb1_noisereduce")


@pytest.fixture(scope="session")
def cache_root(project_root) -> Path:
    return project_root / "engine_outputs" / "emotion"


def test_cache_root_exists(cache_root):
    """engine_outputs/emotion/ must exist (cache-only contract)."""
    assert cache_root.exists(), f"cache root missing: {cache_root}"


@pytest.mark.parametrize("variant", VARIANTS)
def test_variant_cache_dir_present(cache_root, variant):
    """Each ChillsDB variant must have its per_frame cache directory."""
    pf = cache_root / variant / "per_frame"
    assert pf.exists() and pf.is_dir(), f"per_frame missing: {pf}"


@pytest.mark.parametrize("variant", VARIANTS)
def test_variant_has_nine_clips(cache_root, variant):
    """All 9 ChillsDB v1 clip ids must be cached in each variant."""
    pf = cache_root / variant / "per_frame"
    cached = {p.stem for p in pf.glob("*.npz")}
    missing = EXPECTED_CLIPS - cached
    assert not missing, (
        f"variant {variant}: missing cached npz for {sorted(missing)}"
    )


@pytest.mark.parametrize("variant", VARIANTS)
def test_variant_npz_loadable(cache_root, variant):
    """Sample-check: first cached npz must load and carry an r3 tensor."""
    pf = cache_root / variant / "per_frame"
    sample = next(iter(pf.glob("*.npz")))
    z = np.load(sample, allow_pickle=True)
    assert "r3" in z.files, f"r3 array missing in {sample}"
    assert z["r3"].ndim >= 1


def test_variant_manifests_pin_canonical_sha(cache_root, engine_pin):
    """Each variant's manifest.json must pin to the canonical engine SHA."""
    import json
    expected = engine_pin["content_aggregate_sha256"]
    for variant in VARIANTS:
        m = cache_root / variant / "manifest.json"
        assert m.exists(), f"manifest missing: {m}"
        sha = json.loads(m.read_text()).get("engine_sha", "")
        assert sha == expected, (
            f"variant {variant} manifest SHA {sha[:16]} ≠ canonical {expected[:16]}"
        )
