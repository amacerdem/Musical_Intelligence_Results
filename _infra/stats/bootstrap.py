"""Bootstrap primitives: BCa confidence intervals + song-level block bootstrap.

References
----------
Efron 1987 — "Better bootstrap confidence intervals", JASA. (BCa)
Efron & Tibshirani 1993 — *An Introduction to the Bootstrap*. (jackknife
    acceleration estimator).
Lahiri 2003 — *Resampling Methods for Dependent Data*. (block bootstrap).
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import norm


def bca_ci(
    data: np.ndarray,
    *,
    statistic: Callable[[np.ndarray], float],
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int = 1729,
) -> tuple[float, float]:
    """Bias-corrected and accelerated bootstrap CI (Efron 1987).

    `statistic` maps a 1-D array to a float (e.g. np.mean). Returns
    (lo, hi) at coverage (1 - alpha). Acceleration via jackknife.
    """
    data = np.asarray(data, dtype=float).ravel()
    n = data.size
    if n < 2:
        raise ValueError(f"bca_ci needs at least 2 samples, got {n}")

    theta_hat = float(statistic(data))

    rng = np.random.default_rng(seed)
    boot_stats = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_stats[b] = float(statistic(data[idx]))

    # Bias correction z0
    prop_below = float((boot_stats < theta_hat).mean())
    # Clip to (epsilon, 1 - epsilon) so norm.ppf is finite
    eps = 1.0 / (n_boot + 1)
    prop_below = min(max(prop_below, eps), 1.0 - eps)
    z0 = float(norm.ppf(prop_below))

    # Acceleration via jackknife
    jack = np.empty(n, dtype=float)
    for i in range(n):
        sample_jk = np.delete(data, i)
        jack[i] = float(statistic(sample_jk))
    jack_mean = jack.mean()
    num = float(((jack_mean - jack) ** 3).sum())
    den = 6.0 * (((jack_mean - jack) ** 2).sum() ** 1.5)
    # Guard against tiny denominators that would make `a` blow up on
    # near-degenerate (e.g. constant) data. 1e-12 floor prevents CI inversion.
    a = num / den if den > 1e-12 else 0.0

    z_lo = float(norm.ppf(alpha / 2.0))
    z_hi = float(norm.ppf(1.0 - alpha / 2.0))

    def _adj(z):
        return float(norm.cdf(z0 + (z0 + z) / (1.0 - a * (z0 + z))))

    p_lo = _adj(z_lo)
    p_hi = _adj(z_hi)

    lo = float(np.quantile(boot_stats, p_lo))
    hi = float(np.quantile(boot_stats, p_hi))
    return lo, hi


def song_block_bootstrap(
    values: np.ndarray,
    *,
    song_ids: np.ndarray,
    n_boot: int = 1_000,
    seed: int = 1729,
) -> np.ndarray:
    """Block bootstrap by song ID — preserves within-song temporal order.

    Each bootstrap draw resamples songs with replacement (frames within a
    song stay together as one block), concatenates the chosen blocks, then
    trims/cycle-pads to match `len(values)`. Returns (n_boot, n_frames).
    """
    values = np.asarray(values)
    song_ids = np.asarray(song_ids)
    n_frames = values.shape[0]
    if song_ids.shape[0] != n_frames:
        raise ValueError(
            f"values and song_ids length mismatch: {n_frames} vs {song_ids.shape[0]}"
        )

    # Build per-song frame index slices, preserving first-seen order.
    unique_songs, first_idx = np.unique(song_ids, return_index=True)
    order = np.argsort(first_idx)
    unique_songs = unique_songs[order]

    blocks: list[np.ndarray] = []
    for sid in unique_songs:
        block = np.flatnonzero(song_ids == sid)
        # Verify contiguity (frames within a song must be contiguous)
        if block.size > 1 and not np.all(np.diff(block) == 1):
            raise ValueError(
                f"song_id {sid!r} frames are non-contiguous; this primitive "
                "expects songs to occupy contiguous slices."
            )
        blocks.append(values[block])

    n_songs = len(blocks)
    rng = np.random.default_rng(seed)

    out = np.empty((n_boot, n_frames), dtype=values.dtype)
    for b in range(n_boot):
        # Sample songs with replacement
        chosen = rng.integers(0, n_songs, size=n_songs)
        concat = np.concatenate([blocks[i] for i in chosen])
        # Trim or pad (with cycling) to match n_frames
        if concat.size >= n_frames:
            out[b] = concat[:n_frames]
        else:
            # Pad by recycling the concatenation
            reps = int(np.ceil(n_frames / concat.size))
            out[b] = np.tile(concat, reps)[:n_frames]
    return out
