"""L3.1 — Bit-identicality across N same-process runs.

Strongest determinism claim from the paper:

    "max-abs-diff = 0 on the full (B, T, 97) output"

This module pins the in-process axis: 100 back-to-back extracts on the
same audio produce bit-identical 97-D output. (Paper claim is "1000
runs"; we run 100 here for CI tractability and document that the
hardware-level pin can be tightened by changing the parameter.)
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


@pytest.fixture(scope="module")
def reference_features(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    return r3_extract(audio).features.cpu().numpy(), audio


@pytest.mark.parametrize("n_runs", [100])
def test_n_same_process_runs_bit_identical(r3_extract, reference_features, n_runs):
    ref, audio = reference_features
    max_abs_diff = 0.0
    for i in range(n_runs):
        out = r3_extract(audio).features.cpu().numpy()
        diff = float(np.max(np.abs(out - ref)))
        if diff > max_abs_diff:
            max_abs_diff = diff
            failing_run = i
    assert max_abs_diff == 0.0, (
        f"Non-determinism over {n_runs} runs: max_abs_diff = {max_abs_diff:.3e} "
        f"first observed at run {failing_run}"
    )


def test_three_stimulus_families_each_bit_identical(r3_extract):
    """Bit-identicality across multiple stimulus types — guards against any
    stimulus-conditional non-determinism."""
    for name, audio_fn in [
        ("white",   stim.stim_white),
        ("tone_a4", stim.stim_tone_a4),
        ("mix",     stim.stim_mix),
        ("silence", stim.stim_silence),
    ]:
        audio = audio_fn(duration_s=2.0)
        a = r3_extract(audio).features.cpu().numpy()
        b = r3_extract(audio).features.cpu().numpy()
        assert np.array_equal(a, b), f"non-deterministic on {name}"
