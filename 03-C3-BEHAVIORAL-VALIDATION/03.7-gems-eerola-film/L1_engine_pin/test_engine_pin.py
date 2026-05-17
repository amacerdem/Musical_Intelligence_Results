"""L1 — Engine SHA aggregate integrity + paper-time baseline checks."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_has_set2_headline(paper_baseline):
    s2 = paper_baseline["primary_verdict_set2"]
    assert s2["n_clips"] == 110
    assert s2["n_labels"] == 8
    assert s2["n_bonferroni_pass_count"] == 8, "All 8 GEMS labels must be Bonferroni-pass in paper baseline"
    assert s2["n_r3_residual_survivors_count"] >= 7, "≥7/8 R³-residual survival expected"


def test_paper_baseline_has_set1_replication(paper_baseline):
    s1 = paper_baseline["supportive_verdict_set1"]
    assert s1["n_clips"] == 360
    assert s1["channel_replication_identical_count"] >= 4, (
        "≥4/8 identical-channel replication expected from Set 2"
    )


def test_critical_set2_channels_locked(paper_baseline):
    """The mechanistically specific top channels must be locked in paper baseline."""
    s2_labels = paper_baseline["primary_verdict_set2"]["labels"]
    assert s2_labels["sad"]["top_channel"] == "MECH_NEMAC__M0:mpfc_activation"
    assert s2_labels["tender"]["top_channel"] == "MECH_DAP__P1:familiarity_warmth"
    assert s2_labels["tension"]["top_channel"] == "MECH_CDMR__f01:mismatch_amplitude"
    assert s2_labels["energy"]["top_channel"] == "MECH_AAC__A1:hr"  # AAC cross-paradigm
    assert s2_labels["valence"]["top_channel"] == "MECH_SRP__P1:liking"
