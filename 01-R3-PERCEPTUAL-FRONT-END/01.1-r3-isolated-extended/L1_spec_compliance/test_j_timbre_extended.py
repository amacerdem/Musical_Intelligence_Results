"""L1 — Spec compliance for Group J (Timbre Extended, dims 63–82).

Spec, per ``Musical_Intelligence/ear/r3/groups/j_timbre_extended/group.py``:

| idx     | name                  | range | source                                                |
|---------|-----------------------|-------|-------------------------------------------------------|
| 63–75   | mfcc_1 .. mfcc_13     | [0,1] | DCT-II of log-mel, per-coefficient affine map         |
| 76–82   | spectral_contrast_1..7| [0,1] | (peak − valley) / 10 over 7 octave-spaced mel bands  |

Algebraic identity:

    mfcc_k = ((Σ_n mel_log[n] · cos(π·k·(2n+1)/(2·N))) / scale_k + 1) / 2
    spectral_contrast_b = clamp((peak − valley) / 10, 0, 1)

Behavioural fingerprints documented in the spec:

    silence (no spectral content) → spectral_contrast → 0 (peak ≈ valley)
    pure tone (peak in one band) → spectral_contrast in that band → high
    white noise (uniform spectrum) → MFCC near baseline (sigmoid mid)
"""
from __future__ import annotations

import math
import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


GROUP_J_DIMS = tuple(
    [(63 + i, f"mfcc_{i+1}") for i in range(13)] +
    [(76 + i, f"spectral_contrast_{i+1}") for i in range(7)]
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

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_J_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_J_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_J_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_J_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_J_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_J_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# DCT-II structural identity
# ---------------------------------------------------------------------------

def test_dct_matrix_is_orthogonal_within_engine_subset(r3_extract):
    """The engine's DCT-II matrix uses Davis & Mermelstein 1980 formulation:

        D[n,k] = cos(π·(k+1)·(2n+1)/(2·N))   for n ∈ [0,128), k ∈ [0,13)

    The full 128×128 DCT-II is orthogonal; the 128×13 truncation is not
    orthogonal but has unit columns. Verify by recomputing the matrix and
    checking each column has norm √(N/2) per the standard DCT-II identity.
    """
    from Musical_Intelligence.ear.r3.groups.j_timbre_extended.group import (
        _build_dct_matrix,
    )
    M = _build_dct_matrix(128, 13).numpy()
    N = 128
    # Each column k of cos(π·(k+1)·(2n+1)/(2·N)) over n∈[0,N) has norm √(N/2)
    expected_norm = math.sqrt(N / 2.0)
    for k in range(13):
        col_norm = float(np.linalg.norm(M[:, k]))
        assert abs(col_norm - expected_norm) < 1e-4, (
            f"DCT-II column {k} norm = {col_norm:.4f}, expected √(N/2) = "
            f"{expected_norm:.4f} — DCT formula has drifted from "
            f"Davis-Mermelstein 1980."
        )


def test_silence_low_spectral_contrast(stim_outputs):
    """On silence (uniform tiny mel), peak ≈ valley → contrast → 0 after clamp."""
    for b in range(7):
        col = _column(stim_outputs["silence"], 76 + b)
        assert col.max() < 0.05, (
            f"spectral_contrast_{b+1} on silence too high: max = {col.max():.4f}"
        )


def test_pure_tone_higher_band_contrast_than_white(stim_outputs):
    """A pure tone has higher peak/valley contrast than uniform white noise.

    Pick the band most likely to contain the A4 mel bin (440 Hz ≈ mel bin 18,
    falls in band 16-32 → spectral_contrast_4 at idx 79).
    """
    c_tone  = _column(stim_outputs["tone_a4"], 79)
    c_white = _column(stim_outputs["white"], 79)
    # Steady-state median (skip first/last 5 frames).
    assert np.median(c_tone[5:-5]) > np.median(c_white[5:-5]), (
        f"contrast ordering (band 4) broken: "
        f"tone={np.median(c_tone[5:-5]):.3f}, white={np.median(c_white[5:-5]):.3f}"
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_j_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 63:83].cpu().numpy()
    b = r3_extract(audio).features[0, :, 63:83].cpu().numpy()
    assert np.array_equal(a, b)
