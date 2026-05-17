"""L4 — Full-scan LOSO ceiling reproduction (15/21 stimulus-driven, top putamen +0.44)."""
from __future__ import annotations
import csv
from pathlib import Path

import pytest


def test_stage3_ceiling_csv_exists(suite_root):
    csv_path = suite_root / "data" / "stage3_ceiling_ds002725.csv"
    assert csv_path.exists(), "stage3_ceiling_ds002725.csv missing — run code/stage3_loso_ceiling.py"


def test_stage3_top_regions_within_tolerance(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "stage3_ceiling_ds002725.csv"
    by_name = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") != "OK":
                continue
            try:
                by_name[row["region_name"]] = float(row["point_estimate"])
            except (KeyError, ValueError):
                pass

    tol = paper_baseline["tolerance"]["ceiling_abs"]
    for r in paper_baseline["loso_ceiling_ds002725"]["top5_regions"]:
        name = r["name"]
        expected = r["r_ceiling"]
        actual = by_name.get(name)
        assert actual is not None, f"region {name} missing from stage3 CSV"
        assert abs(actual - expected) < tol, (
            f"region {name} ceiling drift: actual={actual:.4f} expected={expected:.4f} tol={tol}"
        )


def test_stage3_n_pass_floor(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "stage3_ceiling_ds002725.csv"
    n_pass = 0
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("status") != "OK":
                continue
            try:
                if float(row["point_estimate"]) > 0.05 and float(row["p_null"]) < 0.05:
                    n_pass += 1
            except (KeyError, ValueError):
                continue
    expected_min = paper_baseline["tolerance"]["n_pass_min_stage3"]
    assert n_pass >= expected_min, (
        f"Only {n_pass} non-brainstem regions pass floor+q05; expected ≥{expected_min}"
    )
