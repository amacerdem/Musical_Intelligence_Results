"""L9 — Reconcile L4/L5 primary verdicts against paper-time baseline."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_set2_complete(paper_baseline):
    s2 = paper_baseline["primary_verdict_set2"]
    assert s2["n_clips"] == 110
    assert s2["n_bonferroni_pass_count"] == 8, "All 8 GEMS labels Bonferroni-pass locked"
    assert s2["n_r3_residual_survivors_count"] >= 7, "≥7/8 R³-residual survival locked"


def test_paper_baseline_mechanistic_specificity(paper_baseline):
    """The 4/8 identical-channel cross-set replication is the headline claim."""
    s2_labels = paper_baseline["primary_verdict_set2"]["labels"]
    s1_labels = paper_baseline["supportive_verdict_set1"]["labels"]
    identical_match_labels = ["sad", "tender", "fear"]
    for label in identical_match_labels:
        s2_top = s2_labels[label]["top_channel"]
        s1_top = s1_labels[label]["top_channel"]
        assert s2_top == s1_top, (
            f"{label}: Set 2 ({s2_top}) ≠ Set 1 ({s1_top}); paper claims identical-channel match"
        )


def test_loso_ceiling_intentionally_absent(paper_baseline):
    """Eerola public deposit has no per-rater data — paper baseline reflects this."""
    assert "loso_ceiling" not in paper_baseline, (
        "Eerola has NO per-rater LOSO ceiling. Do NOT add fake ceiling."
    )
    meta = paper_baseline.get("stimulus_metadata", {})
    assert meta.get("per_rater_data_available") is False
    assert meta.get("loso_ceiling_computable") is False
