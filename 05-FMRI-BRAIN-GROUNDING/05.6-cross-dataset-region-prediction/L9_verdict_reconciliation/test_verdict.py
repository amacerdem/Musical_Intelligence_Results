"""L9 — Verdict reconciliation + companion packages untouched."""
from __future__ import annotations
import json
from pathlib import Path

import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_companion_phases_present():
    """Sibling Section 05 phases (05.4 / 05.3 / 05.5) must be present alongside 05.6."""
    section = Path(__file__).resolve().parents[2]
    assert (section / "05.4-voxelwise-ds003720" / "README.md").exists()
    assert (section / "05.3-ds002725-region-ceiling-N17" / "README.md").exists()
    assert (section / "05.5-ds003720-region-ceiling-N4" / "README.md").exists()


def test_headline_numbers_locked(paper_baseline):
    h = paper_baseline["headline_results"]
    # C1 paradigm-invariance must be > 0.99 (engine signature stability)
    assert h["C1_mi_feature_mean_paradigm_invariance"]["pearson_r"] > 0.99
    # C2 must be > 0.95
    assert h["C2_mi_feature_variance_paradigm_invariance"]["pearson_r"] > 0.95


def test_three_way_separation_summary(paper_baseline):
    """Engine > Model > Brain paradigm-consistency separation."""
    summary = paper_baseline["_summary_interpretation"]
    assert "paradigm-invariant" in summary
    assert "paradigm-specific" in summary or "paradigm-conditional" in summary
