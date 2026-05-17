"""Permutation null distributions.

Three RAM-topology-specific nulls (used by paper Axis 6 — RAM specificity)
plus one generic shuffle null for arbitrary correlation statistics.

All p-values use the plus-one convention:
    p = (count_extreme + 1) / (n_perms + 1)
which avoids p=0 and gives a valid floor at 1/(n_perms+1).

Seeding is via `numpy.random.default_rng(seed)`; never `np.random.seed`.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import pearsonr, spearmanr


def centroid_relocation_null(
    *,
    centroids: np.ndarray,
    peaks: np.ndarray,
    observed_match_rate: float,
    threshold_mm: float = 10.0,
    n_perms: int = 10_000,
    brain_filter: Callable[[np.ndarray], np.ndarray],
    seed: int = 42,
) -> float:
    """RAM-topology null #1: relocate centroids uniformly within brain mask.

    Match rate = fraction of relocated centroids whose nearest peak is within
    `threshold_mm`. Returns one-tailed plus-one p-value
    P(null_match_rate >= observed_match_rate). `brain_filter(coords)` accepts
    (K, 3) and returns (K,) boolean of brain-internal points.
    """
    centroids = np.asarray(centroids, dtype=float)
    peaks = np.asarray(peaks, dtype=float)
    rng = np.random.default_rng(seed)

    # Bounding box from centroids
    lo = centroids.min(axis=0)
    hi = centroids.max(axis=0)
    n = centroids.shape[0]

    count_extreme = 0
    for _ in range(n_perms):
        # Rejection-sample within brain mask
        accepted = np.empty((0, 3), dtype=float)
        # Oversampling factor; loop until we have n points
        while accepted.shape[0] < n:
            need = n - accepted.shape[0]
            cand = rng.uniform(lo, hi, size=(need * 2, 3))
            mask = brain_filter(cand)
            accepted = np.concatenate([accepted, cand[mask]], axis=0)
        relocated = accepted[:n]

        # Nearest-peak distance for each relocated centroid
        # dists[i, j] = |relocated[i] - peaks[j]|
        diff = relocated[:, None, :] - peaks[None, :, :]
        dists = np.linalg.norm(diff, axis=-1)
        nearest = dists.min(axis=1)
        null_rate = float((nearest <= threshold_mm).mean())
        if null_rate >= observed_match_rate:
            count_extreme += 1

    return (count_extreme + 1) / (n_perms + 1)


def label_shuffle_null(
    *,
    labels: list[str],
    peak_labels: list[str],
    observed_match_rate: float,
    n_perms: int = 10_000,
    seed: int = 42,
) -> float:
    """RAM-topology null #2: fixed centroids, shuffle region labels.

    Counts label-equality matches between `peak_labels` and a permuted slice
    of `labels`, aligned positionally up to min(len(peak), len(labels)).
    Returns one-tailed plus-one p-value.
    """
    rng = np.random.default_rng(seed)
    labels_arr = np.array(labels)
    peak_arr = np.array(peak_labels)
    align = min(len(labels_arr), len(peak_arr))
    if align == 0:
        return 1.0

    count_extreme = 0
    for _ in range(n_perms):
        permuted = rng.permutation(labels_arr)
        null_rate = float((permuted[:align] == peak_arr[:align]).mean())
        if null_rate >= observed_match_rate:
            count_extreme += 1
    return (count_extreme + 1) / (n_perms + 1)


def shuffled_link_null(
    *,
    edges: list[tuple[str, str]],
    region_names: list[str],
    hub_regions: list[str],
    observed_hub_concentration: float,
    n_perms: int = 10_000,
    seed: int = 42,
) -> float:
    """RAM topology null: preserve total edge count, randomize each edge's
    region uniformly over `region_names`. Returns one-tailed p-value of
    observed_hub_concentration vs the null distribution.

    Each mechanism's K outgoing edges are preserved by construction (we
    iterate over the supplied `edges` list of (mechanism_id, region_id)
    pairs). For each edge, a region is drawn uniformly at random from the
    region universe. This breaks per-region in-degree (the variable of
    interest) while preserving total edge count and per-mechanism
    out-degree. Hub concentration on `hub_regions` is recomputed under each
    permutation.

    The plus-one convention is used: p = (count_extreme + 1) / (n_perms + 1).

    Note: the previous implementation that shuffled a flat bincount-derived
    array was permutation-invariant under bincount and therefore had zero
    null variance; this implementation re-routes each edge independently to
    a uniformly-chosen region, which produces the multinomial-with-uniform-
    probabilities null appropriate to the paper's claim (RAM topology line
    398).
    """
    rng = np.random.default_rng(seed)
    n_edges = len(edges)
    if n_edges == 0:
        return 1.0
    if not region_names:
        return 1.0

    region_indices = np.arange(len(region_names))
    hub_set = set(hub_regions)
    hub_mask = np.array([r in hub_set for r in region_names], dtype=bool)
    if not hub_mask.any():
        return 1.0

    null_concentrations = np.empty(n_perms, dtype=float)
    for i in range(n_perms):
        sampled_regions = rng.choice(region_indices, size=n_edges, replace=True)
        in_hub = hub_mask[sampled_regions]
        null_concentrations[i] = in_hub.sum() / n_edges
    n_extreme = int((null_concentrations >= observed_hub_concentration).sum())
    return (n_extreme + 1) / (n_perms + 1)


def shuffle_null(
    x: np.ndarray,
    y: np.ndarray,
    *,
    statistic: str = "pearson",
    n_perms: int = 10_000,
    seed: int = 42,
) -> float:
    """Generic two-tailed shuffle null for a correlation statistic.

    Permutes y, recomputes |stat|, counts null draws with |stat| >= |observed|.
    Plus-one convention. statistic in {"pearson", "spearman"}.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if x.size != y.size:
        raise ValueError(f"shuffle_null: x and y must have same length ({x.size} vs {y.size})")

    if statistic == "pearson":
        stat_fn = lambda a, b: float(pearsonr(a, b).statistic)  # noqa: E731
    elif statistic == "spearman":
        stat_fn = lambda a, b: float(spearmanr(a, b).statistic)  # noqa: E731
    else:
        raise ValueError(f"Unknown statistic '{statistic}'")

    observed = abs(stat_fn(x, y))
    rng = np.random.default_rng(seed)
    count_extreme = 0
    for _ in range(n_perms):
        y_perm = rng.permutation(y)
        null_stat = abs(stat_fn(x, y_perm))
        if null_stat >= observed:
            count_extreme += 1
    return (count_extreme + 1) / (n_perms + 1)
