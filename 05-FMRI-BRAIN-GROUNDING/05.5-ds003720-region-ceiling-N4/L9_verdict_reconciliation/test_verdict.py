"""L9 — Reconcile all checks against locked paper baseline."""
from __future__ import annotations
import json
from pathlib import Path

import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_manifest_provenance(suite_root):
    m = json.load(open(suite_root / "data" / "05.5_ds003720_manifest.json"))
    assert m["engine_sha_pin"] == "318eb2f529d7103e8b7d80b01228357fdc4e0217"
    assert m["n_subjects"] >= 4


def test_sibling_05_4_present():
    """Sibling Phase 05.4 (voxelwise ds003720) must be present alongside 05.5."""
    sibling = Path(__file__).resolve().parents[2] / "05.4-voxelwise-ds003720"
    assert (sibling / "README.md").exists()
    assert (sibling / "02-RESULTS.md").exists()
    assert (sibling / "results" / "05.4_voxelwise_correlations.csv").exists()
