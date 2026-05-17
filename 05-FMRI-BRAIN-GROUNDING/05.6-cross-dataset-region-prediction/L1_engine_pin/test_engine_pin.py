"""L1 — Engine SHA + paper-baseline structural checks."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_headline_C1_paradigm_invariance(paper_baseline):
    c1 = paper_baseline["headline_results"]["C1_mi_feature_mean_paradigm_invariance"]
    assert c1["pearson_r"] > 0.95, f"C1 Pearson must be >0.95; locked = {c1['pearson_r']}"
    assert c1["spearman_r"] > 0.95, f"C1 Spearman must be >0.95"
    assert c1["pearson_p_permutation"] < 0.005, "C1 must pass permutation null"


def test_headline_C2_variance_paradigm_invariance(paper_baseline):
    c2 = paper_baseline["headline_results"]["C2_mi_feature_variance_paradigm_invariance"]
    assert c2["pearson_r"] > 0.90, f"C2 Pearson must be >0.90; locked = {c2['pearson_r']}"
    assert c2["spearman_r"] > 0.90
    assert c2["pearson_p_permutation"] < 0.005


def test_headline_B_directional_trend(paper_baseline):
    b = paper_baseline["headline_results"]["B_mi_encoder_cross_dataset"]
    assert b["pearson_r"] > 0, "B should be positive (directional)"
    assert b["spearman_r"] > 0


def test_headline_A_paradigm_specific(paper_baseline):
    """A test: BOLD reliability is paradigm-specific, may have any sign."""
    a = paper_baseline["headline_results"]["A_bold_ceiling_cross_dataset"]
    assert "pearson_r" in a, "A test must produce a Pearson r value"
    assert a["n_pairs"] == 21
