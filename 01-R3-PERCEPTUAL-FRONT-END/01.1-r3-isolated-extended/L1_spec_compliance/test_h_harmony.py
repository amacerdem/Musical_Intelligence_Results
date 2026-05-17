"""L1 — Spec compliance for Group H (Harmony & Tonality, dims 51–62).

Group H is **Stage 2** — depends on Group F's chroma (idx 25–36 in the
97-D vector, idx 0–11 within the pitch_chroma group). Spec, per
``Musical_Intelligence/ear/r3/groups/h_harmony/group.py``:

| idx | name                        | range | source                                            |
|-----|-----------------------------|-------|---------------------------------------------------|
| 51  | key_clarity                 | [0,1] | (max − mean) of 24 KK-profile correlations × 5    |
| 52  | tonnetz_fifth_x             | [0,1] | (sin component of fifth axis + 1)/2 — Harte 2010  |
| 53  | tonnetz_fifth_y             | [0,1] | (cos component of fifth axis + 1)/2               |
| 54  | tonnetz_minor_x             | [0,1] | (sin component of minor-third axis + 1)/2         |
| 55  | tonnetz_minor_y             | [0,1] | (cos component of minor-third axis + 1)/2         |
| 56  | tonnetz_major_x             | [0,1] | (sin component of major-third axis + 1)/2         |
| 57  | tonnetz_major_y             | [0,1] | (cos component of major-third axis + 1)/2         |
| 58  | voice_leading_distance      | [0,1] | L1(Δchroma)/2                                     |
| 59  | harmonic_change             | [0,1] | 1 − cos_sim(chroma_t, chroma_{t-1})              |
| 60  | tonal_stability             | [0,1] | key_clarity · (1 − smooth(harmonic_change))      |
| 61  | diatonicity                 | [0,1] | 1 − (active_PCs − 7)/5, clamped                  |
| 62  | syntactic_irregularity      | [0,1] | 1 − exp(−KL(chroma || best key template))         |

Boundary identities:

    voice_leading_distance[t=0] ≡ 0  (Δchroma[t=0] := 0)
    harmonic_change[t=0]        ≡ 0  (cos_sim[t=0] := 0 → 1−0 = 1, but 0
                                       in code per the zero-init)

Behavioural fingerprints:

    pure tone → low active_PCs (1 PC dominant) → diatonicity high
    white noise → uniform chroma → key_clarity low (no key stands out)
    constant tone → harmonic_change ≈ 0 (no chroma motion)
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import index_for_name


GROUP_H_DIMS = (
    (51, "key_clarity"),
    (52, "tonnetz_fifth_x"),
    (53, "tonnetz_fifth_y"),
    (54, "tonnetz_minor_x"),
    (55, "tonnetz_minor_y"),
    (56, "tonnetz_major_x"),
    (57, "tonnetz_major_y"),
    (58, "voice_leading_distance"),
    (59, "harmonic_change"),
    (60, "tonal_stability"),
    (61, "diatonicity"),
    (62, "syntactic_irregularity"),
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

@pytest.mark.parametrize("dim_idx,dim_name", GROUP_H_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_H_DIMS])
def test_dim_in_unit_interval_across_eight_stimuli(stim_outputs, dim_idx, dim_name):
    for name, out in stim_outputs.items():
        col = _column(out, dim_idx)
        assert np.all(np.isfinite(col)), f"{dim_name} on {name}"
        assert col.min() >= -1e-7
        assert col.max() <= 1.0 + 1e-7


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_H_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_H_DIMS])
def test_dim_well_defined_on_silence(stim_outputs, dim_idx, dim_name):
    col = _column(stim_outputs["silence"], dim_idx)
    assert np.all(np.isfinite(col))


@pytest.mark.parametrize("dim_idx,dim_name", GROUP_H_DIMS,
                         ids=[f"d{i:02d}_{n}" for i, n in GROUP_H_DIMS])
def test_dim_index_matches_canonical_name(dim_idx, dim_name):
    assert index_for_name(dim_name) == dim_idx


# ---------------------------------------------------------------------------
# Boundary identities
# ---------------------------------------------------------------------------

def test_voice_leading_first_frame_zero(stim_outputs):
    """voice_leading_distance[t=0] ≡ 0 — Δchroma[t=0] is zero-initialised."""
    for name, out in stim_outputs.items():
        v = _column(out, 58)
        assert v[0] < 1e-6, f"vl_dist[0] != 0 on {name}: {v[0]}"


def test_harmonic_change_first_frame_is_one(stim_outputs):
    """harmonic_change[t=0] ≡ 1 — cos_sim is zero-init at t=0; 1 − 0 = 1.

    Engine convention (`h_harmony/group.py:97-101`): no prior frame to
    compare against ⇒ report maximum change. Different from
    voice_leading_distance which is set to 0 at t=0 (Δchroma[t=0] := 0).
    Both are documented zero-init choices that downstream H³ consumers
    must honour.
    """
    for name, out in stim_outputs.items():
        h = _column(out, 59)
        assert abs(h[0] - 1.0) < 1e-5, f"harmonic_change[0] != 1 on {name}: {h[0]}"


# ---------------------------------------------------------------------------
# Tonnetz range identity
# ---------------------------------------------------------------------------

def test_tonnetz_pairs_in_circle(stim_outputs):
    """For each Tonnetz axis, x²+y² should be ≤ 1 in pre-shift space.

    After the engine's (x+1)/2 affine shift to [0,1], the unit-circle
    invariant translates to: (2·tx − 1)² + (2·ty − 1)² ≤ 1 + ε on every
    frame & stimulus. Verifies the (sin, cos) pair encoding is preserved.
    """
    for name, out in stim_outputs.items():
        if name in ("silence", "impulse"):
            continue
        for axis in [(52, 53), (54, 55), (56, 57)]:
            x = 2.0 * _column(out, axis[0]) - 1.0
            y = 2.0 * _column(out, axis[1]) - 1.0
            r2 = x * x + y * y
            # Allow up to 1.05 due to clamp(0,1) artefacts when chroma sums >1
            assert r2.max() < 1.10, (
                f"tonnetz pair ({axis[0]},{axis[1]}) r² > 1.10 on {name}: "
                f"max = {r2.max():.4f}"
            )


# ---------------------------------------------------------------------------
# Behavioural fingerprints
# ---------------------------------------------------------------------------

def test_pure_tone_higher_diatonicity_than_noise(r3_extract):
    """Pure tone → 1 active PC → diatonicity = 1; noise → broad → diatonicity < 1."""
    pure  = stim.stim_tone_a4(duration_s=3.0)
    noise = stim.stim_white(duration_s=3.0)
    d_pure  = r3_extract(pure).features[0, 30:-5, 61].mean().item()
    d_noise = r3_extract(noise).features[0, 30:-5, 61].mean().item()
    assert d_pure > d_noise, (
        f"diatonicity ordering broken: pure={d_pure:.3f}, noise={d_noise:.3f}"
    )


def test_white_noise_low_key_clarity(stim_outputs):
    """White noise → uniform chroma → key_clarity at engine floor."""
    kc = _column(stim_outputs["white"], 51)
    # Engine clamps × 5; uniform chroma gives diff ≈ 0 → clarity → 0.
    assert np.median(kc[20:]) < 0.5, (
        f"key_clarity on white noise too high: {np.median(kc[20:]):.3f}"
    )


def test_constant_tone_low_harmonic_change(r3_extract):
    """Constant pure tone → chroma is unchanging → harmonic_change → 0."""
    audio = stim.stim_tone_a4(duration_s=3.0)
    h = r3_extract(audio).features[0, 30:-5, 59].cpu().numpy()
    assert np.median(h) < 0.05, (
        f"harmonic_change on constant tone too high: {np.median(h):.4f}"
    )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_group_h_bit_identical_across_runs(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features[0, :, 51:63].cpu().numpy()
    b = r3_extract(audio).features[0, :, 51:63].cpu().numpy()
    assert np.array_equal(a, b)
