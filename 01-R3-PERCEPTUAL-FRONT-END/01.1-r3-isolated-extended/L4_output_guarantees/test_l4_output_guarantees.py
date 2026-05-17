"""L4 — Output guarantees: shape, range, no-NaN/Inf, dataclass, registry.

Paper claim: ``R3Output`` is a frozen dataclass with
``features: (B, T, 97)``, every dim in `[0, 1]`, no NaN / Inf on any
valid input, and `feature_names` is a frozen 97-tuple matching the
canonical registry.

This module hammers the engine on 1,000 random clips of varied length
and content to provide a probabilistic guarantee of these invariants.
"""
from __future__ import annotations

import dataclasses
import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import DIM_NAMES


# ---------------------------------------------------------------------------
# Shape / dtype / dataclass guarantees
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("duration_s", [0.1, 0.5, 1.0, 5.0, 15.0])
def test_output_shape_BT97(r3_extract, duration_s):
    """Output shape is (1, T, 97) where T = ⌈sr·duration / hop⌉ ± a few."""
    audio = stim.stim_mix(duration_s=duration_s)
    out = r3_extract(audio)
    assert out.features.shape[0] == 1
    assert out.features.shape[2] == 97
    expected_T = int(round(duration_s * stim.SR / stim.HOP))
    actual_T = out.features.shape[1]
    assert abs(actual_T - expected_T) <= 3, (
        f"T drift: expected ≈{expected_T}, got {actual_T}"
    )


def test_output_dtype_is_float32(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    out = r3_extract(audio)
    assert out.features.dtype == torch.float32


def test_r3output_is_frozen_dataclass(r3_extract):
    """`R3Output` is `@dataclass(frozen=True)` — assignment raises."""
    audio = stim.stim_mix(duration_s=1.0)
    out = r3_extract(audio)
    assert dataclasses.is_dataclass(type(out))
    # Frozen ⇒ assignment raises FrozenInstanceError
    with pytest.raises(dataclasses.FrozenInstanceError):
        out.features = torch.zeros_like(out.features)


def test_feature_names_is_frozen_97_tuple(r3_extract):
    audio = stim.stim_mix(duration_s=1.0)
    out = r3_extract(audio)
    assert isinstance(out.feature_names, tuple)
    assert len(out.feature_names) == 97
    assert tuple(out.feature_names) == DIM_NAMES


# ---------------------------------------------------------------------------
# Range, NaN/Inf, hammer probe (1000 random clips)
# ---------------------------------------------------------------------------

def _random_clip_factory(seed: int):
    """Build one of several stimulus types deterministically from *seed*."""
    rng = np.random.default_rng(seed)
    family = int(rng.integers(0, 5))
    duration = float(rng.uniform(0.5, 4.0))
    if family == 0:
        return stim.stim_white(duration_s=duration, seed=seed)
    if family == 1:
        f = float(rng.uniform(80.0, 8000.0))
        amp = float(rng.uniform(0.05, 0.7))
        return stim.stim_tone(f, duration_s=duration, amplitude=amp)
    if family == 2:
        f = float(rng.uniform(80.0, 4000.0))
        m = float(rng.uniform(2.0, 16.0))
        return stim.stim_am_tone(carrier_hz=f, mod_hz=m, duration_s=duration,
                                  mod_depth=float(rng.uniform(0.2, 0.9)))
    if family == 3:
        return stim.stim_pink_noise(duration_s=duration, seed=seed)
    if family == 4:
        return stim.stim_mix(duration_s=duration,
                              freq_hz=float(rng.uniform(110.0, 1760.0)),
                              tone_amp=float(rng.uniform(0.1, 0.5)))
    raise RuntimeError("unreachable")


def test_range_no_nan_no_inf_on_1000_random_clips(r3_extract):
    """1,000 randomly-parameterised stimuli — every dim ∈ [0, 1], no NaN, no Inf."""
    failures = []
    for seed in range(1000):
        audio = _random_clip_factory(seed)
        out = r3_extract(audio)
        f = out.features
        if not torch.isfinite(f).all():
            failures.append(("non-finite", seed))
            continue
        if f.min().item() < -1e-7:
            failures.append(("min<0", seed, f.min().item()))
        if f.max().item() > 1.0 + 1e-7:
            failures.append(("max>1", seed, f.max().item()))
        if failures:
            break  # don't waste time after first failure; report it loud
    assert not failures, f"output guarantees broken: {failures[:5]}"


def test_chroma_partition_holds_on_random_audio(r3_extract):
    """The 12-bin chroma partition sums to ~1 across many random clips
    (skip silent or degenerate cases)."""
    failures = []
    for seed in range(200):
        audio = _random_clip_factory(seed)
        # skip clips with near-zero RMS
        if float(audio.pow(2).mean().sqrt()) < 1e-3:
            continue
        out = r3_extract(audio)
        chroma_sum = out.features[0, 30:-5, 25:37].sum(-1).cpu().numpy()
        # Allow a fraction of degenerate frames
        ok_frac = ((chroma_sum > 0.95) & (chroma_sum < 1.05)).mean()
        if ok_frac < 0.9:
            failures.append((seed, ok_frac, chroma_sum.min(), chroma_sum.max()))
    assert not failures, (
        f"chroma partition broken on random audio: first 5 = {failures[:5]}"
    )
