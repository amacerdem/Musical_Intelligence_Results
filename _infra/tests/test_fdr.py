"""TDD tests for `stats.fdr` — BH, BB, Bonferroni primitives.

Mirrors the import pattern from test_engine_runner.py: put `_infra/` on
sys.path and import via `from stats.fdr import ...`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from stats.fdr import benjamini_bogomolov, benjamini_hochberg, bonferroni  # noqa: E402


# ──────────────────────── Benjamini-Hochberg ────────────────────────


def test_bh_basic_textbook_case():
    """p = [0.001, 0.01, 0.05, 0.5] at q=0.05 → first two pass."""
    p = np.array([0.001, 0.01, 0.05, 0.5])
    pass_mask, q_adj = benjamini_hochberg(p, q=0.05)
    np.testing.assert_array_equal(pass_mask, np.array([True, True, False, False]))
    # q_adjusted must be finite, in [0, 1], and at least as large as the raw p.
    assert np.all(q_adj >= p - 1e-12)
    assert np.all(q_adj <= 1.0 + 1e-12)


def test_bh_all_significant():
    """All tiny p-values pass at q=0.05."""
    p = np.array([1e-6, 1e-5, 1e-4, 1e-3])
    pass_mask, _ = benjamini_hochberg(p, q=0.05)
    assert pass_mask.all()


def test_bh_none_significant():
    """All large p-values fail at q=0.05."""
    p = np.array([0.4, 0.5, 0.6, 0.9])
    pass_mask, _ = benjamini_hochberg(p, q=0.05)
    assert not pass_mask.any()


def test_bh_q_adjusted_monotone_in_rank():
    """When p is sorted ascending, q_adjusted must be non-decreasing."""
    p_sorted = np.array([0.001, 0.005, 0.02, 0.04, 0.10, 0.30])
    _, q_adj = benjamini_hochberg(p_sorted, q=0.05)
    diffs = np.diff(q_adj)
    assert np.all(diffs >= -1e-12), f"q_adjusted not monotone: {q_adj}"


def test_bh_preserves_input_order():
    """If we pass an unsorted p-array, the returned masks/qs align to input order."""
    p = np.array([0.5, 0.001, 0.05, 0.01])
    pass_mask, q_adj = benjamini_hochberg(p, q=0.05)
    # The two smallest p (0.001, 0.01) should pass; 0.05 and 0.5 should not.
    expected = np.array([False, True, False, True])
    np.testing.assert_array_equal(pass_mask, expected)
    # smallest q-adj corresponds to the smallest raw p (index 1)
    assert np.argmin(q_adj) == 1


# ──────────────────────── Benjamini-Bogomolov ────────────────────────


def test_bb_two_families_one_signal():
    """Family A has signal; family B has only noise. Only A retains discoveries."""
    rng = np.random.default_rng(0)
    # Family A: 10 tests, 5 with strong signal (small p), 5 noise
    family_a = np.concatenate([np.full(5, 1e-4), rng.uniform(0.5, 1.0, size=5)])
    # Family B: 10 noise p-values
    family_b = rng.uniform(0.3, 1.0, size=10)
    families = {"A": family_a, "B": family_b}
    pass_dict, q_dict = benjamini_bogomolov(families, q=0.05)

    # A must have at least the 5 strong signals selected
    assert pass_dict["A"][:5].all()
    # B must have nothing significant
    assert not pass_dict["B"].any()
    # q-dicts cover all keys
    assert set(q_dict.keys()) == {"A", "B"}
    assert q_dict["A"].shape == (10,)
    assert q_dict["B"].shape == (10,)


def test_bb_zero_selected_families_returns_all_false():
    """All families noise → zero families pass stage 1 → no within-family rejections."""
    rng = np.random.default_rng(1)
    families = {
        "A": rng.uniform(0.4, 1.0, size=10),
        "B": rng.uniform(0.5, 1.0, size=10),
    }
    pass_dict, _ = benjamini_bogomolov(families, q=0.05)
    assert not pass_dict["A"].any()
    assert not pass_dict["B"].any()


def test_bb_single_family_reduces_to_bh_at_alpha():
    """With one family, BB reduces to within-family BH at level q (n_selected/n_families = 1)."""
    p = np.array([0.001, 0.01, 0.05, 0.5])
    families = {"only": p}
    pass_bb, _ = benjamini_bogomolov(families, q=0.05)
    pass_bh, _ = benjamini_hochberg(p, q=0.05)
    np.testing.assert_array_equal(pass_bb["only"], pass_bh)


# ──────────────────────── Bonferroni ────────────────────────


def test_bonferroni_basic():
    """Standard Bonferroni with alpha/n threshold.

    For p=[0.001, 0.02, 0.05], alpha=0.05, n=3 → threshold ≈ 0.01667.
    Only p=0.001 < threshold passes; p=0.02 fails (above threshold).
    """
    p = np.array([0.001, 0.02, 0.05])
    mask = bonferroni(p, alpha=0.05)
    np.testing.assert_array_equal(mask, np.array([True, False, False]))


def test_bonferroni_spec_threshold_arithmetic():
    """Sanity-check the alpha/n threshold: p=0.01, n=3, alpha=0.05.

    0.01 < 0.05/3 = 0.01667, so it must pass under the standard convention.
    (Per Wright 1992; this is the strict alpha/n form, not the p*n form.)
    """
    p = np.array([0.01])
    # n=3 case requires constructing it manually
    p_full = np.array([0.01, 0.5, 0.5])
    mask = bonferroni(p_full, alpha=0.05)
    assert mask[0]
    # And 0.02 (above 0.0167) must fail
    p_full2 = np.array([0.02, 0.5, 0.5])
    mask2 = bonferroni(p_full2, alpha=0.05)
    assert not mask2[0]


def test_bonferroni_threshold_scales_with_n():
    """alpha=0.05, n=10 → threshold 0.005. p=0.004 passes, p=0.006 does not."""
    p = np.array([0.004, 0.006, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    mask = bonferroni(p, alpha=0.05)
    assert mask[0] and not mask[1]
    assert not mask[2:].any()
