"""L9 — Reconcile L4 ceiling + L5 primary verdict against paper-time baseline."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_has_headline(paper_baseline):
    h8 = paper_baseline["primary_verdict_h8"]
    assert h8["top_ceiling_relative"] > 1.0, "Paper baseline must declare ceiling-saturating"
    assert h8["top_fz_mean_rho"] > 0.40, "Paper baseline top ρ must be above 0.40"
    assert h8["n_bonferroni_pass"] == h8["n_channels"], "Paper baseline must declare full Bonferroni-pass"
