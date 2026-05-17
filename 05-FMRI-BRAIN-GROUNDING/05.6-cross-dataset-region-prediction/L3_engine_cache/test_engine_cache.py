"""L3 — Phase 05.6 output artifacts present."""
from __future__ import annotations
import pytest


def test_per_region_csv(suite_root):
    p = suite_root / "data" / "05.6_cross_dataset_per_region.csv"
    assert p.exists(), "Run code/run_phase05_6.py first"


def test_mi_feature_csv(suite_root):
    p = suite_root / "data" / "05.6_mi_feature_per_region.csv"
    assert p.exists()


def test_correlations_json(suite_root):
    p = suite_root / "data" / "05.6_correlations_summary.json"
    assert p.exists()
