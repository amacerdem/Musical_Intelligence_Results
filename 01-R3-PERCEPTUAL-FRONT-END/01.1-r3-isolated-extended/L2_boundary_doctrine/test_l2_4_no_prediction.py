"""L2.4 — No prediction (Rule 4) — truncation invariance.

Rule 4 (paper §Boundary doctrine):

    The feature does not estimate future states, model temporal
    contingencies, or compute information-theoretic quantities that
    require a reference distribution accumulated over time.

The strong, testable form of Rule 4:

    R³'s output at frame t depends only on past and ±2-neighbour frames,
    not on **any future frames** beyond the documented ±2 window.

Test
----
For a long mel input, truncate at frame ``T_trunc ∈ {344, 600, 1000, 2000}``
and compare R³ output at frames ``t < T_trunc − 2`` to the same frames in
the full-length output. They must be bit-identical: any drift indicates
a future-frame leak.

Stateful (Tier 1/2) dims are excluded from the strict identity — their
warmup-zero / warmup-ramp policy interacts with truncation in a way
that's documented (see L8). Tier-0 dims must be bit-identical.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import DIM_NAMES

WARMUP_ALL = (
    list(range(83, 91))
    + [41, 42, 43, 45, 46, 47, 48, 49, 50]
    + [44]
)
# dim 92 (fluctuation_strength) is set to modulation_4Hz (dim 86, Tier-1 zero)
# by aliasing; it inherits Tier-1 truncation behaviour even though it's not in
# the warmup registry. Disclosed in L1's K_modulation.md and excluded here.
ALIASED_TO_WARMUP = [92]
# velocity_A (8) and acceleration_A (9) normalise their per-frame derivatives
# by the **clip-level mean amplitude** (`b_energy/group.py:32, 39`). This is
# a deliberate "scale-invariance" trade-off: it makes velocity / acceleration
# magnitudes comparable across clips, at the cost of formal Rule-1 frame
# locality (velocity_A[t] depends on amp_raw across all frames via amp_mean).
# Truncation moves amp_mean and produces ε-deltas of ~5e-6. Disclosed in the
# L2_summary report; verified separately in `test_velocity_accel_clip_norm_disclosed`.
CLIP_LEVEL_NORM = [8, 9]
TIER0_STRICT = sorted(
    set(range(97)) - set(WARMUP_ALL) - set(ALIASED_TO_WARMUP) - set(CLIP_LEVEL_NORM)
)


@pytest.fixture(scope="module")
def long_mel_and_audio(stim):
    """A 6-s mix clip — long enough to truncate well inside Tier-2 warmup."""
    audio = stim.stim_mix(duration_s=6.0)
    mel = stim.to_mel(audio)
    return mel, audio


@pytest.mark.parametrize("T_trunc", [344, 600, 1000])
def test_truncation_does_not_change_earlier_frames(r3, long_mel_and_audio, T_trunc):
    """R³ output at frames t < T_trunc − 2 must be bit-identical between
    the full-length and the truncated runs (Tier-0 dims)."""
    mel, audio = long_mel_and_audio
    if mel.shape[-1] <= T_trunc + 5:
        pytest.skip(f"mel too short ({mel.shape[-1]}) for T_trunc={T_trunc}")

    # Full-length run
    with torch.no_grad():
        full_out = r3.extract(mel, audio=audio, sr=44100)

    # Truncated run (truncate both mel and audio consistently)
    audio_trunc = audio[:, : T_trunc * 256]
    mel_trunc   = mel[:, :, :T_trunc]
    with torch.no_grad():
        trunc_out = r3.extract(mel_trunc, audio=audio_trunc, sr=44100)

    # Compare frames 0..T_trunc - safe_skip.
    # safe_skip accounts for the STFT center=True future-reach:
    #   Group A's STFT uses n_fft=4096 ⇒ ±2048 audio samples ⇒ ±8 mel frames.
    # We skip 12 frames at the end to be strictly outside that reach. Engine
    # uses torchaudio's center=True STFTs, so this larger reach is inherited
    # from the audio front-end, not from R³'s formula tower.
    safe_T = T_trunc - 12
    a = full_out.features[0, :safe_T, :].cpu().numpy()
    b = trunc_out.features[0, :safe_T, :].cpu().numpy()

    failures = []
    for dim in TIER0_STRICT:
        if not np.array_equal(a[:, dim], b[:, dim]):
            max_delta = float(np.max(np.abs(a[:, dim] - b[:, dim])))
            failures.append((dim, DIM_NAMES[dim], max_delta))
    assert not failures, (
        f"Truncation at T={T_trunc}: {len(failures)}/{len(TIER0_STRICT)} "
        f"strictly-Rule-1 dims drift between full and truncated runs. "
        f"Top 5 deltas: {sorted(failures, key=lambda x: -x[2])[:5]}"
    )


def test_velocity_accel_clip_norm_disclosed(r3, long_mel_and_audio):
    """**Disclosed engine behaviour**: velocity_A (8) and acceleration_A (9)
    normalise by clip-level mean amplitude, breaking strict Rule-1 frame
    locality. Truncation produces ε-deltas; we pin them as ≤ 1e-4 here.

    Source: ``Musical_Intelligence/ear/r3/groups/b_energy/group.py:32,39``.
    A future engine change to a per-window mean (or to no normalisation)
    would either tighten the bound to 0 or change its signature; in either
    case, this test trips and forces the disclosure to be updated.
    """
    mel, audio = long_mel_and_audio
    T_trunc = 1000

    with torch.no_grad():
        full = r3.extract(mel, audio=audio, sr=44100)
        trunc = r3.extract(mel[:, :, :T_trunc], audio=audio[:, :T_trunc * 256], sr=44100)

    safe_T = T_trunc - 12
    a = full.features[0, :safe_T, :].cpu().numpy()
    b = trunc.features[0, :safe_T, :].cpu().numpy()

    for dim in CLIP_LEVEL_NORM:
        delta = float(np.max(np.abs(a[:, dim] - b[:, dim])))
        # Pin: nonzero (clip-norm leaks) but ≤ 1e-4 (effect is tiny in practice).
        assert 0.0 < delta < 1e-4, (
            f"clip-level-norm disclosure has changed: dim {dim} ({DIM_NAMES[dim]}) "
            f"delta={delta:.3e}; expected (0, 1e-4). Update the disclosure if the "
            f"engine has been refactored to per-window or no normalisation."
        )


def test_short_clip_at_min_stft_window_runs(r3, stim):
    """Minimum-viable clip (n_fft=4096 samples = 16 mel frames) runs to
    completion. Shorter clips violate the audio-path STFT window and are
    not guaranteed by the engine — paper §Limitations boundary case 1."""
    n_min = 4096
    audio = stim.stim_mix(duration_s=2.0)[:, :n_min]
    mel = stim.to_mel(audio)
    with torch.no_grad():
        out = r3.extract(mel, audio=audio, sr=44100)
    assert out.features.shape[1] >= 1
    assert torch.isfinite(out.features).all()
