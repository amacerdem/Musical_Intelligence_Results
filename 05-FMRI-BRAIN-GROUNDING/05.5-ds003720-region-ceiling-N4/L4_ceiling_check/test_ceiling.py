"""L4 — Per-region ceiling reproduction against paper baseline."""
from __future__ import annotations
import csv

import pytest


def test_ceiling_csv_top_regions_match_baseline(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_ceiling.csv"
    by_name = {}
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") != "OK":
                continue
            try:
                by_name[row["region_name"]] = float(row["r_ceiling"])
            except (KeyError, ValueError):
                continue

    tol = paper_baseline["tolerance"]["ceiling_abs"]
    for r in paper_baseline["per_region_ceiling_ds003720"]["top5_regions"]:
        actual = by_name.get(r["name"])
        assert actual is not None, f"region {r['name']} missing from CSV"
        assert abs(actual - r["r_ceiling"]) < tol, (
            f"{r['name']} ceiling drift: actual={actual:.4f} expected={r['r_ceiling']:.4f} tol={tol}"
        )


def test_n_pass_floor_q05(suite_root, paper_baseline):
    csv_path = suite_root / "data" / "05.5_ds003720_per_region_ceiling.csv"
    n_pass = 0
    with open(csv_path) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("is_brainstem") == "True":
                continue
            if row.get("status") != "OK":
                continue
            try:
                if float(row["r_ceiling"]) > 0.05 and float(row["p_null"]) < 0.05:
                    n_pass += 1
            except (KeyError, ValueError):
                continue
    expected = paper_baseline["tolerance"]["n_pass_min"]
    assert n_pass >= expected, f"Only {n_pass} non-brainstem regions pass floor+q05; expected ≥{expected}"
