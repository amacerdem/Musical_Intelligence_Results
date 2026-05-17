"""Pytest fixtures for 23-h4-h5-pmemo-dynamic-emotion.

Engine pin integrity check + project root + PMEmo data paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parent
for _ in range(8):
    if (_PROJECT_ROOT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
        break
    # V-Reproduction fresh-clone fallback: engine vendored at <root>/engine/
    if (_PROJECT_ROOT / "engine" / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
        _PROJECT_ROOT = _PROJECT_ROOT / "engine"
        break
    _PROJECT_ROOT = _PROJECT_ROOT.parent
else:
    raise RuntimeError(f"Could not locate Musical_Intelligence from {_THIS}")
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
def pmemo_annotations_arousal(project_root) -> Path:
    """PMEmo per-rater dynamic arousal CSVs (e.g., 1-A.csv, ...)."""
    candidates = [
        project_root / "datasets" / "emotion" / "PMEmo" / "PMEmo2018" / "PMEmo" / "Annotations" / "Arousal",
        project_root / "Science" / "datasets" / "emotion" / "PMEmo" / "PMEmo2018" / "PMEmo" / "Annotations" / "Arousal",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def pmemo_annotations_valence(project_root) -> Path:
    candidates = [
        project_root / "datasets" / "emotion" / "PMEmo" / "PMEmo2018" / "PMEmo" / "Annotations" / "Valence",
        project_root / "Science" / "datasets" / "emotion" / "PMEmo" / "PMEmo2018" / "PMEmo" / "Annotations" / "Valence",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def engine_cache_dir(project_root) -> Path:
    """PMEmo engine cache (per_frame)."""
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "PMEmo" / "per_frame",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "PMEmo" / "per_frame",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def pooled_csv(project_root) -> Path:
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "PMEmo" / "pooled.csv",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "PMEmo" / "pooled.csv",
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
            "\nENGINE PIN DRIFT — refusing to run 23-h4-h5-pmemo-dynamic-emotion.\n"
            f"  expected SHA-256 aggregate: {expected}\n"
            f"  actual                    : {actual}\n"
            f"  engine root               : {engine_root}\n",
            returncode=2,
        )
    yield
