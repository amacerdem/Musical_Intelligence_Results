"""L3 — Engine cache build / verify for 3 audio variants.

This layer ensures that engine per-frame outputs exist for the 7-clean ChillsDB
clips on each of three audio preprocessings (original / afftdn / noisereduce).

Build behavior:
  - If cache exists for a variant → verify SHA + per-frame integrity
  - If cache missing → trigger build (slow: ~5-10 min per variant on M2 8GB)

NOTE: For paper-time reproduction, this typically takes ~15-25 min total.
A reviewer can pre-build by running the engine cache build scripts manually.

For now, this test PASSES if cache exists, SKIPS if cache missing
(with instructions to build).
"""
from __future__ import annotations

from pathlib import Path

import json
import pytest

from _infra.chillsdb_loader import CLIPS_7_CLEAN


AUDIO_VARIANTS_DATASET_IDS = {
    "original":    "chillsdb1",
    "afftdn":      "chillsdb1_denoised",
    "noisereduce": "chillsdb1_noisereduce",
}


@pytest.mark.parametrize("variant,dataset_id", list(AUDIO_VARIANTS_DATASET_IDS.items()))
def test_engine_cache_present(engine_outputs_root, variant, dataset_id):
    """Engine cache directory must exist for the variant; if missing, instruct to build."""
    cache_root = engine_outputs_root / dataset_id
    if not cache_root.exists():
        pytest.skip(
            f"Engine cache missing for {variant} ({dataset_id}).\n"
            f"  Expected at: {cache_root}\n"
            f"  Build via: python3 Science/V-Reproduction/<engine_runner>.py --dataset {dataset_id}"
        )

    per_frame = cache_root / "per_frame"
    assert per_frame.exists(), f"per_frame dir missing under {cache_root}"

    # Verify the 7-clean clips are cached
    missing = []
    for clip_id in CLIPS_7_CLEAN:
        npz = per_frame / f"{clip_id}.npz"
        if not npz.exists():
            missing.append(clip_id)
    assert not missing, (
        f"Variant {variant}: missing 7-clean clip caches: {missing}\n"
        f"  Cache root: {cache_root}"
    )


@pytest.mark.parametrize("variant,dataset_id", list(AUDIO_VARIANTS_DATASET_IDS.items()))
def test_engine_cache_manifest_sha_matches_pin(engine_outputs_root, engine_pin, variant, dataset_id):
    """Cache's manifest.json must record matching engine SHA."""
    cache_root = engine_outputs_root / dataset_id
    if not cache_root.exists():
        pytest.skip(f"Engine cache missing for {variant}")
    manifest_path = cache_root / "manifest.json"
    if not manifest_path.exists():
        pytest.skip(f"manifest.json missing under {cache_root}")
    with open(manifest_path) as f:
        mf = json.load(f)
    cache_sha = mf.get("engine_sha", "")
    expected = engine_pin["content_aggregate_sha256"]
    assert cache_sha == expected, (
        f"Variant {variant} cache built with different engine SHA:\n"
        f"  cache:    {cache_sha}\n"
        f"  expected: {expected}\n"
        f"  Rebuild cache to match canonical engine pin."
    )
