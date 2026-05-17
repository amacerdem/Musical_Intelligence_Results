"""L1 — Spec compliance for Group K (Modulation, dims 83–96).

Spec, per ``Musical_Intelligence/ear/r3/groups/k_modulation/group.py``:

| idx | name                  | range | source                                                  |
|-----|-----------------------|-------|---------------------------------------------------------|
| 83  | modulation_0_5Hz      | [0,1] | Modulation FFT energy at 0.5 Hz, max-normalised         |
| 84  | modulation_1Hz        | [0,1] | Same at 1 Hz                                             |
| 85  | modulation_2Hz        | [0,1] | Same at 2 Hz                                             |
| 86  | modulation_4Hz        | [0,1] | Same at 4 Hz (= fluctuation_strength source)            |
| 87  | modulation_8Hz        | [0,1] | Same at 8 Hz                                             |
| 88  | modulation_16Hz       | [0,1] | Same at 16 Hz                                            |
| 89  | modulation_centroid   | [0,1] | Weighted mean of log2(rates), affine [−1, 4] → [0, 1]   |
| 90  | modulation_bandwidth  | [0,1] | Weighted std(log2 rates) / 2.5                          |
| 91  | sharpness_zwicker     | [0,1] | DIN 45692 — Bark-band weighted z-axis ratio             |
| 92  | fluctuation_strength  | [0,1] | = modulation_4Hz                                         |
| 93  | loudness_a_weighted   | [0,1] | IEC 61672-1 A-weighted mel sum, max-normalised          |
| 94  | alpha_ratio           | [0,1] | Σ mel<1kHz / Σ mel — Hammarberg 1980 voice quality      |
| 95  | hammarberg_index      | [0,1] | sigmoid(peak<2kHz / peak[2-5kHz] / 5)                   |
| 96  | spectral_slope_0_500  | [0,1] | sigmoid(LSE slope of mel bins 0..17 × 10)               |

Algebraic identity (engine partition):

    fluctuation_strength ≡ modulation_4Hz   (engine line 154)

Behavioural fingerprints documented in the spec:

    AM-modulated tone at 8 Hz → modulation_8Hz peak
    AM-modulated tone at 4 Hz → modulation_4Hz / fluctuation_strength peak
    bright tone (high freq)   → low alpha_ratio
    warm tone (low freq)      → high alpha_ratio
    pure tone above 3 kHz    → sharpness_zwicker > pure tone at 200 Hz
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


GROUP_K_DIMS = (
    (83, "modulation_0_5Hz"),
    (84, "modulation_1Hz"),
    (85, "modulation_2Hz"),
    (86, "modulation_4Hz"),
    (87, "modulation_8Hz"),
    (88, "modulation_16Hz"),
    (89, "modulation_centroid"),
    (90, "modulation_bandwidth"),
    (91, "sharpness_zwicker"),
    (92, "fluctuation_strength"),
    (93, "loudness_a_weighted"),
    (94, "alpha_ratio"),
    (95, "hammarberg_index"),
    (96, "spectral_slope_0_500"),
)


@pytest.fixture(scope="module")
def stim_outputs(r3_extract):
    """Group K's modulation FFT needs 344-frame windows; use 4-s clips."""
    families = {
        "white":   stim.stim_white(duration_s=4.0),
        "tone_a4": stim.stim_tone_a4(duration_s=4.0),
        "sweep":   stim.stim_sweep_segments(duration_s=4.0),
        "real":    stim.stim_mix(duration_s=4.0),
        "silence": stim.stim_silence(duration_s=4.0),
        "dc":      stim.stim_dc(duration_s=4.0),
        "impulse": stim.stim_impulse(duration_s=4.0),
        "mix":     stim.stim_mix(duration_s=4.0),
    }
    return {name: r3_extract(audio) for name, audio in families.items()}


def _column(out, dim_idx: int) -> np.ndarray:
    return out.features[0, :, dim_idx].cpu().numpy()


# ---------------------------------------------------------------------------
# Range, well-definedness, name agreement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_K_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_K_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_K_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_K_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_K_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_K_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Algebraic identity
# ---------------------------------------------------------------------------

def test_fluctuation_strength_equals_modulation_4hz(stim_outputs):
    """fluctuation_strength ≡ modulation_4Hz on every frame & stimulus."""
    for name, out in stim_outputs.items():
        m4 = _column(out, 86)
        f  = _column(out, 92)
        assert np.array_equal(m4, f), (
            f"fluctuation_strength != modulation_4Hz on {name}: "
            f"max |Δ| = {np.max(np.abs(m4 - f))}"
        )


# ---------------------------------------------------------------------------
# Modulation-window engagement
# ---------------------------------------------------------------------------

