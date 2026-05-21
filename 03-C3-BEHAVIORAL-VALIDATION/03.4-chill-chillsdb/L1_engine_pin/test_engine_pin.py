"""L1 — Engine pin integrity test.

The conftest._pin_integrity session fixture is the load-bearing check
(SHA-256 aggregate of all engine .py files vs pinned value). This test
file documents the contract and provides explicit assertions for the
pytest collector.
"""
from __future__ import annotations

from pathlib import Path

from _infra.sha_utils import aggregate_engine_sha


def test_engine_pin_manifest_present(engine_pin):
    """Pin manifest must declare the canonical SHA aggregate."""
    assert "content_aggregate_sha256" in engine_pin
    assert "pinned_commit" in engine_pin
    sha = engine_pin["content_aggregate_sha256"]
    assert len(sha) == 64, f"SHA-256 expected 64 hex chars, got {len(sha)}"
    assert all(c in "0123456789abcdef" for c in sha), "SHA must be lowercase hex"


def test_engine_path_resolves(project_root):
    """Cache-only mode: engine_outputs/ root must be present.

    The reviewer reproduction path is the deposited cache, not the live
    engine; this test verifies the cache root exists rather than the
    Musical_Intelligence/ source tree.
    """
    cache_root = project_root / "engine_outputs"
    assert cache_root.exists(), f"Cache root not found at {cache_root}"
    assert (cache_root / "_aggregate_sha.txt").exists(), \
        f"Engine SHA marker missing at {cache_root}/_aggregate_sha.txt"


def test_engine_sha_matches_pin(project_root, engine_pin):
    """The session-start fixture also checks this; here we make it explicit."""
    engine_root = project_root / "Musical_Intelligence"
    actual = aggregate_engine_sha(engine_root)
    expected = engine_pin["content_aggregate_sha256"]
    assert actual == expected, (
        f"Engine SHA aggregate drift:\n"
        f"  expected: {expected}\n"
        f"  actual:   {actual}\n"
        f"  Did the engine tree change since the pin was frozen?"
    )


def test_paper_baseline_present(paper_baseline):
    """Paper-time baseline must declare the headline TC005 numbers."""
    assert "primary_verdict_tc005_clean7_afftdn" in paper_baseline
    primary = paper_baseline["primary_verdict_tc005_clean7_afftdn"]
    assert primary["audio_preprocessing"] == "afftdn_nr_12"
    assert primary["n_clips"] == 7
    headline_channels = primary["headline_channels"]
    assert len(headline_channels) >= 1, "Expect at least 1 headline channel"
    mmp_row = next((c for c in headline_channels if c["channel"] == "MECH_MMP__P2:familiarity"), None)
    assert mmp_row is not None, "MMP P2:familiarity must be in headline (primary chill marker)"
    assert mmp_row["status"] == "Bonferroni-pass"
    assert mmp_row["rank_biserial_mean"] > 0.20  # paper-time = 0.2306
    assert mmp_row["p_bonf"] < 0.05  # paper-time = 0.0092
