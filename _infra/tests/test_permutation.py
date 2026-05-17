"""TDD tests for `stats.permutation` — RAM topology nulls + generic shuffle null."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from stats.permutation import (  # noqa: E402
    centroid_relocation_null,
    label_shuffle_null,
    shuffle_null,
    shuffled_link_null,
)


# ─────────────────────── centroid_relocation_null ───────────────────────


def _sphere_brain_filter(radius: float = 50.0):
    """Return a callable that masks N×3 coordinates inside a sphere at origin."""
    def filt(coords: np.ndarray) -> np.ndarray:
        d = np.linalg.norm(coords, axis=-1)
        return d <= radius
    return filt


def test_centroid_relocation_returns_valid_pvalue():
    """p must lie in (0, 1] under the plus-one convention."""
    rng = np.random.default_rng(0)
    centroids = rng.uniform(-40, 40, size=(20, 3))
    peaks = centroids + rng.normal(0, 1.0, size=(20, 3))  # very tight match
    obs_rate = 1.0  # every centroid within 10mm of its peak
    p = centroid_relocation_null(
        centroids=centroids,
        peaks=peaks,
        observed_match_rate=obs_rate,
        threshold_mm=10.0,
        n_perms=500,
        brain_filter=_sphere_brain_filter(50.0),
        seed=42,
    )
    assert 0.0 < p <= 1.0


def test_centroid_relocation_high_observed_yields_low_p():
    """A near-perfect observed match (1.0) should produce a small p under random relocation."""
    rng = np.random.default_rng(1)
    centroids = rng.uniform(-40, 40, size=(30, 3))
    peaks = centroids + rng.normal(0, 0.5, size=(30, 3))
    obs_rate = 1.0
    p = centroid_relocation_null(
        centroids=centroids,
        peaks=peaks,
        observed_match_rate=obs_rate,
        threshold_mm=10.0,
        n_perms=2000,
        brain_filter=_sphere_brain_filter(50.0),
        seed=7,
    )
    # Sphere of radius 50 has volume ≫ each peak's 10mm shell ⇒ random relocation
    # rarely matches all 30, so p must be small.
    assert p < 0.05


def test_centroid_relocation_reproducible_with_seed():
    """Same seed → identical p-value."""
    rng = np.random.default_rng(2)
    centroids = rng.uniform(-30, 30, size=(15, 3))
    peaks = centroids + rng.normal(0, 5.0, size=(15, 3))
    p1 = centroid_relocation_null(
        centroids=centroids, peaks=peaks, observed_match_rate=0.8,
        threshold_mm=10.0, n_perms=200,
        brain_filter=_sphere_brain_filter(50.0), seed=99,
    )
    p2 = centroid_relocation_null(
        centroids=centroids, peaks=peaks, observed_match_rate=0.8,
        threshold_mm=10.0, n_perms=200,
        brain_filter=_sphere_brain_filter(50.0), seed=99,
    )
    assert p1 == p2


# ─────────────────────── label_shuffle_null ───────────────────────


def test_label_shuffle_returns_valid_pvalue():
    labels = ["A", "B", "C", "D", "E", "F"]
    peak_labels = ["A", "B", "C", "X", "Y", "Z"]  # 3/6 match
    p = label_shuffle_null(
        labels=labels, peak_labels=peak_labels,
        observed_match_rate=3.0 / 6.0, n_perms=2000, seed=42,
    )
    assert 0.0 < p <= 1.0


def test_label_shuffle_perfect_match_low_p():
    labels = ["A", "B", "C", "D", "E"]
    peak_labels = ["A", "B", "C", "D", "E"]
    p = label_shuffle_null(
        labels=labels, peak_labels=peak_labels,
        observed_match_rate=1.0, n_perms=2000, seed=0,
    )
    # Random label permutation rarely produces a perfect match in 5 slots
    # (chance = 1/5! ≈ 0.008), so p should be small.
    assert p < 0.05


# ─────────────────────── shuffled_link_null ───────────────────────


def _random_edges(n_edges, region_names, seed):
    """Helper: generate n_edges (mech_id, region_id) pairs over region_names."""
    rng = np.random.default_rng(seed)
    mechs = [f"mech_{i}" for i in range(n_edges)]
    chosen = rng.choice(region_names, size=n_edges, replace=True)
    return list(zip(mechs, chosen))


def test_shuffled_link_null_high_concentration_low_p():
    """Observed concentration far exceeding chance must give a small p."""
    region_names = [f"R{i}" for i in range(26)]
    hub_regions = region_names[:5]  # 5/26 ≈ 0.19 chance baseline
    edges = _random_edges(100, region_names, seed=123)
    p = shuffled_link_null(
        edges=edges,
        region_names=region_names,
        hub_regions=hub_regions,
        observed_hub_concentration=0.95,  # well above chance ≈ 0.19
        n_perms=2000,
        seed=42,
    )
    assert p <= 0.001


def test_shuffled_link_null_chance_concentration_pvalue_near_half():
    """Observed concentration ≈ chance should give p ≈ 0.5 (within ~0.15)."""
    region_names = [f"R{i}" for i in range(26)]
    hub_regions = region_names[:5]  # baseline = 5/26 ≈ 0.1923
    edges = _random_edges(500, region_names, seed=7)
    chance = len(hub_regions) / len(region_names)
    p = shuffled_link_null(
        edges=edges,
        region_names=region_names,
        hub_regions=hub_regions,
        observed_hub_concentration=chance,
        n_perms=5000,
        seed=42,
    )
    # Under the null, P(null >= chance) should be ~0.5 (give or take, since
    # the discrete distribution is centred near `chance`). Allow a generous
    # window since with n_edges=500 the SE of the null mean is ~0.018.
    assert 0.30 <= p <= 0.70


def test_shuffled_link_null_reproducible_with_seed():
    """Same seed → identical p-value."""
    region_names = [f"R{i}" for i in range(26)]
    hub_regions = region_names[:5]
    edges = _random_edges(80, region_names, seed=1)
    p1 = shuffled_link_null(
        edges=edges, region_names=region_names, hub_regions=hub_regions,
        observed_hub_concentration=0.4, n_perms=500, seed=99,
    )
    p2 = shuffled_link_null(
        edges=edges, region_names=region_names, hub_regions=hub_regions,
        observed_hub_concentration=0.4, n_perms=500, seed=99,
    )
    assert p1 == p2


def test_shuffled_link_null_plus_one_floor():
    """Observed concentration = 1.0 (saturating) with small n_perms hits the floor."""
    region_names = [f"R{i}" for i in range(26)]
    hub_regions = region_names[:5]
    edges = _random_edges(50, region_names, seed=2)
    p = shuffled_link_null(
        edges=edges, region_names=region_names, hub_regions=hub_regions,
        observed_hub_concentration=1.0, n_perms=100, seed=3,
    )
    # With chance ~0.19 and 50 edges, P(all 50 land on hubs) ≈ 0.19^50, so
    # in 100 perms count_extreme = 0 and p = 1/101.
    assert abs(p - 1.0 / 101.0) < 1e-9


# ─────────────────────── shuffle_null (generic) ───────────────────────


def test_shuffle_null_strong_signal_low_p():
    """y = x + small noise → permutation null gives small p."""
    rng = np.random.default_rng(3)
    x = rng.standard_normal(200)
    y = x + 0.1 * rng.standard_normal(200)
    p = shuffle_null(x, y, statistic="pearson", n_perms=2000, seed=42)
    assert p < 0.01


def test_shuffle_null_independent_data_higher_p():
    """Independent random vectors → p well above 0.05 typically (just a sanity bound)."""
    rng = np.random.default_rng(4)
    x = rng.standard_normal(150)
    y = rng.standard_normal(150)
    p = shuffle_null(x, y, statistic="pearson", n_perms=2000, seed=12345)
    # Very weak/no association: p should not be small. Use loose bound.
    assert p > 0.05


def test_shuffle_null_reproducible_with_seed():
    rng = np.random.default_rng(5)
    x = rng.standard_normal(100)
    y = rng.standard_normal(100)
    p1 = shuffle_null(x, y, statistic="pearson", n_perms=500, seed=42)
    p2 = shuffle_null(x, y, statistic="pearson", n_perms=500, seed=42)
    assert p1 == p2


def test_shuffle_null_supports_spearman():
    rng = np.random.default_rng(6)
    x = rng.standard_normal(100)
    y = x ** 3 + 0.1 * rng.standard_normal(100)  # monotone, non-linear
    p = shuffle_null(x, y, statistic="spearman", n_perms=1000, seed=7)
    assert p < 0.01


def test_shuffle_null_plus_one_convention_floor():
    """p must be ≥ 1/(n_perms+1) — never zero."""
    rng = np.random.default_rng(7)
    x = rng.standard_normal(50)
    y = x.copy()  # perfect correlation
    p = shuffle_null(x, y, statistic="pearson", n_perms=100, seed=42)
    assert p >= 1.0 / 101.0
