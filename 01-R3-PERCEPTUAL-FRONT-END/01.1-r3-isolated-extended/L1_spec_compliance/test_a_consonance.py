"""L1 — Spec compliance for Group A (Consonance, dims 00–06).

Goal of L1 (this layer)
-----------------------
Confirm the engine's output **behaves as the documented spec demands** on
eight stimulus families. This is *engine ↔ spec doc* compliance.

Independent literature re-implementations (engine ↔ original 1993 / 1965 /
1890 publications) live in L10.

Group A spec, per
``Musical_Intelligence/ear/r3/groups/a_consonance/group.py`` and the paper
§Group operator spec:

| idx | name                  | range | source                                                               |
|-----|-----------------------|-------|----------------------------------------------------------------------|
| 00  | roughness             | [0,1] | Plomp & Levelt 1965 + Sethares 1993, weighted by critical bandwidth  |
| 01  | sethares_dissonance   | [0,1] | Sethares 1993 (2nd ed.) pairwise dissonance, F0-free                 |
| 02  | helmholtz_kang        | [0,1] | Pairwise ratio simplicity (Euler 1739, Helmholtz 1863)               |
| 03  | stumpf_fusion         | [0,1] | Pairwise harmonicity (Stumpf 1890), k-tier weighted                  |
| 04  | sensory_pleasantness  | [0,1] | 0.6·(1 − sethares) + 0.4·stumpf                                      |
| 05  | inharmonicity         | [0,1] | 1 − stumpf                                                            |
| 06  | harmonic_deviation    | [0,1] | Spectral decay deviation from 1/rank                                 |

Eight stimulus axis — covers the L1 stimulus family contract.

Algebraic identities the engine **enforces by construction**
(must hold to float-precision on every frame, every stimulus):

    pleasantness  ≡ 0.6 · (1 − sethares_dissonance) + 0.4 · stumpf_fusion
    inharmonicity ≡ 1   − stumpf_fusion

Behavioural fingerprints documented in the spec:

    silence              → all 7 dims well-defined, no NaN/Inf.
    pure tone (single F) → no pairs ⇒ low sethares & roughness,
                           pleasantness pulled by stumpf=1 (no beating).
    perfect-octave dyad  → stumpf high (k=1 tier), inharmonicity low.
    minor-second dyad    → strong roughness peak at Δf/CB ≈ 0.25.

This file is the template; one ``.md`` report per dim accompanies it.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


# ---------------------------------------------------------------------------
# L1 stimulus axis — the eight families
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def stim_outputs(r3_extract):
    """Run the engine on each of the eight L1 stimulus families once."""
    families = {
        "white":   stim.stim_white(duration_s=3.0),
        "tone_a4": stim.stim_tone_a4(duration_s=3.0),
        "sweep":   stim.stim_sweep_segments(duration_s=3.0),
        "real":    stim.stim_mix(duration_s=3.0),  # fallback if no real audio
        "silence": stim.stim_silence(duration_s=3.0),
        "dc":      stim.stim_dc(duration_s=3.0),
        "impulse": stim.stim_impulse(duration_s=3.0),
        "mix":     stim.stim_mix(duration_s=3.0),
    }
    return {name: r3_extract(audio) for name, audio in families.items()}


def _column(out, dim_idx: int) -> np.ndarray:
    """Return the (T,) numpy column for dim *dim_idx* (batch=1)."""
    return out.features[0, :, dim_idx].cpu().numpy()


def _all_columns(stim_outputs, dim_idx: int) -> dict:
    return {name: _column(out, dim_idx) for name, out in stim_outputs.items()}


# ---------------------------------------------------------------------------
# Per-dim well-formedness — applies to every Group A dim across 8 stimuli
# ---------------------------------------------------------------------------

GROUP_A_DIMS = (
    (0, "roughness"),
    (1, "sethares_dissonance"),
    (2, "helmholtz_kang"),
    (3, "stumpf_fusion"),
    (4, "sensory_pleasantness"),
    (5, "inharmonicity"),
    (6, "harmonic_deviation"),
)


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_A_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_A_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    """Every Group A dim ∈ [0, 1] on every L1 stimulus family."""
    cols = _all_columns(stim_outputs, dim_idx)
    for name, col in cols.items():
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}: non-finite value"
        assert col.min() >= -1e-7, f"{dim_name} on {name}: min = {col.min()} < 0"
        assert col.max() <= 1.0 + 1e-7, f"{dim_name} on {name}: max = {col.max()} > 1"


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_A_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_A_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    """Silence input must produce a well-defined Group A column."""
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_A_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_A_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    """The canonical dim registry agrees with this file's GROUP_A_DIMS."""
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Algebraic identities the engine **enforces by construction**
# ---------------------------------------------------------------------------

def test_pleasantness_identity(stim_outputs):
    """pleasantness ≡ 0.6 · (1 − sethares) + 0.4 · stumpf — every frame, every stimulus."""
    for name, out in stim_outputs.items():
        roughness, sethares, helmholtz, stumpf, pleasantness, inh, hdev = (
            _column(out, i) for i in range(7)
        )
        expected = 0.6 * (1.0 - sethares) + 0.4 * stumpf
        # Engine clamps to [0,1]; identity holds when expected is already in range.
        clipped_expected = np.clip(expected, 0.0, 1.0)
        assert np.allclose(pleasantness, clipped_expected, atol=1e-6), (
            f"pleasantness identity broken on {name}: max |Δ| = "
            f"{np.max(np.abs(pleasantness - clipped_expected)):.3e}"
        )


