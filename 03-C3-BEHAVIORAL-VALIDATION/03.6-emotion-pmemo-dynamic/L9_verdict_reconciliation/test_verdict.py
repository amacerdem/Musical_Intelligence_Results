"""L9 — Reconcile L4 ceilings + L5 primary verdicts against paper-time baseline."""
from __future__ import annotations
import pytest


def test_engine_sha_canonical(engine_pin):
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected


def test_paper_baseline_arousal_headline(paper_baseline):
    h4 = paper_baseline["primary_verdict_h4_arousal"]
    assert h4["top_ceiling_relative"] > 0.85, "Arousal paper baseline must be ceiling-saturating"
    assert h4["top_channel"] == "MECH_AAC__E0:emotional_arousal", "Arousal top channel locked"


def test_paper_baseline_valence_headline(paper_baseline):
    h5 = paper_baseline["primary_verdict_h5_valence"]
    assert h5["n_bonferroni_pass"] >= 2, "Valence paper baseline must have ≥2 Bonferroni-pass"
    assert h5["top_channel"] == "MECH_SRP__P0:wanting", "Valence top channel locked"
    assert h5["top_p_bonf"] < 0.05, "Valence top channel Bonferroni-pass locked"


def test_cross_paradigm_replication_recorded(paper_baseline):
    """AAC cluster appears in both TenseMusic (22-h8) and PMEmo (this package)."""
    h4 = paper_baseline["primary_verdict_h4_arousal"]
    cross = h4.get("cross_paradigm_replication")
    assert cross is not None, "Cross-paradigm replication record missing"
    assert cross["tensemusic_top"]["channel"].startswith("MECH_AAC__")
    assert cross["pmemo_top"]["channel"].startswith("MECH_AAC__")