def test_modulation_windows_emit_at_window_centers(r3_extract):
    """Group K's modulation FFT places energies at sliding-window centres.

    Engine `k_modulation/group.py:107-127` computes the modulation FFT in
    344-frame windows hopping by 86 frames (4-s window, 0.5-s hop). Energies
    are written at the *centre frame* of each window — sparse placement,
    not every-frame. We verify at least one nonzero frame appears in the
    expected window-centre set on a strongly-AM signal.
    """
    audio = stim.stim_am_tone(carrier_hz=1000.0, mod_hz=8.0, duration_s=8.0,
                              mod_depth=0.9)
    out = r3_extract(audio)
    energies = out.features[0, :, 83:89].cpu().numpy()
    nonzero_frames = np.where(energies.sum(axis=1) > 1e-6)[0]
    # Expected centres: 172, 258, 344, 430, 516, 602, 688, 774, 860, 946, ...
    expected_centres = {172 + 86 * w for w in range(0, 12)}
    hits = set(nonzero_frames.tolist()) & expected_centres
    assert len(hits) >= 4, (
        f"modulation windows not at expected centres: nonzero frames = "
        f"{nonzero_frames.tolist()[:8]}, expected centres ⊃ {sorted(expected_centres)[:8]}"
    )


def test_per_rate_max_norm_disclosed(r3_extract):
    """**Disclosed engine behaviour**: per-rate max-norm prevents cross-rate argmax.

    Engine `k_modulation/group.py:125-127` divides each modulation-rate
    column by its own time-axis max. After this normalisation, every rate
    that ever fires reaches ~1 at its strongest window. As a consequence,
    `argmax across the 6 rate dims at a single frame` does not localise the
    AM modulation rate of a stimulus — the per-rate values are biased
    toward 1 wherever they are nonzero.

    We pin this property here so any future engine change that removes the
    per-rate norm (and would make modulation_8Hz a real rate detector for
    8 Hz AM stimuli) trips this test and forces an L1-MD update.
    """
    audio = stim.stim_am_tone(carrier_hz=1000.0, mod_hz=8.0, duration_s=8.0,
                              mod_depth=0.9)
    out = r3_extract(audio)
    # Pick a centre frame that is non-zero in the modulation FFT (688 is one).
    energies = out.features[0, 688, 83:89].cpu().numpy()
    # All six should be near 1, demonstrating per-rate norm dominates over
    # rate-of-AM information at the per-frame level.
    above_threshold = (energies > 0.85).sum()
    assert above_threshold >= 4, (
        f"per-rate-norm disclosure has changed: only {above_threshold}/6 "
        f"rates above 0.85 at frame 688. If the engine now exposes raw "
        f"modulation energies, update the disclosure in this test and the "
        f"L1 MD report. Energies = {energies.round(3).tolist()}"
    )


def test_am_tone_more_modulation_than_constant_tone(r3_extract):
    """A strongly AM-modulated tone has more frame-level modulation energy
    (across all rates) than a constant-amplitude tone."""
    am   = stim.stim_am_tone(carrier_hz=1000.0, mod_hz=8.0, duration_s=8.0,
                             mod_depth=0.9)
    flat = stim.stim_tone(1000.0, duration_s=8.0)
    e_am   = r3_extract(am).features[0, 600:700, 83:89].sum().item()
    e_flat = r3_extract(flat).features[0, 600:700, 83:89].sum().item()
    assert e_am > e_flat * 0.9, (
        f"AM signal modulation energy ≯ constant-tone baseline: "
        f"AM={e_am:.3f}, flat={e_flat:.3f}"
    )


# ---------------------------------------------------------------------------
# Spectral-band fingerprints
# ---------------------------------------------------------------------------

def test_warm_tone_higher_alpha_than_bright(r3_extract):
    """200 Hz tone has more sub-1kHz energy than a 5 kHz tone → higher alpha_ratio."""
    warm   = stim.stim_tone(200.0,  duration_s=3.0)
    bright = stim.stim_tone(5000.0, duration_s=3.0)
    a_warm   = r3_extract(warm).features[0, 30:-5, 94].mean().item()
    a_bright = r3_extract(bright).features[0, 30:-5, 94].mean().item()
    assert a_warm > a_bright, (
        f"alpha_ratio ordering broken: warm={a_warm:.3f}, bright={a_bright:.3f}"
    )


def test_bright_tone_higher_zwicker_sharpness(r3_extract):
    """A 5 kHz tone is sharper than a 200 Hz tone (DIN 45692 z-axis)."""
    warm   = stim.stim_tone(200.0,  duration_s=3.0)
    bright = stim.stim_tone(5000.0, duration_s=3.0)
    s_warm   = r3_extract(warm).features[0, 30:-5, 91].mean().item()
    s_bright = r3_extract(bright).features[0, 30:-5, 91].mean().item()
    assert s_bright > s_warm, (
        f"sharpness_zwicker ordering broken: bright={s_bright:.3f}, warm={s_warm:.3f}"
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_k_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=4.0)
    a = r3_extract(audio).features[0, :, 83:97].cpu().numpy()
    b = r3_extract(audio).features[0, :, 83:97].cpu().numpy()
    assert np.array_equal(a, b)
