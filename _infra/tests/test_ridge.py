"""TDD tests for `stats.ridge` — LOSO ridge + banded ridge wrapper."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from stats.ridge import (  # noqa: E402
    _HIMALAYA_AVAILABLE,
    banded_ridge_held_out_r,
    loso_ridge_held_out_r,
)

_HAS_HIMALAYA = _HIMALAYA_AVAILABLE


# ──────────────────────────── LOSO ridge ────────────────────────────


def test_loso_ridge_recovers_linear_signal():
    """Synthetic linear signal with 4 subjects → held-out r should be > 0.5."""
    rng = np.random.default_rng(0)
    n_subj, n_per_subj, n_feat = 4, 80, 10
    n = n_subj * n_per_subj
    beta = rng.standard_normal(n_feat)
    X = rng.standard_normal((n, n_feat))
    y = X @ beta + 0.5 * rng.standard_normal(n)
    subjects = np.repeat(np.arange(n_subj), n_per_subj)
    r = loso_ridge_held_out_r(X, y, subjects=subjects)
    assert r > 0.5, f"LOSO r too low for clean linear signal: {r}"
    assert np.isfinite(r)


def test_loso_ridge_random_data_low_r():
    """y is independent of X → held-out r should be near 0."""
    rng = np.random.default_rng(1)
    n_subj, n_per_subj, n_feat = 4, 60, 8
    n = n_subj * n_per_subj
    X = rng.standard_normal((n, n_feat))
    y = rng.standard_normal(n)
    subjects = np.repeat(np.arange(n_subj), n_per_subj)
    r = loso_ridge_held_out_r(X, y, subjects=subjects)
    assert abs(r) < 0.30, f"|LOSO r| should be small for independent data: {r}"
    assert np.isfinite(r)


def test_loso_ridge_returns_finite_with_2_subjects():
    """Minimal viable case: 2 subjects."""
    rng = np.random.default_rng(2)
    X = rng.standard_normal((40, 5))
    beta = rng.standard_normal(5)
    y = X @ beta + 0.5 * rng.standard_normal(40)
    subjects = np.repeat([0, 1], 20)
    r = loso_ridge_held_out_r(X, y, subjects=subjects)
    assert np.isfinite(r)


# ──────────────────────────── Banded ridge ────────────────────────────


def test_banded_ridge_runs_and_returns_finite_r():
    """Two feature groups, joint signal → finite, non-NaN held-out r."""
    rng = np.random.default_rng(3)
    n_subj, n_per_subj = 4, 60
    n = n_subj * n_per_subj
    g1 = rng.standard_normal((n, 6))
    g2 = rng.standard_normal((n, 4))
    beta1 = rng.standard_normal(6)
    beta2 = rng.standard_normal(4)
    y = g1 @ beta1 + g2 @ beta2 + 0.5 * rng.standard_normal(n)
    subjects = np.repeat(np.arange(n_subj), n_per_subj)
    r = banded_ridge_held_out_r([g1, g2], y, subjects=subjects)
    assert np.isfinite(r)
    # Banded ridge on a real signal should outperform random (loose bound).
    assert r > 0.0


@pytest.mark.skipif(_HAS_HIMALAYA, reason="himalaya available; fallback path not exercised")
def test_banded_ridge_falls_back_when_himalaya_missing():
    """When himalaya is not installed, banded_ridge falls back to single-alpha RidgeCV."""
    rng = np.random.default_rng(4)
    n = 80
    g1 = rng.standard_normal((n, 4))
    g2 = rng.standard_normal((n, 3))
    y = g1 @ rng.standard_normal(4) + g2 @ rng.standard_normal(3) + 0.3 * rng.standard_normal(n)
    subjects = np.repeat(np.arange(4), n // 4)
    r = banded_ridge_held_out_r([g1, g2], y, subjects=subjects)
    assert np.isfinite(r)


@pytest.mark.skipif(not _HAS_HIMALAYA, reason="himalaya not installed")
def test_banded_ridge_uses_himalaya_when_available():
    """When himalaya is installed, the himalaya path is exercised and returns finite r."""
    rng = np.random.default_rng(5)
    n_subj, n_per_subj = 3, 60
    n = n_subj * n_per_subj
    g1 = rng.standard_normal((n, 6))
    g2 = rng.standard_normal((n, 4))
    y = g1 @ rng.standard_normal(6) + g2 @ rng.standard_normal(4) + 0.4 * rng.standard_normal(n)
    subjects = np.repeat(np.arange(n_subj), n_per_subj)
    r = banded_ridge_held_out_r([g1, g2], y, subjects=subjects)
    assert np.isfinite(r)


def test_loso_ridge_skips_constant_y_folds():
    """Constant-y folds must be skipped, not biased toward 0."""
    rng = np.random.default_rng(0)
    n_subjects = 4
    n_per = 50
    X = rng.normal(size=(n_subjects * n_per, 5))
    beta = rng.normal(size=5)
    y = X @ beta + rng.normal(scale=0.3, size=X.shape[0])
    # Make subject 0's y constant — should be skipped, not folded as r=0
    y[:n_per] = 1.0
    subjects = np.repeat(np.arange(n_subjects), n_per)
    r = loso_ridge_held_out_r(X, y, subjects=subjects)
    assert np.isfinite(r)
    assert r > 0.3  # signal still detectable from remaining 3 subjects


@pytest.mark.skipif(not _HAS_HIMALAYA, reason="himalaya not installed")
def test_banded_ridge_himalaya_returns_held_out_r_in_unit_interval():
    """Banded ridge held-out r must be in [-1, 1] (Pearson correlation contract)."""
    rng = np.random.default_rng(0)
    n_subjects = 3
    n_per = 80
    g1 = rng.normal(size=(n_subjects * n_per, 4))
    g2 = rng.normal(size=(n_subjects * n_per, 6))
    beta = rng.normal(size=10)
    y = (
        np.concatenate([g1, g2], axis=1) @ beta
        + rng.normal(scale=0.5, size=n_subjects * n_per)
    )
    subjects = np.repeat(np.arange(n_subjects), n_per)
    r = banded_ridge_held_out_r([g1, g2], y, subjects=subjects, seed=1)
    assert -1.0 <= r <= 1.0
    assert r > 0.2  # signal recoverable
