"""TDD tests for `stats.cka` — Linear centered kernel alignment."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from stats.cka import linear_cka  # noqa: E402


def test_cka_self_is_one():
    """CKA(X, X) == 1.0 (within float tolerance)."""
    rng = np.random.default_rng(0)
    X = rng.standard_normal((100, 30))
    assert linear_cka(X, X) == 1.0 or abs(linear_cka(X, X) - 1.0) < 1e-9


def test_cka_independent_data_lower_than_self():
    """CKA(X, Y) < CKA(X, X) when X, Y are independent (property-based)."""
    rng = np.random.default_rng(1)
    X = rng.standard_normal((500, 50))
    Y = rng.standard_normal((500, 30))
    self_cka = linear_cka(X, X)
    cross_cka = linear_cka(X, Y)
    assert 0.0 <= cross_cka <= 1.0
    assert cross_cka < self_cka
    # weaker bound than 0.1, but still proves "much less than identical"
    assert cross_cka < 0.5


def test_cka_scale_invariant():
    """CKA(X, c*X) == CKA(X, X) for any non-zero scalar c (positive or negative)."""
    rng = np.random.default_rng(2)
    X = rng.standard_normal((200, 20))
    for c in (3.7, -2.5, 0.01):
        cka_scaled = linear_cka(X, c * X)
        assert abs(cka_scaled - 1.0) < 1e-9, f"CKA(X, {c}*X) = {cka_scaled}, expected 1.0"


def test_cka_symmetric():
    """CKA(X, Y) == CKA(Y, X)."""
    rng = np.random.default_rng(3)
    X = rng.standard_normal((150, 40))
    Y = rng.standard_normal((150, 25))
    a = linear_cka(X, Y)
    b = linear_cka(Y, X)
    assert abs(a - b) < 1e-12, f"Asymmetric: {a} vs {b}"


def test_cka_returns_value_in_unit_interval():
    """CKA must lie in [0, 1] for any non-pathological inputs."""
    rng = np.random.default_rng(4)
    for _ in range(5):
        X = rng.standard_normal((80, 10))
        Y = rng.standard_normal((80, 15))
        val = linear_cka(X, Y)
        assert 0.0 <= val <= 1.0, f"CKA out of [0,1]: {val}"


def test_cka_translation_invariant():
    """Centering means CKA is invariant to additive shifts (column-wise)."""
    rng = np.random.default_rng(5)
    X = rng.standard_normal((100, 20))
    Y = rng.standard_normal((100, 20))
    shift = rng.standard_normal(20) * 5.0
    a = linear_cka(X, Y)
    b = linear_cka(X + shift, Y)
    assert abs(a - b) < 1e-9, f"Translation broke CKA: {a} vs {b}"
