"""Engine SHA pin enforcement.

Every analysis script in C3-Cognitive-Signals/, C3-Region/, and C3-Neurochemicals/
calls assert_pinned_sha() as its first action. Any mismatch halts execution.

The pin is read from Musical_Intelligence_Outputs/_build/_engine_pin.json,
which is itself frozen and SHA-stamped at engine release.
"""
from __future__ import annotations

import json
from pathlib import Path

V_REPRO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_PIN_PATH = V_REPRO_ROOT / "Musical_Intelligence_Outputs" / "_build" / "_engine_pin.json"

EXPECTED_SHA = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
EXPECTED_COMMIT = "318eb2f529d7103e8b7d80b01228357fdc4e0217"


class EnginePinMismatch(RuntimeError):
    pass


def load_pin() -> dict:
    if not ENGINE_PIN_PATH.exists():
        raise EnginePinMismatch(f"Engine pin file missing: {ENGINE_PIN_PATH}")
    return json.loads(ENGINE_PIN_PATH.read_text())


def assert_pinned_sha(expected_sha: str = EXPECTED_SHA) -> dict:
    """Halt if engine SHA in the pin file differs from `expected_sha`.

    Returns the full pin dict on success; raises EnginePinMismatch on failure.
    """
    pin = load_pin()
    actual = pin.get("engine_sha_aggregate")
    if actual != expected_sha:
        raise EnginePinMismatch(
            f"Engine SHA mismatch.\n  expected: {expected_sha}\n  actual:   {actual}"
        )
    return pin


def assert_dataset_cache_sha(dataset_manifest_path: Path, expected_sha: str = EXPECTED_SHA) -> dict:
    """Halt if the dataset cache's manifest disagrees with the pinned engine SHA."""
    if not dataset_manifest_path.exists():
        raise EnginePinMismatch(f"Dataset manifest missing: {dataset_manifest_path}")
    manifest = json.loads(dataset_manifest_path.read_text())
    actual = manifest.get("engine_sha")
    if actual != expected_sha:
        raise EnginePinMismatch(
            f"Dataset cache SHA mismatch ({dataset_manifest_path}).\n"
            f"  expected: {expected_sha}\n  actual:   {actual}"
        )
    return manifest


if __name__ == "__main__":
    pin = assert_pinned_sha()
    print(f"OK engine SHA {pin['engine_sha_aggregate'][:16]}...")
    print(f"   commit {pin['engine_commit_sha'][:12]}")
    print(f"   cardinalities {pin['cardinalities']}")
