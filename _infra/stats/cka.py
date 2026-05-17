"""Linear Centered Kernel Alignment (CKA).

Reference
---------
Kornblith, Norouzi, Lee, Hinton (2019), "Similarity of neural network
representations revisited", ICML. We use the linear-kernel form, which
admits the efficient feature-space identity:

    CKA(X, Y) = ||X^T Y||_F^2 / (||X^T X||_F * ||Y^T Y||_F)

after column-mean centering of X and Y. This avoids forming the
n×n Gram matrices explicitly.
"""
from __future__ import annotations

import numpy as np


def linear_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Linear CKA between (n_samples, n_features) representations X and Y.

    Feature dimensions of X and Y need not match; both are mean-centered
    along the sample axis (Kornblith 2019). Returns a value in [0, 1].

    Edge case: if either centered matrix is all-zero (constant features),
    returns 0.0.
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.ndim != 2 or Y.ndim != 2:
        raise ValueError(f"CKA requires 2-D arrays; got {X.shape}, {Y.shape}")
    if X.shape[0] != Y.shape[0]:
        raise ValueError(
            f"CKA requires same n_samples; got {X.shape[0]} vs {Y.shape[0]}"
        )

    # Mean-centre along the sample axis (per feature)
    Xc = X - X.mean(axis=0, keepdims=True)
    Yc = Y - Y.mean(axis=0, keepdims=True)

    # Frobenius norms of cross- and self-Gram matrices via feature-space identity
    cross = float(np.linalg.norm(Xc.T @ Yc, ord="fro") ** 2)
    nx = float(np.linalg.norm(Xc.T @ Xc, ord="fro"))
    ny = float(np.linalg.norm(Yc.T @ Yc, ord="fro"))

    denom = nx * ny
    if denom < 1e-30:
        return 0.0
    cka = cross / denom
    # Numerical safety: clamp to [0, 1]
    if cka < 0.0:
        cka = 0.0
    elif cka > 1.0:
        cka = 1.0
    return cka
