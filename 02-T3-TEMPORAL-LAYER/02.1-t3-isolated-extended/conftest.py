"""Pytest fixtures for T³ Isolated Validation.

Fixtures
--------
* ``project_root``    — repo root containing ``Musical_Intelligence/`` engine source
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
    # Cache-only mode: MI_Results root has engine_outputs/ + _infra/
    if (_PROJECT_ROOT / "engine_outputs").is_dir() and (_PROJECT_ROOT / "_infra").is_dir():
        break
    _PROJECT_ROOT = _PROJECT_ROOT.parent
else:
    raise RuntimeError(f"Could not locate MI_Results from {_THIS}")
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Validation-suite root (this conftest's parent) for `from _infra import …`
_SUITE_ROOT = _THIS.parent
if str(_SUITE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SUITE_ROOT))
_INFRA = _SUITE_ROOT / "_infra"

# BUILD-mode engine resolution: try sibling-checkout (../Musical_Intelligence/)
# in addition to in-tree and vendored. Only needed when MI_BUILD_ORACLE=1.
_PARENT = _PROJECT_ROOT.parent
if (_PARENT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
    if str(_PARENT) not in sys.path:
        sys.path.insert(0, str(_PARENT))

# Engine-facts stubs: BUILD records, CACHE installs sys.modules stubs.
from _infra import engine_facts as _engine_facts  # noqa: E402

if _engine_facts.BUILD_MODE:
    _engine_facts.setup_recording()
else:
    _engine_facts.install_stubs()


def pytest_sessionfinish(session, exitstatus):
    """BUILD mode: save the engine_facts manifest on session end."""
    from _infra.oracle import BUILD_MODE
    if not BUILD_MODE:
        return
    from _infra import engine_facts
    engine_facts.save_facts()


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
    """Halt the session if the engine tree drifts. CACHE mode skips this check."""
    from _infra.oracle import BUILD_MODE
    if not BUILD_MODE:
        yield  # cache mode: engine not present, oracle is source of truth
        return
    from _infra.sha_utils import aggregate_engine_sha
    engine_root = project_root / "Musical_Intelligence"
    if not engine_root.exists():
        engine_root = project_root.parent / "Musical_Intelligence"
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
    """Session-scoped H3Extractor (BUILD mode) or oracle-backed shim (CACHE mode).

    Note: H3Extractor() is stateless beyond construction (L2.1 confirmed),
    so a single session-scoped instance is shared across all tests safely.
    """
    from _infra.oracle import BUILD_MODE, Oracle
    if BUILD_MODE:
        from Musical_Intelligence.ear.h3 import H3Extractor
        return H3Extractor()
    oracle = Oracle.instance()

    class _H3Shim:
        """Cache-only shim mimicking H3Extractor.extract(r3_features, demand)
        + .constants / .attention attributes (loaded from manifest).
        """
        def __init__(self):
            self._attrs = self._load_attrs()

        def _load_attrs(self):
            """Load h3.constants + h3.attention from the pin manifest."""
            import json
            with open(_INFRA / "manifests" / "engine_pin.json") as f:
                pin = json.load(f)
            return pin.get("h3_attrs", {})

        def __getattr__(self, name):
            if name in self._attrs:
                v = self._attrs[name]
                if isinstance(v, dict):
                    from types import SimpleNamespace
                    return SimpleNamespace(**v)
                return v
            raise AttributeError(
                f"CACHE mode: h3.{name} not in oracle attrs "
                f"(available: {list(self._attrs)})"
            )

        def extract(self, r3_features, demand):
            return oracle.lookup(r3_features, demand)

    return _H3Shim()


@pytest.fixture(scope="session")
def stim():
    """Convenience: shortcut for `from _infra import stimuli`."""
    from _infra import stimuli
    return stimuli


@pytest.fixture(scope="session")
def h3_extract(h3) -> Callable[[Tensor, set], object]:
    """(r3_features, demand) → H3Output. BUILD mode runs live + records; CACHE mode looks up.

    Wraps `h3.extract(...)` in a `torch.no_grad()` context to ensure no
    autograd graph is built (T³ has no learnable parameters; gradients
    would be wasted memory).
    """
    from _infra.oracle import BUILD_MODE, Oracle
    if BUILD_MODE:
        oracle = Oracle.instance()
        def _run(r3_features: Tensor, demand: set):
            with torch.no_grad():
                output = h3.extract(r3_features, demand)
            oracle.record(r3_features, demand, output)
            return output
        return _run
    oracle = Oracle.instance()
    def _run(r3_features: Tensor, demand: set):
        return oracle.lookup(r3_features, demand)
    return _run


# ---------------------------------------------------------------------------
# Cache-only mode: skip engine-source-dependent tests if engine not vendored
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(config, items):
    """Skip only if BOTH the engine source and the oracle cache are absent.

    BUILD mode (MI_BUILD_ORACLE=1) → never skip.
    Oracle cache present → run via cache-backed fixtures.
    Engine present (in-tree / sibling / vendored) → run normally.
    Otherwise → skip.
    """
    from _infra.oracle import ORACLE_PATH, BUILD_MODE
    if BUILD_MODE:
        return
    if ORACLE_PATH.exists():
        return
    engine_candidates = [
        _PROJECT_ROOT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
        _PROJECT_ROOT.parent / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
        _PROJECT_ROOT / "_infra" / "engine" / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
    ]
    if any(p.exists() for p in engine_candidates):
        return
    import pytest
    marker = pytest.mark.skip(
        reason="neither engine source nor oracle cache available — "
               "rebuild with `MI_BUILD_ORACLE=1 pytest` or vendor engine source"
    )
    for item in items:
        item.add_marker(marker)
