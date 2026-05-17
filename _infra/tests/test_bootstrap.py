"""TDD tests for `stats.bootstrap` — BCa CI + song-block bootstrap."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from stats.bootstrap import bca_ci, song_block_bootstrap  # noqa: E402


# ─────────────────────────── BCa CI ───────────────────────────


def test_bca_ci_covers_true_mean():
    """Sample from N(0.5, 0.1) with N=500. 95% CI on the mean must contain 0.5."""
    rng = np.random.default_rng(42)
    data = rng.normal(loc=0.5, scale=0.1, size=500)
    lo, hi = bca_ci(data, statistic=np.mean, n_boot=1000, alpha=0.05, seed=1729)
    assert lo < 0.5 < hi
    assert (hi - lo) < 0.05


def test_bca_ci_lo_lt_hi():
    """CI must be ordered correctly even on a small sample."""
    rng = np.random.default_rng(7)
    data = rng.normal(loc=0.0, scale=1.0, size=20)
    lo, hi = bca_ci(data, statistic=np.mean, n_boot=500, alpha=0.05, seed=1729)
    assert lo < hi


def test_bca_ci_reproducible_with_seed():
    """Same seed → identical (lo, hi)."""
    rng = np.random.default_rng(11)
    data = rng.normal(loc=0.0, scale=1.0, size=50)
    lo1, hi1 = bca_ci(data, statistic=np.mean, n_boot=500, alpha=0.05, seed=1729)
    lo2, hi2 = bca_ci(data, statistic=np.mean, n_boot=500, alpha=0.05, seed=1729)
    assert lo1 == lo2 and hi1 == hi2


def test_bca_ci_different_alpha_levels_nest():
    """99% CI must be wider than (or equal to) 95% CI on the same data/seed."""
    rng = np.random.default_rng(13)
    data = rng.normal(loc=0.0, scale=1.0, size=100)
    lo95, hi95 = bca_ci(data, statistic=np.mean, n_boot=1000, alpha=0.05, seed=1729)
    lo99, hi99 = bca_ci(data, statistic=np.mean, n_boot=1000, alpha=0.01, seed=1729)
    # 99% interval at least as wide as 95% (same draws + same data)
    assert (hi99 - lo99) >= (hi95 - lo95) - 1e-9


def test_bca_ci_supports_arbitrary_statistic():
    """Should work for the median as well as the mean."""
    rng = np.random.default_rng(17)
    data = rng.normal(loc=2.0, scale=0.5, size=200)
    lo, hi = bca_ci(data, statistic=np.median, n_boot=500, alpha=0.05, seed=1729)
    assert lo < 2.0 < hi


def test_bca_ci_degenerate_constant_data():
    """BCa CI on constant data must not crash; CI collapses to point."""
    data = np.full(50, 0.42)
    lo, hi = bca_ci(data, statistic=np.mean, n_boot=200, alpha=0.05, seed=1)
    assert abs(lo - 0.42) < 1e-9
    assert abs(hi - 0.42) < 1e-9


# ─────────────────────── song_block_bootstrap ───────────────────────


def test_song_block_bootstrap_shape():
    """Output shape: (n_boot, n_frames)."""
    rng = np.random.default_rng(0)
    n_frames = 200
    values = rng.standard_normal(n_frames)
    song_ids = np.repeat(np.arange(10), 20)  # 10 songs × 20 frames
    out = song_block_bootstrap(values, song_ids=song_ids, n_boot=8, seed=1729)
    assert out.shape == (8, n_frames)


def test_song_block_bootstrap_preserves_block_structure():
    """Each contiguous block in the output must come from a single song's block.

    With unique values per song (so we can recognise the block by value),
    every chunk in a single bootstrap row should be a contiguous slice of
    the original `values` corresponding to one song id.
    """
    n_songs = 5
    block_len = 10
    n_frames = n_songs * block_len
    # Each song's block has constant value = song_id (0..4)
    song_ids = np.repeat(np.arange(n_songs), block_len)
    values = song_ids.astype(float)  # value == song_id

    out = song_block_bootstrap(values, song_ids=song_ids, n_boot=4, seed=1729)
    # In every bootstrap row, the first block_len values must all equal one
    # song_id (because resampling is at the song level and block_len=10 here).
    for row in out:
        for start in range(0, n_frames, block_len):
            block = row[start:start + block_len]
            assert np.all(block == block[0]), f"Block not homogeneous: {block}"


def test_song_block_bootstrap_reproducible_with_seed():
    rng = np.random.default_rng(0)
    values = rng.standard_normal(60)
    song_ids = np.repeat(np.arange(6), 10)
    a = song_block_bootstrap(values, song_ids=song_ids, n_boot=5, seed=1729)
    b = song_block_bootstrap(values, song_ids=song_ids, n_boot=5, seed=1729)
    np.testing.assert_array_equal(a, b)


def test_song_block_bootstrap_different_seeds_differ():
    rng = np.random.default_rng(0)
    values = rng.standard_normal(60)
    song_ids = np.repeat(np.arange(6), 10)
    a = song_block_bootstrap(values, song_ids=song_ids, n_boot=5, seed=1729)
    b = song_block_bootstrap(values, song_ids=song_ids, n_boot=5, seed=42)
    # Almost surely not identical
    assert not np.array_equal(a, b)
