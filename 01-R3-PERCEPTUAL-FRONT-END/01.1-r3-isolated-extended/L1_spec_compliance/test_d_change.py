"""L1 — Spec compliance for Group D (Change, dims 21–24).

Spec, per ``Musical_Intelligence/ear/r3/groups/d_change/group.py``:

| idx | name                          | range | formula                                                   |
|-----|-------------------------------|-------|-----------------------------------------------------------|
| 21  | spectral_flux                 | [0,1] | sigmoid(10·(L2(Δmel)/√128 − 0.15)) — frame-to-frame flux |
| 22  | distribution_entropy          | [0,1] | H(p) / log(128) — Shannon, normalised, p ∝ mel           |
| 23  | distribution_flatness         | [0,1] | exp(mean log p) / mean(p) — Wiener entropy / GM-AM ratio |
| 24  | distribution_concentration    | [0,1] | (HHI − 1/N) / (1 − 1/N) — normalised Herfindahl          |

Algebraic / boundary identities:

    spectral_flux[t=0] ≡ 0 (boundary frame) → output = sigmoid(-1.5) ≈ 0.182
    distribution_entropy ∈ [0, 1] strictly (Shannon clamped against log(128))
    HHI bounds: uniform(p=1/N) → concentration = 0; single-bin → 1
    flatness: white-noise-like spectrum → flatness near 1; peaked → near 0

Behavioural fingerprints documented in the spec:

    identical-frame stream → spectral_flux ≈ baseline (no change)
    silence → entropy → 0/0 baseline (uniform tiny values gives ≈ 1)
    white noise → flatness high (broad uniform spectrum)
    pure tone   → flatness low  (single peak ⇒ peaked spectrum)
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


GROUP_D_DIMS = (
    (21, "spectral_flux"),
    (22, "distribution_entropy"),
    (23, "distribution_flatness"),
    (24, "distribution_concentration"),
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

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_D_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_D_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_D_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_D_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_D_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_D_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Boundary identity
# ---------------------------------------------------------------------------

def test_flux_first_frame_at_baseline(stim_outputs):
    """flux[t=0] ≡ 0 (engine boundary) → sigmoid(10·(0 − 0.15)) = sigmoid(-1.5) ≈ 0.182."""
    expected = 1.0 / (1.0 + np.exp(1.5))  # ≈ 0.1824
    for name, out in stim_outputs.items():
        f = _column(out, 21)
        assert abs(f[0] - expected) < 5e-3, (
            f"flux[0] != sigmoid(-1.5) on {name}: {f[0]:.4f}"
        )


# ---------------------------------------------------------------------------
# Behavioural fingerprints
# ---------------------------------------------------------------------------

def test_white_noise_higher_flatness_than_pure_tone(stim_outputs):
    """White noise has a broad spectrum (flatness ~ 1); pure tone is peaked."""
    f_white = _column(stim_outputs["white"], 23)
    f_tone  = _column(stim_outputs["tone_a4"], 23)
    assert np.median(f_white[20:]) > np.median(f_tone[20:]), (
        f"flatness ordering broken: white={np.median(f_white[20:]):.3f} "
        f"!> tone={np.median(f_tone[20:]):.3f}"
    )


def test_pure_tone_higher_concentration_than_white(stim_outputs):
    """Pure tone concentrates energy in one mel bin → high concentration."""
    c_white = _column(stim_outputs["white"], 24)
    c_tone  = _column(stim_outputs["tone_a4"], 24)
    assert np.median(c_tone[20:]) > np.median(c_white[20:])


def test_pure_tone_lower_entropy_than_white(stim_outputs):
    """Pure tone → entropy < log(128); white noise → entropy → 1."""
    e_white = _column(stim_outputs["white"], 22)
    e_tone  = _column(stim_outputs["tone_a4"], 22)
    assert np.median(e_white[20:]) > np.median(e_tone[20:])


def test_constant_input_low_steady_flux(r3_extract):
    """Constant tone (steady spectrum) → flux at boundary baseline."""
    audio = stim.stim_tone_a4(duration_s=3.0)
    f = r3_extract(audio).features[0, :, 21].cpu().numpy()
    # Steady-state flux must stay close to its sigmoid(-1.5) baseline (≈0.182)
    expected = 1.0 / (1.0 + np.exp(1.5))
    steady = f[100:-50]
    assert abs(np.median(steady) - expected) < 0.05, (
        f"steady tone flux drifted from baseline: median = {np.median(steady):.4f}"
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_d_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 21:25].cpu().numpy()
    b = r3_extract(audio).features[0, :, 21:25].cpu().numpy()
    assert np.array_equal(a, b)
