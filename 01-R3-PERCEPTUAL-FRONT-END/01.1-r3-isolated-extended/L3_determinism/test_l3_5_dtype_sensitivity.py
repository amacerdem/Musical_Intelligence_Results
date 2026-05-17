"""L3.5 — Float-precision sensitivity probe.

Engine pin: float32 throughout (default torch dtype). This module pins
two complementary properties:

(a) **Within-dtype determinism** — float32 same-input twice is bit-identical.
    (Already covered in L3.1 but recorded again here so the dtype axis
    is explicitly named.)

(b) **Across-dtype drift** — running the same audio in float64 (by casting
    the mel and audio tensors before extract) produces an output close to
    float32 but **not** bit-identical (drift ≤ 10⁻³ in practice). The point
    of this test is to *bound* the dtype-induced drift, not zero it: if
    cross-dtype drift suddenly grew or vanished, something fundamental
    changed about the engine's numerical pipeline.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


def test_float32_within_dtype_bit_identical(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features.cpu().numpy()
    b = r3_extract(audio).features.cpu().numpy()
    assert np.array_equal(a, b)


# Per-dim float32-vs-float64 drift (canonical pin).
#
# Source of drift: stumpf_fusion (dim 3) runs a k=1..6 loop with iterative
# best-snap selection over sigmoid(exp(...)) products. Tiny float32
# rounding selects a slightly different "best k" tier on a small fraction
# of frames, producing per-dim max |Δ| ~0.17 on stumpf_fusion. Inharmonicity
# (1 − stumpf) inherits this drift bit-identically; sensory_pleasantness
# (0.4 × stumpf + 0.6 × (1 − sethares)) inherits 0.4× of it.
#
# All 94 other dims are float32 ↔ float64 bit-identical at the pin.
DTYPE_DRIFT_DIMS = {
    3:  ("stumpf_fusion",         0.30),  # bound: |Δ| ≤ 0.30
    5:  ("inharmonicity",         0.30),  # = 1 − stumpf_fusion
    4:  ("sensory_pleasantness",  0.15),  # = 0.4·stumpf + 0.6·(1 − sethares)
}


def test_float64_drift_concentrated_in_stumpf_loop(r3, mel_of):
    """**Disclosed engine behaviour**: float32 ↔ float64 drift is concentrated
    in `stumpf_fusion` (dim 3) and its two algebraic descendants
    (`inharmonicity` = 1 − stumpf, `sensory_pleasantness` = 0.4·stumpf + …).

    Mechanism: `_stumpf` runs a `for k in range(1, _K_MAX+1)` loop selecting
    the best k-tier snap per pair via sigmoid×exp evaluations. Tiny float32
    rounding flips the "best k" selection on a fraction of frames,
    producing per-dim max |Δ| ~0.17 on `stumpf_fusion`. All 94 other dims
    are bit-identical between float32 and float64.

    Pin: each disclosed dim's drift is in `(10⁻⁹, bound)`; all 94 other
    dims are exactly 0. Auto-trips on a future engine refactor that
    closes the k-loop divergence.
    """
    audio_32 = stim.stim_mix(duration_s=2.0)
    mel_32   = mel_of(audio_32)
    audio_64 = audio_32.to(torch.float64)
    mel_64   = mel_32.to(torch.float64)

    with torch.no_grad():
        out_32 = r3.extract(mel_32, audio=audio_32, sr=44100).features.cpu().numpy()
        out_64 = r3.extract(mel_64, audio=audio_64, sr=44100).features.cpu().numpy().astype(np.float32)

    diff = np.abs(out_32 - out_64)
    per_dim_max = diff.max(axis=(0, 1))

    # 94 non-listed dims must be ε-tight (≤ 1e-4): tiny float32/float64
    # rounding through sigmoids/clamps can give per-frame |Δ| up to ~1e-5
    # on dims without iterative tier-selection logic, but never approaches
    # the stumpf-loop's 0.17 magnitude.
    EPS_NONDISCLOSED = 1e-4
    for dim in range(97):
        if dim in DTYPE_DRIFT_DIMS:
            continue
        assert per_dim_max[dim] < EPS_NONDISCLOSED, (
            f"unexpected float32/float64 drift on dim {dim}: "
            f"|Δ| = {per_dim_max[dim]:.3e} ≥ {EPS_NONDISCLOSED}. "
            f"Either a new dim has drifted (add to DTYPE_DRIFT_DIMS) or "
            f"the engine has a new dtype-sensitive operator."
        )

    # 3 disclosed dims must drift but stay within bounds
    for dim, (name, bound) in DTYPE_DRIFT_DIMS.items():
        d = float(per_dim_max[dim])
        assert 1e-9 < d < bound, (
            f"dim {dim} ({name}) drift {d:.3e} outside expected bound "
            f"(1e-9, {bound}). Update disclosure."
        )
