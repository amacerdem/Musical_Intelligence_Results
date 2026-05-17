"""Pytest fixtures for T³ Isolated Validation.

Fixtures
--------
* ``project_root``    — repo root path (``/Volumes/SRC-9/SRC Musical Intelligence``)
* ``engine_pin``      — parsed _infra/manifests/engine_pin.json dict
* ``h3``              — ``H3Extractor`` instance (cached session-scope)
* ``stim``            — module shortcut: ``from _infra import stimuli as stim``
* ``h3_extract``      — callable: (r3_features, demand) → ``H3Output``
* ``demand``          — module shortcut for ``from _infra.stimuli import demand_*``

Engine-pin integrity check
--------------------------
A session-start fixture (``_pin_integrity``) computes the SHA-256 aggregate
of all .py files in the engine tree and asserts it matches
``content_aggregate_sha256`` in the pin manifest. If the engine tree drifts,
every test halts with a clear message at session-start rather than producing
misleading results downstream.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

import pytest
import torch
from torch import Tensor


# ---------------------------------------------------------------------------
# Path bootstrap — make `Musical_Intelligence` importable
# ---------------------------------------------------------------------------

_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parent
for _ in range(8):
    if (_PROJECT_ROOT / "Musical_Intelligence" / "ear" / "h3" / "extractor.py").exists():
        break
    # V-Reproduction fresh-clone fallback: engine vendored at <root>/engine/
    if (_PROJECT_ROOT / "engine" / "Musical_Intelligence" / "ear" / "h3" / "extractor.py").exists():
        _PROJECT_ROOT = _PROJECT_ROOT / "engine"
        break
    _PROJECT_ROOT = _PROJECT_ROOT.parent
else:
    raise RuntimeError(f"Could not locate Musical_Intelligence/ear/h3 from {_THIS}")
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Validation-suite root (this conftest's parent) for `from _infra import …`
_SUITE_ROOT = _THIS.parent
if str(_SUITE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SUITE_ROOT))
_INFRA = _SUITE_ROOT / "_infra"


# ---------------------------------------------------------------------------
# Pin manifest
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def project_root() -> Path:
    return _PROJECT_ROOT


@pytest.fixture(scope="session")
def engine_pin() -> dict:
    with open(_INFRA / "manifests" / "engine_pin.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Pin-integrity gate (runs first, halts session on drift)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _pin_integrity(engine_pin, project_root):
    """Halt the session if the engine tree no longer matches the pin manifest."""
    from _infra.sha_utils import aggregate_engine_sha
    engine_root = project_root / "Musical_Intelligence"
    actual = aggregate_engine_sha(engine_root)
    expected = engine_pin["content_aggregate_sha256"]
    if actual != expected:
        pytest.exit(
            "\nENGINE PIN DRIFT — refusing to run isolated validation.\n"
            f"  expected SHA-256 aggregate: {expected}\n"
            f"  actual                    : {actual}\n"
            f"  engine root               : {engine_root}\n"
            "Reproduce the canonical pin or update _infra/manifests/engine_pin.json.\n",
            returncode=2,
        )
    yield


# ---------------------------------------------------------------------------
# H³ extractor + helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def h3():
    """Session-scoped H3Extractor instance.

    Note: H3Extractor() is stateless beyond construction (L2.1 confirmed),
    so a single session-scoped instance is shared across all tests safely.
    """
    from Musical_Intelligence.ear.h3 import H3Extractor
    return H3Extractor()


@pytest.fixture(scope="session")
def stim():
    """Convenience: shortcut for `from _infra import stimuli`."""
    from _infra import stimuli
    return stimuli


@pytest.fixture(scope="session")
def h3_extract(h3) -> Callable[[Tensor, set], object]:
    """End-to-end helper: (r3_features, demand) → H3Output.

    Wraps `h3.extract(...)` in a `torch.no_grad()` context to ensure no
    autograd graph is built (T³ has no learnable parameters; gradients
    would be wasted memory).
    """
    def _run(r3_features: Tensor, demand: set):
        with torch.no_grad():
            return h3.extract(r3_features, demand)
    return _run
