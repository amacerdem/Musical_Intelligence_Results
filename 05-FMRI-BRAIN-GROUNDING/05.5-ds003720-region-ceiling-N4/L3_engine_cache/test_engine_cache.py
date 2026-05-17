"""L3 — Stage outputs check (ceiling + saturation CSVs)."""
from __future__ import annotations
import pytest


def test_ceiling_csv_exists(suite_root):
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_ceiling.csv"
    assert csv_path.exists(), "Run code/run_phase05_5.py first"


def test_saturation_csv_exists(suite_root):
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_saturation.csv"
    assert csv_path.exists(), "Run code/run_phase05_5.py first"


def test_manifest_exists(suite_root):
    m = suite_root / "data" / "05.5_ds003720_manifest.json"
    assert m.exists(), "Run code/run_phase05_5.py first"
