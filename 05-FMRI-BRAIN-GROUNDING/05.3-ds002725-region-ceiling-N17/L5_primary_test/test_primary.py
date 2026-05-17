"""L5 — PRIMARY: Mendelssohn-window encoder + saturation verdict.

Confirms paper-canonical numbers per region from Stage 4:
  - top channels (A1_HG, STG, MGB, SOC, SMA) within tolerance
  - 16/21 non-brainstem ceiling-saturating (AT_CEILING + EXCEEDS)
  - 5 EXCEEDS regions: IFG, ACC, PMC, caudate, MGB
"""
from __future__ import annotations
import csv

import pytest


def test_stage4_encoder_csv_exists(suite_root):
    csv_path = suite_root / "data" / "stage4_encoder_ds002725.csv"
    assert csv_path.exists()


def test_stage4_top_regions_within_tolerance(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "stage4_encoder_ds002725.csv"
    by_name = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") != "OK":
                continue
            try:
                by_name[row["region_name"]] = (
                    float(row["r_mi_point"]),
                    row["verdict"],
                )
            except (KeyError, ValueError):
                pass

    tol = paper_baseline["tolerance"]["r_mi_abs"]
    for r in paper_baseline["encoder_saturation_ds002725_mendelssohn"]["top5_regions"]:
        name = r["name"]
        expected_r = r["r_mi"]
        expected_verdict = r["verdict"]
        actual = by_name.get(name)
        assert actual is not None, f"region {name} missing"
        actual_r, actual_verdict = actual
        assert abs(actual_r - expected_r) < tol, (
            f"{name} r_MI drift: actual={actual_r:.4f} expected={expected_r:.4f}"
        )
        assert actual_verdict == expected_verdict, (
            f"{name} verdict mismatch: actual={actual_verdict} expected={expected_verdict}"
        )


def test_stage4_exceeds_regions(suite_root, paper_baseline):
    """The 5 EXCEEDS regions must include IFG, ACC, PMC, caudate, MGB."""
    csv_path = suite_root / "data" / "stage4_encoder_ds002725.csv"
    exceeds = set()
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("verdict") == "EXCEEDS":
                exceeds.add(row["region_name"])
    expected = set(paper_baseline["encoder_saturation_ds002725_mendelssohn"]["exceeds_regions"])
    assert expected.issubset(exceeds), (
        f"Expected EXCEEDS regions missing: {expected - exceeds}"
    )


def test_stage4_n_saturating(suite_root, paper_baseline):
    """Total non-brainstem ceiling-saturating count (AT_CEILING + EXCEEDS)."""
    csv_path = suite_root / "data" / "stage4_encoder_ds002725.csv"
    n_sat = 0
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("verdict") in ("AT_CEILING", "EXCEEDS"):
                n_sat += 1
    expected_min = paper_baseline["tolerance"]["n_saturating_min_stage4"]
    assert n_sat >= expected_min, (
        f"Only {n_sat} ceiling-saturating non-brainstem regions; expected ≥{expected_min}"
    )
