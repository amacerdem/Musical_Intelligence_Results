"""Pytest fixtures for 21-c3-chill-prediction.

Fixtures
--------
* ``project_root``    — repo root (auto-discovered upward from this file)
* ``engine_pin``      — parsed _infra/manifests/engine_pin.json dict
* ``chillsdb_root``   — ChillsDB v1 audio root path
* ``engine_outputs``  — Musical_Intelligence_Outputs/emotion/<dataset>/ helper
* ``paper_baseline``  — parsed _infra/paper_time_baseline.json (Tier-1 frozen numbers)

Engine-pin integrity check
--------------------------
Session-start fixture (``_pin_integrity``) computes SHA-256 aggregate of all .py
files under Musical_Intelligence/ and asserts it matches the pin manifest. If
the engine drifts, every test halts at session-start.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------

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
    raise RuntimeError(f"Could not locate Musical_Intelligence/ear/r3 from {_THIS}")
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_SUITE_ROOT = _THIS.parent
if str(_SUITE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SUITE_ROOT))
_INFRA = _SUITE_ROOT / "_infra"


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

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
def chillsdb_root(project_root) -> Path:
    """ChillsDB v1 audio root. Tries multiple canonical locations.

    Local repo layout has engine duplicated at both project root AND Science/;
    so project_root may resolve to either. Try both candidates.
    May not exist on a fresh clone — L2 verifies.
    """
    candidates = [
        project_root / "datasets" / "emotion" / "chillsdb",
        project_root / "Science" / "datasets" / "emotion" / "chillsdb",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]  # fall through to canonical path; L2 will fail informatively


@pytest.fixture(scope="session")
def engine_outputs_root(project_root) -> Path:
    candidates = [
        project_root / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion",
        project_root / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "emotion",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[-1]


# ---------------------------------------------------------------------------
# Pin-integrity gate
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _pin_integrity(engine_pin, project_root):
    """Halt the session if engine drifts from the pinned SHA aggregate."""
    from _infra.sha_utils import aggregate_engine_sha
    engine_root = project_root / "Musical_Intelligence"
    actual = aggregate_engine_sha(engine_root)
    expected = engine_pin["content_aggregate_sha256"]
    if actual != expected:
        pytest.exit(
            "\nENGINE PIN DRIFT — refusing to run 21-c3-chill-prediction.\n"
            f"  expected SHA-256 aggregate: {expected}\n"
            f"  actual                    : {actual}\n"
            f"  engine root               : {engine_root}\n"
            "Reproduce the canonical pin or update _infra/manifests/engine_pin.json.\n",
            returncode=2,
        )
    yield
