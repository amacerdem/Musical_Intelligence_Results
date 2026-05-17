"""Statistical primitives for chill reproduction.

Mann-Whitney rank-biserial for event-window vs out-of-window comparison.
Bonferroni + BH-FDR corrections.
Within-clip event-time shuffle null.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy import stats as scistats


ENGINE_HZ = 172.265625
SAFEZONE_S = 8.0


def event_window_mask(n_frames: int, event_times_s: Sequence[float],
                      window_s: float = 5.0, engine_hz: float = ENGINE_HZ) -> np.ndarray:
    """Build a boolean mask: True at frames within ±window_s of any event."""
    mask = np.zeros(n_frames, dtype=bool)
    win_samples = int(window_s * engine_hz)
    for t in event_times_s:
        center = int(t * engine_hz)
        lo = max(0, center - win_samples)
        hi = min(n_frames, center + win_samples + 1)
        mask[lo:hi] = True
    return mask


def safezone_mask(n_frames: int, safezone_s: float = SAFEZONE_S,
                  engine_hz: float = ENGINE_HZ) -> np.ndarray:
    """Build a boolean mask: True at frames AFTER the safezone (i.e., usable)."""
    sz_samples = int(safezone_s * engine_hz)
    mask = np.zeros(n_frames, dtype=bool)
    mask[sz_samples:] = True
    return mask


def rank_biserial(signal: np.ndarray, in_mask: np.ndarray,
                  alternative: str = "two-sided") -> tuple[float, float]:
    """Mann-Whitney U rank-biserial between signal[in_mask] vs signal[~in_mask].

    Returns: (rank_biserial, p_value)
      rank_biserial ∈ [-1, +1]: positive = in-window > out-of-window
    """
    sig_in = signal[in_mask]
    sig_out = signal[~in_mask]
    if len(sig_in) < 10 or len(sig_out) < 10:
        return float("nan"), float("nan")
    res = scistats.mannwhitneyu(sig_in, sig_out, alternative=alternative)
    rb = 2.0 * res.statistic / (len(sig_in) * len(sig_out)) - 1.0
    return rb, float(res.pvalue)


def event_time_shuffle_null(signal: np.ndarray, n_events: int,
                            window_s: float, engine_hz: float,
                            valid_mask: np.ndarray,
                            n_perm: int = 500,
                            rng: np.random.Generator = None) -> np.ndarray:
    """Compute null rank-biserial distribution via random event-time placement.

    Each permutation: place n_events random timestamps within valid_mask=True
    region; recompute rank-biserial; record.
    """
    if rng is None:
        rng = np.random.default_rng(2026051200)
    n_frames = len(signal)
    valid_indices = np.where(valid_mask)[0]
    win_samples = int(window_s * engine_hz)
    valid_range_lo = valid_indices[0] + win_samples
    valid_range_hi = valid_indices[-1] - win_samples
    null_rbs = np.zeros(n_perm, dtype=np.float32)
    for i in range(n_perm):
        # Random event time centers
        if valid_range_hi <= valid_range_lo:
            null_rbs[i] = float("nan")
            continue
        centers = rng.integers(low=valid_range_lo, high=valid_range_hi, size=n_events)
        shuf_mask = np.zeros(n_frames, dtype=bool)
        for c in centers:
            lo = max(0, c - win_samples)
            hi = min(n_frames, c + win_samples + 1)
            shuf_mask[lo:hi] = True
        # Apply safezone (only frames in valid_mask considered)
        shuf_mask &= valid_mask
        rb, _ = rank_biserial(signal[valid_mask], shuf_mask[valid_mask])
        null_rbs[i] = rb
    return null_rbs


def empirical_p_one_sided(observed: float, null: np.ndarray) -> float:
    """One-sided empirical p: fraction of null >= observed (for positive observed)."""
    null = null[~np.isnan(null)]
    if len(null) == 0:
        return float("nan")
    if observed >= 0:
        return float(np.mean(null >= observed))
    else:
        return float(np.mean(null <= observed))


def fisher_combined_p(pvals: Sequence[float]) -> float:
    """Fisher's combined probability test (chi-squared on -2*sum(log(p)))."""
    pvals = np.asarray([p for p in pvals if not np.isnan(p) and p > 0], dtype=float)
    if len(pvals) == 0:
        return float("nan")
    chi2 = -2 * np.sum(np.log(pvals))
    df = 2 * len(pvals)
    return float(scistats.chi2.sf(chi2, df))


def bh_fdr(pvals: Sequence[float]) -> np.ndarray:
    """Benjamini-Hochberg FDR adjustment. Returns q-values aligned to input order."""
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    if n == 0:
        return np.array([])
    order = np.argsort(pvals)
    ranked = pvals[order]
    q = ranked * n / (np.arange(n) + 1)
    # Ensure monotonicity
    for i in range(n - 2, -1, -1):
        q[i] = min(q[i], q[i + 1])
    q = np.clip(q, 0, 1)
    out = np.empty(n, dtype=float)
    out[order] = q
    return out


def bonferroni(pvals: Sequence[float]) -> np.ndarray:
    """Bonferroni-adjusted p-values (capped at 1.0)."""
    n = len(pvals)
    return np.clip(np.asarray(pvals, dtype=float) * n, 0, 1)