def test_inharmonicity_identity(stim_outputs):
    """inharmonicity ≡ 1 − stumpf_fusion — every frame, every stimulus."""
    for name, out in stim_outputs.items():
        stumpf = _column(out, 3)
        inh = _column(out, 5)
        expected = np.clip(1.0 - stumpf, 0.0, 1.0)
        assert np.allclose(inh, expected, atol=1e-6), (
            f"inharmonicity identity broken on {name}: max |Δ| = "
            f"{np.max(np.abs(inh - expected)):.3e}"
        )


# ---------------------------------------------------------------------------
# Behavioural fingerprints
# ---------------------------------------------------------------------------

def test_silence_low_dissonance(stim_outputs):
    """On silence, sethares dissonance is low (no peaks ⇒ no pairs ⇒ no beating)."""
    sethares_silence = _column(stim_outputs["silence"], 1)
    # Engine's sigmoid baseline at zero input ≈ sigmoid(-2) ≈ 0.119.
    assert sethares_silence.mean() < 0.2, (
        f"sethares on silence too high: mean = {sethares_silence.mean():.3f}"
    )


def test_silence_low_roughness(stim_outputs):
    """On silence, roughness is low."""
    rough_silence = _column(stim_outputs["silence"], 0)
    # Same sigmoid baseline ⇒ ≤ 0.2.
    assert rough_silence.mean() < 0.2


def test_pure_tone_low_sethares(stim_outputs):
    """A pure 440 Hz tone has only one peak — no beating partials."""
    sethares_tone = _column(stim_outputs["tone_a4"], 1)
    # Allow startup transients for a few frames; check steady-state median.
    steady = sethares_tone[20:]
    assert np.median(steady) < 0.3, (
        f"sethares on pure A4 too high: median = {np.median(steady):.3f}"
    )


def test_pure_tone_high_stumpf(stim_outputs):
    """No-beating ⇒ stumpf returns to its no-beating ceiling (1.0 → sigmoid clamp)."""
    stumpf_tone = _column(stim_outputs["tone_a4"], 3)
    # Engine's continuous blend: little beating → fallback 1.0.
    steady = stumpf_tone[20:]
    assert np.median(steady) > 0.85, (
        f"stumpf on pure tone too low: median = {np.median(steady):.3f}"
    )


def test_octave_dyad_more_consonant_than_minor_second(r3_extract):
    """Perfect-octave dyad is *more* consonant than a minor-second dyad.

    Direction-of-effect test, not a magnitude claim. Mirrors a structural
    spec property: the engine's stumpf_fusion / pleasantness must order
    these two stimuli correctly.
    """
    octave = stim.stim_dyad(220.0, (1, 2))      # 220 Hz + 440 Hz
    minor2 = stim.stim_dyad(220.0, (15, 16))    # 220 Hz + ~234.7 Hz
    out_oct = r3_extract(octave)
    out_m2  = r3_extract(minor2)
    # Use steady frames (20..end-5 to dodge clip boundaries)
    steady = slice(20, -5)
    pleasantness_oct = out_oct.features[0, steady, 4].mean().item()
    pleasantness_m2  = out_m2.features[0, steady, 4].mean().item()
    sethares_oct = out_oct.features[0, steady, 1].mean().item()
    sethares_m2  = out_m2.features[0, steady, 1].mean().item()
    assert pleasantness_oct > pleasantness_m2, (
        f"pleasantness ordering broken: oct={pleasantness_oct:.3f} "
        f"!> m2={pleasantness_m2:.3f}"
    )
    assert sethares_oct < sethares_m2, (
        f"sethares ordering broken: oct={sethares_oct:.3f} "
        f"!< m2={sethares_m2:.3f}"
    )


def test_harmonic_dyad_low_inharmonicity(r3_extract):
    """A perfect-fifth harmonic dyad is more harmonic (low inh) than random noise."""
    fifth = stim.stim_dyad(220.0, (2, 3))  # 220 + 330 Hz
    noise = stim.stim_white(duration_s=stim.DEFAULT_DURATION_S)
    out_fifth = r3_extract(fifth)
    out_noise = r3_extract(noise)
    steady = slice(20, -5)
    inh_fifth = out_fifth.features[0, steady, 5].mean().item()
    inh_noise = out_noise.features[0, steady, 5].mean().item()
    assert inh_fifth < inh_noise, (
        f"inharmonicity ordering broken: fifth={inh_fifth:.3f} "
        f"!< noise={inh_noise:.3f}"
    )


# ---------------------------------------------------------------------------
# Determinism — same audio → bit-identical output
# ---------------------------------------------------------------------------

def test_group_a_bit_identical_across_runs(r3_extract):
    """Running the same audio twice produces bit-identical Group A output."""
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 0:7].cpu().numpy()
    b = r3_extract(audio).features[0, :, 0:7].cpu().numpy()
    assert np.array_equal(a, b), (
        f"Group A non-deterministic across runs: max |Δ| = {np.max(np.abs(a - b))}"
    )
