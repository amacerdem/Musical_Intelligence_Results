"""Ridge regression primitives: LOSO ridge + banded-ridge wrapper.

Used by Axis-7c (cross-subject voxelwise encoding). Banded ridge supports
separate alphas per feature group, with himalaya as the preferred backend
and a single-alpha RidgeCV fallback when himalaya is unavailable.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import RidgeCV

_HIMALAYA_AVAILABLE = False
try:
    from himalaya.ridge import GroupRidgeCV
    from himalaya.scoring import correlation_score  # noqa: F401
    _HIMALAYA_AVAILABLE = True
except ImportError:
    GroupRidgeCV = None  # type: ignore[assignment]


def _safe_pearson(y_true, y_pred):
    """Pearson r, returning None when either input is constant (so callers
    can skip the fold rather than fold a 0 into a Fisher-z mean)."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return None
    return float(pearsonr(y_true, y_pred).statistic)


def loso_ridge_held_out_r(
    X: np.ndarray,
    y: np.ndarray,
    *,
    subjects: np.ndarray,
    alphas=(0.1, 1.0, 10.0, 100.0, 1000.0),
) -> float:
    """Leave-one-subject-out ridge with nested alpha selection (RidgeCV).

    For each subject: train RidgeCV on all other subjects (inner CV picks
    alpha), predict the held-out subject's y, record Pearson r. Return the
    Fisher-z averaged held-out r across subjects.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    subjects = np.asarray(subjects)
    unique_subj = np.unique(subjects)
    if unique_subj.size < 2:
        raise ValueError(f"LOSO needs ≥ 2 subjects; got {unique_subj.size}")

    rs: list[float] = []
    for s in unique_subj:
        train_mask = subjects != s
        test_mask = ~train_mask
        if test_mask.sum() < 2:
            continue
        model = RidgeCV(alphas=alphas)
        model.fit(X[train_mask], y[train_mask])
        y_pred = model.predict(X[test_mask])
        r = _safe_pearson(y[test_mask], y_pred)
        if r is None:  # constant y in this fold — skip rather than bias toward 0
            continue
        rs.append(r)

    if not rs:
        return float("nan")

    # Fisher-z mean
    rs_arr = np.clip(np.array(rs), -0.999999, 0.999999)
    z = np.arctanh(rs_arr)
    z_mean = float(z.mean())
    return float(np.tanh(z_mean))


def banded_ridge_held_out_r(
    feature_groups: list[np.ndarray],
    y: np.ndarray,
    *,
    subjects: np.ndarray,
    alphas_per_group=(0.1, 1.0, 10.0, 100.0, 1000.0),
    seed: int = 0,
    cv: int = 2,
    n_iter: int = 10,
) -> float:
    """Banded ridge — separate alpha per feature group, LOSO held-out r.

    Uses himalaya's GroupRidgeCV when available; otherwise falls back to
    concatenated single-alpha RidgeCV with a warning. Returns Fisher-z
    averaged held-out Pearson r across LOSO folds.

    Parameters
    ----------
    seed : int
        Random state for himalaya's GroupRidgeCV (controls inner CV draws).
    cv : int
        Inner-CV folds for GroupRidgeCV.
    n_iter : int
        Number of random-search iterations for himalaya's per-group alpha
        selection.
    """
    feature_groups = [np.asarray(g, dtype=float) for g in feature_groups]
    y = np.asarray(y, dtype=float).ravel()
    subjects = np.asarray(subjects)
    n = y.shape[0]
    for g in feature_groups:
        if g.shape[0] != n:
            raise ValueError(
                f"banded_ridge: feature group has {g.shape[0]} rows; expected {n}"
            )

    unique_subj = np.unique(subjects)
    if unique_subj.size < 2:
        raise ValueError(f"banded_ridge LOSO needs ≥ 2 subjects; got {unique_subj.size}")

    if not _HIMALAYA_AVAILABLE:
        warnings.warn(
            "himalaya not installed — banded_ridge_held_out_r falling back to "
            "concatenated single-alpha RidgeCV.",
            RuntimeWarning,
            stacklevel=2,
        )
        X_concat = np.concatenate(feature_groups, axis=1)
        return loso_ridge_held_out_r(
            X_concat, y, subjects=subjects, alphas=alphas_per_group
        )

    # Himalaya path: per-group alpha selection via random-search CV.
    rs: list[float] = []
    alphas_arr = np.asarray(alphas_per_group, dtype=float)
    for s in unique_subj:
        train_mask = subjects != s
        test_mask = ~train_mask
        if test_mask.sum() < 2:
            continue
        Xs_train = [g[train_mask] for g in feature_groups]
        Xs_test = [g[test_mask] for g in feature_groups]

        model = GroupRidgeCV(
            groups="input",
            random_state=seed,
            cv=cv,
            solver_params=dict(
                alphas=alphas_arr,
                n_iter=n_iter,
            ),
        )
        try:
            model.fit(Xs_train, y[train_mask])
            y_pred = model.predict(Xs_test)
            y_pred = np.asarray(y_pred).ravel()
            r = _safe_pearson(y[test_mask], y_pred)
        except Exception:
            # If himalaya fails for any reason in this fold, fall back per-fold
            X_train = np.concatenate(Xs_train, axis=1)
            X_test = np.concatenate(Xs_test, axis=1)
            ridge = RidgeCV(alphas=alphas_per_group)
            ridge.fit(X_train, y[train_mask])
            r = _safe_pearson(y[test_mask], ridge.predict(X_test))

        if r is None:  # constant y this fold — skip rather than bias toward 0
            continue
        rs.append(r)

    if not rs:
        return float("nan")
    rs_arr = np.clip(np.array(rs), -0.999999, 0.999999)
    return float(np.tanh(np.arctanh(rs_arr).mean()))
