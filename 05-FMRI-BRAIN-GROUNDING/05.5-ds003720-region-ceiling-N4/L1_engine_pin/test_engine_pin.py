"""L1 — Engine SHA aggregate integrity + paper-baseline structural checks."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_baseline_has_ceiling_headline(paper_baseline):
    c = paper_baseline["per_region_ceiling_ds003720"]
    assert c["n_subjects"] >= 4
    assert c["n_pass_floor_q05_non_brainstem"] >= 10, (
        f"Must have ≥10 non-brainstem regions passing floor+q05; got {c['n_pass_floor_q05_non_brainstem']}"
    )


def test_baseline_top_regions_locked(paper_baseline):
    c = paper_baseline["per_region_ceiling_ds003720"]
    names = {r["name"] for r in c["top5_regions"]}
    # hippocampus is the headline strongest region per Phase 05.5 results
    assert "hippocampus" in names, "hippocampus must be in top5"


def test_baseline_data_source_locked(paper_baseline):
    src = paper_baseline.get("_source_data", {})
    assert "ckpt_bold" in str(src), "Source must be cycle-17 ckpt_bold"
