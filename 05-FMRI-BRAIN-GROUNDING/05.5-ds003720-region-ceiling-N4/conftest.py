"""Pytest fixtures for 05.5-ds003720-region-ceiling-N4."""
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
def ckpt_bold_dir(project_root) -> Path:
    candidates = [
        project_root / "V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-AP-v2-08-nakai/RunPod-Exp-01/ckpt_bold",
        project_root / "datasets/paper-anchors/voxelwise-encoding/ckpt_bold",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def per_subject_per_region_csv(project_root) -> Path:
    candidates = [
        project_root / "Bold-fMRI/ds003720/06_encoding/per_subject_per_region_r.csv",
        project_root / "datasets/paper-anchors/voxelwise-encoding/per_subject_per_region_r.csv",
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
            f"\nENGINE PIN DRIFT — refusing 05.5-ds003720-region-ceiling-N4.\n"
            f"  expected: {expected}\n  actual: {actual}\n",
            returncode=2,
        )
    yield
