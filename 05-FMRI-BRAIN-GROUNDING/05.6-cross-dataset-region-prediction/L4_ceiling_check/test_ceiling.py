"""L4 — Paradigm-invariance correlations (C1 + C2) match paper baseline within tolerance."""
from __future__ import annotations
import json
import pytest


def test_C1_mean_paradigm_invariance(suite_root, paper_baseline):
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    actual = summary["C1_mi_feature_mean_cross_dataset"]
    expected_min = paper_baseline["tolerance"]["C1_pearson_min"]
    assert actual["pearson_r"] >= expected_min, (
        f"C1 Pearson dropped below paradigm-invariance threshold: "
        f"actual={actual['pearson_r']:.4f}, min={expected_min}"
    )
    p_max = paper_baseline["tolerance"]["C1_C2_p_perm_max"]
    assert actual["pearson_p_permutation"] < p_max, (
        f"C1 p_perm too high: {actual['pearson_p_permutation']:.4g}"
    )


def test_C2_variance_paradigm_invariance(suite_root, paper_baseline):
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    actual = summary["C2_mi_feature_variance_cross_dataset"]
    expected_min = paper_baseline["tolerance"]["C2_pearson_min"]
    assert actual["pearson_r"] >= expected_min, (
        f"C2 Pearson dropped: actual={actual['pearson_r']:.4f}, min={expected_min}"
    )
    p_max = paper_baseline["tolerance"]["C1_C2_p_perm_max"]
    assert actual["pearson_p_permutation"] < p_max


def test_n_pairs_correct(suite_root):
    summary = json.load(open(suite_root / "data" / "05.6_correlations_summary.json"))
    for key in ("A_bold_ceiling_cross_dataset", "B_mi_encoder_cross_dataset",
                "C1_mi_feature_mean_cross_dataset", "C2_mi_feature_variance_cross_dataset"):
        assert summary[key]["n_pairs"] == 21, f"{key} n_pairs ≠ 21"
