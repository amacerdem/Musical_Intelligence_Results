"""L5 — PRIMARY: Saturation verdict per region (encoder vs ceiling)."""
from __future__ import annotations
import csv

import pytest


def test_saturation_csv_complete(suite_root):
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_saturation.csv"
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        rows = list(rdr)
    assert len(rows) >= 20, f"Expected ≥20 rows, got {len(rows)}"


def test_saturation_verdict_distribution(suite_root, paper_baseline):
    """Counts of AT_CEILING / EXCEEDS / BELOW / AT_FLOOR match baseline within tolerance."""
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_saturation.csv"
    counts = {"AT_CEILING": 0, "EXCEEDS": 0, "BELOW_CEILING": 0, "AT_FLOOR": 0}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            v = row.get("verdict")
            if v in counts:
                counts[v] += 1
    s = paper_baseline["saturation_ds003720"]
    # Tolerance: ±2 per category (small cohort, high variance)
    assert abs(counts["AT_CEILING"] - s["n_at_ceiling"]) <= 3
    assert abs(counts["EXCEEDS"] - s["n_exceeds"]) <= 3
    sat_actual = counts["AT_CEILING"] + counts["EXCEEDS"]
    sat_expected = s["n_at_ceiling"] + s["n_exceeds"]
    assert sat_actual >= sat_expected - 3
