"""L1 — Engine SHA aggregate integrity + paper-time baseline checks."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_has_arousal_headline(paper_baseline):
    h4 = paper_baseline["primary_verdict_h4_arousal"]
    assert h4["top_ceiling_relative"] > 0.85, "Arousal must be ceiling-saturating ≥ 85%"
    assert h4["top_channel"].startswith("MECH_AAC__"), "Arousal top channel must be AAC autonomic cluster"


def test_paper_baseline_has_valence_headline(paper_baseline):
    h5 = paper_baseline["primary_verdict_h5_valence"]
    assert h5["n_bonferroni_pass"] >= 2, "Valence must have ≥2 Bonferroni-pass channels"
    assert h5["top_p_bonf"] < 0.05, "Valence top channel must pass Bonferroni"
    assert h5["top_channel"].startswith("MECH_SRP__"), "Valence top channel must be SRP reward cluster"


def test_loso_ceilings_present(paper_baseline):
    cA = paper_baseline["loso_ceiling_arousal"]
    cV = paper_baseline["loso_ceiling_valence"]
    assert cA["point_estimate"] > 0.15, "Arousal ceiling must be above sampling noise"
    assert cV["point_estimate"] > 0.13, "Valence ceiling must be above sampling noise"
    assert cA["n_loso_trials"] >= 5000, f"Arousal LOSO n_trials too low: {cA['n_loso_trials']}"
    assert cV["n_loso_trials"] >= 5000, f"Valence LOSO n_trials too low: {cV['n_loso_trials']}"
