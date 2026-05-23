"""Pytest fixtures for R³ Isolated Validation.

Fixtures
--------
* ``project_root``    — repo root containing ``Musical_Intelligence/`` engine source
* ``engine_pin``      — parsed _infra/manifests/engine_pin.json dict
* ``r3``              — ``R3Extractor`` instance (cached session-scope)
* ``stim``            — module shortcut: ``from _infra import stimuli as stim``
* ``mel_of``          — callable: audio Tensor → engine-canonical log-mel
* ``r3_extract``      — callable: audio Tensor → ``R3Output``

Engine-pin integrity check
--------------------------
A session-start fixture (``_pin_integrity``) computes the SHA-256 aggregate of
all .py files in the engine tree and asserts it matches ``content_aggregate_sha256``
in the pin manifest. If the engine tree drifts, every test halts with a clear
message at session-start rather than producing misleading results downstream.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
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
# Walk up until we find the project root (contains Musical_Intelligence/ear/r3).
# Also accept V-Reproduction fresh-clone layout where the engine is vendored
# at <root>/engine/Musical_Intelligence/ (the parent-checkout dev mode keeps
# the engine at <root>/Musical_Intelligence/).
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
# in addition to in-tree (MI_Results/Musical_Intelligence/) and vendored
# (_infra/engine/Musical_Intelligence/). Only needed when MI_BUILD_ORACLE=1.
_PARENT = _PROJECT_ROOT.parent
if (_PARENT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
    if str(_PARENT) not in sys.path:
        sys.path.insert(0, str(_PARENT))

# ----------------------------------------------------------------------------
# Engine-facts stubs (CACHE mode): inject Musical_Intelligence.* into
# sys.modules BEFORE any test does `from Musical_Intelligence... import …`.
# In BUILD mode: register fact recording on import + save on session end.
# ----------------------------------------------------------------------------
from _infra import engine_facts as _engine_facts  # noqa: E402

if _engine_facts.BUILD_MODE:
    # Set up monkey-patches so live engine imports get recorded as tests call them
    _engine_facts.setup_recording()
else:
    # CACHE mode: install stubs immediately so tests' module-level imports resolve
    _engine_facts.install_stubs()


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
# R³ extractor + helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def r3():
    """Session-scoped R3Extractor (BUILD mode) or oracle-backed shim (CACHE mode).

    BUILD mode wraps the live extractor so every .extract() call records its
    output under BOTH audio-key (if given) and mel-key — letting the cache
    serve subsequent lookups whether the test passes audio or mel.
    """
    from _infra.oracle import BUILD_MODE, Oracle
    if BUILD_MODE:
        from Musical_Intelligence.ear.r3.extractor import R3Extractor
        extractor = R3Extractor()
        oracle = Oracle.instance()
        _orig_extract = extractor.extract

        def _wrapped_extract(mel, *, audio=None, sr=44100):
            output = _orig_extract(mel, audio=audio, sr=sr)
            oracle.record_tensor(mel, output)
            if audio is not None:
                oracle.record_tensor(audio, output)
            return output

        extractor.extract = _wrapped_extract
        return extractor

    # Prefer the engine_facts R3Extractor stub (has total_dim, extract sig,
    # oracle-backed extract method). Fall back to a minimal local shim if
    # the stub isn't installed (e.g. running tests directly without facts).
    import sys as _sys
    _extractor_mod = _sys.modules.get("Musical_Intelligence.ear.r3.extractor")
    if _extractor_mod is not None and hasattr(_extractor_mod, "R3Extractor"):
        return _extractor_mod.R3Extractor()

    oracle = Oracle.instance()

    class _R3Shim:
        """Cache-only shim mimicking R3Extractor.extract(mel, audio=, sr=)."""
        total_dim = 97
        def extract(self, mel=None, audio=None, sr=44100):
            if audio is not None:
                try:
                    return oracle.lookup_tensor(audio)
                except KeyError:
                    pass
            if mel is not None:
                return oracle.lookup_tensor(mel)
            raise RuntimeError(
                "CACHE mode: r3.extract() needs either audio= or mel positional arg"
            )

    return _R3Shim()


@pytest.fixture(scope="session")
def stim():
    """Convenience: shortcut for `from _infra import stimuli`."""
    from _infra import stimuli
    return stimuli


@pytest.fixture(scope="session")
def mel_of() -> Callable[[Tensor], Tensor]:
    """Map audio Tensor (1, N) → engine-canonical log-mel (1, 128, T)."""
    from _infra.stimuli import to_mel
    def _convert(audio: Tensor) -> Tensor:
        return to_mel(audio)
    return _convert


@pytest.fixture(scope="session")
def r3_extract(r3, mel_of) -> Callable[[Tensor], object]:
    """audio Tensor → R3Output. BUILD mode runs live engine (extractor wrapper
    records audio+mel keys); CACHE mode looks up by audio key."""
    from _infra.oracle import BUILD_MODE, Oracle
    if BUILD_MODE:
        # r3.extract is already wrapped above — just call it through, recording
        # happens inside the wrapper for both audio and mel keys.
        def _run(audio: Tensor):
            with torch.no_grad():
                return r3.extract(mel_of(audio), audio=audio, sr=44100)
        return _run
    oracle = Oracle.instance()
    def _run(audio: Tensor):
        return oracle.lookup_tensor(audio)
    return _run


# ---------------------------------------------------------------------------
# Cache-only mode: skip engine-source-dependent tests if engine not vendored
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(config, items):
    """Skip only if BOTH the engine source and the oracle cache are absent.

    BUILD mode (MI_BUILD_ORACLE=1) → never skip (tests need to populate oracle).
    Oracle cache present → run via cache-backed fixtures.
    Engine present (in-tree or sibling-checkout or vendored) → run normally,
        UNLESS MI_FORCE_CACHE_MODE=1 — in which case ignore engine and rely on
        cache (useful for in-place reviewer-mode simulation while sibling
        engine source is visible on the developer machine).
    Otherwise → skip with clear rebuild instruction.
    """
    import os as _os
    from _infra.oracle import ORACLE_PATH, BUILD_MODE
    if BUILD_MODE:
        return  # build mode: run all tests against live engine to populate oracle
    if ORACLE_PATH.exists():
        return  # oracle cache available, run via cache-backed fixtures
    if _os.environ.get("MI_FORCE_CACHE_MODE") == "1":
        import pytest as _pt
        marker = _pt.mark.skip(
            reason="MI_FORCE_CACHE_MODE=1 but oracle cache is missing — rebuild"
        )
        for item in items:
            item.add_marker(marker)
        return
    engine_candidates = [
        _PROJECT_ROOT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
        _PROJECT_ROOT.parent / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
        _PROJECT_ROOT / "_infra" / "engine" / "Musical_Intelligence" / "ear" / "r3" / "extractor.py",
    ]
    if any(p.exists() for p in engine_candidates):
        return  # engine present somewhere, run normally
    import pytest
    marker = pytest.mark.skip(
        reason="neither engine source nor oracle cache available — "
               "rebuild with `MI_BUILD_ORACLE=1 pytest` or vendor engine source"
    )
    for item in items:
        item.add_marker(marker)


def pytest_sessionfinish(session, exitstatus):
    """BUILD mode: save the engine_facts manifest on session end."""
    from _infra.oracle import BUILD_MODE
    if not BUILD_MODE:
        return
    from _infra import engine_facts
    engine_facts.save_facts()
