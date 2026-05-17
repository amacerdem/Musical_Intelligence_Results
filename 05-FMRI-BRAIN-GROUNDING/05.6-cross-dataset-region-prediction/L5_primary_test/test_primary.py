"""L5 — B directional + A paradigm-specific verdict checks."""
from __future__ import annotations
import json
import pytest


def test_B_directional_trend(suite_root, paper_baseline):
    """B (MI encoder cross-paradigm) must be in positive direction (suggestive trend)."""
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    b = summary["B_mi_encoder_cross_dataset"]
    min_dir = paper_baseline["tolerance"]["B_direction_min"]
    assert b["pearson_r"] >= min_dir, (
        f"B Pearson must be ≥ {min_dir} (directional trend); got {b['pearson_r']:.4f}"
    )


def test_A_paradigm_specific_descriptive(suite_root):
    """A (BOLD reliability cross-paradigm) is descriptive — any sign accepted, no power claim."""
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    a = summary["A_bold_ceiling_cross_dataset"]
    assert a["status"] == "OK"
    assert "pearson_r" in a


def test_paper_canonical_three_way_separation(suite_root):
    """The three-way separation: engine > encoder > brain in cross-paradigm consistency."""
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    c1 = summary["C1_mi_feature_mean_cross_dataset"]["pearson_r"]
    b = summary["B_mi_encoder_cross_dataset"]["pearson_r"]
    # Engine paradigm-invariance >> encoder cross-paradigm transfer
    assert c1 > b + 0.5, (
        f"Engine paradigm-invariance (C1={c1:.3f}) must be substantially higher than "
        f"encoder cross-paradigm transfer (B={b:.3f}). Three-way separation broken."
    )
