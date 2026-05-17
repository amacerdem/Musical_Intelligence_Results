"""Pytest fixtures for 24-h18-h25-eerola-film-gems.

Engine pin integrity check + project root + Eerola Set 1/Set 2 paths.
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
def eerola_ratings_set2(project_root) -> Path:
    candidates = [
        project_root / "datasets" / "emotion" / "eerola_film" / "mean_ratings_set2.csv",
        project_root / "Science" / "datasets" / "emotion" / "eerola_film" / "mean_ratings_set2.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def eerola_ratings_set1(project_root) -> Path:
    candidates = [
        project_root / "datasets" / "emotion" / "eerola_film" / "mean_ratings_set1.csv",
        project_root / "Science" / "datasets" / "emotion" / "eerola_film" / "mean_ratings_set1.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def engine_cache_set2(project_root) -> Path:
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film_set2" / "per_frame",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film_set2" / "per_frame",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def engine_cache_set1(project_root) -> Path:
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film" / "per_frame",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film" / "per_frame",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


@pytest.fixture(scope="session")
def pooled_csv_set2(project_root) -> Path:
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film_set2" / "pooled.csv",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion" / "eerola_film_set2" / "pooled.csv",
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
            "\nENGINE PIN DRIFT — refusing to run 24-h18-h25-eerola-film-gems.\n"
            f"  expected SHA-256 aggregate: {expected}\n"
            f"  actual                    : {actual}\n"
            f"  engine root               : {engine_root}\n",
            returncode=2,
        )
    yield
