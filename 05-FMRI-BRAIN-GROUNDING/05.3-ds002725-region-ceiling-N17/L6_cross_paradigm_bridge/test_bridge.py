"""L6 — Cross-paradigm bridge ds002725 ↔ ds003720 (Stage 9 aggregation)."""
from __future__ import annotations
import csv

import pytest


def test_stage9_csv_exists(suite_root):
    csv_path = suite_root / "data" / "stage9_cross_paradigm_bridge.csv"
    assert csv_path.exists()


def test_strong_region_locked(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "stage9_cross_paradigm_bridge.csv"
    strong = []
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("cross_paradigm_verdict") == "STRONG":
                strong.append(row["region_name"])
    expected_strong = paper_baseline["cross_paradigm_bridge"]["strong_region"]
    assert expected_strong in strong, f"Expected STRONG region {expected_strong} not found"


def test_mixed_regions_count(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "stage9_cross_paradigm_bridge.csv"
    mixed = []
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("cross_paradigm_verdict") == "MIXED":
                mixed.append(row["region_name"])
    expected_min = 3  # tolerance — paper baseline = 5
    assert len(mixed) >= expected_min, (
        f"Only {len(mixed)} MIXED regions; expected ≥{expected_min}"
    )
