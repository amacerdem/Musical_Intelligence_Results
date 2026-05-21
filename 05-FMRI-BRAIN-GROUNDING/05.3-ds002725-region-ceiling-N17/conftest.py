"""Pytest fixtures for 05.3-ds002725-region-ceiling-N17.

Engine pin integrity check + project root + ds002725 BOLD/MI cache paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

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

_SUITE_ROOT = _THIS.parent
if str(_SUITE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SUITE_ROOT))
_INFRA = _SUITE_ROOT / "_infra"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return _PROJECT_ROOT


@pytest.fixture(scope="session")
def suite_root() -> Path:
    return _SUITE_ROOT


@pytest.fixture(scope="session")
def engine_pin() -> dict:
    with open(_INFRA / "manifests" / "engine_pin.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def paper_baseline() -> dict:
    with open(_INFRA / "manifests" / "paper_time_baseline.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def ds002725_bold_cache(project_root) -> Path:
    """ds002725 N=17 paper-canonical ROI BOLD cache (per-subject *_bold_26.npz)."""
    candidates = [
        project_root / "Bold-fMRI" / "exp-02-cross-subject-17" / "checkpoints",
        project_root / "datasets" / "paper-anchors" / "mech-region" / "bold-26region" / "checkpoints",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def ds002725_mi_cache(project_root) -> Path:
    """ds002725 MI engine per-frame outputs."""
    candidates = [
        project_root / "engine_outputs" / "neuroimaging" / "ds002725" / "per_frame",
        project_root / "engine_outputs" / "neuroimaging" / "ds002725" / "per_frame",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session", autouse=True)
def _pin_integrity(engine_pin, project_root):
    from _infra.sha_utils import aggregate_engine_sha
    engine_root = project_root / "Musical_Intelligence"
    actual = aggregate_engine_sha(engine_root)
    expected = engine_pin["content_aggregate_sha256"]
    if actual != expected:
        pytest.exit(
            "\nENGINE PIN DRIFT — refusing to run 05.3-ds002725-region-ceiling-N17.\n"
            f"  expected SHA-256 aggregate: {expected}\n"
            f"  actual                    : {actual}\n"
            f"  engine root               : {engine_root}\n",
            returncode=2,
        )
    yield
