"""L9 — Reconcile all positive verdicts against paper-time baseline."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_baseline_complete(paper_baseline):
    """All four primary positive evidence axes locked in paper_baseline."""
    assert "loso_ceiling_ds002725" in paper_baseline
    assert "encoder_saturation_ds002725_mendelssohn" in paper_baseline
    assert "mendelssohn_pilot_paradox_resolution" in paper_baseline
    assert "cross_paradigm_bridge" in paper_baseline


def test_headline_numbers(paper_baseline):
    """The four paper-headline numbers must be locked."""
    c = paper_baseline["loso_ceiling_ds002725"]
    assert c["headline_passing_floor_and_q05"] == 15, "Stage 3: 15/21 PASS locked"

    s = paper_baseline["encoder_saturation_ds002725_mendelssohn"]
    assert s["headline_ceiling_saturating"] == 16, "Stage 4: 16/21 ceiling-saturating locked"
    assert s["headline_at_ceiling"] == 11
    assert s["headline_exceeds"] == 5

    p = paper_baseline["mendelssohn_pilot_paradox_resolution"]
    assert p["phase13_sub08_single_subject_r"] == 0.59
    assert p["phase21_full_scan_ceiling_amygdala"] > 0.35

    b = paper_baseline["cross_paradigm_bridge"]
    assert b["strong_region"] == "STG"
    assert b["n_regions_strong_both"] >= 1


def test_cohort_paper_canonical(paper_baseline):
    """N=17 paper-canonical cohort enforced."""
    c = paper_baseline["loso_ceiling_ds002725"]
    s = paper_baseline["encoder_saturation_ds002725_mendelssohn"]
    assert c["n_subjects"] == 17
    assert s["n_subjects"] == 17
