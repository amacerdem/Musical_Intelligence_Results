"""L1 — Engine SHA aggregate integrity + paper-time baseline checks."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_loso_ceiling_headline(paper_baseline):
    c = paper_baseline["loso_ceiling_ds002725"]
    assert c["n_subjects"] == 17, "Cohort must be N=17 paper-canonical"
    assert c["headline_passing_floor_and_q05"] >= 13, "Must have ≥13 regions passing floor+q05"
    # Top-5 regions sanity
    top = {r["name"]: r["r_ceiling"] for r in c["top5_regions"]}
    assert top.get("putamen", 0) > 0.40, "putamen ceiling must be > 0.40"
    assert top.get("amygdala", 0) > 0.35, "amygdala ceiling must be > 0.35"
    assert top.get("MGB", 0) > 0.30, "MGB ceiling must be > 0.30"


def test_paper_baseline_saturation_headline(paper_baseline):
    s = paper_baseline["encoder_saturation_ds002725_mendelssohn"]
    assert s["headline_ceiling_saturating"] >= 14, (
        f"Must have ≥14 ceiling-saturating regions (AT_CEILING + EXCEEDS); paper baseline = {s['headline_ceiling_saturating']}"
    )
    assert s["n_subjects"] == 17
    # Top-5 sanity
    top = {r["name"]: r["r_mi"] for r in s["top5_regions"]}
    assert top.get("A1_HG", 0) > 0.45, "A1_HG r_MI must be > 0.45 (headline)"
    assert top.get("STG", 0) > 0.30, "STG r_MI must be > 0.30"


def test_paper_baseline_mendelssohn_paradox_resolved(paper_baseline):
    p = paper_baseline["mendelssohn_pilot_paradox_resolution"]
    assert p["phase21_full_scan_ceiling_amygdala"] > 0.35, "amygdala full-scan ceiling > 0.35"
    assert abs(p["phase13_n17_cross_subject_median_rho"]) < 0.05, "Phase 05.1 result preserved verbatim"


def test_paper_baseline_cross_paradigm_bridge(paper_baseline):
    b = paper_baseline["cross_paradigm_bridge"]
    assert b["n_regions_strong_both"] + b["n_regions_mixed"] >= 4, (
        "≥4 regions must show ds002725↔ds003720 paradigm-cross consistency"
    )
    assert b["strong_region"] == "STG", "STG must be the canonical STRONG region"
