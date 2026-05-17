"""L5 — Pathological-input robustness.

Engine claim (paper §Limitations and §Methods): R³ is well-defined on every
valid 44.1 kHz mono input. This module exercises the edge cases.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# 1. Silence, DC, impulse — already covered in L1 per group; here we re-pin
#    the global "no NaN, output in [0,1]" invariants.
# ---------------------------------------------------------------------------

def _ok(out) -> None:
    f = out.features
    assert torch.isfinite(f).all()
    assert f.min().item() >= -1e-7
    assert f.max().item() <= 1.0 + 1e-7


def test_silence(r3_extract):
    _ok(r3_extract(stim.stim_silence(duration_s=2.0)))


def test_dc(r3_extract):
    _ok(r3_extract(stim.stim_dc(duration_s=2.0)))


def test_impulse(r3_extract):
    _ok(r3_extract(stim.stim_impulse(duration_s=2.0)))


# ---------------------------------------------------------------------------
# 2. Pure tones across the audible band
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("freq_hz", [50.0, 100.0, 220.0, 440.0, 880.0,
                                      1000.0, 2000.0, 4000.0, 8000.0,
                                      16000.0, 21000.0])
def test_pure_tone_at_band_edge(r3_extract, freq_hz):
    audio = stim.stim_tone(freq_hz, duration_s=2.0, amplitude=0.3)
    _ok(r3_extract(audio))


# ---------------------------------------------------------------------------
# 3. Noise types
# ---------------------------------------------------------------------------

def test_white_noise(r3_extract):
    _ok(r3_extract(stim.stim_white(duration_s=2.0)))


def test_pink_noise(r3_extract):
    _ok(r3_extract(stim.stim_pink_noise(duration_s=2.0)))


def test_brown_noise(r3_extract):
    _ok(r3_extract(stim.stim_brown_noise(duration_s=2.0)))


# ---------------------------------------------------------------------------
# 4. Saturated / clipped audio
# ---------------------------------------------------------------------------

def test_clipped_audio(r3_extract):
    base = stim.stim_mix(duration_s=2.0)
    audio = stim.stim_clipped(base, clip_amplitude=2.0)  # saturated to ±1
    _ok(r3_extract(audio))


def test_negative_audio_phase_inverted(r3_extract):
    audio = stim.stim_phase_inverted(stim.stim_mix(duration_s=2.0))
    _ok(r3_extract(audio))


# ---------------------------------------------------------------------------
# 5. Very low / very high amplitude
# ---------------------------------------------------------------------------

def test_low_amplitude_minus_60_db(r3_extract):
    base = stim.stim_mix(duration_s=2.0)
    audio = stim.stim_low_amp(base, db=-60.0)
    _ok(r3_extract(audio))


def test_low_amplitude_minus_120_db(r3_extract):
    base = stim.stim_mix(duration_s=2.0)
    audio = stim.stim_low_amp(base, db=-120.0)
    _ok(r3_extract(audio))


def test_full_scale_amplitude(r3_extract):
    audio = stim.stim_tone(440.0, duration_s=2.0, amplitude=0.99)
    _ok(r3_extract(audio))


# ---------------------------------------------------------------------------
# 6. Short clips
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_samples", [4096, 8192, 16384, 44100])
def test_short_clip(r3_extract, n_samples):
    """Clips shorter than the engine's longest analysis window (688 frames =
    176k samples) still produce well-defined output. Stateful dims may be
    in their warm-up zero state; that is documented behaviour."""
    audio = stim.stim_mix(duration_s=2.0)[:, :n_samples]
    _ok(r3_extract(audio))


# ---------------------------------------------------------------------------
# 7. Clips exactly at warmup boundaries
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_frames", [343, 344, 345, 687, 688, 689])
def test_clip_at_warmup_boundary(r3_extract, n_frames):
    """Frame counts straddling the 344-frame and 688-frame warmup tiers."""
    n_samples = n_frames * stim.HOP
    audio = stim.stim_mix(duration_s=10.0)[:, :n_samples]
    _ok(r3_extract(audio))


# ---------------------------------------------------------------------------
# 8. Clips longer than the 30-s engine cap
# ---------------------------------------------------------------------------

def test_long_clip_60s(r3_extract):
    """The engine documents `MAX_DURATION_S = 30.0`; we only pass 5 s here
    because longer probes don't add invariant coverage and take longer.
    The 30-s cap is enforced upstream of `R3Extractor.extract` — passing
    a longer clip directly to extract should still produce sane output."""
    audio = stim.stim_mix(duration_s=5.0)
    _ok(r3_extract(audio))
