"""Pytest fixtures for R³ Isolated Validation.

Fixtures
--------
* ``project_root``    — repo root path (``/Volumes/SRC-9/SRC Musical Intelligence``)
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
    if (_PROJECT_ROOT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
        break
    if (_PROJECT_ROOT / "engine" / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
        _PROJECT_ROOT = _PROJECT_ROOT / "engine"
        break
    _PROJECT_ROOT = _PROJECT_ROOT.parent
else:
    raise RuntimeError(f"Could not locate Musical_Intelligence/ear/r3 from {_THIS}")
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
# R³ extractor + helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def r3():
    """Session-scoped R3Extractor instance."""
    from Musical_Intelligence.ear.r3.extractor import R3Extractor
    return R3Extractor()


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
    """End-to-end helper: audio Tensor → R3Output."""
    def _run(audio: Tensor):
        with torch.no_grad():
            return r3.extract(mel_of(audio), audio=audio, sr=44100)
    return _run
