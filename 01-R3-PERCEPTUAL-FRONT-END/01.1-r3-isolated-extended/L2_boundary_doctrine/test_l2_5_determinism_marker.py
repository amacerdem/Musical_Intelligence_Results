"""L2.5 — Determinism (Rule 5) marker.

Rule 5 (paper §Boundary doctrine):

    R³ uses no learned parameters or trained weights. Every computation is
    a closed-form function of the spectrogram.

L2.5 plants a single sanity-grade fingerprint: same audio, repeated three
times in the same process, must produce bit-identical R³ output. Full
cross-axis determinism (cross-process, cross-thread, cross-OS, cross-HW,
cross-torch-version) is L3's job.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


def test_three_runs_same_audio_bit_identical(r3_extract):
    """Three back-to-back extracts on the same audio produce bit-identical
    97-D output. If this fails, Rule 5 is violated and L3's broader probes
    will fail more loudly."""
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features.cpu().numpy()
    b = r3_extract(audio).features.cpu().numpy()
    c = r3_extract(audio).features.cpu().numpy()
    assert np.array_equal(a, b)
    assert np.array_equal(b, c)
