"""Bit-identical determinism + layer-coverage tests for the engine runner.

Note on imports: `V-Reproduction` contains a hyphen and is therefore NOT a
valid Python identifier; we cannot use `from V_Reproduction._infra... import`
without a package shim. We instead put `_infra/` itself on sys.path and
import `engine.runner`. This is the simplest pattern that does not require
restructuring the V-Reproduction directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from engine.runner import REQUIRED_LAYERS, run_engine  # noqa: E402

# Stimulus corpus: Science/V1/stimuli/micro_beliefs is canonical (1,581 WAVs across 19 categories incl. F1-F9)
_REPO_ROOT = _INFRA.parent.parent.parent
_TEST_AUDIO_CANDIDATES = (
    _INFRA.parent.parent / "V1" / "stimuli" / "micro_beliefs",  # Science/V1/stimuli/micro_beliefs
)


@pytest.fixture(scope="module")
def short_clip() -> Path:
    """A short test stimulus (<= 5s) for fast determinism check.

    Picks the smallest WAV by file size to keep R3 → H3 → C3 + beliefs
    runtime per call to a few seconds.
    """
    for root in _TEST_AUDIO_CANDIDATES:
        if root.exists():
            wavs = list(root.glob("**/*.wav"))
            if wavs:
                wavs.sort(key=lambda p: (p.stat().st_size, p.name))
                return wavs[0]
    pytest.skip(
        f"No micro_beliefs WAVs found at any of: "
        f"{[str(p) for p in _TEST_AUDIO_CANDIDATES]}"
    )


def test_engine_returns_required_layers(short_clip):
    """All six layers must be present when REQUIRED_LAYERS is requested."""
    out = run_engine(short_clip)
    for layer in REQUIRED_LAYERS:
        assert layer in out, f"Missing layer {layer}; available: {list(out)}"


def test_engine_r3_is_array_with_finite_values(short_clip):
    """R³ output is a finite, non-empty (T, 97) array."""
    out = run_engine(short_clip, return_layers=("r3",))
    r3 = out["r3"]
    arr = np.asarray(r3)
    assert arr.size > 0, "R³ array is empty"
    assert arr.shape[-1] == 97, f"R³ last dim should be 97, got {arr.shape[-1]}"
    assert np.all(np.isfinite(arr)), "R³ contains non-finite values"


def test_engine_bit_identical_3_runs(short_clip):
    """Engine MUST produce bit-identical R³ across 3 consecutive calls.

    This is stronger than the paper's |Δρ| ≤ 8.8×10⁻⁵ engine-determinism
    claim. If this ever fails, do NOT touch the engine — diagnose
    BLAS/threading first (the runner already pins thread counts to 1).
    """
    runs = [run_engine(short_clip, return_layers=("r3",)) for _ in range(3)]
    a, b, c = (np.asarray(r["r3"]) for r in runs)
    np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(a, c)


def test_engine_bit_identical_full_layers(short_clip):
    """Bit-identical determinism extended to C3, beliefs, RAM, neuro layers.

    R3 is most deterministic-by-construction; the harder test is whether the
    Bayesian belief cycle and execution graph also reproduce exactly.
    """
    runs = [run_engine(short_clip, return_layers=("c3", "ram", "neuro", "beliefs")) for _ in range(2)]
    out_a, out_b = runs

    # RAM, neuro: arrays
    np.testing.assert_array_equal(np.asarray(out_a["ram"]), np.asarray(out_b["ram"]))
    np.testing.assert_array_equal(np.asarray(out_a["neuro"]), np.asarray(out_b["neuro"]))

    # c3 and beliefs: dict-of-arrays; iterate keys and assert each
    for key in out_a["c3"]:
        if key not in out_b["c3"]:
            continue
        np.testing.assert_array_equal(np.asarray(out_a["c3"][key]), np.asarray(out_b["c3"][key]))
    for key in out_a["beliefs"]:
        if key not in out_b["beliefs"]:
            continue
        # belief value is a dict[trace_name -> ndarray]; compare per-trace
        traces_a = out_a["beliefs"][key]
        traces_b = out_b["beliefs"][key]
        for trace_name in traces_a:
            if trace_name not in traces_b:
                continue
            np.testing.assert_array_equal(
                np.asarray(traces_a[trace_name]),
                np.asarray(traces_b[trace_name]),
            )
