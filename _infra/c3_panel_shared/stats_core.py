"""Cross-segment statistical utilities.

- Spearman ρ with Fisher-Z 95% CI
- Benjamini-Hochberg FDR
- Label-permutation null for arbitrary scalar statistics
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats as scistats


@dataclass(frozen=True)
class CorrResult:
    rho: float
    n: int
    p_raw: float
    ci_low_95: float
    ci_high_95: float

    def to_dict(self) -> dict:
        return {
            "effect": self.rho,
            "n": self.n,
            "p_raw": self.p_raw,
            "ci_low_95": self.ci_low_95,
            "ci_high_95": self.ci_high_95,
        }


def fisher_z(rho: float) -> float:
    if rho >= 1.0:
        rho = 1.0 - 1e-12
    if rho <= -1.0:
        rho = -1.0 + 1e-12
    return 0.5 * math.log((1 + rho) / (1 - rho))


def fisher_z_inv(z: float) -> float:
    e2z = math.exp(2 * z)
    return (e2z - 1) / (e2z + 1)


def fisher_z_ci(rho: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """95% Fisher-Z CI for a Spearman correlation. n is the sample size."""
    if n < 4:
        return (float("nan"), float("nan"))
    z = fisher_z(rho)
    se = 1.0 / math.sqrt(n - 3)
    crit = scistats.norm.ppf(1 - alpha / 2)
    return fisher_z_inv(z - crit * se), fisher_z_inv(z + crit * se)


def spearman_with_ci(x: np.ndarray, y: np.ndarray, alpha: float = 0.05) -> CorrResult:
    """Spearman ρ + p + Fisher-Z CI. NaNs in either vector are dropped."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    n = int(x.size)
    if n < 3:
        return CorrResult(rho=float("nan"), n=n, p_raw=float("nan"),
                          ci_low_95=float("nan"), ci_high_95=float("nan"))
    res = scistats.spearmanr(x, y)
    rho = float(res.correlation if hasattr(res, "correlation") else res.statistic)
    p = float(res.pvalue)
    lo, hi = fisher_z_ci(rho, n, alpha=alpha)
    return CorrResult(rho=rho, n=n, p_raw=p, ci_low_95=lo, ci_high_95=hi)


def bh_fdr(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted q-values for an array of p-values.

    Returns an array same shape as input. NaN p-values map to NaN q.
    """
    p = np.asarray(p_values, dtype=float)
    finite = np.isfinite(p)
    q = np.full_like(p, np.nan)
    if finite.sum() == 0:
        return q
    pf = p[finite]
    m = pf.size
    order = np.argsort(pf)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, m + 1)
    raw = pf * m / ranks
    sorted_p = pf[order]
    sorted_q = sorted_p * m / np.arange(1, m + 1)
    # monotone non-increasing from the largest p downward
    sorted_q_mono = np.minimum.accumulate(sorted_q[::-1])[::-1]
    sorted_q_mono = np.minimum(sorted_q_mono, 1.0)
    qf = np.empty_like(pf)
    qf[order] = sorted_q_mono
    q[finite] = qf
    return q


def perm_null_spearman(x: np.ndarray, y: np.ndarray, n_perm: int = 1000,
                       seed: int | None = None) -> tuple[float, np.ndarray]:
    """Two-sided permutation null for Spearman ρ.

    Returns (perm_p, null_distribution). perm_p = fraction of |ρ_perm| >= |ρ_obs|.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size < 3:
        return float("nan"), np.array([])
    obs = scistats.spearmanr(x, y)
    rho_obs = float(obs.correlation if hasattr(obs, "correlation") else obs.statistic)
    rng = np.random.default_rng(seed)
    nulls = np.empty(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        r = scistats.spearmanr(x, y_perm)
        nulls[i] = r.correlation if hasattr(r, "correlation") else r.statistic
    perm_p = float((np.abs(nulls) >= abs(rho_obs)).mean())
    return perm_p, nulls


def directional_pass(rho: float, predicted_sign: str, q: float, q_threshold: float = 0.05) -> bool:
    """A row passes if the sign matches AND q < threshold."""
    if not math.isfinite(rho) or not math.isfinite(q):
        return False
    if q >= q_threshold:
        return False
    if predicted_sign == "+":
        return rho > 0
    if predicted_sign == "-":
        return rho < 0
    raise ValueError(f"predicted_sign must be '+' or '-'; got {predicted_sign!r}")


if __name__ == "__main__":
    # Tiny self-check
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    y = 0.4 * x + rng.normal(size=200) * 0.5
    res = spearman_with_ci(x, y)
    print(f"smoke: rho={res.rho:.3f} n={res.n} p={res.p_raw:.2e} CI=[{res.ci_low_95:.3f}, {res.ci_high_95:.3f}]")
    ps = np.array([0.001, 0.01, 0.04, 0.05, 0.2, 0.5, 0.9])
    print(f"smoke: BH-FDR of {ps.tolist()} → {bh_fdr(ps).round(3).tolist()}")
