"""L1 — Engine SHA aggregate integrity check.

The session-start fixture (conftest._pin_integrity) is load-bearing. This
file documents the contract via explicit assertions.
"""
from __future__ import annotations
from _infra.sha_utils import aggregate_engine_sha


def test_engine_pin_manifest_present(engine_pin):
    assert "content_aggregate_sha256" in engine_pin
    sha = engine_pin["content_aggregate_sha256"]
    assert len(sha) == 64


def test_engine_sha_matches_pin(project_root, engine_pin):
    actual = aggregate_engine_sha(project_root / "Musical_Intelligence")
    expected = engine_pin["content_aggregate_sha256"]
    assert actual == expected, f"Engine drift: expected {expected}, got {actual}"


def test_paper_baseline_present(paper_baseline):
    assert "primary_verdict_h8" in paper_baseline
    h8 = paper_baseline["primary_verdict_h8"]
    assert h8["top_channel"] == "MECH_AAC__F1:hr_pred_2s"
    assert h8["top_fz_mean_rho"] > 0.40
    assert h8["n_bonferroni_pass"] == 15
    assert h8["top_ceiling_relative"] > 1.0  # ceiling-saturating
