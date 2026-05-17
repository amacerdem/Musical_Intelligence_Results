"""L3.4 — Cross-thread-count determinism.

Sweeping `torch.set_num_threads({1, 2, 4, 8})` between runs leaves R³
output bit-identical — pinning that R³'s `torch.stft / matmul / conv1d`
calls do not introduce thread-order non-determinism on the canonical pin.

Note: hardware-level `MKL` / `OMP` non-determinism is real for some
operations, but R³'s current operator set (mel @ matrix, FFT, sum,
reductions to single-frame outputs) is determined by torchaudio +
PyTorch's deterministic kernels for these shapes. This test pins that
property.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


@pytest.mark.parametrize("n_threads", [1, 2, 4, 8])
def test_thread_count_does_not_change_output(r3_extract, n_threads):
    audio = stim.stim_mix(duration_s=2.0)
    saved = torch.get_num_threads()
    try:
        torch.set_num_threads(1)
        baseline = r3_extract(audio).features.cpu().numpy()
        torch.set_num_threads(n_threads)
        other = r3_extract(audio).features.cpu().numpy()
    finally:
        torch.set_num_threads(saved)
    assert np.array_equal(baseline, other), (
        f"thread-count {n_threads} changed R³ output. "
        f"max |Δ| = {np.max(np.abs(baseline - other)):.3e}"
    )
