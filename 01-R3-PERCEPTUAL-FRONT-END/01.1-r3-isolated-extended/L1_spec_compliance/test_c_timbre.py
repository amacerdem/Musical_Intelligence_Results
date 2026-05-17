"""L1 — Spec compliance for Group C (Timbre, dims 12–20).

Spec, per ``Musical_Intelligence/ear/r3/groups/c_timbre/group.py``:

| idx | name                        | range | formula                                                       |
|-----|-----------------------------|-------|---------------------------------------------------------------|
| 12  | warmth                      | [0,1] | sigmoid(6·(low_lt_1kHz_energy_ratio − 0.7))                  |
| 13  | sharpness                   | [0,1] | sigmoid(6·(zwicker_high_emphasis − 0.3))                     |
| 14  | tonalness                   | [0,1] | mel_peak / mel_sum                                            |
| 15  | clarity                     | [0,1] | (mel·bins_axis).sum / mel.sum / N — normalised mel centroid   |
| 16  | spectral_smoothness         | [0,1] | 1 − |Δmel|.mean() / frame_energy                              |
| 17  | spectral_autocorrelation    | [0,1] | lag-1 autocorrelation of mel spectrum                         |
| 18  | tristimulus1                | [0,1] | mel[:N/3].sum / mel.sum                                       |
| 19  | tristimulus2                | [0,1] | mel[N/3:2N/3].sum / mel.sum                                   |
| 20  | tristimulus3                | [0,1] | mel[2N/3:].sum / mel.sum                                      |

Algebraic identity (engine partition):

    tristimulus1 + tristimulus2 + tristimulus3 ≈ 1 (with mel.sum > eps)

Behavioural fingerprints documented in the spec:

    bright tone (high freq) → sharpness > warmth
    dark tone (low freq)    → warmth   > sharpness
    pure tone               → tonalness high (single peak / sum)
    white noise             → tonalness low  (broad spectrum)
    constant spectrum       → spectral_smoothness high (no per-frame jaggedness)
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


GROUP_C_DIMS = (
    (12, "warmth"),
    (13, "sharpness"),
    (14, "tonalness"),
    (15, "clarity"),
    (16, "spectral_smoothness"),
    (17, "spectral_autocorrelation"),
    (18, "tristimulus1"),
    (19, "tristimulus2"),
    (20, "tristimulus3"),
)


@pytest.fixture(scope="module")
def stim_outputs(r3_extract):
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

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_C_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_C_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_C_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_C_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_C_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_C_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Algebraic identity: tristimulus partition
# ---------------------------------------------------------------------------

def test_tristimulus_partition(stim_outputs):
    """tristimulus1 + tristimulus2 + tristimulus3 ≈ 1 on every frame & stimulus.

    Engine clamps each component to [0,1] (line 134), but the partition equality
    holds before clamp. We verify the post-clamp sum lies within [0.95, 1.05]
    on stimuli with non-trivial spectral content. Silence- and impulse-like
    inputs are excluded because total_mel → eps and the partition degenerates
    by definition (each tristimulus → 0 / eps = 0). The engine documents this
    edge case via the .clamp(min=eps) guard on line 145.
    """
    NON_DEGENERATE = ("white", "tone_a4", "sweep", "real", "dc", "mix")
    for name in NON_DEGENERATE:
        out = stim_outputs[name]
        t1 = _column(out, 18)
        t2 = _column(out, 19)
        t3 = _column(out, 20)
        s = t1 + t2 + t3
        ok = (s > 0.95) & (s < 1.05)
        # Allow first ~5 frames as boundary (mel padding effects)
        steady_ok = ok[5:].mean() > 0.95
        assert steady_ok, (
            f"tristimulus partition broken on {name}: "
            f"sum range = [{s[5:].min():.3f}, {s[5:].max():.3f}], "
            f"frames in [0.95,1.05] = {ok[5:].mean():.3f}"
        )


# ---------------------------------------------------------------------------
# Behavioural fingerprints
# ---------------------------------------------------------------------------

def test_bright_tone_higher_sharpness_than_warm(r3_extract):
    """A 4 kHz tone is sharper / less warm than a 200 Hz tone."""
    bright = stim.stim_tone(4000.0, duration_s=3.0)
    warm   = stim.stim_tone(200.0,  duration_s=3.0)
    out_b = r3_extract(bright)
    out_w = r3_extract(warm)
    steady = slice(20, -5)
    s_b = out_b.features[0, steady, 13].mean().item()
    s_w = out_w.features[0, steady, 13].mean().item()
    w_b = out_b.features[0, steady, 12].mean().item()
    w_w = out_w.features[0, steady, 12].mean().item()
    assert s_b > s_w, f"sharpness ordering broken: 4kHz={s_b:.3f}, 200Hz={s_w:.3f}"
    assert w_w > w_b, f"warmth ordering broken: 4kHz={w_b:.3f}, 200Hz={w_w:.3f}"


def test_pure_tone_more_tonal_than_white_noise(stim_outputs):
    tonal_pure = _column(stim_outputs["tone_a4"], 14)
    tonal_white = _column(stim_outputs["white"], 14)
    assert np.median(tonal_pure[20:]) > np.median(tonal_white[20:]), (
        "tonalness should be higher on a single-peak tone than on broad white noise"
    )


def test_silence_smoothness_at_clamp_or_baseline(stim_outputs):
    """Silence: spec_diff ≈ 0 → smoothness ≈ 1; or division gates clamp at 0.

    Engine: smoothness = (1 − clamp(spec_diff/frame_energy, 0, 1)).clamp(0,1).
    On exact silence, both numerator and denominator → eps, so the ratio
    can be 0/eps = 0, giving smoothness = 1. This is the documented behavior.
    """
    s = _column(stim_outputs["silence"], 16)
    assert s.mean() > 0.95, f"smoothness on silence too low: mean = {s.mean():.4f}"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_c_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 12:21].cpu().numpy()
    b = r3_extract(audio).features[0, :, 12:21].cpu().numpy()
    assert np.array_equal(a, b)
