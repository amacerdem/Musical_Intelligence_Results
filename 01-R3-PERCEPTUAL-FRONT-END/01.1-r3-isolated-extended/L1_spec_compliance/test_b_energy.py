"""L1 — Spec compliance for Group B (Energy, dims 07–11).

Group B spec, per
``Musical_Intelligence/ear/r3/groups/b_energy/group.py``:

| idx | name           | range | source                                                          |
|-----|----------------|-------|-----------------------------------------------------------------|
| 07  | amplitude      | [0,1] | RMS of log-mel, sigmoid(8·(rms − 0.25))                         |
| 08  | velocity_A     | [0,1] | First derivative of RMS, sigmoid(8·diff1 / mean_rms)            |
| 09  | acceleration_A | [0,1] | Second derivative of RMS, sigmoid(12·diff2 / mean_rms)          |
| 10  | loudness       | [0,1] | Stevens 1957 power-law amp^0.3, sigmoid(6·(L − 0.5))            |
| 11  | onset_strength | [0,1] | HWR spectral flux per mel bin, sigmoid(12·(onset − 0.3))        |

Algebraic / structural identities:

    amplitude = sigmoid(8·(rms_log_mel − 0.25))      — single-stimulus reference
    diff1[t=0]  ≡ 0  (boundary frame)
    diff2[t=0,1] ≡ 0  (two boundary frames)
    onset[t=0] ≡ 0   (boundary frame)

Behavioural fingerprints documented in the spec:

    silence              → amplitude near sigmoid(-2) ≈ 0.12 (no energy)
    full-amplitude tone  → amplitude > silence amplitude
    impulse              → onset peak in first non-zero frames
    constant-amplitude tone → velocity_A ≈ 0.5 (zero diff in steady state)
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


# Engine slice for Group B — kept here so a registry drift breaks loudly.
GROUP_B_DIMS = (
    (7,  "amplitude"),
    (8,  "velocity_A"),
    (9,  "acceleration_A"),
    (10, "loudness"),
    (11, "onset_strength"),
)


@pytest.fixture(scope="module")
def stim_outputs(r3_extract):
    """Run engine on the eight L1 stimulus families."""
    families = {
        "white":   stim.stim_white(duration_s=3.0),
        "tone_a4": stim.stim_tone_a4(duration_s=3.0),
        "sweep":   stim.stim_sweep_segments(duration_s=3.0),
        "real":    stim.stim_mix(duration_s=3.0),
        "silence": stim.stim_silence(duration_s=3.0),
        "dc":      stim.stim_dc(duration_s=3.0),
        "impulse": stim.stim_impulse(duration_s=3.0),
        "mix":     stim.stim_mix(duration_s=3.0),
    }
    return {name: r3_extract(audio) for name, audio in families.items()}


def _column(out, dim_idx: int) -> np.ndarray:
    return out.features[0, :, dim_idx].cpu().numpy()


# ---------------------------------------------------------------------------
# Range, well-definedness, name agreement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_B_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_B_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}: non-finite"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_B_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_B_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_B_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_B_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Boundary-frame identities (engine-enforced via diff1/diff2/onset zero-init)
# ---------------------------------------------------------------------------

def test_velocity_first_frame_is_neutral(stim_outputs):
    """diff1[t=0] ≡ 0 ⇒ velocity[t=0] = sigmoid(0) = 0.5 ± numerical."""
    for name, out in stim_outputs.items():
        v = _column(out, 8)
        assert abs(v[0] - 0.5) < 1e-6, (
            f"velocity_A[0] should be sigmoid(0)=0.5 on {name}, got {v[0]:.6f}"
        )


def test_acceleration_first_two_frames_are_neutral(stim_outputs):
    """diff2[t=0,1] ≡ 0 ⇒ acceleration[t=0,1] = 0.5 ± numerical."""
    for name, out in stim_outputs.items():
        a = _column(out, 9)
        assert abs(a[0] - 0.5) < 1e-6, f"acceleration_A[0] != 0.5 on {name}: {a[0]}"
        assert abs(a[1] - 0.5) < 1e-6, f"acceleration_A[1] != 0.5 on {name}: {a[1]}"


def test_onset_first_frame_is_baseline(stim_outputs):
    """onset[t=0] ≡ 0 ⇒ output ≈ sigmoid(-3.6) ≈ 0.027."""
    expected_baseline = 1.0 / (1.0 + np.exp(3.6))  # ≈ 0.0266
    for name, out in stim_outputs.items():
        o = _column(out, 11)
        assert abs(o[0] - expected_baseline) < 1e-3, (
            f"onset[0] != baseline on {name}: {o[0]:.4f} vs {expected_baseline:.4f}"
        )


# ---------------------------------------------------------------------------
# Behavioural fingerprints
# ---------------------------------------------------------------------------

def test_silence_amplitude_baseline(stim_outputs):
    """Silence ⇒ rms_log_mel = 0 ⇒ amplitude = sigmoid(-2) ≈ 0.119."""
    expected = 1.0 / (1.0 + np.exp(2.0))  # ≈ 0.1192
    amp = _column(stim_outputs["silence"], 7)
    assert abs(np.median(amp) - expected) < 5e-3, (
        f"silence amplitude not at sigmoid(-2): median = {np.median(amp):.4f}"
    )


def test_silence_loudness_baseline(stim_outputs):
    """Silence ⇒ amp^0.3 = 0 ⇒ loudness = sigmoid(-3) ≈ 0.0474."""
    expected = 1.0 / (1.0 + np.exp(3.0))
    L = _column(stim_outputs["silence"], 10)
    assert abs(np.median(L) - expected) < 5e-3, (
        f"silence loudness not at sigmoid(-3): median = {np.median(L):.4f}"
    )


def test_amplitude_orders_silence_below_tone(stim_outputs):
    """Pure tone has higher amplitude than silence."""
    a_silence = _column(stim_outputs["silence"], 7).mean()
    a_tone    = _column(stim_outputs["tone_a4"], 7).mean()
    assert a_tone > a_silence, (
        f"amplitude ordering broken: tone={a_tone:.3f} !> silence={a_silence:.3f}"
    )


def test_loudness_orders_silence_below_tone(stim_outputs):
    """Pure tone is louder than silence."""
    L_silence = _column(stim_outputs["silence"], 10).mean()
    L_tone    = _column(stim_outputs["tone_a4"], 10).mean()
    assert L_tone > L_silence


def test_onset_responds_to_burst(r3_extract):
    """Tone burst onset (silence → tone transition) ⇒ onset spikes at burst start.

    Engine onset = HWR (rising-edge) of frame-to-frame mel difference.
    A Dirac at t=0 has only a falling edge after frame 0, so doesn't fire
    onset; we use a burst that starts mid-clip to create a real rising edge.
    """
    sr = stim.SR
    n_total = stim.DEFAULT_DURATION_S * sr
    # silence half + tone half (rising edge in the middle)
    silence = stim.stim_silence(stim.DEFAULT_DURATION_S / 2)
    tone    = stim.stim_tone_a4(stim.DEFAULT_DURATION_S / 2)
    audio = torch.cat([silence, tone], dim=-1)
    o = r3_extract(audio).features[0, :, 11].cpu().numpy()
    # burst starts at frame ≈ T/2; check max in surrounding window beats baseline.
    mid_start = len(o) // 2 - 5
    mid_end   = len(o) // 2 + 25
    burst_max  = o[mid_start:mid_end].max()
    silence_mean = o[10:mid_start].mean()
    # Direction-of-effect: burst peak must be at least 2× the silence baseline.
    assert burst_max > 2.0 * silence_mean, (
        f"onset failed to spike on tone-burst start: "
        f"burst_max={burst_max:.3f}, silence_mean={silence_mean:.3f}"
    )


def test_velocity_zero_in_steady_state(r3_extract):
    """Constant-amplitude tone ⇒ steady-state diff1 ≈ 0 ⇒ velocity ≈ 0.5."""
    audio = stim.stim_tone_a4(duration_s=4.0)
    v = r3_extract(audio).features[0, :, 8].cpu().numpy()
    # Use middle of the clip to dodge boundary effects
    steady = v[100:-100]
    assert abs(np.median(steady) - 0.5) < 0.02, (
        f"velocity_A on steady tone not at 0.5: median = {np.median(steady):.4f}"
    )


def test_acceleration_zero_in_steady_state(r3_extract):
    """Constant-amplitude tone ⇒ steady-state diff2 ≈ 0 ⇒ acceleration ≈ 0.5."""
    audio = stim.stim_tone_a4(duration_s=4.0)
    a = r3_extract(audio).features[0, :, 9].cpu().numpy()
    steady = a[100:-100]
    assert abs(np.median(steady) - 0.5) < 0.02


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_b_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 7:12].cpu().numpy()
    b = r3_extract(audio).features[0, :, 7:12].cpu().numpy()
    assert np.array_equal(a, b)
