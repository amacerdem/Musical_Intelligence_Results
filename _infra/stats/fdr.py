"""FDR primitives: Benjamini-Hochberg, Benjamini-Bogomolov, Bonferroni.

References
----------
Benjamini & Hochberg 1995 — JRSS-B, "Controlling the false discovery rate".
Heller, Chatterjee, Krieger, Shaffer 2018 — Biostatistics, "Post-selection
    inference following aggregate level hypothesis testing in large-scale
    genomic data" (the BB hierarchical procedure used here).
"""
from __future__ import annotations

from typing import Mapping

import numpy as np


def benjamini_hochberg(
    p_values, q: float = 0.05
) -> tuple[np.ndarray, np.ndarray]:
    """Standard Benjamini-Hochberg FDR control.

    Parameters
    ----------
    p_values : array_like
        1-D array of raw p-values, any order.
    q : float, default 0.05
        Target FDR level.

    Returns
    -------
    pass_mask : np.ndarray of bool, same length as `p_values`
        True iff the corresponding null hypothesis is rejected at FDR ≤ q.
    q_adjusted : np.ndarray of float, same length as `p_values`
        Step-down BH-adjusted p-values (a.k.a. BH q-values), aligned to the
        input order. q_adjusted[i] = min over k ≥ rank(i) of (n / k) * p[k]_sorted,
        clipped to [0, 1].

    Notes
    -----
    The mask is computed as `q_adjusted ≤ q` (equivalent to the standard
    largest-k step-up rule).
    """
    p = np.asarray(p_values, dtype=float).ravel()
    n = p.size
    if n == 0:
        return np.zeros(0, dtype=bool), np.zeros(0, dtype=float)

    order = np.argsort(p, kind="mergesort")  # stable
    p_sorted = p[order]
    ranks = np.arange(1, n + 1)

    # Raw BH adjusted: (n/k) * p[k]_sorted
    raw_adj = p_sorted * n / ranks

    # Step-down monotone: q_adj[k] = min over j ≥ k of raw_adj[j]
    q_sorted = np.minimum.accumulate(raw_adj[::-1])[::-1]
    q_sorted = np.clip(q_sorted, 0.0, 1.0)

    # Restore input order
    q_adjusted = np.empty(n, dtype=float)
    q_adjusted[order] = q_sorted

    pass_mask = q_adjusted <= q
    return pass_mask, q_adjusted


def benjamini_bogomolov(
    families: Mapping[str, np.ndarray], q: float = 0.05
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Hierarchical Benjamini-Bogomolov FDR (Heller et al. 2018).

    Two-stage procedure:
      Stage 1 — Compute the per-family minimum p-value, apply BH at level q
                across families. The selected families are those that pass
                this stage.
      Stage 2 — For each selected family, apply BH at the *adjusted* level
                q' = q * R / m, where R = #selected, m = #families. Families
                not selected receive an all-False mask.

    Parameters
    ----------
    families : dict[str, np.ndarray]
        Mapping family-name -> 1-D array of raw p-values within that family.
    q : float, default 0.05
        Target hierarchical FDR level.

    Returns
    -------
    pass_dict : dict[str, np.ndarray of bool]
        Per-family rejection masks (input length preserved).
    q_dict : dict[str, np.ndarray of float]
        Per-family within-family BH-adjusted q-values. For unselected
        families this is all 1.0 (no rejection at any level ≤ q).
    """
    family_names = list(families.keys())
    m = len(family_names)
    if m == 0:
        return {}, {}

    # Stage 1: BH on family-min p-values
    min_ps = np.array(
        [float(np.min(np.asarray(families[name], dtype=float))) for name in family_names]
    )
    selected_mask, _ = benjamini_hochberg(min_ps, q=q)
    n_selected = int(selected_mask.sum())

    pass_dict: dict[str, np.ndarray] = {}
    q_dict: dict[str, np.ndarray] = {}

    if n_selected == 0:
        for name in family_names:
            arr = np.asarray(families[name], dtype=float)
            pass_dict[name] = np.zeros(arr.shape, dtype=bool)
            q_dict[name] = np.ones(arr.shape, dtype=float)
        return pass_dict, q_dict

    alpha_within = q * n_selected / m

    for name, sel in zip(family_names, selected_mask):
        arr = np.asarray(families[name], dtype=float).ravel()
        if sel:
            mask, q_adj = benjamini_hochberg(arr, q=alpha_within)
            pass_dict[name] = mask
            q_dict[name] = q_adj
        else:
            pass_dict[name] = np.zeros(arr.shape, dtype=bool)
            q_dict[name] = np.ones(arr.shape, dtype=float)

    return pass_dict, q_dict


def bonferroni(p_values, alpha: float = 0.05) -> np.ndarray:
    """Bonferroni correction.

    Returns a boolean mask where p_i < alpha / n. Strict inequality matches
    the textbook definition.
    """
    p = np.asarray(p_values, dtype=float).ravel()
    n = p.size
    if n == 0:
        return np.zeros(0, dtype=bool)
    threshold = alpha / n
    return p < threshold
